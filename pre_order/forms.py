from django import forms
from .models import *

# forms
class PreOrderForm(forms.ModelForm):
    class Meta:
        model = PreOrder
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(PreOrderForm, self).__init__(*args, **kwargs)
        self.fields['created_by'].required = False
        self.fields['is_deleted'].required = False

class PreOrderDetailsForm(forms.ModelForm):
    class Meta:
        model = PreOrderDetails
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(PreOrderDetailsForm, self).__init__(*args, **kwargs)
        self.fields['created_by'].required = False
        self.fields['is_deleted'].required = False
        self.fields['unit_price'].required = False

class BarcodeForm(forms.ModelForm):
    class Meta:
        model = Barcode
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(BarcodeForm, self).__init__(*args, **kwargs)
        self.fields['sku'].required = False
        self.fields['bst'].required = False

class ScannedBarcodeForm(forms.ModelForm):
    class Meta:
        model = ScannedBarcode
        fields = "__all__"


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)
        self.fields['updated_by'].required = False

class StockLogForm(forms.ModelForm):
    class Meta:
        model = StockLog
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(StockLogForm, self).__init__(*args, **kwargs)
        self.fields['created_by'].required = False

class SupplierForm(forms.ModelForm):
    """docstring for ClassName"""
    class Meta:
        model = Supplier
        fields = "__all__"

class ItemCategoryForm(forms.ModelForm):
    """docstring for ClassName"""
    class Meta:
        model = ItemCategory
        fields = "__all__"

class ItemHeadForm(forms.ModelForm):
    """docstring for ClassName"""
    class Meta:
        model = Item
        fields = "__all__"

class ItemDetailsForm(forms.ModelForm):
    class Meta:
        model = ItemDetails
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ItemDetailsForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].required = False
