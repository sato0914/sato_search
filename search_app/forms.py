from django import forms
from .models import Product
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SearchForm(forms.Form):
    query = forms.CharField(
        label='検索キーワード',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '検索したいキーワードを入力'})
    )
    min_price = forms.DecimalField(
        label='最低価格',
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': '最低価格を入力'})
    )
    max_price = forms.DecimalField(
        label='最高価格',
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': '最高価格を入力'})
    )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image']

    image = forms.ImageField(required=False)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")