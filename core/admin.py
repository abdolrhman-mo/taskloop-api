from django.contrib import admin
from .models import Session, Task

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('id', 'user1__username', 'user2__username')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'text', 'is_done', 'created_at', 'updated_at')
    list_filter = ('is_done', 'created_at', 'updated_at')
    search_fields = ('id', 'text', 'session__id')
