from django import forms

from .models import InventoryAdjustment


class InventoryAdjustmentAdminForm(forms.ModelForm):
    class Meta:
        model = InventoryAdjustment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove system-only reasons from manual entry
        SYSTEM_REASONS = {"PURCHASE", "SALE"}

        # Filter out system-only choices
        allowed_choices = [
            choice
            for choice in self.fields["reason"].choices
            if choice[0] not in SYSTEM_REASONS
        ]
        self.fields["reason"].choices = allowed_choices
