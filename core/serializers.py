from rest_framework import serializers
from .models import Session, Task
from django.contrib.auth.models import User

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'user1', 'user2', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'session', 'text', 'is_done', 'created_at', 'updated_at']
