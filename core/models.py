from django.db import models
from django.contrib.auth.models import User


class Session(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.id} between {self.user1} and {self.user2}"

class Task(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='tasks')
    text = models.TextField()
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
