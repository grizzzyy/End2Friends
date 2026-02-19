from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from .models import StudyRoom

def room_chat(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    return render(request, "rooms/chat.html", {"room": room})
