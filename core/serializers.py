from rest_framework import serializers
from .models import Session, Task
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class SessionSerializer(serializers.ModelSerializer):
    creator_username = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()
    participants = ParticipantSerializer(source='participants.all', many=True, read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'uuid', 'name', 'creator', 'creator_username', 'participants', 'participants_count', 'created_at']

    def get_creator_username(self, obj):
        return obj.creator.username if obj.creator else None

    def get_participants_count(self, obj):
        return obj.participants.count()

class TaskSerializer(serializers.ModelSerializer):
    session_uuid = serializers.UUIDField(source='session.uuid', read_only=True)
    creator_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'session', 'session_uuid', 'user', 'creator_username', 'text', 'is_done', 'created_at', 'updated_at']
