from django.db import models
from django.contrib.auth.models import User

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
