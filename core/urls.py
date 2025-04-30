from django.urls import path
from .views import (
    CreateSessionView, SessionDetailView, UserSessionsView,
    TaskListView, AddTaskView, UpdateTaskView, DeleteTaskView, ListUsersView
)

urlpatterns = [
    path('create', CreateSessionView.as_view()),
    path('<int:id>', SessionDetailView.as_view()),
    path('', UserSessionsView.as_view()),
    path('<int:id>/tasks', TaskListView.as_view()),
    path('<int:id>/tasks/add', AddTaskView.as_view()),
    path('<int:id>/tasks/<int:taskId>', UpdateTaskView.as_view()),
    path('task/<int:id>/delete/<int:taskId>', DeleteTaskView.as_view(), name='delete_task'),
    path('users/', ListUsersView.as_view(), name='list_users'),
]
