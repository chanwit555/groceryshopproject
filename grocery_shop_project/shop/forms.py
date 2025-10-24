from django import forms
from django.contrib.auth.models import User
from .models import Product
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=4)
    class Meta:
        model = User
        fields = ['first_name','username','password']
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','category','price','stock']
