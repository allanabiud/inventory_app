from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Row
from django import forms
from django.core.exceptions import ValidationError

from .models import Customer, Sale


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            "item",
            "customer",
            "quantity",
            "unit_price",
            "description",
            "date",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"style": "height: 100px"}),
            "date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {"date": "Date of Sale", "quantity": "Quantity Sold"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["item"].widget.attrs.update(
            {
                "class": "select2-item",
                "data-placeholder": "Select an item",
            }
        )

        self.fields["customer"].widget.attrs.update(
            {
                "class": "select2-customer",
                "data-placeholder": "Select a customer",
            }
        )

        self.fields["quantity"].widget.attrs.update({"min": 1})
        self.fields["unit_price"].required = False
        self.fields["unit_price"].widget.attrs.update(
            {
                "placeholder": "Unit price",
                "step": "0.01",
                "class": "form-control",
            }
        )

        self.helper = FormHelper()
        self.helper.form_method = "post"

        self.helper.layout = Layout(
            Row(
                Column(Field("item"), css_class="col-md-6"),
                Column(Field("customer"), css_class="col-md-6"),
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
                                       name="unit_price"
                                       id="id_unit_price"
                                       class="form-control {% if errors.unit_price %}is-invalid{% endif %}"
                                       placeholder="Unit Price"
                                       value="{{ form.unit_price.value|default_if_none:'' }}"
                                       step="0.01">
                                <label for="id_unit_price" class="form-label">Unit Price</label>
                            </div>
                        </div>
                        <div class="form-text">
                            Leave blank to use the item's default selling price.
                        </div>
                        {% if errors.unit_price %}
                            <div class="invalid-feedback d-block">
                                {% for error in errors.unit_price %}{{ error }}{% endfor %}
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

    def clean_unit_price(self):
        price = self.cleaned_data.get("unit_price")
        if price is not None and price <= 0:
            raise ValidationError("Unit price must be a positive number.")
        return price

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get("item")  # type: ignore
        quantity = cleaned_data.get("quantity")  # type: ignore

        if self.instance.pk is None and item and quantity:
            if item.current_stock < quantity:
                self.add_error(
                    "quantity",
                    f"Not enough stock. Only {item.current_stock} unit(s) available.",
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Sale's save() handles stock deduction and sales_number
        if commit:
            instance.save()
        return instance


class CustomerForm(forms.ModelForm):
    """Form for creating and updating customers, styled with Crispy Forms."""

    class Meta:
        model = Customer
        fields = ["name", "email", "phone", "address"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column(
                    FloatingField("name", placeholder="Customer name"),
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
