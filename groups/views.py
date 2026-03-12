from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django import forms

from .models import StudyChannel


class StudyChannelForm(forms.ModelForm):
    class Meta:
        model = StudyChannel
        fields = ["name", "description", "is_private"]

@login_required
def create_channel(request, room_id):
    from rooms.models import StudyRoom, RoomMembership
    room = get_object_or_404(StudyRoom, id=room_id)

    is_member = RoomMembership.objects.filter(
        user=request.user, room=room
    ).exists()
    if not is_member:
        return redirect('room_list')

    if request.method == 'POST':
        form = StudyChannelForm(request.POST)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.creator = request.user
            channel.room = room
            channel.save()
            return redirect('room_chat', room_id=room.id)
    else:
        form = StudyChannelForm()
    return render(request, 'groups/create_channel.html', {
        'form': form,
        'room': room
    })

@login_required
def join_channel(request, channel_id):
    channel = get_object_or_404(StudyChannel, id=channel_id)

    Membership.objects.get_or_create(
        user=request.user,
        channel=channel,
        defaults={"role": "member"}
    )

    return redirect("list_channels")


@login_required
def leave_channel(request, channel_id):
    channel = get_object_or_404(StudyChannel, id=channel_id)

    Membership.objects.filter(
        user=request.user,
        channel=channel
    ).delete()

    return redirect("list_channels")


@login_required
def list_channels(request):
    channels = StudyChannel.objects.filter(
        memberships__user=request.user
    ).distinct()

    return render(request, "groups/list_channels.html", {"channels": channels})