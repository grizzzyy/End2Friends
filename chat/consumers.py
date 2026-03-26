from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
import traceback


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        try:
            self.room_id = self.scope["url_route"]["kwargs"]["room_name"]
            self.room_group_name = f"chat_{self.room_id}"

            # AUTH GUARD — reject unauthenticated users immediately
            user = self.scope["user"]
            if not user.is_authenticated:
                await self.close()
                return

            # PARTICIPANT CHECK — user must be in this conversation
            is_member = await self.user_in_conversation(user, self.room_id)
            if not is_member:
                await self.close()
                return

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()
            print(f"[WS] Connected: {self.room_id} | User: {user}")

        except Exception as e:
            print(f"[WS ERROR] Connect failed: {e}")
            traceback.print_exc()
            await self.close()

    async def disconnect(self, close_code):
        print(f"[WS] Disconnected: code={close_code}")
        try:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
        except Exception as e:
            print(f"[WS ERROR] Disconnect error: {e}")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            message = data.get("message", "").strip()
            user = self.scope["user"]
            msg_type = data.get("type", "chat")

            print(f"[WS] Message from {user}: {message}")

            if not user.is_authenticated:
                print("[WS] Rejected - unauthenticated user")
                return
            
            if msg_type == "edit":
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "message_edited", "message_id": data.get("message_id"), "content": data.get("content", "")},
                )
                return

            if msg_type == "delete":
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "message_deleted", "message_id": data.get("message_id")},
                )
                return

            if not message:
                print("[WS] Rejected - empty message")
                return            

            save_id = await self.save_message(user, self.room_id, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": user.username,
                    "message_id": save_id,
                },
            )

        except Exception as e:
            print(f"[WS ERROR] Receive failed: {e}")
            traceback.print_exc()

    async def chat_message(self, event):
        try:
            await self.send(
                text_data=json.dumps(
                    {
                        "message": event["message"],
                        "username": event["username"],
                    }
                )
            )
        except Exception as e:
            print(f"[WS ERROR] Send failed: {e}")


    @database_sync_to_async
    def save_message(self, user, room_id, content):
        from .models import Conversation, Message

        try:
            conversation = Conversation.objects.get(room_id=room_id)
            msg = Message.objects.create(
                conversation=conversation, user=user, content=content
            )
            print(f"[WS] Saved message id={msg.id}")
            return msg.id
        except Conversation.DoesNotExist:
            print(f"[WS ERROR] Conversation not found for room_id={room_id}")
        except Exception as e:
            print(f"[WS ERROR] Save failed: {e}")
            traceback.print_exc()


    @database_sync_to_async
    def user_in_conversation(self, user, room_id):
        from .models import Conversation

        return Conversation.objects.filter(room_id=room_id, participants=user).exists()


class ChannelConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for room channel chat."""

    async def connect(self):
        try:
            self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
            self.room_group_name = f"channel_{self.channel_id}"

            user = self.scope["user"]
            if not user.is_authenticated:
                await self.close()
                return

            # Check if user is a member of the room this channel belongs to
            is_member = await self.user_is_channel_member(user, self.channel_id)
            if not is_member:
                await self.close()
                return

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            print(f"[WS Channel] Connected: channel={self.channel_id} | User: {user}")

        except Exception as e:
            print(f"[WS Channel ERROR] Connect failed: {e}")
            traceback.print_exc()
            await self.close()

    async def disconnect(self, close_code):
        print(f"[WS Channel] Disconnected: code={close_code}")
        try:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
        except Exception as e:
            print(f"[WS Channel ERROR] Disconnect error: {e}")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            message = data.get("message", "").strip()
            user = self.scope["user"]

            print(f"[WS Channel] Message from {user}: {message}")

            if not message or not user.is_authenticated:
                return

            # Save message to database
            await self.save_channel_message(user, self.channel_id, message)

            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "user": user.username,
                },
            )

        except Exception as e:
            print(f"[WS Channel ERROR] Receive failed: {e}")
            traceback.print_exc()

    async def chat_message(self, event):
        try:
            await self.send(
                text_data=json.dumps({
                    "message": event["message"],
                    "user": event["user"],
                })
            )
        except Exception as e:
            print(f"[WS Channel ERROR] Send failed: {e}")

    @database_sync_to_async
    def user_is_channel_member(self, user, channel_id):
        from rooms.models import Channel, RoomMembership

        try:
            channel = Channel.objects.get(id=channel_id)
            return RoomMembership.objects.filter(user=user, room=channel.room).exists()
        except Channel.DoesNotExist:
            return False

    @database_sync_to_async
    def save_channel_message(self, user, channel_id, content):
        from rooms.models import Channel, Message

        try:
            channel = Channel.objects.get(id=channel_id)
            msg = Message.objects.create(
                channel=channel,
                user=user,
                content=content
            )
            print(f"[WS Channel] Saved message id={msg.id}")
        except Channel.DoesNotExist:
            print(f"[WS Channel ERROR] Channel not found: {channel_id}")
        except Exception as e:
            print(f"[WS Channel ERROR] Save failed: {e}")
            traceback.print_exc()
