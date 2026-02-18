from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# conversation model -> represents any chat space
class Conversation(models.Model):
    # name of the conversation
    name = models.CharField(max_length=255, blank=True, null=True)

    # is the conversation a private chat? public ? group chat
    is_private = models.BooleanField(default=False)

    # a convo can have many users
    participants = models.ManyToManyField(User, related_name="conversations")

    # return the name of the convo
    def __str__(self):
        return self.name or "Private Conversation"

# message model -> create blueprint for a message
class Message(models.Model):
    # every message belongs to ONE convo
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    
    # every message is written by ONE user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # actual text of the message 
    content = models.TextField()
    # timestamp when the message is created
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["timestamp"]

