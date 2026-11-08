from django import forms
from db_adapter import CourseAdapter

class TeacherUserForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, label='Username', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password')

class TeacherForm(forms.Form):
    mobile = forms.CharField(max_length=20, label='Mobile Number', widget=forms.TextInput(attrs={'class': 'form-control'}))
    course = forms.ChoiceField(choices=[], required=False, label='Assigned Course', widget=forms.Select(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        courses = CourseAdapter.get_all()
        course_choices = [(c.get('id'), c.get('course_name')) for c in courses]
        self.fields['course'].choices = [('', 'Select Course')] + course_choices

