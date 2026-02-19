import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rooms.models import StudyRoom, RoomMembership
from .models import Conversation, Message
from django.contrib.auth.models import AnonymousUser


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]

        # Check if the user is logged in
        user = self.scope["user"]
        if isinstance(user, AnonymousUser):
            await self.close()
            return

        # Check if the room exists and user is a member
        is_allowed = await self.user_in_room(user.id, self.room_id)
        if not is_allowed:
            await self.close()
            return

        # Create or get the conversation for this room
        self.conversation = await self.get_conversation(self.room_id)

        # WebSocket group name
        self.room_group_name = f"chat_room_{self.room_id}"

        # Join the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data["message"]
        user = self.scope["user"]

        # Save message to database
        message = await self.create_message(self.conversation.id, user.id, message_text)

        # Broadcast message to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "user": user.username,
                "message": message_text,
                "timestamp": str(message.timestamp),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # -------------------------------------------------------
    # Database helper functions
    # --------------------------------------------------------

    @database_sync_to_async
    def user_in_room(self, user_id, room_id):
        return RoomMembership.objects.filter(user_id=user_id, room_id=room_id).exists()

    @database_sync_to_async
    def get_conversation(self, room_id):
        conversation, created = Conversation.objects.get_or_create(room_id=room_id)
        return conversation

    @database_sync_to_async
    def create_message(self, conversation_id, user_id, content):
        return Message.objects.create(
            conversation_id=conversation_id,
            user_id=user_id,
            content=content
        )
