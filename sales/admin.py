from django.contrib import admin

from .models import Customer, Sale


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email", "phone")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "sales_number",
        "customer",
        "item",
        "quantity",
        "selling_price_display",
        "discount_display",
        "date",
    )
    search_fields = ("sales_number", "customer__name", "item__name")
    list_filter = ("date", "customer")
    readonly_fields = ("sales_number", "created_at")

    @admin.display(description="Selling Price")
    def selling_price_display(self, obj):
        return f"KES {obj.selling_price:.2f}"

    @admin.display(description="Discount")
    def discount_display(self, obj):
        if obj.discount > 0:
            return f"KES {obj.discount:.2f} ({obj.discount}%)"
        return "–"
