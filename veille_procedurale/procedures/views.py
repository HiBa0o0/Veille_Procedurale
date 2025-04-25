from django.shortcuts import get_object_or_404, render, redirect
from .models import Procedure, ProcedureRevision, ActivityDetail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
import json

@login_required
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

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'procedures/create.html', {'users': users})

def procedure_success(request):
    return render(request, 'procedures/success.html')

def home(request):
    return render(request, 'procedures/home.html')

def procedure_list(request):
    procedure_list = Procedure.objects.all().order_by('-created_at')
    paginator = Paginator(procedure_list, 9)  # 9 procedures per page
    page = request.GET.get('page')
    procedures = paginator.get_page(page)
    return render(request, 'procedures/list.html', {'procedures': procedures})

def procedure_detail(request, pk):
    procedure = get_object_or_404(Procedure, pk=pk)
    return render(request, 'procedures/detail.html', {
        'procedure': procedure,
        'concerned_users': procedure.concerned_users.all()
    })

@login_required
def procedure_edit(request, pk):
    procedure = get_object_or_404(Procedure, pk=pk)
    
    if procedure.created_by != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette procédure.")
        return redirect('procedures:detail', pk=pk)

    if request.method == 'POST':
        change_description = request.POST.get('change_description', '').strip()
        
        if not change_description:
            messages.error(request, "La description des modifications est obligatoire.")
            return render(request, 'procedures/edit.html', {
                'procedure': procedure,
                'users': User.objects.exclude(id=request.user.id)
            })

        try:
            # Create revision with current state
            ProcedureRevision.objects.create(
                procedure=procedure,
                version=procedure.revisions.count() + 1,
                title=procedure.title,
                description=procedure.description,
                bpmn_diagram=procedure.bpmn_diagram,
                modified_by=request.user,
                change_description=change_description
            )

            # Update procedure
            procedure.title = request.POST.get('title')
            procedure.description = request.POST.get('description')
            procedure.bpmn_diagram = request.POST.get('bpmn_diagram')
            procedure.concerned_users.set(request.POST.getlist('concerned_users'))
            
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
            
            procedure.save()

            messages.success(request, "Procédure mise à jour avec succès.")
            return redirect('procedures:detail', pk=pk)
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
            
    return render(request, 'procedures/edit.html', {
        'procedure': procedure,
        'users': User.objects.exclude(id=request.user.id)
    })

@login_required
def procedure_delete(request, pk):
    procedure = get_object_or_404(Procedure, pk=pk)
    
    # Vérifier si l'utilisateur est le créateur
    if procedure.created_by != request.user:
        return redirect('procedures:detail', pk=pk)

    if request.method == 'POST':
        procedure.delete()
        return redirect('procedures:list')
    
    return redirect('procedures:detail', pk=pk)