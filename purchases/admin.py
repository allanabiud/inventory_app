from django.contrib import admin

from .models import Purchase, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email", "phone")


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "purchase_number",
        "supplier",
        "item",
        "quantity",
        "unit_cost_display",
        "total_cost_display",
        "date",
    )
    search_fields = ("purchase_number", "supplier__name", "item__name")
    list_filter = ("date", "supplier")
    readonly_fields = ("purchase_number", "created_at")

    @admin.display(description="Unit Cost")
    def unit_cost_display(self, obj):
        return f"KES {obj.unit_cost:.2f}"

    @admin.display(description="Total Cost")
    def total_cost_display(self, obj):
        return f"KES {obj.total_cost:.2f}"
