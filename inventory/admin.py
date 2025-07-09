from django.contrib import admin

from .forms import InventoryAdjustmentAdminForm
from .models import Category, InventoryAdjustment, Item, ItemImage, UnitOfMeasure


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ("name", "abbreviation", "description")
    search_fields = ("name", "abbreviation")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1
    readonly_fields = ("upload_date", "thumbnail")
    fields = ("image", "caption", "thumbnail", "upload_date")


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "unit",
        "category",
        "selling_price",
        "purchase_price",
        "opening_stock",
        "reorder_point",
        "current_stock",
        "created_at",
    )
    list_filter = ("unit", "category")
    search_fields = ("name", "sku")
    readonly_fields = ("created_at", "updated_at")
    inlines = (ItemImageInline,)
    ordering = ("-created_at",)


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    form = InventoryAdjustmentAdminForm
    list_display = (
        "item",
        "adjustment_type",
        "quantity_adjusted",
        "cost_price",
        "reason",
        "date",
        "created_at",
    )
    list_filter = ("adjustment_type", "reason", "date")
    search_fields = ("item__name", "description")
    date_hierarchy = "date"
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
