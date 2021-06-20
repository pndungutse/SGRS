from django.db import models
from django.contrib.auth.models import User

# Create your models here.

GENDER = [
    ("M", "MALE"),
    ("F", "FEMALE"),
]
PHYSICAL_DISABILITY = [
    ("YES", "YES"),
    ("NO", "NO")
]
QUATER = [
    ("QUATER1", "QUATER1"),
    ("QUATER2", "QUATER2"),
    ("QUATER3", "QUATER3"),
]

class District(models.Model):
    user = models.OneToOneField(User,null=True, on_delete=models.CASCADE)
    district_name = models.CharField(max_length=30, blank=False)
    profile_pc = models.ImageField(default="anonymous-user.png", null=True, blank=True)

    def __str__(self):
        return self.district_name

class Sector(models.Model):
    user = models.OneToOneField(User,null=True, on_delete=models.CASCADE)
    sector_name = models.CharField(max_length=30)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    profile_pc = models.ImageField(default="anonymous-user.png", null=True, blank=True)

    def __str__(self):
        return self.sector_name

class School(models.Model):
    user = models.OneToOneField(User,null=True, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=30)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    profile_pc = models.ImageField(default="anonymous-user.png", null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.school_name

class Classe(models.Model):
    class_name = models.CharField(max_length=30)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return self.class_name

class Course(models.Model):
    course_name = models.CharField(max_length=30)
    course_desc = models.CharField(max_length=50)

    def __str__(self):
        return self.course_name

class Student(models.Model):
    f_name = models.CharField(max_length=30, blank=False)
    l_name = models.CharField(max_length=30, blank=False)
    gender = models.CharField(max_length=1, choices=GENDER)
    dob = models.DateField()
    year_reg = models.IntegerField()
    physical_disability = models.CharField(max_length=15, choices=PHYSICAL_DISABILITY, default="NO")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    
    

    def __str__(self):
        return self.f_name  

class Student_Course(models.Model):
    student = models.ForeignKey(Student, on_delete = models.CASCADE)
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    mid_marks = models.FloatField(default=0.0)
    final_marks = models.FloatField(default=0.0)
    quater = models.CharField(max_length=10, choices=QUATER)  
