from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from datetime import date
from .models import Booking


class CustomUserCreationForm(UserCreationForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    phone = forms.CharField(max_length=15)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('birth_date', 'phone')


class SignInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'room',
            'first_name',
            'last_name',
            'address',
            'email',
            'no_of_guests',
            'check_in',
            'check_out',
            'special_request',
        ]
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def clean_check_in(self):
        check_in = self.cleaned_data.get('check_in')
        if check_in < date.today():
            raise forms.ValidationError("Check-in date must be today or later.")
        return check_in
    
    def clean_check_out(self):
        check_out = self.cleaned_data.get('check_out')
        if check_out < date.today():
            raise forms.ValidationError("Check-out date must be today or later.")
        return check_out
    
    def clean_on_of_guests(self):
        no_of_guests = self.cleaned_data.get('no_of_guests')
        if no_of_guests < 1:
            raise forms.ValidationError("Number of guests must be at least 1.")
        return no_of_guests

