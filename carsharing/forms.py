from django import forms
from django.contrib.auth.models import User

from carsharing.models import Document


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class RegisterForm(forms.Form):

    username = forms.CharField()
    password = forms.CharField()
    email = forms.EmailField()

    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username).first()
        if user is not None:
            raise forms.ValidationError("Пользователь с таким именем уже существует")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).first()
        if user is not None:
            raise forms.ValidationError("Пользователь с такой почтой уже существует")
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError("Пароль должен состоять из 8 и более символов")
        return password


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ('passport', 'driving_license', 'driving_category')
