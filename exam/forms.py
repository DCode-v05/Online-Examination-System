from django import forms
from db_adapter import CourseAdapter

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    Message = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 30, 'class': 'form-control'}))

class TeacherSalaryForm(forms.Form):
    salary = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

class CourseForm(forms.Form):
    course_name = forms.CharField(max_length=50, label='Course Name', widget=forms.TextInput(attrs={'class': 'form-control'}))

class QuestionForm(forms.Form):
    courseID = forms.ChoiceField(choices=[], label='Course', widget=forms.Select(attrs={'class': 'form-control'}))
    marks = forms.IntegerField(label='Marks', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    question = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 50, 'class': 'form-control'}), label='Question')
    question_type = forms.ChoiceField(
        choices=[('radio', 'Single Choice'), ('checkbox', 'Multiple Choice'), ('text', 'Paragraph')],
        initial='radio',
        label='Question Type',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    option1 = forms.CharField(max_length=200, required=False, label='Option 1', widget=forms.TextInput(attrs={'class': 'form-control'}))
    option2 = forms.CharField(max_length=200, required=False, label='Option 2', widget=forms.TextInput(attrs={'class': 'form-control'}))
    option3 = forms.CharField(max_length=200, required=False, label='Option 3', widget=forms.TextInput(attrs={'class': 'form-control'}))
    option4 = forms.CharField(max_length=200, required=False, label='Option 4', widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer = forms.ChoiceField(
        choices=[('Option1', 'Option1'), ('Option2', 'Option2'), ('Option3', 'Option3'), ('Option4', 'Option4')],
        required=False,
        label='Answer',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    multiple_answers = forms.CharField(max_length=400, required=False, label='Multiple Answers', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Option1,Option3'}))
    text_answer = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Expected text answer'}), required=False, label='Text Answer')
    
    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        courses = CourseAdapter.get_all()
        course_choices = [(c.get('id'), c.get('course_name')) for c in courses]
        self.fields['courseID'].choices = [('', 'Course Name')] + course_choices

class QuestionFormNoCourse(forms.Form):
    marks = forms.IntegerField(label='Marks', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    question = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 50, 'class': 'form-control'}), label='Question')
    question_type = forms.ChoiceField(
        choices=[('radio', 'Single Choice'), ('checkbox', 'Multiple Choice'), ('text', 'Paragraph')],
        initial='radio',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Question Type'
    )
    option1 = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Option 1')
    option2 = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Option 2')
    option3 = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Option 3')
    option4 = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Option 4')
    answer = forms.ChoiceField(
        choices=[('Option1', 'Option1'), ('Option2', 'Option2'), ('Option3', 'Option3'), ('Option4', 'Option4')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Answer'
    )
    multiple_answers = forms.CharField(max_length=400, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Option1,Option3'}), label='Multiple Answers')
    text_answer = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Expected text answer'}), required=False, label='Text Answer')
