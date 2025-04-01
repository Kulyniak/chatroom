from django.db import models
import uuid
# Create your models here.

class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    create_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    
    
class Message(models.Model):
    chat = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    username = models.CharField(max_length=50)
    text = models.TextField() 
    timestamp = models.DateTimeField(auto_now_add=True)