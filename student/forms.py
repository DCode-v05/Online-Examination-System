from django import forms

# Student signup forms - now using simple forms instead of ModelForms
class StudentUserForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, label='Username', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password')

class StudentForm(forms.Form):
    mobile = forms.CharField(max_length=20, label='Mobile Number', widget=forms.TextInput(attrs={'class': 'form-control'}))
