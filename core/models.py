from django.db import models
from django.contrib.auth.models import User


class Session(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False, null=False, default="Session")
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.name} between {self.user1} and {self.user2}"

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='tasks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tasks', default=1)
    text = models.TextField()
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task {self.id} in session {self.session.id}"
