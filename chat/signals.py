from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message


@receiver(post_save, sender=Message)
def create_task_from_flagged_message(sender, instance, **kwargs):
    # Only fire when is_flagged just became True
    if not instance.is_flagged:
        return

    # Avoid creating duplicate tasks if message is saved again
    from accounts.models import Task
    already_exists = Task.objects.filter(source_message=instance).exists()
    if already_exists:
        return

    Task.objects.create(
        user=instance.user,
        title=f'Flagged: {instance.content[:80]}',
        source_message=instance,
        priority='medium',
        due_date=None,  # user sets this later from dashboard
    )
