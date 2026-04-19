from django import forms
from django.core import validators
from django.contrib.auth.models import Group

from .models import Product


# class ProductForm(forms.Form):
#     name = forms.CharField(max_length=100)
#     price = forms.DecimalField(min_value=1, max_value=100000, decimal_places=2)
#     description = forms.CharField(
#         label="Product description",
#         widget=forms.Textarea(attrs={"rows":5, "cols": "30"}),
#         validators=[validators.RegexValidator(
#            regex=r"great",
#            message="Field must contain word 'great'",
#         )],
#     )

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = "name", "price", "description", "discount"
#
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"

    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )

class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
