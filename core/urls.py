from django.urls import path
from .views import (
    CreateSessionView, SessionDetailView, UserSessionsView,
    TaskListView, AddTaskView, UpdateTaskView, DeleteTaskView
)

urlpatterns = [
    path('create', CreateSessionView.as_view()),
    path('<uuid:id>', SessionDetailView.as_view()),
    path('', UserSessionsView.as_view()),
    path('<uuid:id>/tasks', TaskListView.as_view()),
    path('<uuid:id>/tasks/add', AddTaskView.as_view()),
    path('<uuid:id>/tasks/<uuid:taskId>', UpdateTaskView.as_view()),
    path('<uuid:id>/tasks/<uuid:taskId>', DeleteTaskView.as_view()),  # same URL, different method
]
