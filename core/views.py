from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Session, Task
from .serializers import SessionSerializer, TaskSerializer

class CreateSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user1 = request.user
        user2_id = request.data.get('user2_id')

        if not user2_id:
            return Response({'error': 'user2_id is required'}, status=400)

        session = Session.objects.create(user1=user1, user2_id=user2_id)
        return Response({'session_id': str(session.id)}, status=201)

class SessionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        session = get_object_or_404(Session, id=id)
        serializer = SessionSerializer(session)
        return Response(serializer.data)

class UserSessionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sessions = Session.objects.filter(models.Q(user1=request.user) | models.Q(user2=request.user))
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)

class TaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        session = get_object_or_404(Session, id=id)
        if request.user != session.user1 and request.user != session.user2:
            return Response({'error': 'Not authorized'}, status=403)
        tasks = session.tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class AddTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        session = get_object_or_404(Session, id=id)
        if request.user != session.user1 and request.user != session.user2:
            return Response({'error': 'Not authorized'}, status=403)

        text = request.data.get('text')
        if not text:
            return Response({'error': 'Task text required'}, status=400)

        task = Task.objects.create(session=session, text=text)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=201)

class UpdateTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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

    def delete(self, request, id, taskId):
        session = get_object_or_404(Session, id=id)
        task = get_object_or_404(Task, id=taskId, session=session)

        if request.user != session.user1 and request.user != session.user2:
            return Response({'error': 'Not authorized'}, status=403)

        task.delete()
        return Response({'deleted': True})
