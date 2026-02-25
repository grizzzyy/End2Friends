from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django import forms

from .models import Channel, Membership


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ["name", "description", "is_private"]


@login_required
def create_channel(request):
    if request.method == "POST":
        form = ChannelForm(request.POST)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.creator = request.user
            channel.save()

            Membership.objects.create(
                user=request.user,
                channel=channel,
                role="owner"
            )
            return redirect("list_channels")
    else:
        form = ChannelForm()

    return render(request, "channels/create_channel.html", {"form": form})


@login_required
def join_channel(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)

    Membership.objects.get_or_create(
        user=request.user,
        channel=channel,
        defaults={"role": "member"}
    )

    return redirect("list_channels")


@login_required
def leave_channel(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)

    Membership.objects.filter(
        user=request.user,
        channel=channel
    ).delete()

    return redirect("list_channels")


@login_required
def list_channels(request):
    channels = Channel.objects.filter(
        memberships__user=request.user
    ).distinct()

    return render(request, "channels/list_channels.html", {"channels": channels})