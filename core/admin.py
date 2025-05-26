from django.contrib import admin
from .models import Session, Task

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'creator', 'get_participants', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('id', 'participants__username')

    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'text', 'user', 'is_done', 'created_at', 'updated_at')
    list_filter = ('is_done', 'created_at', 'updated_at')
    search_fields = ('id', 'text', 'session__id')
