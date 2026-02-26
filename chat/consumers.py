from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
import traceback

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_id}'

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            print(f"[WS] Connected: {self.room_id} | User: {self.scope['user']}")

        except Exception as e:
            print(f"[WS ERROR] Connect failed: {e}")
            traceback.print_exc()
            await self.close()

    async def disconnect(self, close_code):
        print(f"[WS] Disconnected: code={close_code}")
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception as e:
            print(f"[WS ERROR] Disconnect error: {e}")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            user = self.scope['user']

            print(f"[WS] Message from {user}: {message}")

            if not message or not user.is_authenticated:
                print(f"[WS] Rejected - empty message or unauthenticated user")
                return

            await self.save_message(user, self.room_id, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': user.username,
                }
            )

        except Exception as e:
            print(f"[WS ERROR] Receive failed: {e}")
            traceback.print_exc()

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'username': event['username'],
            }))
        except Exception as e:
            print(f"[WS ERROR] Send failed: {e}")

    @database_sync_to_async
    def save_message(self, user, room_id, content):
        from .models import Conversation, Message
        try:
            conversation = Conversation.objects.get(room_id=room_id)
            msg = Message.objects.create(
                conversation=conversation,
                user=user,
                content=content
            )
            print(f"[WS] Saved message id={msg.id}")
        except Conversation.DoesNotExist:
            print(f"[WS ERROR] Conversation not found for room_id={room_id}")
        except Exception as e:
            print(f"[WS ERROR] Save failed: {e}")
            traceback.print_exc()