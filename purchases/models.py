from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now

from inventory.models import Item


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    purchase_number = models.CharField(max_length=30, unique=True, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    supplier = models.ForeignKey("Supplier", on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.purchase_number} - {self.supplier or 'Unknown Supplier'}"

    def clean(self):
        if self.quantity is None or self.quantity == 0:
            raise ValidationError("Quantity must be greater than zero.")
        if self.unit_cost is not None and self.unit_cost <= 0:
            raise ValidationError("Unit cost must be a positive number.")

    def save(self, *args, **kwargs):
        from .utils import generate_purchase_number

        is_new = self.pk is None

        if not self.purchase_number:
            self.purchase_number = generate_purchase_number()

        if self.unit_cost is None:
            if not self.item.purchase_price:
                raise ValidationError("No purchasing price set for this item.")
            self.unit_cost = self.item.purchase_price

        self.full_clean()

        # Adjust stock
        if is_new:
            self.item.current_stock += self.quantity
        else:
            original = Purchase.objects.get(pk=self.pk)
            if self.item == original.item:
                self.item.current_stock -= original.quantity
                self.item.current_stock += self.quantity
            else:
                original.item.current_stock -= original.quantity
                original.item.save()
                self.item.current_stock += self.quantity

        self.item.save()
        super().save(*args, **kwargs)

    @property
    def total_cost(self):
        return self.unit_cost * self.quantity
