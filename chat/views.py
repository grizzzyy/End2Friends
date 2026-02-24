from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message

@login_required
def index(request):
    return render(request, "chat/chat.html")

@login_required
def chat_room(request, room_name):
    conversation, _ = Conversation.objects.get_or_create(room_id=room_name)
    messages = conversation.messages.select_related('user').all()
    return render(request, "chat/chat.html", {
        "room_name": room_name,
        "messages": messages,
        "conversation": conversation,
    })