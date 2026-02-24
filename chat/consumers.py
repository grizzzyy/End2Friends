from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import Conversation, Message


class chatconsumer(AsyncWebsocketConsumer):

    # runs when a user connects
    async def connect(self):
        # get room id from the url
        self.room_id = self.scope['url_route']['kwargs']['room_name']

        # group name for this chat room
        self.room_group_name = f"chat_{self.room_id}"

        # add this connection to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # accept the websocket connection
        await self.accept()

    # runs when a user disconnects
    async def disconnect(self, close_code):
        # remove connection from the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # handles messages sent from the client
    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data.get('message', '')
        user = self.scope['user']

        # save message to database
        await self.save_message(user, self.room_id, message)

        # send message to everyone in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username,
            }
        )

    # handles messages sent to the group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
        }))

    # saves a message to the database
    @database_sync_to_async
    def save_message(self, user, room_id, content):
        # get or create the conversation
        convo, _ = Conversation.objects.get_or_create(room_id=room_id)

        # create the message
        Message.objects.create(
            conversation=convo,
            user=user,
            content=content
        )
