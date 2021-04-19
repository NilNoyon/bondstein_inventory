from django import forms
from .models import *

# forms
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"

class ResponsiblePersonForm(forms.ModelForm):
    class Meta:
        model = ResponsiblePerson
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ResponsiblePersonForm, self).__init__(*args, **kwargs)
        self.fields['address'].required = False

class SalesOrderForm(forms.ModelForm):
	class Meta:
		model = SalesOrder
		fields = "__all__"

class SODetailsForm(forms.ModelForm):
	class Meta:
		model = SODetails
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		super(SODetailsForm, self).__init__(*args, **kwargs)
		self.fields['remarks'].required = False
		self.fields['barcode'].required = False

class STChallanForm(forms.ModelForm):
	class Meta:
		model = STChallan
		fields = "__all__"

class STCDetailsForm(forms.ModelForm):
	class Meta:
		model = STCDetails
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		super(STCDetailsForm, self).__init__(*args, **kwargs)
		self.fields['remarks'].required = False
		self.fields['barcode'].required = False

class STCBarcodeForm(forms.ModelForm):
	class Meta:
		model = STCBarcode
		fields = "__all__"
