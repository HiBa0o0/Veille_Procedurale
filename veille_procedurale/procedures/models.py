from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Procedure(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    bpmn_diagram = models.TextField()  # XML du diagramme BPMN
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    concerned_users = models.ManyToManyField(User, related_name='concerned_procedures', blank=True) 

    def __str__(self):
        return self.title

class ProcedureRevision(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='revisions')
    version = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    bpmn_diagram = models.TextField()
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now_add=True)
    change_description = models.TextField(help_text="Description des modifications apportées")

    class Meta:
        ordering = ['-version']

class ActivityDetail(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='activities')
    activity_id = models.CharField(max_length=100)  # BPMN element ID
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)  # Optional
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Optional

    class Meta:
        unique_together = ['procedure', 'activity_id']

    def __str__(self):
        return self.name

class ProcedureReadStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='procedure_reads')
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='read_status')
    is_read = models.BooleanField(default=False)
    read_date = models.DateTimeField(null=True, blank=True)
    is_signed = models.BooleanField(default=False)
    signed_date = models.DateTimeField(null=True, blank=True)
    signature_data = models.TextField(null=True, blank=True)  # Pour stocker la signature

    class Meta:
        unique_together = ['user', 'procedure']

class ProcedureNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('new', 'Nouvelle procédure'),
        ('update', 'Mise à jour procédure'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='procedure_notifications')
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} pour {self.user.username}"

class UserProfile(models.Model):
    USER_TYPES = (
        ('quality', 'Cellule de qualité'),
        ('regular', 'Utilisateur normal'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='regular')

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

    def is_quality_cell(self):
        return self.user_type == 'quality'