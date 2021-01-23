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
