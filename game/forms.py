from django import forms
from .models import CustomUser

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[('student', 'Moksleivis'), ('teacher', 'Mokytojas')])

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'role']