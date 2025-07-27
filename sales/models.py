from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now

from inventory.models import Item


class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Sale(models.Model):
    sales_number = models.CharField(max_length=30, unique=True, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    customer = models.ForeignKey("Customer", on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sales_number} - {self.customer or 'Walk-in'}"

    def clean(self):
        if self.pk:
            original = Sale.objects.get(pk=self.pk)
            restored_stock = self.item.current_stock + original.quantity
            if self.quantity > restored_stock:
                raise ValidationError("Not enough stock available for this sale.")
        else:
            if self.quantity > self.item.current_stock:
                raise ValidationError("Not enough stock available for this sale.")

    def save(self, *args, **kwargs):
        from .utils import generate_sales_number

        is_new = self.pk is None

        if not self.sales_number:
            self.sales_number = generate_sales_number()

        # Run validation *before* changing stock
        self.full_clean()

        # Adjust stock
        if is_new:
            self.item.current_stock -= self.quantity
        else:
            original = Sale.objects.get(pk=self.pk)
            if self.item == original.item:
                # Same item: restore then deduct
                self.item.current_stock += original.quantity
                self.item.current_stock -= self.quantity
            else:
                # Different item: restore original, deduct from new
                original.item.current_stock += original.quantity
                original.item.save()
                self.item.current_stock -= self.quantity

        self.item.save()

        # Compute discount
        if self.item.selling_price:
            expected_price = Decimal(self.item.selling_price) * self.quantity
            actual_price = self.unit_price * self.quantity
            self._discount = max(expected_price - actual_price, Decimal("0.00"))
        else:
            self._discount = Decimal("0.00")

        super().save(*args, **kwargs)

    @property
    def selling_price(self):
        return self.unit_price * self.quantity

    @property
    def discount(self):
        if hasattr(self, "_discount"):
            return self._discount
        if self.item and self.item.selling_price:
            expected_price = Decimal(self.item.selling_price) * self.quantity
            actual_price = self.unit_price * self.quantity
            return max(expected_price - actual_price, Decimal("0.00"))
        return Decimal("0.00")
