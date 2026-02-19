from django.shortcuts import render

def index(request):
    return render(request, "chat/index.html")

def chat_room(request, room_name):
    return render(request, "chat/chat_room.html", {"room_name": room_name})
