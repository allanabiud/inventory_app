from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Purchase


@receiver(post_delete, sender=Purchase)
def deduct_stock_on_purchase_delete(sender, instance, **kwargs):
    if instance.item and instance.item.current_stock >= instance.quantity:
        instance.item.current_stock -= instance.quantity
        instance.item.save()
