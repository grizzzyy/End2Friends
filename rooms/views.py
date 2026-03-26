from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db import IntegrityError
from .models import StudyRoom, RoomMembership, RoomInvite, Channel, Message

User = get_user_model()


@login_required
def room_list(request):
    my_rooms = StudyRoom.objects.filter(memberships__user=request.user)
    public_rooms = StudyRoom.objects.filter(
        is_private=False
    ).exclude(memberships__user=request.user)
    return render(request, 'rooms/room_list.html', {
        'my_rooms': my_rooms,
        'public_rooms': public_rooms,
    })


@login_required
def create_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        room_type = request.POST.get('room_type', 'study')
        is_private = request.POST.get('is_private') == 'on'

        room = StudyRoom.objects.create(
            name=name,
            description=description,
            room_type=room_type,
            is_private=is_private,
            created_by=request.user
        )

        RoomMembership.objects.create(
            user=request.user, room=room, role='owner'
        )

        return redirect('rooms:room_chat', room_id=room.id)

    return render(request, 'rooms/create_room.html')


@login_required
def join_room(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)

    if not room.is_private:
        RoomMembership.objects.get_or_create(
            user=request.user, room=room,
            defaults={'role': 'member'}
        )

    return redirect('rooms:room_chat', room_id=room.id)


@login_required
def send_invite(request, room_id):
    if request.method != 'POST':
        return redirect('rooms:room_list')

    room = get_object_or_404(StudyRoom, id=room_id)

    is_member = RoomMembership.objects.filter(
        user=request.user, room=room
    ).exists()

    if not is_member:
        return redirect('rooms:room_list')

    username = request.POST.get('username')
    invited_user = get_object_or_404(User, username=username)

    already_member = RoomMembership.objects.filter(
        user=invited_user, room=room
    ).exists()

    if already_member:
        return redirect('rooms:room_chat', room_id=room.id)

    already_invited = RoomInvite.objects.filter(
        invited_user=invited_user, room=room, accepted=False
    ).exists()

    if already_invited:
        return redirect('rooms:room_chat', room_id=room.id)

    RoomInvite.objects.create(
        room=room,
        invited_user=invited_user,
        invited_by=request.user
    )

    return redirect('rooms:room_chat', room_id=room.id)


@login_required
def accept_invite(request, invite_id):
    invite = get_object_or_404(
        RoomInvite, id=invite_id, invited_user=request.user
    )

    invite.accepted = True
    invite.save()

    RoomMembership.objects.get_or_create(
        user=request.user,
        room=invite.room,
        defaults={'role': 'member'}
    )

    return redirect('rooms:room_chat', room_id=invite.room.id)


@login_required
def decline_invite(request, invite_id):
    invite = get_object_or_404(
        RoomInvite, id=invite_id, invited_user=request.user
    )

    invite.delete()
    return redirect('dashboard')


@login_required
def my_invites(request):
    invites = RoomInvite.objects.filter(
        invited_user=request.user,
        accepted=False
    ).select_related('room', 'invited_by')

    return render(request, 'rooms/invites.html', {'invites': invites})


@login_required
def room_detail(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)

    membership = RoomMembership.objects.filter(
        user=request.user, room=room
    ).first()

    return render(request, "rooms/room_detail.html", {
        "room": room,
        "membership": membership,
    })


@login_required
def room_chat(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)

    membership = RoomMembership.objects.filter(
        user=request.user, room=room
    ).first()

    if not membership and room.is_private:
        return redirect('rooms:room_list')

    members = RoomMembership.objects.filter(
        room=room
    ).select_related('user')

    # Get all channels for this room
    channels = room.room_channels.all().order_by('created_at')

    return render(request, 'rooms/chat.html', {
        'room': room,
        'members': members,
        'membership': membership,
        'channels': channels,
    })

    
    
@login_required
def join_by_code(request, code):
    room = get_object_or_404(StudyRoom, invite_code=code)

    RoomMembership.objects.get_or_create(
        user=request.user,
        room=room,
        defaults={'role': 'member'}
    )

    return redirect('rooms:room_chat', room_id=room.id)


@login_required
def delete_room(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    
    # Only the owner can delete
    membership = RoomMembership.objects.filter(
        user=request.user, room=room, role='owner'
    ).first()
    
    if not membership:
        return redirect('rooms:room_list')
    
    if request.method == 'POST':
        room.delete()
        return redirect('dashboard')
    
    return redirect('rooms:room_detail', room_id=room_id)


@login_required
def create_channel(request, room_id):
    """Create a new channel - owner only."""
    room = get_object_or_404(StudyRoom, id=room_id)
    
    # Check if user is owner
    membership = RoomMembership.objects.filter(
        user=request.user, room=room, role='owner'
    ).first()
    
    if not membership:
        messages.error(request, "Only the room owner can create channels.")
        return redirect('rooms:room_chat', room_id=room_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        
        # Validate blank name
        if not name:
            messages.error(request, "Channel name cannot be empty.")
            return redirect('rooms:room_chat', room_id=room_id)
        
        # Try to create (unique_together will catch duplicates)
        try:
            Channel.objects.create(
                name=name,
                room=room,
                created_by=request.user
            )
            messages.success(request, f"Channel '#{name}' created!")
        except IntegrityError:
            messages.error(request, f"A channel named '{name}' already exists.")
        
        return redirect('rooms:room_chat', room_id=room_id)
    
    return redirect('rooms:room_chat', room_id=room_id)


@login_required
def delete_channel(request, room_id, channel_id):
    """Delete a channel - owner only."""
    room = get_object_or_404(StudyRoom, id=room_id)
    channel = get_object_or_404(Channel, id=channel_id, room=room)
    
    # Check if user is owner
    membership = RoomMembership.objects.filter(
        user=request.user, room=room, role='owner'
    ).first()
    
    if not membership:
        messages.error(request, "Only the room owner can delete channels.")
        return redirect('rooms:room_chat', room_id=room_id)
    
    if request.method == 'POST':
        channel_name = channel.name
        channel.delete()
        messages.success(request, f"Channel '#{channel_name}' deleted.")
        return redirect('rooms:room_chat', room_id=room_id)
    
    return redirect('rooms:room_chat', room_id=room_id)


@login_required
def channel_chat(request, room_id, channel_id):
    """View a channel's chat - members only."""
    room = get_object_or_404(StudyRoom, id=room_id)
    channel = get_object_or_404(Channel, id=channel_id, room=room)
    
    # Check if user is a member
    membership = RoomMembership.objects.filter(
        user=request.user, room=room
    ).first()
    
    if not membership:
        messages.error(request, "You must be a member to view this channel.")
        return redirect('rooms:room_list')
    
    # Get all channels for sidebar
    channels = room.room_channels.all().order_by('created_at')
    
    # Get messages for this channel
    channel_messages = channel.messages.select_related('user').order_by('timestamp')
    
    # Get room members
    members = RoomMembership.objects.filter(room=room).select_related('user')
    
    return render(request, 'rooms/channel_chat.html', {
        'room': room,
        'channel': channel,
        'channels': channels,
        'channel_messages': channel_messages,
        'members': members,
        'membership': membership,
    })
