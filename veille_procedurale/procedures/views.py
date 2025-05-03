from django.shortcuts import get_object_or_404, render, redirect
from .models import Procedure, ProcedureRevision, ActivityDetail , ProcedureReadStatus, ProcedureNotification
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.utils import timezone
from .decorators import quality_cell_required
from .utils import send_procedure_notification

@login_required
@quality_cell_required
def create_procedure(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        bpmn_diagram = request.POST.get('bpmn_diagram')
        concerned_users = request.POST.getlist('concerned_users')

        procedure = Procedure.objects.create(
            title=title,
            description=description,
            bpmn_diagram=bpmn_diagram,
            created_by=request.user
        )
        procedure.concerned_users.set(concerned_users)

        # Send notifications to concerned users
        concerned_users = User.objects.filter(id__in=concerned_users)
        message = f"Une nouvelle procédure '{procedure.title}' vous a été assignée."
        send_procedure_notification(procedure, concerned_users, 'new', message)

        # Save activity details
        activity_details = json.loads(request.POST.get('activity_details', '{}'))
        for activity_id, details in activity_details.items():
            ActivityDetail.objects.create(
                procedure=procedure,
                activity_id=activity_id,
                name=details['name'],
                description=details['description'],
                responsible_id=details['responsible'],
            )

        return redirect('procedures:procedure_success')

    # Filter users to show only regular users
    users = User.objects.filter(profile__user_type='regular').exclude(id=request.user.id)
    return render(request, 'procedures/create.html', {'users': users})

def procedure_success(request):
    return render(request, 'procedures/success.html')

def home(request):
    context = {}
    
    if request.user.is_authenticated:
        if request.user.profile.is_quality_cell():
            # Stats pour la cellule qualité
            context.update({
                'total_procedures': Procedure.objects.count(),
                'active_users': User.objects.filter(profile__user_type='regular').count(),
                'signed_procedures': ProcedureReadStatus.objects.filter(is_signed=True).count()
            })
        else:
            # Stats pour les utilisateurs normaux
            user_procedures = Procedure.objects.filter(concerned_users=request.user)
            context.update({
                'total_procedures': user_procedures.count(),
                'read_procedures': ProcedureReadStatus.objects.filter(
                    user=request.user,
                    is_read=True
                ).count(),
                'signed_procedures': ProcedureReadStatus.objects.filter(
                    user=request.user,
                    is_signed=True
                ).count()
            })
    
    return render(request, 'procedures/home.html', context)

@login_required
@quality_cell_required
def procedure_list(request):
    procedure_list = Procedure.objects.all().order_by('-created_at')
    paginator = Paginator(procedure_list, 9)  # 9 procedures per page
    page = request.GET.get('page')
    procedures = paginator.get_page(page)
    return render(request, 'procedures/list.html', {'procedures': procedures})

@login_required
def procedure_detail(request, pk):
    procedure = get_object_or_404(Procedure, pk=pk)
    
    # Check if user has access
    if not request.user.profile.is_quality_cell() and request.user not in procedure.concerned_users.all():
        messages.error(request, "Vous n'avez pas accès à cette procédure.")
        return redirect('procedures:my_procedures')

    # Update read status automatically when viewing details
    if not request.user.profile.is_quality_cell():
        read_status, created = ProcedureReadStatus.objects.get_or_create(
            user=request.user,
            procedure=procedure
        )
        
        # Mark as read if not already read
        if not read_status.is_read:
            read_status.is_read = True
            read_status.read_date = timezone.now()
            read_status.save()

    return render(request, 'procedures/detail.html', {
        'procedure': procedure,
        'concerned_users': procedure.concerned_users.all()
    })

@login_required
@quality_cell_required
def procedure_edit(request, pk):
    procedure = get_object_or_404(Procedure, pk=pk)
    
    if request.method == 'POST':
        try:
            # Create revision with current state
            ProcedureRevision.objects.create(
                procedure=procedure,
                version=procedure.revisions.count() + 1,
                title=procedure.title,
                description=procedure.description,
                bpmn_diagram=procedure.bpmn_diagram,
                modified_by=request.user,
                change_description=request.POST.get('change_description', '').strip()
            )

            # Update procedure basic info
            procedure.title = request.POST.get('title')
            procedure.description = request.POST.get('description')
            procedure.bpmn_diagram = request.POST.get('bpmn_diagram')
            
            # Get user IDs and convert to list of integers
            new_user_ids = [int(id) for id in request.POST.getlist('concerned_users')]
            
            # Get user querysets
            old_users = set(procedure.concerned_users.all())
            new_users = set(User.objects.filter(id__in=new_user_ids))
            
            # First, update the M2M relationship
            procedure.concerned_users.set(new_user_ids)
            procedure.save()
            
            # Then handle notifications and read status
            completely_new_users = new_users - old_users
            existing_users = new_users & old_users
            
            if completely_new_users:
                new_message = f"La procédure '{procedure.title}' vous a été assignée."
                send_procedure_notification(procedure, completely_new_users, 'new', new_message)
            
            if existing_users:
                update_message = f"La procédure '{procedure.title}' a été mise à jour."
                send_procedure_notification(procedure, existing_users, 'update', update_message)
            
            # Reset read status for existing users
            ProcedureReadStatus.objects.filter(
                procedure=procedure,
                user__in=existing_users
            ).update(
                is_read=False,
                is_signed=False,
                read_date=None,
                signed_date=None
            )
            
            # Create read status for new users
            new_statuses = [
                ProcedureReadStatus(
                    user=user,
                    procedure=procedure,
                    is_read=False,
                    is_signed=False
                ) for user in completely_new_users
            ]
            if new_statuses:
                ProcedureReadStatus.objects.bulk_create(new_statuses)

            # Update activity details
            activity_details = json.loads(request.POST.get('activity_details', '{}'))
            
            # Delete existing activities
            procedure.activities.all().delete()
            
            # Create new activities
            for activity_id, details in activity_details.items():
                ActivityDetail.objects.create(
                    procedure=procedure,
                    activity_id=activity_id,
                    name=details['name'],
                    description=details.get('description', ''),
                    responsible_id=details.get('responsible')
                )
            
            messages.success(request, "Procédure mise à jour avec succès.")
            return redirect('procedures:detail', pk=pk)
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
    
    # Pour le GET request, montrer seulement les utilisateurs réguliers
    users = User.objects.exclude(id=request.user.id).filter(profile__user_type='regular')
    return render(request, 'procedures/edit.html', {
        'procedure': procedure,
        'users': users
    })

@login_required
@quality_cell_required
def procedure_delete(request, pk):
    procedure = get_object_or_404(Procedure, pk=pk)
    
    # Vérifier si l'utilisateur est le créateur
    if procedure.created_by != request.user:
        return redirect('procedures:detail', pk=pk)

    if request.method == 'POST':
        procedure.delete()
        return redirect('procedures:list')
    
    return redirect('procedures:detail', pk=pk)

@login_required
def my_procedures(request):
    # Récupérer les procédures où l'utilisateur est concerné
    procedures = Procedure.objects.filter(concerned_users=request.user)
    read_status = {
        status.procedure_id: status 
        for status in ProcedureReadStatus.objects.filter(user=request.user)
    }
    
    return render(request, 'procedures/my_procedures.html', {
        'procedures': procedures,
        'read_status': read_status
    })

@login_required
def mark_as_read(request, pk):
    procedure = get_object_or_404(Procedure, pk=pk)
    if request.user not in procedure.concerned_users.all():
        messages.error(request, "Vous n'avez pas accès à cette procédure.")
        return redirect('procedures:my_procedures')

    status, created = ProcedureReadStatus.objects.get_or_create(
        user=request.user,
        procedure=procedure
    )
    
    if request.method == 'POST':
        status.is_read = True
        status.read_date = timezone.now()
        status.signature_data = request.POST.get('signature_data')
        status.is_signed = True
        status.signed_date = timezone.now()
        status.save()
        
        messages.success(request, "Procédure marquée comme lue et signée.")
        return redirect('procedures:my_procedures')

    return render(request, 'procedures/sign_procedure.html', {
        'procedure': procedure,
        'status': status
    })

@login_required
def notifications(request):
    notifications = ProcedureNotification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Mark notifications as read
    notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'procedures/notifications.html', {
        'notifications': notifications
    })

@login_required
@quality_cell_required
def procedure_tracking(request, pk):
    procedure = get_object_or_404(Procedure, pk=pk)
    
    # Get all users concerned by this procedure
    concerned_users = procedure.concerned_users.all()
    
    # Get read/sign status for each user
    tracking_data = []
    for user in concerned_users:
        status = ProcedureReadStatus.objects.filter(
            procedure=procedure,
            user=user
        ).first()
        
        tracking_data.append({
            'user': user,
            'is_read': status.is_read if status else False,
            'read_date': status.read_date if status else None,
            'is_signed': status.is_signed if status else False,
            'signed_date': status.signed_date if status else None,
        })

    context = {
        'procedure': procedure,
        'tracking_data': tracking_data,
        'total_users': len(concerned_users),
        'read_count': sum(1 for data in tracking_data if data['is_read']),
        'signed_count': sum(1 for data in tracking_data if data['is_signed']),
    }
    
    return render(request, 'procedures/tracking.html', context)