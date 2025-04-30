from rest_framework import serializers
from .models import Session, Task
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class SessionSerializer(serializers.ModelSerializer):
    user1_username = serializers.SerializerMethodField()
    user2_username = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ['id', 'name', 'user1', 'user2', 'user1_username', 'user2_username', 'created_at']

    def get_user1_username(self, obj):
        return obj.user1.username

    def get_user2_username(self, obj):
        return obj.user2.username

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'session', 'user', 'text', 'is_done', 'created_at', 'updated_at']
