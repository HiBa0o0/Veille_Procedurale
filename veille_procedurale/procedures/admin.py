from django.contrib import admin
from .models import UserProfile, Procedure, ProcedureRevision, ActivityDetail, ProcedureNotification

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'user__email')

@admin.register(ProcedureNotification)
class ProcedureNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'procedure', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'procedure__title', 'message')

# Register your models here.
