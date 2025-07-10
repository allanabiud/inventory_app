from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.html import format_html

from .utils import item_image_upload_path


class UnitOfMeasure(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.abbreviation:
            return f"{self.name} ({self.abbreviation})"
        else:
            return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True)
    unit = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    opening_stock = models.IntegerField(blank=True, null=True)
    reorder_point = models.IntegerField(blank=True, null=True)
    current_stock = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.full_clean()  # Call full_clean to run validation including clean() method
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=item_image_upload_path)
    caption = models.CharField(max_length=200, blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True, null=True)

    def thumbnail(self):
        try:
            return format_html(
                '<img src="{}" style="max-height: 100px;" />', self.image.url
            )
        except Exception:
            return "No image"

    def __str__(self):
        return f"{self.item.name} Image"


class InventoryAdjustment(models.Model):
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    ADJUSTMENT_TYPES = (
        (INCREASE, "Increase"),
        (DECREASE, "Decrease"),
    )

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="adjustments")
    adjustment_type = models.CharField(max_length=10, choices=ADJUSTMENT_TYPES)
    quantity_adjusted = models.IntegerField()
    cost_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    REASON_CHOICES = (
        ("PURCHASE", "Purchase"),
        ("SALE", "Sale"),
        ("STOCK_COUNT", "Stock Count"),
        ("STOLEN", "Stolen Goods"),
        ("DAMAGED", "Damaged Goods"),
        ("OTHER", "Other"),
    )
    reason = models.CharField(
        max_length=100, choices=REASON_CHOICES, default="STOCK_COUNT"
    )
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        # Reverse previous adjustment if updating
        if not is_new:
            previous = InventoryAdjustment.objects.get(pk=self.pk)

            if previous.adjustment_type == self.INCREASE:
                self.item.current_stock -= previous.quantity_adjusted
            elif previous.adjustment_type == self.DECREASE:
                self.item.current_stock += previous.quantity_adjusted

        # Apply new adjustment
        if self.adjustment_type == self.DECREASE:
            if (
                self.item.current_stock is not None
                and self.item.current_stock < self.quantity_adjusted
            ):
                raise ValidationError(
                    f"Cannot decrease stock by {self.quantity_adjusted}."
                    f" Only {self.item.current_stock} in stock."
                )
            self.item.current_stock -= self.quantity_adjusted
        elif self.adjustment_type == self.INCREASE:
            self.item.current_stock += self.quantity_adjusted

        self.item.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.adjustment_type} of {self.quantity_adjusted} for {self.item.name} on {self.date}"
