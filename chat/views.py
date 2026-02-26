from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message

@login_required
def index(request):
    return render(request, "chat/chat.html")

@login_required
def chat_room(request, room_name):
    conversation, _ = Conversation.objects.get_or_create(room_id=room_name)
    conversation.participants.add(request.user)
    messages = conversation.messages.select_related('user').all()

    # Also add user to the accounts Channel if it exists
    try:
        from accounts.models import Channel
        channel = Channel.objects.get(name=room_name)
        channel.members.add(request.user)
    except Exception:
        pass

    # Get user's channels for sidebar
    user_channels = request.user.channels.all()

    return render(request, "chat/chat.html", {
        "room_name": room_name,
        "messages": messages,
        "conversation": conversation,
        "channels": user_channels,
    })