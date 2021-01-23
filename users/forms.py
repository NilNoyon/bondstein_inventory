from django import forms
from .models import User, Warehouse

class WarehouseForm(forms.ModelForm):
    """docstring for ClassName"""
    class Meta:
        model = Warehouse
        fields = "__all__"

class UserAddForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'fullname', 'password', 'email', 'is_active', 'designation','role','date_joined','warehouse')
        widgets = {
            'password': forms.PasswordInput()
        }

    def __init__(self, *args, **kwargs):
        super(UserAddForm, self).__init__(*args, **kwargs)
        self.fields['password'].required = False
        self.fields['designation'].required = False
        self.fields['date_joined'].required = False


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'fullname', 'email', 'is_active', 'designation','role','date_joined','warehouse')

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['password'].required = False
        self.fields['designation'].required = False
        self.fields['date_joined'].required = False