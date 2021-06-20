from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column
from crispy_forms.bootstrap import InlineRadios, FormActions
from .models import District,Sector,School,Classe,Student,Course,Student_Course,User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, ValidationError
from datetime import date
import datetime


class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = '__all__'
        labels = {
            'district_name': 'District Name',
            'profile_pc':'Profilr_Pic',
            'user': 'User',
        }
    def clean_district_name(self):
        district_name = self.cleaned_data.get('district_name')
        if (district_name == ""):
            raise forms.ValidationError('This field cannot be left blank')
        return district_name

class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = '__all__'
        labels = {
            'sector_name':'Sector Name',
            'district':'District Name',
            'profile_pc':'Profilr_Pic',
            'user': 'User',
        }
    def __init__(self, *args, **kwargs):
        super(SectorForm,self).__init__(*args, **kwargs)
        self.fields['district'].empty_label = "Select District"

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = '__all__'
        
        labels = {
            'school_name':'School Name',
            'sector':'Sector Name',
            'logo':'Logo',
            'profile_pc': 'Profile Pic',
            'user':'User'
        }
    def __init__(self, *args, **kwargs):
        super(SchoolForm,self).__init__(*args, **kwargs)
        self.fields['sector'].empty_label = "Select Sector"

class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ('class_name','school')
        labels = {
            'class_name':'Class Name',
            'school':'School Name'
        }
    def __init__(self, *args, **kwargs):
        super(ClasseForm,self).__init__(*args, **kwargs)
        self.fields['school'].empty_label = "Select School"

class DateInput(forms.DateInput):
    input_type = 'date'

class StudentForm(forms.ModelForm):
    dob =forms.DateField(widget=DateInput)
    # year_reg=forms.IntegerField(widget=forms.Select())
    class Meta:
        model = Student
        fields = ('f_name','l_name','gender','dob','year_reg','physical_disability','classe')
        labels = {
            'f_name':'First Name',
            'l_name':'Last Name',
            'gender':'Gender',
            'dob':'Date of Birth',
            'year_reg':'Registration Year',
            'classe':'Class Name',
            'physical_disability':'Physical Disability?'
            
        }
        
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.helper.attrs = {
    #         'novalidate': ''
    #     }
    def clean_dob(self):
        data = self.cleaned_data.get('dob')
        if str(data) > str(datetime.datetime.today().date()):
            raise forms.ValidationError(
                'you can\'t add future date')
        return data
    def clean_first_name(self):
        data = self.cleaned_data.get('f_name')
        if data == "":
            raise ValidationError("First Name is Required")
        return data
   
    def __init__(self,*args,**kwargs):
        super(StudentForm,self).__init__(*args,**kwargs)
        self.fields['classe'].empty_label = "Select Class"
        self.fields['gender'].empty_label = "Select Gender"
        
    

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('course_name', 'course_desc')
        labels = {
            'course_name':'Course Name',
            'course_desc':'Course Description'
        }

class StudentCourseForm(forms.ModelForm):
    class Meta:
        model = Student_Course
        fields = ('student','course','quater', 'mid_marks', 'final_marks')
        labels = {
            'course':'Course Name',
            'mid_marks':'Mid Marks',
            'final_marks':'Final Marks',
            'student':'Student Name'
        }
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2'
        )
        
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        
        for fieldname in ['username','email','password1','password2']:
            self.fields[fieldname].help_text = None
    def save(self, commit=True):
        user = super(RegistrationForm,self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            
        return user
    
