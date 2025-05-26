from django.db import models
from django.contrib.auth.models import User
import uuid

# For Your Info
# null=True: The database will allow NULL values for this field
# blank=True: The field is optional in forms and validation
class Session(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, blank=False, null=False, default="Session")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sessions')
    # user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_user1')
    # user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_user2')
    participants = models.ManyToManyField(User, related_name='sessions_participant')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        creator_name = self.creator.username if self.creator else "No creator"
        participants = list(self.participants.all())
        if not participants:
            return f"Session {self.name} (creator: {creator_name})"
        participants_names = ", ".join([user.username for user in participants])
        return f"Session {self.name} (creator: {creator_name}) with {participants_names}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # If this is a new session, add user1 and user2 to participants
        if is_new:
            self.participants.add(self.creator)

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
