from django.db import models
from django.contrib.auth import get_user_model
import shortuuid
import os

User = get_user_model()

# represents any chat space (DM, group chat, etc.)
class Conversation(models.Model):
    # a name for the conversation
    name = models.CharField(max_length=255, blank=True, null=True)
    # unique room identifier
    room_id = models.CharField(max_length=50, unique=True, blank=True)
    # whether this is a private dm
    is_private = models.BooleanField(default=False)
    # user who created or manages the conversation
    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='administered_conversations'
    )
    # users who are part of the conversation
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        blank=True
    )
    # users currently online in this conversation
    users_online = models.ManyToManyField(
        User,
        related_name='online_in_conversations',
        blank=True
    )

    # auto-generate a room ID if one doesn't exist
    def save(self, *args, **kwargs):
        if not self.room_id:
            self.room_id = shortuuid.uuid()
        super().save(*args, **kwargs)

    # show name if available, otherwise fallback to room ID
    def __str__(self):
        return self.name or f"DM({self.room_id})"


# represents a single message inside a conversation
class Message(models.Model):
    # the conversation this message belongs to
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    # the user who sent the message
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # optional file attachment
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    # text content of the message
    content = models.TextField(blank=True)
    # when the message was created
    timestamp = models.DateTimeField(auto_now_add=True)

    # moderation / state fields from teammate's migration
    # whether this message has been flagged for review
    is_flagged = models.BooleanField(default=False)
    # reason the message was flagged
    flag_reason = models.CharField(max_length=255, blank=True, default='')
    # whether this message has been edited
    is_edited = models.BooleanField(default=False)
    # when the message was last edited
    edited_at = models.DateTimeField(blank=True, null=True)
    # whether this message has been deleted
    is_deleted = models.BooleanField(default=False)
    # when the message was deleted
    deleted_at = models.DateTimeField(blank=True, null=True)
    # whether this message is pinned
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]

    # show username and either text or "[file]"
    def __str__(self):
        preview = self.content if self.content else "[file]"
        return f"{self.user.username}: {preview}"

    # return just the file name (not the full path)
    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        return None

    # quick check to see if the uploaded file is an image
    @property
    def is_image(self):
        if not self.file:
            return False
        try:
            from PIL import Image
            img = Image.open(self.file)
            img.verify()
            return True
        except Exception:
            return False