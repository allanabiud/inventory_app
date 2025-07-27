from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Sale


@receiver(post_delete, sender=Sale)
def restore_stock_on_sale_delete(sender, instance, **kwargs):
    if instance.item:
        instance.item.current_stock += instance.quantity
        instance.item.save()
