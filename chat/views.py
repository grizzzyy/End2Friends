from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        is_private=True,
        participants=request.user
    ).order_by('-messages__timestamp').distinct()
    return render(request, "chat/inbox.html", {"conversations": conversations})

@login_required
def start_dm(request, username):
    other_user = get_object_or_404(User, username=username)

    conversation = Conversation.objects.filter(
        is_private=True,
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if not conversation:
        conversation = Conversation.objects.create(is_private=True)
        conversation.participants.add(request.user, other_user)

    return redirect('chat_room', room_name=conversation.room_id)

@login_required
def chat_room(request, room_name):
    conversation = get_object_or_404(Conversation, room_id=room_name)

    if request.user not in conversation.participants.all():
        return redirect('inbox')

    messages = conversation.messages.select_related('user').all()

    other_user = None
    if conversation.is_private:
        other_user = conversation.participants.exclude(id=request.user.id).first()

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
        "other_user": other_user,
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def delete_conversation(request, room_id):
    convo = get_object_or_404(Conversation, room_id=room_id)

    # Only allow participants to delete
    if request.user in convo.participants.all():
        convo.delete()

    return redirect('inbox')
