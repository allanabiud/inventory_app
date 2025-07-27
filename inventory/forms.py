from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Row
from django import forms

from .models import Category, InventoryAdjustment, UnitOfMeasure


# CATEGORY FORM
class CategoryForm(forms.ModelForm):
    """
    Django form for adding/editing Category objects,
    styled with Crispy Forms and Bootstrap 5 Floating Fields.
    """

    class Meta:
        model = Category
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column(
                    FloatingField("name", placeholder="Category name"),
                    css_class="col-md-6",
                ),
                css_class="g-4 mb-4",
            ),
            Row(
                Column(
                    FloatingField("description", placeholder="Description"),
                    css_class="col-md-12",
                ),
                css_class="g-4 mb-4",
            ),
        )

        # Set custom widget for description to control its height
        self.fields["description"].widget = forms.Textarea(
            attrs={"style": "height: 100px"}
        )
        # Make description field optional
        self.fields["description"].required = False

    def clean_name(self):
        """
        Custom validation to ensure category name is unique (case-insensitive).
        Handles both creation and update scenarios.
        """
        name = self.cleaned_data["name"]
        # Check if a category with this name already exists
        # If this is a new object (self.instance.pk is None), check all existing categories.
        # If this is an existing object being updated, exclude itself from the check.
        if self.instance.pk is None:
            if Category.objects.filter(name__iexact=name).exists():
                raise forms.ValidationError("A category with this name already exists.")
        else:
            if (
                Category.objects.filter(name__iexact=name)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise forms.ValidationError("A category with this name already exists.")
        return name


# UNIT FORM
class UnitOfMeasureForm(forms.ModelForm):
    """
    Django form for adding/editing UnitOfMeasure objects,
    styled with Crispy Forms and Bootstrap 5 Floating Fields.
    """

    class Meta:
        model = UnitOfMeasure
        fields = ["name", "abbreviation", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column(
                    FloatingField("name", placeholder="Unit name"), css_class="col-md-6"
                ),
                Column(
                    FloatingField("abbreviation", placeholder="Abbreviation"),
                    css_class="col-md-6",
                ),
                css_class="g-4 mb-4",
            ),
            Row(
                Column(
                    FloatingField("description", placeholder="Description"),
                    css_class="col-md-12",
                ),
                css_class="g-4 mb-4",
            ),
        )

        # Set custom widget for description to control its height
        self.fields["description"].widget = forms.Textarea(
            attrs={"style": "height: 100px"}
        )
        # Ensure abbreviation and description are not required
        self.fields["abbreviation"].required = False
        self.fields["description"].required = False

    def clean_name(self):
        """
        Custom validation to ensure unit name is unique (case-insensitive).
        Handles both creation and update scenarios.
        """
        name = self.cleaned_data["name"]
        if self.instance.pk is None:  # Creating a new object
            if UnitOfMeasure.objects.filter(name__iexact=name).exists():
                raise forms.ValidationError("A unit with this name already exists.")
        else:  # Updating an existing object
            if (
                UnitOfMeasure.objects.filter(name__iexact=name)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise forms.ValidationError("A unit with this name already exists.")
        return name


# ADJUSTMENT FORM
class InventoryAdjustmentForm(forms.ModelForm):
    class Meta:
        model = InventoryAdjustment
        fields = [
            "item",
            "adjustment_type",
            "quantity_adjusted",
            "cost_price",
            "reason",
            "description",
        ]
        widgets = {
            "adjustment_type": forms.Select(),
            "description": forms.Textarea(attrs={"style": "height: 100px"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["item"].widget.attrs.update(
            {
                "class": "select2-item",
                "data-placeholder": "Select an item",
            }
        )

        self.fields["reason"].widget.attrs.update(
            {
                "class": "form-select",
            }
        )

        self.fields["adjustment_type"].widget.attrs.update(
            {
                "class": "form-select",
            }
        )
        self.fields["adjustment_type"].required = False

        self.fields["quantity_adjusted"].min_value = 1  # type: ignore
        self.fields["cost_price"].required = False
        self.fields["description"].required = False

        self.helper = FormHelper()
        self.helper.form_method = "post"

        self.helper.layout = Layout(
            Row(
                Column(
                    Field("item"),
                    css_class="col-md-6",
                ),
                Column(
                    Field("adjustment_type", placeholder="Select Adjustment Type"),
                    css_class="col-md-6",
                ),
                css_class="g-4 mb-4",
            ),
            Row(
                Column(
                    FloatingField("quantity_adjusted", placeholder="Quantity Adjusted"),
                    HTML(
                        '<div class="form-text text-muted">How many units to add or subtract.</div>'
                    ),
                    css_class="col-md-6",
                ),
                Column(
                    HTML(
                        """
                        <div class="input-group has-validation">
                            <span class="input-group-text">KES</span>
                            <div class="form-floating flex-grow-1">
                                <input type="number"
                                       name="cost_price"
                                       id="id_cost_price"
                                       class="form-control {% if errors.cost_price %}is-invalid{% endif %}"
                                       placeholder="Cost Price"
                                       value="{{ form.cost_price.value|default_if_none:'' }}"
                                       step="0.01">
                                <label for="id_cost_price" class="form-label">Cost Price</label>
                            </div>
                        </div>
                        {% if errors.cost_price %}
                            <div class="invalid-feedback d-block">
                                {% for error in errors.cost_price %}{{ error }}{% endfor %}
                            </div>
                        {% endif %}
                    """
                    ),
                    css_class="col-md-6",
                ),
                css_class="g-4 mb-4",
            ),
            Row(
                Column(
                    FloatingField("reason"),
                    css_class="col-md-6",
                ),
                Column(
                    FloatingField("description"),
                    css_class="col-md-12",
                ),
                css_class="g-4 mb-4",
            ),
        )

    def clean_quantity_adjusted(self):
        quantity = self.cleaned_data.get("quantity_adjusted")
        if quantity is None or quantity <= 0:
            raise forms.ValidationError("Enter a valid positive quantity.")
        return quantity

    def clean_cost_price(self):
        cost = self.cleaned_data.get("cost_price")
        if cost is not None and cost < 0:
            raise forms.ValidationError("Cost price cannot be negative.")
        return cost

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get("item")  # type: ignore
        adjustment_type = cleaned_data.get("adjustment_type")  # type: ignore
        quantity_adjusted = cleaned_data.get("quantity_adjusted")  # type: ignore

        if not adjustment_type:
            self.add_error("adjustment_type", "Please select an adjustment type.")

        if item and adjustment_type and quantity_adjusted is not None:
            if adjustment_type == InventoryAdjustment.DECREASE:
                if self.instance and self.instance.pk:
                    previous_quantity_adjusted = self.instance.quantity_adjusted
                    previous_adjustment_type = self.instance.adjustment_type

                    temp_stock = item.current_stock
                    if previous_adjustment_type == InventoryAdjustment.INCREASE:
                        temp_stock -= previous_quantity_adjusted
                    elif previous_adjustment_type == InventoryAdjustment.DECREASE:
                        temp_stock += previous_quantity_adjusted

                    if temp_stock < quantity_adjusted:
                        self.add_error(
                            "quantity_adjusted",
                            f"Cannot decrease stock by {quantity_adjusted}. Only {temp_stock} in stock after reversing previous adjustment.",
                        )
                else:
                    if (
                        item.current_stock is not None
                        and item.current_stock < quantity_adjusted
                    ):
                        self.add_error(
                            "quantity_adjusted",
                            f"Cannot decrease stock by {quantity_adjusted}. Only {item.current_stock} in stock.",
                        )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
