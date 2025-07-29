from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Row
from django import forms
from django.core.exceptions import ValidationError

from .models import Purchase, Supplier


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = [
            "item",
            "supplier",
            "quantity",
            "unit_cost",
            "description",
            "date",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"style": "height: 100px"}),
            "date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {"date": "Date of Purchase", "quantity": "Quantity Purchased"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["item"].widget.attrs.update(
            {
                "class": "select2-item",
                "data-placeholder": "Select an item",
            }
        )

        self.fields["supplier"].widget.attrs.update(
            {
                "class": "select2-supplier",
                "data-placeholder": "Select a supplier",
            }
        )

        self.fields["quantity"].widget.attrs.update({"min": 1})
        self.fields["unit_cost"].required = False
        self.fields["unit_cost"].widget.attrs.update(
            {
                "placeholder": "Unit cost",
                "step": "0.01",
                "class": "form-control",
            }
        )

        self.helper = FormHelper()
        self.helper.form_method = "post"

        self.helper.layout = Layout(
            Row(
                Column(Field("item"), css_class="col-md-6"),
                Column(Field("supplier"), css_class="col-md-6"),
                css_class="g-4 mb-4",
            ),
            Row(
                Column(FloatingField("quantity"), css_class="col-md-6"),
                Column(
                    HTML(
                        """
                        <div class="input-group has-validation">
                            <span class="input-group-text">KES</span>
                            <div class="form-floating flex-grow-1">
                                <input type="number"
                                       name="unit_cost"
                                       id="id_unit_cost"
                                       class="form-control {% if errors.unit_cost %}is-invalid{% endif %}"
                                       placeholder="Unit Cost"
                                       value="{{ form.unit_cost.value|default_if_none:'' }}"
                                       step="0.01">
                                <label for="id_unit_cost" class="form-label">Unit Cost</label>
                            </div>
                        </div>
                        <div class="form-text">
                            Leave blank to use the item's default purchasing price.
                        </div>
                        {% if errors.unit_cost %}
                            <div class="invalid-feedback d-block">
                                {% for error in errors.unit_cost %}{{ error }}{% endfor %}
                            </div>
                        {% endif %}
                        """
                    ),
                    css_class="col-md-6",
                ),
                css_class="g-4 mb-4",
            ),
            Row(
                Column(FloatingField("date"), css_class="col-md-6"),
                Column(FloatingField("description"), css_class="col-md-12"),
                css_class="g-4 mb-4",
            ),
        )

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is None or quantity <= 0:
            raise ValidationError("Quantity must be a positive number.")
        return quantity

    def clean_unit_cost(self):
        cost = self.cleaned_data.get("unit_cost")
        if cost is not None and cost <= 0:
            raise ValidationError("Unit cost must be a positive number.")
        return cost

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Purchase model's save() handles stock increase and purchase_number
        if commit:
            instance.save()
        return instance


class SupplierForm(forms.ModelForm):
    """Form for creating and updating suppliers, styled with Crispy Forms."""

    class Meta:
        model = Supplier
        fields = ["name", "email", "phone", "address"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column(
                    FloatingField("name", placeholder="Supplier name"),
                    css_class="col-md-6",
                ),
                Column(
                    FloatingField("email", placeholder="Email address"),
                    css_class="col-md-6",
                ),
                css_class="g-4 mb-4",
            ),
            Row(
                Column(
                    FloatingField("phone", placeholder="Phone number"),
                    css_class="col-md-6",
                ),
                Column(
                    FloatingField("address", placeholder="Physical or mailing address"),
                    css_class="col-md-6",
                ),
                css_class="g-4 mb-4",
            ),
        )

        # Optional fields
        self.fields["email"].required = False
        self.fields["phone"].required = False
        self.fields["address"].required = False
