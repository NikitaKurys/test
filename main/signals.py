from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import MainTable


@receiver(pre_delete, sender=MainTable)
def release_room_on_delete(sender, instance, **kwargs):
    if instance.room:
        instance.room.occupied = False
        instance.room.save()
