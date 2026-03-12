from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import StudyRoom, RoomMembership


def room_chat(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    return render(request, "rooms/chat.html", {"room": room})


@login_required
def join_by_code(request, code):
    room = get_object_or_404(StudyRoom, invite_code=code)

    RoomMembership.objects.get_or_create(
        user=request.user,
        room=room,
        defaults={'role': 'member'}
    )

    return redirect('rooms:room_chat', room_id=room.id)
