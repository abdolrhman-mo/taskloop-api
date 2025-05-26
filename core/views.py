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
        'uuid': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
        'name': openapi.Schema(type=openapi.TYPE_STRING)
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

# Define UUID parameter for session endpoints
session_uuid_param = openapi.Parameter(
    'uuid',
    openapi.IN_PATH,
    description="Session UUID",
    type=openapi.TYPE_STRING,
    format='uuid',
    required=True
)

# Define UUID parameter for task endpoints
task_uuid_param = openapi.Parameter(
    'taskId',
    openapi.IN_PATH,
    description="Task ID",
    type=openapi.TYPE_INTEGER,
    required=True
)

class CreateSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Session name')
            },
            required=['name']
        ),
        responses={201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'uuid': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                'name': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ), 400: 'Bad Request'}
    )

    def post(self, request):
        name = request.data.get('name')
        if not name:
            return Response({'error': 'Session name is required'}, status=400)

        session = Session.objects.create(
            name=name,
            creator=request.user
        )
        return Response({
            'uuid': str(session.uuid),
            'name': session.name
        }, status=201)

class SessionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param, session_uuid_param],
        responses={200: SessionSerializer, 404: 'Not Found'}
    )
    def get(self, request, uuid):
        try:
            session = Session.objects.get(uuid=uuid)
            
            # Check if user is already a participant
            is_participant = session.participants.filter(id=request.user.id).exists()
            
            if not is_participant:
                # Add user as participant if they're not already in the session
                session.participants.add(request.user)
                status_code = 201  # Created - new participant added
            else:
                status_code = 200  # OK - existing participant

            serializer = SessionSerializer(session)
            return Response(serializer.data, status=status_code)
            
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

class UserSessionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param],
        responses={200: SessionSerializer(many=True)}
    )
    def get(self, request):
        # Get all sessions where the user is a participant
        sessions = Session.objects.filter(participants=request.user)
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)

class TaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param, session_uuid_param],
        responses={200: TaskSerializer(many=True), 403: 'Forbidden', 404: 'Not Found'}
    )
    def get(self, request, uuid):
        try:
            session = Session.objects.get(uuid=uuid)
            # Check if user is a participant in the session
            if not session.participants.filter(id=request.user.id).exists():
                return Response({'error': 'Not authorized to view tasks in this session'}, status=403)
            
            tasks = session.tasks.all()
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

class AddTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param, session_uuid_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, description='Task description')
            },
            required=['text']
        ),
        responses={201: TaskSerializer, 400: 'Bad Request', 403: 'Forbidden', 404: 'Not Found'}
    )
    def post(self, request, uuid):
        try:
            session = Session.objects.get(uuid=uuid)
            
            # Ensure the requester is part of the session
            if not session.participants.filter(id=request.user.id).exists():
                return Response({'error': 'Not authorized to add tasks to this session'}, status=403)

            # Validate text
            text = request.data.get('text')
            if not text:
                return Response({'error': 'Task text is required'}, status=400)

            # Create the task with the requesting user as the creator
            task = Task.objects.create(
                session=session,
                text=text,
                user=request.user
            )
            serializer = TaskSerializer(task)
            return Response(serializer.data, status=201)

        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

class UpdateTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param, session_uuid_param, task_uuid_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, description='Updated task description'),
                'is_done': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Task completion status')
            },
            required=[]
        ),
        responses={200: TaskSerializer, 403: 'Forbidden', 404: 'Not Found', 400: 'Bad Request'}
    )
    def put(self, request, uuid, taskId):
        try:
            session = Session.objects.get(uuid=uuid)
            task = get_object_or_404(Task, id=taskId, session=session)

            # Check if user is a participant in the session
            if not session.participants.filter(id=request.user.id).exists():
                return Response({'error': 'Not authorized to update tasks in this session'}, status=403)

            # Update task text if provided
            new_text = request.data.get('text')
            if new_text is not None:
                if not new_text.strip():
                    return Response({'error': 'Task text cannot be empty'}, status=400)
                task.text = new_text

            # Update completion status if provided
            if 'is_done' in request.data:
                task.is_done = request.data['is_done']

            task.save()
            return Response(TaskSerializer(task).data)
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

class DeleteTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param, session_uuid_param, task_uuid_param],
        responses={200: '{"deleted": true}', 403: 'Forbidden', 404: 'Not Found'}
    )
    def delete(self, request, uuid, taskId):
        try:
            session = Session.objects.get(uuid=uuid)
            task = get_object_or_404(Task, id=taskId, session=session)

            # Check if user is a participant in the session
            if not session.participants.filter(id=request.user.id).exists():
                return Response({'error': 'Not authorized to delete tasks in this session'}, status=403)

            task.delete()
            return Response({'deleted': True})
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

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
        manual_parameters=[token_param, session_uuid_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='New session name'),
            }
        ),
        responses={200: SessionSerializer, 403: 'Forbidden', 404: 'Not Found', 400: 'Bad Request'}
    )
    def put(self, request, uuid):
        """
        Update session details.
        Requires authentication and session participation.
        """
        try:
            session = Session.objects.get(uuid=uuid)
            
            # Check if user is a participant in the session
            if not session.participants.filter(id=request.user.id).exists():
                return Response({'error': 'Not authorized to update this session'}, status=403)

            # Update session name if provided
            name = request.data.get('name')
            if name:
                if not name.strip():
                    return Response({'error': 'Session name cannot be empty'}, status=400)
                session.name = name
                session.save()

            serializer = SessionSerializer(session)
            return Response(serializer.data)
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

    @swagger_auto_schema(
        manual_parameters=[token_param, session_uuid_param],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'session_uuid': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                }
            ),
            403: 'Forbidden',
            404: 'Not Found'
        }
    )
    def delete(self, request, uuid):
        """
        Delete a session.
        Requires authentication and session creator status.
        Returns a success message with the deleted session UUID.
        """
        try:
            session = Session.objects.get(uuid=uuid)
            
            # Only the creator can delete the session
            if request.user != session.creator:
                return Response({'error': 'Only the session creator can delete the session'}, status=403)

            session_uuid = str(session.uuid)
            session.delete()
            return Response({
                'message': 'Session deleted successfully',
                'session_uuid': session_uuid
            }, status=status.HTTP_200_OK)
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

class SessionParticipantsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param, session_uuid_param],
        responses={200: UserSerializer(many=True), 403: 'Forbidden', 404: 'Not Found'}
    )
    def get(self, request, uuid):
        """
        Get all session participants.
        Requires authentication and session membership.
        Returns list of all users participating in the session.
        """
        try:
            session = Session.objects.get(uuid=uuid)
            
            # Check if user is a participant in the session
            if not session.participants.filter(id=request.user.id).exists():
                return Response({'error': 'Not authorized to view participants of this session'}, status=403)

            # Get all participants including the creator
            participants = session.participants.all()
            serializer = UserSerializer(participants, many=True)
            return Response(serializer.data)
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

class LeaveSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[token_param, session_uuid_param],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'session_uuid': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                }
            ),
            403: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            404: 'Not Found'
        }
    )
    def post(self, request, uuid):
        """
        Leave a session.
        Requires authentication and session participation.
        Creator cannot leave the session.
        """
        try:
            session = Session.objects.get(uuid=uuid)
            
            # Check if user is a participant in the session
            if not session.participants.filter(id=request.user.id).exists():
                return Response({'error': 'You are not a participant in this session'}, status=403)
            
            # Check if user is the creator
            if request.user == session.creator:
                return Response({
                    'error': 'Session creator cannot leave the session. Transfer ownership or delete the session instead.'
                }, status=403)

            # Remove user from participants
            session.participants.remove(request.user)
            
            return Response({
                'message': 'Successfully left the session',
                'session_uuid': str(session.uuid)
            }, status=200)
            
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)
