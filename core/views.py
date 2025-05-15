from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db import models
from django.contrib.auth.models import User
from .models import Session, Task
from .serializers import SessionSerializer, TaskSerializer, UserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets

# Define request/response schemas
session_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'session_id': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

task_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'text': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

# Define token parameter
token_param = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="Token auth: Token <your_token>",
    type=openapi.TYPE_STRING
)

class CreateSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user2_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Session name')
            },
            required=['user2_id', 'name']
        ),
        responses={201: session_response_schema, 400: 'Bad Request'}
    )
    def post(self, request):
        user1 = request.user
        user2_id = request.data.get('user2_id')
        name = request.data.get('name')

        if not user2_id:
            return Response({'error': 'user2_id is required'}, status=400)

        if not name:
            return Response({'error': 'Session name is required'}, status=400)

        session = Session.objects.create(user1=user1, user2_id=user2_id, name=name)
        return Response({'session_id': str(session.id)}, status=201)

class SessionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        responses={200: SessionSerializer, 404: 'Not Found'}
    )
    def get(self, request, id):
        session = get_object_or_404(Session, id=id)
        serializer = SessionSerializer(session)
        return Response(serializer.data)

class UserSessionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        responses={200: SessionSerializer(many=True)}
    )
    def get(self, request):
        sessions = Session.objects.filter(models.Q(user1=request.user) | models.Q(user2=request.user))
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)

class TaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        responses={200: TaskSerializer(many=True), 403: 'Forbidden', 404: 'Not Found'}
    )
    def get(self, request, id):
        session = get_object_or_404(Session, id=id)
        if request.user != session.user1 and request.user != session.user2:
            return Response({'error': 'Not authorized'}, status=403)
        tasks = session.tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class AddTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, description='Task description'),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user assigned to the task')
            },
            required=['text', 'user_id']
        ),
        responses={201: TaskSerializer, 400: 'Bad Request', 403: 'Forbidden', 404: 'Not Found'}
    )
    def post(self, request, id):
        session = get_object_or_404(Session, id=id)
        
        # Ensure the requester is part of the session
        if request.user != session.user1 and request.user != session.user2:
            return Response({'error': 'Not authorized to add tasks to this session'}, status=403)

        # Validate text
        text = request.data.get('text')
        if not text:
            return Response({'error': 'Task text is required'}, status=400)

        # Validate user_id
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'Task owner (user_id) is required'}, status=400)

        # Verify the user exists and is part of the session
        try:
            user = User.objects.get(id=user_id)
            
            # Check if the user is part of the session
            if user != session.user1 and user != session.user2:
                return Response({'error': 'Task owner must be a participant in the session'}, status=403)

            # Create the task
            task = Task.objects.create(session=session, text=text, user=user)
            serializer = TaskSerializer(task)
            return Response(serializer.data, status=201)

        except User.DoesNotExist:
            return Response({'error': 'Invalid user ID'}, status=404)

class UpdateTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'is_done': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            }
        ),
        responses={200: TaskSerializer, 403: 'Forbidden', 404: 'Not Found'}
    )
    def put(self, request, id, taskId):
        session = get_object_or_404(Session, id=id)
        task = get_object_or_404(Task, id=taskId, session=session)

        if request.user != session.user1 and request.user != session.user2:
            return Response({'error': 'Not authorized'}, status=403)

        task.is_done = request.data.get('is_done', task.is_done)
        task.save()
        return Response(TaskSerializer(task).data)

class DeleteTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        responses={200: '{"deleted": true}', 403: 'Forbidden', 404: 'Not Found'}
    )
    def delete(self, request, id, taskId):
        session = get_object_or_404(Session, id=id)
        task = get_object_or_404(Task, id=taskId, session=session)

        if request.user != session.user1 and request.user != session.user2:
            return Response({'error': 'Not authorized'}, status=403)

        task.delete()
        return Response({'deleted': True})

class ListUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request):
        """
        List all users except the current user.
        Requires authentication.
        """
        users = User.objects.exclude(id=request.user.id)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class SessionManagementView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='New session name'),
            }
        ),
        responses={200: SessionSerializer, 403: 'Forbidden', 404: 'Not Found'}
    )
    def put(self, request, id):
        """
        Update session details.
        Requires authentication and session ownership.
        """
        session = get_object_or_404(Session, id=id)
        
        # Check if user is part of the session
        if request.user != session.user1 and request.user != session.user2:
            return Response({'error': 'Not authorized'}, status=403)

        # Update session name if provided
        name = request.data.get('name')
        if name:
            session.name = name
            session.save()

        serializer = SessionSerializer(session)
        return Response(serializer.data)

    @swagger_auto_schema(
        manual_parameters=[token_param],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'session_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            ),
            403: 'Forbidden',
            404: 'Not Found'
        }
    )
    def delete(self, request, id):
        """
        Delete a session.
        Requires authentication and session ownership.
        Returns a success message with the deleted session ID.
        """
        session = get_object_or_404(Session, id=id)
        
        # Check if user is part of the session
        if request.user != session.user1 and request.user != session.user2:
            return Response({'error': 'Not authorized'}, status=403)

        session_id = session.id
        session.delete()
        return Response({
            'message': 'Session deleted successfully',
            'session_id': session_id
        }, status=status.HTTP_200_OK)

class SessionParticipantsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        responses={200: UserSerializer(many=True), 403: 'Forbidden', 404: 'Not Found'}
    )
    def get(self, request, id):
        """
        Get session participants.
        Requires authentication and session membership.
        """
        session = get_object_or_404(Session, id=id)
        
        # Check if user is part of the session
        if request.user != session.user1 and request.user != session.user2:
            return Response({'error': 'Not authorized'}, status=403)

        # Get both participants
        participants = [session.user1, session.user2]
        serializer = UserSerializer(participants, many=True)
        return Response(serializer.data)
