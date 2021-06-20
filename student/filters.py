import django_filters
from .models import Student_Course, Student

class StudentFilter(django_filters.FilterSet):
    class Meta:
        model = Student
        fields = '__all__'
        

class Student_CourseFilter(django_filters.FilterSet):
    class Meta:
        model = Student_Course
        fields = '__all__'
        exclude = ['student','mid_marks','final_marks']
