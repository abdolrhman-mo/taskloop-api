from django.urls import path
from .views import (
    CreateSessionView, SessionDetailView, UserSessionsView,
    TaskListView, AddTaskView, UpdateTaskView, DeleteTaskView, ListUsersView,
    SessionManagementView, SessionParticipantsView, LeaveSessionView
)

urlpatterns = [
    path('create', CreateSessionView.as_view()),
    path('<uuid:uuid>', SessionDetailView.as_view()),
    path('', UserSessionsView.as_view()),
    path('<uuid:uuid>/manage', SessionManagementView.as_view(), name='session_manage'),
    path('<uuid:uuid>/users', SessionParticipantsView.as_view(), name='session_participants'),
    path('<uuid:uuid>/leave', LeaveSessionView.as_view(), name='leave_session'),
    path('<uuid:uuid>/tasks', TaskListView.as_view()),
    path('<uuid:uuid>/tasks/add', AddTaskView.as_view()),
    path('<uuid:uuid>/tasks/<int:taskId>', UpdateTaskView.as_view()),
    path('task/<uuid:uuid>/delete/<int:taskId>', DeleteTaskView.as_view(), name='delete_task'),
    path('users/', ListUsersView.as_view(), name='list_users'),
]
