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

class FOForm(forms.ModelForm):
	class Meta:
		model = FloatingSalesOrder
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		super(FOForm, self).__init__(*args, **kwargs)
		self.fields['total_item'].required = False
		self.fields['total_sell'].required = False
		self.fields['total_return'].required = False

class FODetailsForm(forms.ModelForm):
	class Meta:
		model = FloatingSalesDetails
		fields = "__all__"

class CDForm(forms.ModelForm):
	class Meta:
		model = ChannelDemand
		fields = "__all__"

class CDDetailsForm(forms.ModelForm):
	class Meta:
		model = ChannelDemandDetails
		fields = "__all__"
