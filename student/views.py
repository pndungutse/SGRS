from django.http import JsonResponse, HttpResponse
from django import template
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.views.generic import View
from.utils  import render_to_pdf
from django.template.loader import get_template
from rest_framework.views import APIView
from rest_framework.response import Response
from django.forms import inlineformset_factory
from django.template.loader import render_to_string
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import login, logout
from .models import District, School, Sector,Classe,Student,Student_Course,Course
from django.db.models import Q, F
from .forms import DistrictForm,SectorForm,SchoolForm,ClasseForm,StudentForm,CourseForm,StudentCourseForm,RegistrationForm
from .decolator import unauthenticated_user, allowed_users
from .filters import StudentFilter,Student_CourseFilter
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.db import connection
import datetime
import xlwt




# @login_required(login_url='/login')
# Create your views here.
def home_view(request):
    template = 'home.html'
    context = {}
    return render(request, template, context)

# @login_required(login_url='/login')
# @allowed_users(allowed_roles=['reb','district','sector','secretary'])
# def home(request):

#     districts = District.objects.all()
#     sectors = Sector.objects.all()
#     schools = School.objects.all()


#     total_districts = districts.count()
#     total_sectors = sectors.count()
#     total_schools = schools.count()
    

#     context = {'total_districts':total_districts,'total_sectors':total_sectors,
#     'total_schools':total_schools,'districts':districts,'sectors':sectors,'schools':schools}
#     return render(request,'home.html',context)

# @login_required(login_url='/login')
# @allowed_users(allowed_roles=['reb'])
# def dashboard(request):
#     districts = District.objects.all()
#     sectors = Sector.objects.all()
#     schools = School.objects.all()


#     total_districts = districts.count()
#     total_sectors = sectors.count()
#     total_schools = schools.count()

#     context = {'total_districts':total_districts,
#     'total_sectors':total_sectors,'total_schools':total_schools,
#     'districts':districts,'sectors':sectors,'schools':schools}
#     return render(request,'dashboard.html',context)
@unauthenticated_user
def loginOrg(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # log the user in
            user = form.get_user()
            login(request, user)
            if District.objects.filter(user=user):
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect('districtPage')
            elif Sector.objects.filter(user=user):
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect('sectorPage')
            elif School.objects.filter(user=user):
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect('schoolPage')
    else:
        form = AuthenticationForm()
    return render(request, 'loginOrg.html', {'form':form})

@login_required(login_url='/login')
@allowed_users(allowed_roles=['reb','district'])
def sector_create(request, id=0):
    if(request.method == "GET"):
        if id == 0:
            form = SectorForm()
        else:
            sector = Sector.objects.get(pk=id)
            form = SectorForm(instance = sector)
        return render(request,'districtPages/districtSectorForm.html',{'form':form})
    else:
        if id==0:
            form = SectorForm(request.POST)
        else:
            sector = Sector.objects.get(pk=id)
            form = SectorForm(request.POST,instance = sector)
        if form.is_valid():
            form.save()
            messages.success(request, 'The transaction on Sector has been made Successfully')
        return redirect('districtPage')
@login_required(login_url='/login')
@allowed_users(allowed_roles=['reb','district'])
def sector_delete(request, id):
    sector = Sector.objects.get(pk=id)
    sector.delete()
    messages.success(request, 'Sector has been deleted Successfully')
    return redirect('districtPage')

@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector'])
def school_create(request):
    userr = request.user.id
    sector = Sector.objects.get(user=userr)
    users = User.objects.all()
    
    sector = Sector.objects.get(user=userr)
    form = SchoolForm(initial={'sector':sector})
    form.fields['sector'].queryset = Sector.objects.filter(user=userr)
    
    if(request.method == "POST"):
        form = SchoolForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'School has been Created Successfully')
            return redirect('schoolList')
    context = {'form':form,'sector':sector}
    return render(request,'sectorPages/sectorSchoolForm.html',context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector'])
def school_update(request, pk_school):
    user = request.user
    sector = Sector.objects.get(user=user)
    school = School.objects.get(id=pk_school)
    form = SchoolForm(instance=school)
    form.fields['sector'].queryset = School.objects.filter(sector=sector.id)
    if request.method == 'POST':
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid:
            form.save()
            messages.success(request, 'School has been Updated Successfully')
            return redirect('schoolList')
    context = {'form':form}
    return render(request, 'sectorPages/sectorSchoolForm.html',context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['reb','district','sector'])
def school_delete(request, id):
    school = School.objects.get(pk=id)
    school.delete()
    messages.success(request, 'School has been deleted Successfully')
    return redirect('sectorPage')
@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])
def classe_create(request):
    userr = request.user.id
    schooll = School.objects.get(user=userr)
    form = ClasseForm(initial={'school':schooll})
    if(request.method == "POST"):
        form = ClasseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class has been Created Successfully')
            return redirect('classeList')
    context = {'form':form,'school':schooll}
    return render(request,'schoolPages/schoolClassForm.html',context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])
def class_update(request, pk_class):
    classe = Classe.objects.get(id=pk_class)
    form = ClasseForm(instance=classe)
    if request.method == 'POST':
        form = ClasseForm(request.POST, instance=classe)
        if form.is_valid:
            form.save()
            messages.success(request, 'Class has been Updated Successfully')
            return redirect('classeList')
    context = {'form':form}
    return render(request, 'schoolPages/schoolclassForm.html',context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])
def class_delete(request, id):
    classe = Classe.objects.get(pk=id)
    classe.delete()
    messages.success(request, 'Class has been deleted Successfully')
    return redirect('classeList')

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])
def student_create(request):
    user = request.user.id
    school = School.objects.get(user=user)
    school_id = school.id
    
    classes = Classe.objects.filter(school = school_id) 
    form = StudentForm()
    form.fields['classe'].queryset = Classe.objects.filter(school=school_id)
    if request.method == "GET":
        context = {'form':form,'school':school}
        return render(request,"schoolPages/schoolStudentForm.html",context)
    else:
        
        form = StudentForm(request.POST)
        if form.is_valid:
            form.save()
            first_name = form.cleaned_data.get('f_name')
            last_name = form.cleaned_data.get('l_name')
            messages.success(request, 'Student has been Created Successfully ' +first_name)
        return redirect('studentList')
    
@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])
def student_update(request, pk_student):
    
    user = request.user
    school = School.objects.get(user=user)
    school_id = school.id
    
    student = Student.objects.get(id=pk_student)
    form = StudentForm(instance=student)
    form.fields['classe'].queryset = Classe.objects.filter(school=school_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid:
            form.save()
            messages.success(request, 'Student has been Updated Successfully')
            return redirect('studentList')
    context = {'form':form}
    return render(request, 'schoolPages/schoolStudentForm.html',context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])
def student_delete(request, pk_student):
    student = Student.objects.get(id=pk_student)
    if request.method=='POST':
        student.delete()
        messages.success(request,'The Student has been delele successfully')
        return redirect('studentList')
    context = {'student':student}
    return render(request, 'deleteoption.html', context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])
def course_create(request):
    user = request.user
    school = School.objects.get(user=user)
    if request.method == "GET":
        form = CourseForm()
        context = {'form':form,'school':school}
        return render(request,'schoolPages/schoolCourseForm.html',context)
    else:
        form = CourseForm(request.POST)
        if form.is_valid:
            form.save()
            messages.success(request, 'Course has been Created Successfully')
        return redirect('courseList')
@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])   
def course_update(request, pk_course):
    course = Course.objects.get(id=pk_course)
    form = CourseForm(instance=course)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid:
            form.save()
            messages.success(request, 'Course has been Updated Successfully')
            return redirect('schoolPages/home_school.html')
    context = {'form':form}
    return render(request, 'schoolPages/schoolCourseForm.html',context)

@unauthenticated_user
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # log the user in
            user = form.get_user()
            login(request, user)
            if District.objects.filter(user=user):
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect('districtPage')
            elif Sector.objects.filter(user=user):
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect('sectorPage')
            elif School.objects.filter(user=user):
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect('schoolPage')
            elif user.is_superuser:
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect(rebPage)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', { 'form': form })


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

@unauthenticated_user
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
             #  log the user in
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', { 'form': form })    
    
def school(request, pk_school):
    schooll = School.objects.get(id=pk_school)
    classes = schooll.classe_set.all()
    total_classes = classes.count()
    context = {'schooll':schooll, 'classes':classes, 'total_classes':total_classes}
    return render(request, 'sectorPages/school.html', context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])
def studentList(request):
    user=request.user
    school = School.objects.get(user=user)
    school_id = school.id
    
    now = datetime.datetime.now()
    year = now.year
    
    cursor = connection.cursor()
    students = 'select student_student.id,f_name,l_name,gender,dob,year_reg, physical_disability,class_name from student_student,student_classe,student_school where student_student.classe_id=student_classe.id and student_classe.school_id=student_school.id and student_school.id=%s and student_student.year_reg=%s' %(school_id,year)
    cursor.execute(students)
    answers = cursor.fetchall()
    paginator = Paginator(answers, 8) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    # myFilter1 = StudentFilter(request.GET, queryset=student_list)
    
    
    context = {'page_obj':page_obj,'school':school}
    return render(request,'schoolPages/studentList.html',context)

register = template.Library() 

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])
def courseList(request):
    
    user = request.user
    school= School.objects.get(user=user)
    course_list = Course.objects.all()
    paginator = Paginator(course_list, 5) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj':page_obj,'school':school}
    return render(request,'schoolPages/courseList.html',context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])
def classeList(request):
    
    user = request.user
    school = School.objects.get(user=user)
    school_id = school.id
    
    
    class_list = Classe.objects.filter(school=school_id)
    paginator = Paginator(class_list, 5) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj':page_obj,'school':school}
    
    return render(request, 'schoolPages/classeList.html',context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['district'])  
def sectorList(request):
    
    user = request.user
    district = District.objects.get(user=user)
    
    sector_list = Sector.objects.filter(district=request.user.district)
    paginator = Paginator(sector_list, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj':page_obj,'district':district}
    
    return render(request,'districtPages/sectorList.html',context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector'])  
def schoolList(request):
    
    user = request.user
    sector = Sector.objects.get(user=user)
    
    school_list = School.objects.filter(sector=request.user.sector)
    paginator = Paginator(school_list, 5) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj':page_obj,'sector':sector}
    
    return render(request,'sectorPages/schoolList.html',context)

def classe(request, pk_class):
    user = request.user
    school = School.objects.get(user=user)
    classee = Classe.objects.get(id=pk_class)
    students = classee.student_set.all()
    total_students = students.count()
    myFilter = StudentFilter()
    context = {'classee':classee,'students':students, 'total_students':total_students,'myFilter':myFilter, 'school':school}
    template = 'schoolPages/student.html'
    
    return render(request, template, context)

def student(request, pk_student):
    user = request.user
    school = School.objects.get(user=user)
    
    studentt = Student.objects.get(id=pk_student)
    student_courses = studentt.student_course_set.all()
    myFilter = Student_CourseFilter(request.GET, queryset=student_courses)
    student_courses = myFilter.qs

    context = {'studentt':studentt,'student_courses':student_courses,'myFilter':myFilter,'school':school}
    return render(request, 'schoolPages/student.html', context)

@login_required(login_url='/login')
def view401(request):
    return render(request,'401.html')

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary'])  
def searchClass(request):
    try:
        year = request.GET.get('year')
        q = request.GET.get('q')
    except:
        year = None
        q = None
    if year:
        if q:
            schooluser = request.user.id
            school = School.objects.get(user=schooluser)
        
            classes = Classe.objects.filter(school=school.id)
            
        
            classee = Classe.objects.get(school=school.id,id=q)
            
            classee_id = classee.id
            
            students = Student.objects.filter(classe=classee_id, year_reg=year)
            total_students = students.count()
            
            template = 'schoolPages/classe.html'
            context = {'query':q, 'classee':classee,'classee_id':classee_id,'students':students,'total_students':total_students,'classes':classes,'school':school}
    else:
        schooluser = request.user.id
        school = School.objects.get(user=schooluser)
        
        classes = Classe.objects.filter(school=school.id)
        
        template = 'schoolPages/searchClass.html'
        context = {'classes':classes,'school':school}
    
    return render(request,template,context)

def createStudentCourse(request, pk_student):
    user = request.user
    school = School.objects.get(user=user)
    Student_CourseFormSet = inlineformset_factory(Student, Student_Course, fields=('course','quater','mid_marks','final_marks'),max_num=15, extra=15)
    studentt = Student.objects.get(id=pk_student)
    formSet = Student_CourseFormSet(instance=studentt)
    # form = StudentCourseForm(initial={'student':studentt})
    if request.method == 'POST':
        #form = StudentCourseForm(request.POST)
        formSet = Student_CourseFormSet(request.POST,instance=studentt)
        if formSet.is_valid():
            formSet.save()
            messages.success(request, 'The Student has been given marks successfully')
            return redirect('searchClass')
    context = {'formSet':formSet,'studentt':studentt,'school':school}
    return render(request,'schoolPages/studentcourse.html', context)

def student_course_update(request, pk_student_course):
    
    studentcourse = Student_Course.objects.get(id=pk_student_course)
    form = StudentCourseForm(instance=studentcourse)
    if request.method == 'POST':
        form = StudentCourseForm(request.POST, instance=studentcourse)
        if form.is_valid:
            form.save()
            messages.success(request, 'Marks has been Updated Successfully')
            return redirect('schoolPage')
    context = {'form':form}
    return render(request, 'schoolPages/studentcourse.html',context)

def student_course_delete(request, pk_student_course):
    studentcourse = Student_Course.objects.get(id=pk_student_course)
    if request.method=='POST':
        studentcourse.delete()
        messages.success(request,'The marks has been delele successfully')
        return redirect('schoolPage')
    context = {'studentcourse':studentcourse}
    return render(request, 'deletestudent_course_option.html', context)

def createClass(request, pk_class):
    classe = Classe.objects.get(id=pk_class)
    form = StudentForm(initial={'classe':classe})
    
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class')
    context = {'form':form}
    return render(request,'schoolPages/schoolStudentForm.html', context)
 
@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector'])  
def sectorPage(request):
    
    now = datetime.datetime.now()
    year = now.year
    
    n_allstudents = 0
    
    total_engl_student = 0
    total_math_student = 0
    total_social_student = 0
    total_est_student = 0
    total_kiny_student = 0
    
    
    count_math_25 = 0
    count_math_50 = 0
    count_math_75 = 0
    count_math_100 = 0
    
    count_est_25 = 0
    count_est_50 = 0
    count_est_75 = 0
    count_est_100 = 0
    
    count_engl_25 = 0
    count_engl_50 = 0
    count_engl_75 = 0
    count_engl_100 = 0
    
    count_social_25 = 0
    count_social_50 = 0
    count_social_75 = 0
    count_social_100 = 0
    
    count_kiny_25 = 0
    count_kiny_50 = 0
    count_kiny_75 = 0
    count_kiny_100 = 0
    
    
    user = request.user
    sector = Sector.objects.get(user=user)
    sector_id = sector.id
    schools = School.objects.filter(sector=sector_id)
    for school in schools:
        classes = Classe.objects.filter(school=school.id)
        for classe in classes:
            students = Student.objects.filter(classe=classe.id,year_reg=year)
            for student in students:
                n_allstudents =n_allstudents + 1
                for math_quater1_year1 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                    total_math_quater1_year1 = math_quater1_year1.mid_marks + math_quater1_year1.final_marks
                for est_quater1_year1 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                    total_est_quater1_year1 = est_quater1_year1.mid_marks + est_quater1_year1.final_marks
                for social_quater1_year1 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                    total_social_quater1_year1 = social_quater1_year1.mid_marks + social_quater1_year1.final_marks
                for kiny_quater1_year1 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                    total_kiny_quater1_year1 = kiny_quater1_year1.mid_marks + kiny_quater1_year1.final_marks
                for engl_quater1_year1 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                    total_engl_quater1_year1 = engl_quater1_year1.mid_marks + engl_quater1_year1.final_marks
                    
                for math_quater2_year1 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                    total_math_quater2_year1 = math_quater2_year1.mid_marks + math_quater2_year1.final_marks
                for est_quater2_year1 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                    total_est_quater2_year1 = est_quater2_year1.mid_marks + est_quater2_year1.final_marks
                for social_quater2_year1 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                    total_social_quater2_year1 = social_quater2_year1.mid_marks + social_quater2_year1.final_marks
                for kiny_quater2_year1 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                    total_kiny_quater2_year1 = kiny_quater2_year1.mid_marks + kiny_quater2_year1.final_marks
                for engl_quater2_year1 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                    total_engl_quater2_year1 = engl_quater2_year1.mid_marks + engl_quater2_year1.final_marks
                
                for math_quater3_year1 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                    total_math_quater3_year1 = math_quater3_year1.mid_marks + math_quater3_year1.final_marks
                for est_quater3_year1 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                    total_est_quater3_year1 = est_quater3_year1.mid_marks + est_quater3_year1.final_marks
                for social_quater3_year1 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                    total_social_quater3_year1 = social_quater3_year1.mid_marks + social_quater3_year1.final_marks
                for kiny_quater3_year1 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                    total_kiny_quater3_year1 = kiny_quater3_year1.mid_marks + kiny_quater3_year1.final_marks
                for engl_quater3_year1 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                    total_engl_quater3_year1 = engl_quater3_year1.mid_marks + engl_quater3_year1.final_marks
                    
                    total_math_year1 = total_math_quater1_year1 +total_math_quater2_year1 + total_math_quater3_year1
                    total_est_year1 = total_est_quater1_year1 + total_est_quater2_year1 + total_est_quater3_year1
                    total_social_year1 = total_social_quater1_year1 + total_social_quater2_year1 + total_social_quater3_year1
                    total_kiny_year1 = total_kiny_quater1_year1 + total_kiny_quater2_year1 + total_kiny_quater3_year1
                    total_engl_year1 = total_engl_quater1_year1 + total_engl_quater2_year1 + total_engl_quater3_year1
                    
                    total_math_year1_percent = (total_math_year1 * 100)/600
                    total_est_year1_percent = (total_est_year1 * 100)/600
                    total_social_year1_percent = (total_social_year1 * 100)/600
                    total_kiny_year1_percent = (total_kiny_year1 * 100)/600
                    total_engl_year1_percent = (total_engl_year1 * 100)/600
                    
                    if total_math_year1_percent >= 0 and total_math_year1_percent <= 100:
                        total_math_student = total_math_student + 1 
                        if total_math_year1_percent<=25:
                            count_math_25 = count_math_25 + 1
                        if total_math_year1_percent<=50 and total_math_year1_percent>=26:
                            count_math_50 = count_math_50 + 1
                        if total_math_year1_percent<=75 and total_math_year1_percent>=51:
                            count_math_75 = count_math_75 + 1
                        if total_math_year1_percent<=100 and total_math_year1_percent>=76:
                            count_math_100 = count_math_100 + 1 
                    
                    if total_est_year1_percent >= 0 and total_est_year1_percent <= 100:
                        total_est_student = total_est_student + 1    
                        if total_est_year1_percent<=25:
                            count_est_25 = count_est_25 + 1
                        if total_est_year1_percent<=50 and total_est_year1_percent>=26:
                            count_est_50 = count_est_50 + 1
                        if total_est_year1_percent<=75 and total_est_year1_percent>=51:
                            count_est_75 = count_est_75 + 1
                        if total_est_year1_percent<=100 and total_est_year1_percent>=76:
                            count_est_100 = count_est_100 + 1 
                    
                    if total_social_year1_percent >= 0 and total_social_year1_percent <= 100:
                        total_social_student = total_social_student + 1     
                        if total_social_year1_percent<=25:
                            count_social_25 = count_social_25 + 1
                        if total_social_year1_percent<=50 and total_social_year1_percent>=26:
                            count_social_50 = count_social_50 + 1
                        if total_social_year1_percent<=75 and total_social_year1_percent>=51:
                            count_social_75 = count_social_75 + 1
                        if total_social_year1_percent<=100 and total_social_year1_percent>=76:
                            count_social_100 = count_social_100 + 1
                     
                    if total_kiny_year1_percent >= 0 and total_kiny_year1_percent <= 100:
                        total_kiny_student = total_kiny_student + 1    
                        if total_kiny_year1_percent<=25:
                            count_kiny_25 = count_kiny_25 + 1
                        if total_kiny_year1_percent<=50 and total_kiny_year1_percent>=26:
                            count_kiny_50 = count_kiny_50 + 1
                        if total_kiny_year1_percent<=75 and total_kiny_year1_percent>=51:
                            count_kiny_75 = count_kiny_75 + 1
                        if total_kiny_year1_percent<=100 and total_kiny_year1_percent>=76:
                            count_kiny_100 = count_kiny_100 + 1 
                    
                    if total_engl_year1_percent >= 0 and total_engl_year1_percent <= 100:
                        total_engl_student = total_engl_student + 1     
                        if total_engl_year1_percent<=25:
                            count_engl_25 = count_engl_25 + 1
                        if total_engl_year1_percent<=50 and total_engl_year1_percent>=26:
                            count_engl_50 = count_engl_50 + 1
                        if total_engl_year1_percent<=75 and total_engl_year1_percent>=51:
                            count_engl_75 = count_engl_75 + 1
                        if total_engl_year1_percent<=100 and total_engl_year1_percent>=76:
                            count_engl_100 = count_engl_100 + 1
    
    context = {'total_engl_student':total_engl_student,'total_math_student':total_math_student,'total_social_student':total_social_student,'total_est_student':total_est_student,'total_kiny_student':total_kiny_student,
        'user':user,'sector':sector,'n_allstudents':n_allstudents,'schools':schools,
               'count_math_25':count_math_25,'count_math_50':count_math_50,'count_math_75':count_math_75,'count_math_100':count_math_100,
               'count_est_25':count_est_25,'count_est_50':count_est_50,'count_est_75':count_est_75,'count_est_100':count_est_100,
               'count_social_25':count_social_25,'count_social_50':count_social_50,'count_social_75':count_social_75,'count_social_100':count_social_100,
               'count_kiny_25':count_kiny_25,'count_kiny_50':count_kiny_50,'count_kiny_75':count_kiny_75,'count_kiny_100':count_kiny_100,
               'count_engl_25':count_engl_25,'count_engl_50':count_engl_50,'count_engl_75':count_engl_75,'count_engl_100':count_engl_100}

    
    return render(request, 'sectorPages/home_sector.html',context)  
 
@login_required(login_url='/login')
@allowed_users(allowed_roles=['district'])
def districtPage(request):
    
    now = datetime.datetime.now()
    year = now.year
    
    n_students = 0
    
    total_engl_student = 0
    total_math_student = 0
    total_social_student = 0
    total_est_student = 0
    total_kiny_student = 0
    
    
    count_math_25 = 0
    count_math_50 = 0
    count_math_75 = 0
    count_math_100 = 0
    
    count_est_25 = 0
    count_est_50 = 0
    count_est_75 = 0
    count_est_100 = 0
    
    count_engl_25 = 0
    count_engl_50 = 0
    count_engl_75 = 0
    count_engl_100 = 0
    
    count_social_25 = 0
    count_social_50 = 0
    count_social_75 = 0
    count_social_100 = 0
    
    count_kiny_25 = 0
    count_kiny_50 = 0
    count_kiny_75 = 0
    count_kiny_100 = 0
    
    
    user = request.user
    district = District.objects.get(user = user)
    district_id = district.id
    sectors = Sector.objects.filter(district = district_id)
    
    for sector in sectors:
        schools = School.objects.filter(sector=sector.id)
        for school in schools:
            classes = Classe.objects.filter(school=school.id)
            for classe in classes:
                students = Student.objects.filter(classe=classe.id, year_reg=year)
                for student in students:
                    n_students = n_students +1
                    for math_quater1_year1 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                        total_math_quater1_year1 = math_quater1_year1.mid_marks + math_quater1_year1.final_marks
                    for est_quater1_year1 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                        total_est_quater1_year1 = est_quater1_year1.mid_marks + est_quater1_year1.final_marks
                    for social_quater1_year1 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                        total_social_quater1_year1 = social_quater1_year1.mid_marks + social_quater1_year1.final_marks
                    for kiny_quater1_year1 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                        total_kiny_quater1_year1 = kiny_quater1_year1.mid_marks + kiny_quater1_year1.final_marks
                    for engl_quater1_year1 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                        total_engl_quater1_year1 = engl_quater1_year1.mid_marks + engl_quater1_year1.final_marks
                        
                    for math_quater2_year1 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                        total_math_quater2_year1 = math_quater2_year1.mid_marks + math_quater2_year1.final_marks
                    for est_quater2_year1 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                        total_est_quater2_year1 = est_quater2_year1.mid_marks + est_quater2_year1.final_marks
                    for social_quater2_year1 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                        total_social_quater2_year1 = social_quater2_year1.mid_marks + social_quater2_year1.final_marks
                    for kiny_quater2_year1 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                        total_kiny_quater2_year1 = kiny_quater2_year1.mid_marks + kiny_quater2_year1.final_marks
                    for engl_quater2_year1 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                        total_engl_quater2_year1 = engl_quater2_year1.mid_marks + engl_quater2_year1.final_marks
                    
                    for math_quater3_year1 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                        total_math_quater3_year1 = math_quater3_year1.mid_marks + math_quater3_year1.final_marks
                    for est_quater3_year1 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                        total_est_quater3_year1 = est_quater3_year1.mid_marks + est_quater3_year1.final_marks
                    for social_quater3_year1 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                        total_social_quater3_year1 = social_quater3_year1.mid_marks + social_quater3_year1.final_marks
                    for kiny_quater3_year1 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                        total_kiny_quater3_year1 = kiny_quater3_year1.mid_marks + kiny_quater3_year1.final_marks
                    for engl_quater3_year1 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                        total_engl_quater3_year1 = engl_quater3_year1.mid_marks + engl_quater3_year1.final_marks
                        
                        total_math_year1 = total_math_quater1_year1 +total_math_quater2_year1 + total_math_quater3_year1
                        total_est_year1 = total_est_quater1_year1 + total_est_quater2_year1 + total_est_quater3_year1
                        total_social_year1 = total_social_quater1_year1 + total_social_quater2_year1 + total_social_quater3_year1
                        total_kiny_year1 = total_kiny_quater1_year1 + total_kiny_quater2_year1 + total_kiny_quater3_year1
                        total_engl_year1 = total_engl_quater1_year1 + total_engl_quater2_year1 + total_engl_quater3_year1
                        
                        total_math_year1_percent = (total_math_year1 * 100)/600
                        total_est_year1_percent = (total_est_year1 * 100)/600
                        total_social_year1_percent = (total_social_year1 * 100)/600
                        total_kiny_year1_percent = (total_kiny_year1 * 100)/600
                        total_engl_year1_percent = (total_engl_year1 * 100)/600
                        
                        if total_math_year1_percent >= 0 and total_math_year1_percent <= 100:
                            total_math_student = total_math_student + 1 
                            if total_math_year1_percent<=25:
                                count_math_25 = count_math_25 + 1
                            if total_math_year1_percent<=50 and total_math_year1_percent>=26:
                                count_math_50 = count_math_50 + 1
                            if total_math_year1_percent<=75 and total_math_year1_percent>=51:
                                count_math_75 = count_math_75 + 1
                            if total_math_year1_percent<=100 and total_math_year1_percent>=76:
                                count_math_100 = count_math_100 + 1 
                                
                        if total_est_year1_percent >= 0 and total_est_year1_percent <= 100:
                            total_est_student = total_est_student + 1    
                            if total_est_year1_percent<=25:
                                count_est_25 = count_est_25 + 1
                            if total_est_year1_percent<=50 and total_est_year1_percent>=26:
                                count_est_50 = count_est_50 + 1
                            if total_est_year1_percent<=75 and total_est_year1_percent>=51:
                                count_est_75 = count_est_75 + 1
                            if total_est_year1_percent<=100 and total_est_year1_percent>=76:
                                count_est_100 = count_est_100 + 1 
                        
                        if total_social_year1_percent >= 0 and total_social_year1_percent <= 100:
                            total_social_student = total_social_student + 1    
                            if total_social_year1_percent<=25:
                                count_social_25 = count_social_25 + 1
                            if total_social_year1_percent<=50 and total_social_year1_percent>=26:
                                count_social_50 = count_social_50 + 1
                            if total_social_year1_percent<=75 and total_social_year1_percent>=51:
                                count_social_75 = count_social_75 + 1
                            if total_social_year1_percent<=100 and total_social_year1_percent>=76:
                                count_social_100 = count_social_100 + 1
                         
                        if total_kiny_year1_percent >= 0 and total_kiny_year1_percent <= 100:
                            total_kiny_student = total_kiny_student + 1    
                            if total_kiny_year1_percent<=25:
                                count_kiny_25 = count_kiny_25 + 1
                            if total_kiny_year1_percent<=50 and total_kiny_year1_percent>=26:
                                count_kiny_50 = count_kiny_50 + 1
                            if total_kiny_year1_percent<=75 and total_kiny_year1_percent>=51:
                                count_kiny_75 = count_kiny_75 + 1
                            if total_kiny_year1_percent<=100 and total_kiny_year1_percent>=76:
                                count_kiny_100 = count_kiny_100 + 1 
                        
                        if total_engl_year1_percent >= 0 and total_engl_year1_percent <= 100:
                            total_engl_student = total_engl_student + 1     
                            if total_engl_year1_percent<=25:
                                count_engl_25 = count_engl_25 + 1
                            if total_engl_year1_percent<=50 and total_engl_year1_percent>=26:
                                count_engl_50 = count_engl_50 + 1
                            if total_engl_year1_percent<=75 and total_engl_year1_percent>=51:
                                count_engl_75 = count_engl_75 + 1
                            if total_engl_year1_percent<=100 and total_engl_year1_percent>=76:
                                count_engl_100 = count_engl_100 + 1

    
    context = {'total_engl_student':total_engl_student,'total_math_student':total_math_student,'total_social_student':total_social_student,'total_est_student':total_est_student,'total_kiny_student':total_kiny_student,
        'user':user,'district':district,'sectors':sectors,'n_students':n_students,
               'count_math_25':count_math_25,'count_math_50':count_math_50,'count_math_75':count_math_75,'count_math_100':count_math_100,
               'count_est_25':count_est_25,'count_est_50':count_est_50,'count_est_75':count_est_75,'count_est_100':count_est_100,
               'count_social_25':count_social_25,'count_social_50':count_social_50,'count_social_75':count_social_75,'count_social_100':count_social_100,
               'count_kiny_25':count_kiny_25,'count_kiny_50':count_kiny_50,'count_kiny_75':count_kiny_75,'count_kiny_100':count_kiny_100,
               'count_engl_25':count_engl_25,'count_engl_50':count_engl_50,'count_engl_75':count_engl_75,'count_engl_100':count_engl_100}
    
    return render(request, 'districtPages/home_district.html',context)
@login_required(login_url='/login')
@user_passes_test(lambda u: u.is_superuser)
def rebPage(request):
    
    now = datetime.datetime.now()
    year = now.year
    
    n_allstudents = 0
    
    total_engl_student = 0
    total_math_student = 0
    total_social_student = 0
    total_est_student = 0
    total_kiny_student = 0
    
    count_math_25 = 0
    count_math_50 = 0
    count_math_75 = 0
    count_math_100 = 0
    
    count_est_25 = 0
    count_est_50 = 0
    count_est_75 = 0
    count_est_100 = 0
    
    count_engl_25 = 0
    count_engl_50 = 0
    count_engl_75 = 0
    count_engl_100 = 0
    
    count_social_25 = 0
    count_social_50 = 0
    count_social_75 = 0
    count_social_100 = 0
    
    count_kiny_25 = 0
    count_kiny_50 = 0
    count_kiny_75 = 0
    count_kiny_100 = 0
    
    districts = District.objects.all()
    for district in districts:
        sectors = Sector.objects.filter(district=district.id)
        for sector in sectors:
            schools = School.objects.filter(sector=sector.id)
            for school in schools:
                classes = Classe.objects.filter(school=school.id)
                for classe in classes:
                    students = Student.objects.filter(classe=classe.id, year_reg=year)
                    for student in students:
                        n_allstudents =n_allstudents + 1
                        for math_quater1_year1 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                            total_math_quater1_year1 = math_quater1_year1.mid_marks + math_quater1_year1.final_marks
                        for est_quater1_year1 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                            total_est_quater1_year1 = est_quater1_year1.mid_marks + est_quater1_year1.final_marks
                        for social_quater1_year1 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                            total_social_quater1_year1 = social_quater1_year1.mid_marks + social_quater1_year1.final_marks
                        for kiny_quater1_year1 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                            total_kiny_quater1_year1 = kiny_quater1_year1.mid_marks + kiny_quater1_year1.final_marks
                        for engl_quater1_year1 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                            total_engl_quater1_year1 = engl_quater1_year1.mid_marks + engl_quater1_year1.final_marks
                    
                        for math_quater2_year1 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                            total_math_quater2_year1 = math_quater2_year1.mid_marks + math_quater2_year1.final_marks
                        for est_quater2_year1 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                            total_est_quater2_year1 = est_quater2_year1.mid_marks + est_quater2_year1.final_marks
                        for social_quater2_year1 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                            total_social_quater2_year1 = social_quater2_year1.mid_marks + social_quater2_year1.final_marks
                        for kiny_quater2_year1 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                            total_kiny_quater2_year1 = kiny_quater2_year1.mid_marks + kiny_quater2_year1.final_marks
                        for engl_quater2_year1 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                            total_engl_quater2_year1 = engl_quater2_year1.mid_marks + engl_quater2_year1.final_marks
                
                        for math_quater3_year1 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                            total_math_quater3_year1 = math_quater3_year1.mid_marks + math_quater3_year1.final_marks
                        for est_quater3_year1 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                            total_est_quater3_year1 = est_quater3_year1.mid_marks + est_quater3_year1.final_marks
                        for social_quater3_year1 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                            total_social_quater3_year1 = social_quater3_year1.mid_marks + social_quater3_year1.final_marks
                        for kiny_quater3_year1 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                            total_kiny_quater3_year1 = kiny_quater3_year1.mid_marks + kiny_quater3_year1.final_marks
                        for engl_quater3_year1 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                            total_engl_quater3_year1 = engl_quater3_year1.mid_marks + engl_quater3_year1.final_marks
                    
                            total_math_year1 = total_math_quater1_year1 +total_math_quater2_year1 + total_math_quater3_year1
                            total_est_year1 = total_est_quater1_year1 + total_est_quater2_year1 + total_est_quater3_year1
                            total_social_year1 = total_social_quater1_year1 + total_social_quater2_year1 + total_social_quater3_year1
                            total_kiny_year1 = total_kiny_quater1_year1 + total_kiny_quater2_year1 + total_kiny_quater3_year1
                            total_engl_year1 = total_engl_quater1_year1 + total_engl_quater2_year1 + total_engl_quater3_year1
                    
                            total_math_year1_percent = (total_math_year1 * 100)/600
                            total_est_year1_percent = (total_est_year1 * 100)/600
                            total_social_year1_percent = (total_social_year1 * 100)/600
                            total_kiny_year1_percent = (total_kiny_year1 * 100)/600
                            total_engl_year1_percent = (total_engl_year1 * 100)/600

                            if total_math_year1_percent >= 0 and total_math_year1_percent <= 100:
                                total_math_student = total_math_student + 1 
                                if total_math_year1_percent<=25:
                                    count_math_25 = count_math_25 + 1
                                if total_math_year1_percent<=50 and total_math_year1_percent>=26:
                                    count_math_50 = count_math_50 + 1
                                if total_math_year1_percent<=75 and total_math_year1_percent>=51:
                                    count_math_75 = count_math_75 + 1
                                if total_math_year1_percent<=100 and total_math_year1_percent>=76:
                                    count_math_100 = count_math_100 + 1 

                            if total_est_year1_percent >= 0 and total_est_year1_percent <= 100:
                                total_est_student = total_est_student + 1 
                                if total_est_year1_percent<=25:
                                    count_est_25 = count_est_25 + 1
                                if total_est_year1_percent<=50 and total_est_year1_percent>=26:
                                    count_est_50 = count_est_50 + 1
                                if total_est_year1_percent<=75 and total_est_year1_percent>=51:
                                    count_est_75 = count_est_75 + 1
                                if total_est_year1_percent<=100 and total_est_year1_percent>=76:
                                    count_est_100 = count_est_100 + 1 

                            if total_social_year1_percent >= 0 and total_social_year1_percent <= 100:
                                total_social_student = total_social_student + 1 
                                if total_social_year1_percent<=25:
                                    count_social_25 = count_social_25 + 1
                                if total_social_year1_percent<=50 and total_social_year1_percent>=26:
                                    count_social_50 = count_social_50 + 1
                                if total_social_year1_percent<=75 and total_social_year1_percent>=51:
                                    count_social_75 = count_social_75 + 1
                                if total_social_year1_percent<=100 and total_social_year1_percent>=76:
                                    count_social_100 = count_social_100 + 1

                            if total_kiny_year1_percent >= 0 and total_kiny_year1_percent <= 100:
                                total_kiny_student = total_kiny_student + 1 
                                if total_kiny_year1_percent<=25:
                                    count_kiny_25 = count_kiny_25 + 1
                                if total_kiny_year1_percent<=50 and total_kiny_year1_percent>=26:
                                    count_kiny_50 = count_kiny_50 + 1
                                if total_kiny_year1_percent<=75 and total_kiny_year1_percent>=51:
                                    count_kiny_75 = count_kiny_75 + 1
                                if total_kiny_year1_percent<=100 and total_kiny_year1_percent>=76:
                                    count_kiny_100 = count_kiny_100 + 1 

                            if total_engl_year1_percent >= 0 and total_engl_year1_percent <= 100:
                                total_engl_student = total_engl_student + 1 
                                if total_engl_year1_percent<=25:
                                    count_engl_25 = count_engl_25 + 1
                                if total_engl_year1_percent<=50 and total_engl_year1_percent>=26:
                                    count_engl_50 = count_engl_50 + 1
                                if total_engl_year1_percent<=75 and total_engl_year1_percent>=51:
                                    count_engl_75 = count_engl_75 + 1
                                if total_engl_year1_percent<=100 and total_engl_year1_percent>=76:
                                    count_engl_100 = count_engl_100 + 1
    
    context = {'total_engl_student':total_engl_student,'total_math_student':total_math_student,'total_social_student':total_social_student,'total_est_student':total_est_student,'total_kiny_student':total_kiny_student,
        'n_allstudents':n_allstudents,'schools':schools,'districts':districts,
               'count_math_25':count_math_25,'count_math_50':count_math_50,'count_math_75':count_math_75,'count_math_100':count_math_100,
               'count_est_25':count_est_25,'count_est_50':count_est_50,'count_est_75':count_est_75,'count_est_100':count_est_100,
               'count_social_25':count_social_25,'count_social_50':count_social_50,'count_social_75':count_social_75,'count_social_100':count_social_100,
               'count_kiny_25':count_kiny_25,'count_kiny_50':count_kiny_50,'count_kiny_75':count_kiny_75,'count_kiny_100':count_kiny_100,
               'count_engl_25':count_engl_25,'count_engl_50':count_engl_50,'count_engl_75':count_engl_75,'count_engl_100':count_engl_100}         
    
    return render(request, 'rebPages/home.html',context)

@login_required(login_url='/login')
@user_passes_test(lambda u: u.is_superuser)
def rebStatisticalReport(request):
    no_students = 0
    now = datetime.datetime.now()
    year = now.year
    

    
    districts = District.objects.all()
    for district in districts:
        sectors = Sector.objects.filter(district=district.id)
        for sector in sectors:
            schools = School.objects.filter(sector=sector)
            for school in schools:
                classes = Classe.objects.filter(school=school.id)
                for classe in classes:
                    students = Student.objects.filter(classe=classe.id)
                    for student in students:
                        no_students = no_students + 1
    
    courses = Course.objects.all()
    
    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count, count(*) from student_student where student_student.year_reg=%s" %year
    cursor.execute(male_female)
    answers = cursor.fetchall()
    
    context = {'answers':answers,'districts':districts,'courses':courses,'no_students':no_students}
    
    return render(request, 'rebPages/rebStatisticalReports.html',context)

@login_required(login_url='/login')
@user_passes_test(lambda u: u.is_superuser)
def districtList(request):
    district_list = District.objects.all()
    paginator = Paginator(district_list, 5) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj':page_obj}
    return render(request, 'rebPages/districtList.html',context)

@login_required(login_url='/login')
@user_passes_test(lambda u: u.is_superuser)
def district_create(request):

    form = DistrictForm()
    
    if(request.method == "POST"):
        form = DistrictForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'District has been Created Successfully')
            return redirect('rebPage')
    context = {'form':form}
    return render(request,'rebPages/rebDistrictForm.html',context)

@login_required(login_url='/login')
@user_passes_test(lambda u: u.is_superuser)
def district_update(request, pk_district):

    district = District.objects.get(id=pk_district)
    form = DistrictForm(instance=district)
    if request.method == 'POST':
        form = DistrictForm(request.POST, instance=district)
        if form.is_valid:
            form.save()
            messages.success(request, 'District has been Updated Successfully')
            return redirect('rebPage')
    context = {'form':form}
    return render(request, 'rebPages/rebDistrictForm.html',context)

@login_required(login_url='/login')
@user_passes_test(lambda u: u.is_superuser)
def district_delete(request, id):
    district = District.objects.get(pk=id)
    district.delete()
    messages.success(request, 'District has been deleted Successfully')
    return redirect('rebPage')

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary']) 
def schoolPage(request):
    user = request.user
    school = School.objects.get(user=user)
    school_id = school.id
    classes = Classe.objects.filter(school=school_id)
    
    now = datetime.datetime.now()
    year = now.year

    total_kiny_student = 0
    total_engl_student = 0
    total_math_student = 0
    total_est_student = 0
    total_social_student = 0
    count_math_100_percent = 0
    
    count_math_25 = 0
    count_math_50 = 0
    count_math_75 = 0
    count_math_100 = 0
    
    count_est_25 = 0
    count_est_50 = 0
    count_est_75 = 0
    count_est_100 = 0
    
    count_engl_25 = 0
    count_engl_50 = 0
    count_engl_75 = 0
    count_engl_100 = 0
    
    count_social_25 = 0
    count_social_50 = 0
    count_social_75 = 0
    count_social_100 = 0
    
    count_kiny_25 = 0
    count_kiny_50 = 0
    count_kiny_75 = 0
    count_kiny_100 = 0
    
    for classe in classes:
        students_year1 = Student.objects.filter(classe=classe.id,year_reg=year)
        for student in students_year1:
            for math_quater1_year1 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                total_math_quater1_year1 = math_quater1_year1.mid_marks + math_quater1_year1.final_marks
            for est_quater1_year1 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                total_est_quater1_year1 = est_quater1_year1.mid_marks + est_quater1_year1.final_marks
            for social_quater1_year1 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                total_social_quater1_year1 = social_quater1_year1.mid_marks + social_quater1_year1.final_marks
            for kiny_quater1_year1 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                total_kiny_quater1_year1 = kiny_quater1_year1.mid_marks + kiny_quater1_year1.final_marks
            for engl_quater1_year1 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                total_engl_quater1_year1 = engl_quater1_year1.mid_marks + engl_quater1_year1.final_marks
                
            for math_quater2_year1 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                total_math_quater2_year1 = math_quater2_year1.mid_marks + math_quater2_year1.final_marks
            for est_quater2_year1 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                total_est_quater2_year1 = est_quater2_year1.mid_marks + est_quater2_year1.final_marks
            for social_quater2_year1 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                total_social_quater2_year1 = social_quater2_year1.mid_marks + social_quater2_year1.final_marks
            for kiny_quater2_year1 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                total_kiny_quater2_year1 = kiny_quater2_year1.mid_marks + kiny_quater2_year1.final_marks
            for engl_quater2_year1 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                total_engl_quater2_year1 = engl_quater2_year1.mid_marks + engl_quater2_year1.final_marks
            
            for math_quater3_year1 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                total_math_quater3_year1 = math_quater3_year1.mid_marks + math_quater3_year1.final_marks
            for est_quater3_year1 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                total_est_quater3_year1 = est_quater3_year1.mid_marks + est_quater3_year1.final_marks
            for social_quater3_year1 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                total_social_quater3_year1 = social_quater3_year1.mid_marks + social_quater3_year1.final_marks
            for kiny_quater3_year1 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                total_kiny_quater3_year1 = kiny_quater3_year1.mid_marks + kiny_quater3_year1.final_marks
            for engl_quater3_year1 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                total_engl_quater3_year1 = engl_quater3_year1.mid_marks + engl_quater3_year1.final_marks
                
                total_math_year1 = total_math_quater1_year1 +total_math_quater2_year1 + total_math_quater3_year1
                total_est_year1 = total_est_quater1_year1 + total_est_quater2_year1 + total_est_quater3_year1
                total_social_year1 = total_social_quater1_year1 + total_social_quater2_year1 + total_social_quater3_year1
                total_kiny_year1 = total_kiny_quater1_year1 + total_kiny_quater2_year1 + total_kiny_quater3_year1
                total_engl_year1 = total_engl_quater1_year1 + total_engl_quater2_year1 + total_engl_quater3_year1
                
                total_math_year1_percent = (total_math_year1 * 100)/600
                total_est_year1_percent = (total_est_year1 * 100)/600
                total_social_year1_percent = (total_social_year1 * 100)/600
                total_kiny_year1_percent = (total_kiny_year1 * 100)/600
                total_engl_year1_percent = (total_engl_year1 * 100)/600
   
                if total_math_year1_percent >= 0 and total_math_year1_percent <= 100:
                    total_math_student = total_math_student + 1
                    if total_math_year1_percent<=25:
                        count_math_25 = count_math_25 + 1
                    if total_math_year1_percent<=50 and total_math_year1_percent>=26:
                        count_math_50 = count_math_50 + 1
                    if total_math_year1_percent<=75 and total_math_year1_percent>=51:
                        count_math_75 = count_math_75 + 1
                    if total_math_year1_percent<=100 and total_math_year1_percent>=76:
                        count_math_100 = count_math_100 + 1
                                                
                if total_est_year1_percent >= 0 and total_est_year1_percent <= 100:
                    total_est_student = total_est_student + 1     
                    if total_est_year1_percent<=25:
                        count_est_25 = count_est_25 + 1
                    if total_est_year1_percent<=50 and total_est_year1_percent>=26:
                        count_est_50 = count_est_50 + 1
                    if total_est_year1_percent<=75 and total_est_year1_percent>=51:
                        count_est_75 = count_est_75 + 1
                    if total_est_year1_percent<=100 and total_est_year1_percent>=76:
                        count_est_100 = count_est_100 + 1 
                
                if total_social_year1_percent >= 0 and total_social_year1_percent <= 100:
                    total_social_student = total_social_student + 1     
                    if total_social_year1_percent<=25:
                        count_social_25 = count_social_25 + 1
                    if total_social_year1_percent<=50 and total_social_year1_percent>=26:
                        count_social_50 = count_social_50 + 1
                    if total_social_year1_percent<=75 and total_social_year1_percent>=51:
                        count_social_75 = count_social_75 + 1
                    if total_social_year1_percent<=100 and total_social_year1_percent>=76:
                        count_social_100 = count_social_100 + 1
                        
                if total_kiny_year1_percent >= 0 and total_kiny_year1_percent <= 100:
                    total_kiny_student = total_kiny_student + 1      
                    if total_kiny_year1_percent<=25:
                        count_kiny_25 = count_kiny_25 + 1
                    if total_kiny_year1_percent<=50 and total_kiny_year1_percent>=26:
                        count_kiny_50 = count_kiny_50 + 1
                    if total_kiny_year1_percent<=75 and total_kiny_year1_percent>=51:
                        count_kiny_75 = count_kiny_75 + 1
                    if total_kiny_year1_percent<=100 and total_kiny_year1_percent>=76:
                        count_kiny_100 = count_kiny_100 + 1 
                
                if total_engl_year1_percent >= 0 and total_engl_year1_percent <= 100:
                    total_engl_student = total_engl_student + 1     
                    if total_engl_year1_percent<=25:
                        count_engl_25 = count_engl_25 + 1
                    if total_engl_year1_percent<=50 and total_engl_year1_percent>=26:
                        count_engl_50 = count_engl_50 + 1
                    if total_engl_year1_percent<=75 and total_engl_year1_percent>=51:
                        count_engl_75 = count_engl_75 + 1
                    if total_engl_year1_percent<=100 and total_engl_year1_percent>=76:
                        count_engl_100 = count_engl_100 + 1
                    
                    
    context = {'count_engl_25':count_engl_25,'count_engl_50':count_engl_50,'count_engl_75':count_engl_75,'count_engl_100':count_engl_100,'total_engl_student':total_engl_student,'school_id':school_id,
        'total_social_student':total_social_student,'total_est_student':total_est_student,'total_engl_student':total_engl_student,'total_kiny_student':total_kiny_student,
        'total_math_student':total_math_student,'school':school,'count_math_25':count_math_25,'count_math_50':count_math_50,'count_math_75':count_math_75,'count_math_100':count_math_100,
               'count_est_25':count_est_25,'count_est_50':count_est_50,'count_est_75':count_est_75,'count_est_100':count_est_100,
               'count_social_25':count_social_25,'count_social_50':count_social_50,'count_social_75':count_social_75,'count_social_100':count_social_100,
               'count_kiny_25':count_kiny_25,'count_kiny_50':count_kiny_50,'count_kiny_75':count_kiny_75,'count_kiny_100':count_kiny_100,
               'count_engl_25':count_engl_25,'count_engl_50':count_engl_50,'count_engl_75':count_engl_75,'count_engl_100':count_engl_100}
    return render(request,'schoolPages/home_school.html', context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary']) 
def schoolStatisticalReport(request):
    n_students = 0
    user = request.user
    school = School.objects.get(user = user)
    school_id = school.id
    classes = Classe.objects.filter(school=school_id)
    
    for classe in classes:
        students = Student.objects.filter(classe=classe.id)
        for student in students:
            n_students = n_students + 1
    
    now = datetime.datetime.now()
    year = now.year
    
    courses = Course.objects.all()

    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count, count(*) as n_students from student_student inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id where student_student.year_reg=%s and student_school.id=%s" %(year, school_id)
    cursor.execute(male_female)
    answers2 = cursor.fetchall()
    
    context = {'school':school,'school_id':school_id,'classes':classes,'answers2':answers2,'courses':courses,'n_students':n_students}
    return render(request, 'schoolPages/schoolStatisticalReport.html', context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary']) 
def classWithQuaterMarks(request):
    template = get_template('schoolPages/classWithQuaterMarks.html')
    user = request.user
    school = School.objects.get(user=user)
    schoolId = school.id
    
    try:
        classe = request.GET.get('classe')
        course = request.GET.get('course')
        year = request.GET.get('year')
        quater = request.GET.get('quater')
    except:
        classe = None
        course = None
        year = None
        quater = None
        
    if classe:
        classeSearched = classe
        classee = Classe.objects.get(id=4)
        if course:
            courseSearched = course
            if year:
                yearSearched = year
                if quater:
                    quaterSearched = quater
                    cursor = connection.cursor()
                    students_marks = "select f_name,l_name, mid_marks, final_marks from student_student inner join student_student_course on student_student.id=student_student_course.student_id inner join student_course on student_course.id=student_student_course.course_id inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id where student_course.id=%s and student_student_course.quater='%s' and student_classe.id=%s and student_school.id=%s and student_student.year_reg=%s" %(courseSearched, quaterSearched, classeSearched, schoolId, yearSearched)
                    cursor.execute(students_marks)
                    answers = cursor.fetchall()  
    
    context = {'answers':answers,'classee':classee,'courseSearched':courseSearched,'yearSearched':yearSearched,'quaterSearched':quaterSearched,'school':school}
    html = template.render(context)
    pdf= render_to_pdf('schoolPages/classWithQuaterMarks.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "Classes_List of marks in %s year %s at %s" %(classee, yearSearched, school)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"
    
@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary']) 
def schoolAvgFromSchool(request):
    template = get_template('schoolPages/schoolAvgFromSchool.html')
    user = request.user
    school =  School.objects.get(user=user)
    school_id = school.id
    try:
        year = request.GET.get("year")
    except:
        year = None
        
    if year:
        yearSearched = year
        cursor = connection.cursor()
        course_marks = "select student_classe.class_name, avg(student_student_course.final_marks), sum(student_student_course.final_marks) as final_exam, sum(student_student_course.mid_marks) as mid_exam from student_student_course inner join student_student on student_student.id=student_student_course.student_id inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id where student_student.year_reg=%s and student_school.id=%s group by student_classe.class_name order by avg(student_student_course.final_marks) desc" %(yearSearched, school_id)
        cursor.execute(course_marks)
        answers = cursor.fetchall()
        
    context = {'answers':answers,'school':school,'yearSearched':yearSearched}
    html = template.render(context)
    pdf= render_to_pdf('schoolPages/schoolAvgFromSchool.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "Classes_List Bases on Performance in %s year %s" %(school, yearSearched)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

def schoolStatisticalReportYear(request):
    user = request.user
    school = School.objects.get(user=user)
    school_id = school.id
    
    try:
        classe = request.GET.get('classe')
        year = request.GET.get('year')
    except:
        classe = None
        year = None
        
    if year:
        yearSearched = year
        if classe:
            classeSearched = classe
            classee = Classe.objects.get(school=school_id, id=classe)
            students = Student.objects.filter(classe=classee,year_reg=year)
            
            for student in students:
                studentss = Student_Course.objects.filter(student = student)
            
            
                
            
                    
            
    context = {'classee':classee,'students':students,'yearSearched':yearSearched,'studentss':studentss}
    return render(request, 'schoolPages/schoolStatisticalReportYear.html', context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary']) 
def schoolTwoYearReport(request):
    
    template = get_template('schoolPages/schoolTwoYearReport.html')
    count_math_25 = 0
    count_math_50 = 0
    count_math_75 = 0
    count_math_100 = 0
    
    count_est_25 = 0
    count_est_50 = 0
    count_est_75 = 0
    count_est_100 = 0
    
    count_engl_25 = 0
    count_engl_50 = 0
    count_engl_75 = 0
    count_engl_100 = 0
    
    count_social_25 = 0
    count_social_50 = 0
    count_social_75 = 0
    count_social_100 = 0
    
    count_kiny_25 = 0
    count_kiny_50 = 0
    count_kiny_75 = 0
    count_kiny_100 = 0
    
    
    
    count_math_year1_25 = 0
    count_math_year1_50 = 0
    count_math_year1_75 = 0
    count_math_year1_100 = 0
    
    count_est_year1_25 = 0
    count_est_year1_50 = 0
    count_est_year1_75 = 0
    count_est_year1_100 = 0
    
    count_engl_year1_25 = 0
    count_engl_year1_50 = 0
    count_engl_year1_75 = 0
    count_engl_year1_100 = 0
    
    count_social_year1_25 = 0
    count_social_year1_50 = 0
    count_social_year1_75 = 0
    count_social_year1_100 = 0
    
    count_kiny_year1_25 = 0
    count_kiny_year1_50 = 0
    count_kiny_year1_75 = 0
    count_kiny_year1_100 = 0
  

    count_student_year1 = 0
    count_student_year2 = 0
    
    
    
   
    
    try:
        year1 = request.GET.get('year1')
        year2 = request.GET.get('year2')
    except:
        year1 = None
        year2 = None
        
    if year1:
        year1Searched = year1
        if year2:
            year2Searched = year2
            user = request.user
            school = School.objects.get(user=user)
            sector = school.sector
            district = sector.district
            school_id = school.id
            classes = Classe.objects.filter(school=school_id)
            number_of_classes = classes.count()
            for classe in classes:
                students_year1 = Student.objects.filter(classe=classe.id,year_reg=year1Searched)
                for student in students_year1:
                    count_student_year1 = count_student_year1+1
                    for math_quater1_year1 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                        total_math_quater1_year1 = math_quater1_year1.mid_marks + math_quater1_year1.final_marks
                    for est_quater1_year1 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                        total_est_quater1_year1 = est_quater1_year1.mid_marks + est_quater1_year1.final_marks
                    for social_quater1_year1 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                        total_social_quater1_year1 = social_quater1_year1.mid_marks + social_quater1_year1.final_marks
                    for kiny_quater1_year1 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                        total_kiny_quater1_year1 = kiny_quater1_year1.mid_marks + kiny_quater1_year1.final_marks
                    for engl_quater1_year1 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                        total_engl_quater1_year1 = engl_quater1_year1.mid_marks + engl_quater1_year1.final_marks
                        
                    for math_quater2_year1 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                        total_math_quater2_year1 = math_quater2_year1.mid_marks + math_quater2_year1.final_marks
                    for est_quater2_year1 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                        total_est_quater2_year1 = est_quater2_year1.mid_marks + est_quater2_year1.final_marks
                    for social_quater2_year1 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                        total_social_quater2_year1 = social_quater2_year1.mid_marks + social_quater2_year1.final_marks
                    for kiny_quater2_year1 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                        total_kiny_quater2_year1 = kiny_quater2_year1.mid_marks + kiny_quater2_year1.final_marks
                    for engl_quater2_year1 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                        total_engl_quater2_year1 = engl_quater2_year1.mid_marks + engl_quater2_year1.final_marks
                    
                    for math_quater3_year1 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                        total_math_quater3_year1 = math_quater3_year1.mid_marks + math_quater3_year1.final_marks
                    for est_quater3_year1 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                        total_est_quater3_year1 = est_quater3_year1.mid_marks + est_quater3_year1.final_marks
                    for social_quater3_year1 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                        total_social_quater3_year1 = social_quater3_year1.mid_marks + social_quater3_year1.final_marks
                    for kiny_quater3_year1 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                        total_kiny_quater3_year1 = kiny_quater3_year1.mid_marks + kiny_quater3_year1.final_marks
                    for engl_quater3_year1 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                        total_engl_quater3_year1 = engl_quater3_year1.mid_marks + engl_quater3_year1.final_marks
                        
                        total_math_year1 = total_math_quater1_year1 +total_math_quater2_year1 + total_math_quater3_year1
                        total_est_year1 = total_est_quater1_year1 + total_est_quater2_year1 + total_est_quater3_year1
                        total_social_year1 = total_social_quater1_year1 + total_social_quater2_year1 + total_social_quater3_year1
                        total_kiny_year1 = total_kiny_quater1_year1 + total_kiny_quater2_year1 + total_kiny_quater3_year1
                        total_engl_year1 = total_engl_quater1_year1 + total_engl_quater2_year1 + total_engl_quater3_year1
                        
                        total_math_year1_percent = (total_math_year1 * 100)/600
                        total_est_year1_percent = (total_est_year1 * 100)/600
                        total_social_year1_percent = (total_social_year1 * 100)/600
                        total_kiny_year1_percent = (total_kiny_year1 * 100)/600
                        total_engl_year1_percent = (total_engl_year1 * 100)/600
                        
                        if total_math_year1_percent<=25:
                            count_math_year1_25 = count_math_year1_25 + 1
                        if total_math_year1_percent<=50 and total_math_year1_percent>=26:
                            count_math_year1_50 = count_math_year1_50 + 1
                        if total_math_year1_percent<=75 and total_math_year1_percent>=51:
                            count_math_year1_75 = count_math_year1_75 + 1
                        if total_math_year1_percent<=100 and total_math_year1_percent>=76:
                            count_math_year1_100 = count_math_year1_100 + 1 
                            
                        if total_est_year1_percent<=25:
                            count_est_year1_25 = count_est_year1_25 + 1
                        if total_est_year1_percent<=50 and total_est_year1_percent>=26:
                            count_est_year1_50 = count_est_year1_50 + 1
                        if total_est_year1_percent<=75 and total_est_year1_percent>=51:
                            count_est_year1_75 = count_est_year1_75 + 1
                        if total_est_year1_percent<=100 and total_est_year1_percent>=76:
                            count_est_year1_100 = count_est_year1_100 + 1 
                            
                        if total_social_year1_percent<=25:
                            count_social_year1_25 = count_social_year1_25 + 1
                        if total_social_year1_percent<=50 and total_social_year1_percent>=26:
                            count_social_year1_50 = count_social_year1_50 + 1
                        if total_social_year1_percent<=75 and total_social_year1_percent>=51:
                            count_social_year1_75 = count_social_year1_75 + 1
                        if total_social_year1_percent<=100 and total_social_year1_percent>=76:
                            count_social_year1_100 = count_social_year1_100 + 1
                            
                        if total_kiny_year1_percent<=25:
                            count_kiny_year1_25 = count_kiny_year1_25 + 1
                        if total_kiny_year1_percent<=50 and total_kiny_year1_percent>=26:
                            count_kiny_year1_50 = count_kiny_year1_50 + 1
                        if total_kiny_year1_percent<=75 and total_kiny_year1_percent>=51:
                            count_kiny_year1_75 = count_kiny_year1_75 + 1
                        if total_kiny_year1_percent<=100 and total_kiny_year1_percent>=76:
                            count_kiny_year1_100 = count_kiny_year1_100 + 1 
                            
                        if total_engl_year1_percent<=25:
                            count_engl_year1_25 = count_engl_year1_25 + 1
                        if total_engl_year1_percent<=50 and total_engl_year1_percent>=26:
                            count_engl_year1_50 = count_engl_year1_50 + 1
                        if total_engl_year1_percent<=75 and total_engl_year1_percent>=51:
                            count_engl_year1_75 = count_engl_year1_75 + 1
                        if total_engl_year1_percent<=100 and total_engl_year1_percent>=76:
                            count_engl_year1_100 = count_engl_year1_100 + 1
                        
                        
                students_year2 = Student.objects.filter(classe=classe.id, year_reg=year2Searched)
                for studentt in students_year2:
                    count_student_year2 = count_student_year2+1
                    for math_quater1 in studentt.student_course_set.filter(course=1, quater = 'QUATER1'):
                        total_math_quater1_year2 = math_quater1.mid_marks + math_quater1.final_marks 
                    for est_quater1 in studentt.student_course_set.filter(course=2, quater = 'QUATER1'):
                        total_est_quater1_year2 = est_quater1.mid_marks + est_quater1.final_marks  
                    for social_quater1 in studentt.student_course_set.filter(course=3, quater = 'QUATER1'):
                        total_social_quater1_year2 = social_quater1.mid_marks + social_quater1.final_marks
                    for kiny_quater1 in studentt.student_course_set.filter(course=4, quater = 'QUATER1'):
                        total_kiny_quater1_year2 = kiny_quater1.mid_marks + kiny_quater1.final_marks 
                    for engl_quater1 in studentt.student_course_set.filter(course=5, quater = 'QUATER1'):
                        total_engl_quater1_year2 = engl_quater1.mid_marks + engl_quater1.final_marks  
                        
                    for math_quater2 in studentt.student_course_set.filter(course=1, quater = 'QUATER2'):
                        total_math_quater2_year2 = math_quater2.mid_marks + math_quater2.final_marks
                    for est_quater2 in studentt.student_course_set.filter(course=2, quater = 'QUATER2'):
                        total_est_quater2_year2 = est_quater2.mid_marks + est_quater2.final_marks
                    for social_quater2 in studentt.student_course_set.filter(course=3, quater = 'QUATER2'):
                        total_social_quater2_year2 = social_quater2.mid_marks + social_quater2.final_marks
                    for kiny_quater2 in studentt.student_course_set.filter(course=4, quater = 'QUATER2'):
                        total_kiny_quater2_year2 = kiny_quater2.mid_marks + kiny_quater2.final_marks
                    for engl_quater2 in studentt.student_course_set.filter(course=5, quater = 'QUATER2'):
                        total_engl_quater2_year2 = engl_quater2.mid_marks + engl_quater2.final_marks     
                    
                    for math_quater3 in studentt.student_course_set.filter(course=1, quater = 'QUATER3'):
                        total_math_quater3_year2 = math_quater3.mid_marks + math_quater3.final_marks
                    for est_quater3 in studentt.student_course_set.filter(course=2, quater = 'QUATER3'):
                        total_est_quater3_year2 = est_quater3.mid_marks + est_quater3.final_marks 
                    for social_quater3 in studentt.student_course_set.filter(course=3, quater = 'QUATER3'):
                        total_social_quater3_year2 = social_quater3.mid_marks + social_quater3.final_marks
                    for kiny_quater3 in studentt.student_course_set.filter(course=4, quater = 'QUATER3'):
                        total_kiny_quater3_year2 = kiny_quater3.mid_marks + kiny_quater3.final_marks 
                    for engl_quater3 in studentt.student_course_set.filter(course=5, quater = 'QUATER3'):
                        total_engl_quater3_year2 = engl_quater3.mid_marks + engl_quater3.final_marks

                            
                        total_math = total_math_quater1_year2 + total_math_quater2_year2 + total_math_quater3_year2
                        total_est = total_est_quater1_year2 + total_est_quater2_year2 + total_est_quater3_year2
                        total_social = total_social_quater1_year2 + total_social_quater2_year2 + total_social_quater3_year2
                        total_kiny = total_kiny_quater1_year2 + total_kiny_quater2_year2 + total_kiny_quater3_year2
                        total_engl = total_engl_quater1_year2 + total_engl_quater2_year2 + total_engl_quater3_year2
                        
                        
                        
                        total_math_percent = (total_math * 100)/600
                        total_est_percent = (total_est * 100)/600
                        total_social_percent = (total_social * 100)/600
                        total_kiny_percent = (total_kiny * 100)/600
                        total_engl_percent = (total_engl * 100)/600
                        
                        
                        if total_math_percent<=25:
                            count_math_25 = count_math_25 + 1
                        if total_math_percent<=50 and total_math_percent>=26:
                            count_math_50 = count_math_50 + 1
                        if total_math_percent<=75 and total_math_percent>=51:
                            count_math_75 = count_math_75 + 1
                        if total_math_percent<=100 and total_math_percent>=76:
                            count_math_100 = count_math_100 + 1   
                            
                        if total_est_percent<=25:
                            count_est_25 = count_est_25 + 1
                        if total_est_percent<=50 and total_est_percent>=26:
                            count_est_50 = count_est_50 + 1
                        if total_est_percent<=75 and total_est_percent>=51:
                            count_est_75 = count_est_75 + 1
                        if total_est_percent<=100 and total_est_percent>=76:
                            count_est_100 = count_est_100 + 1 
                            
                        if total_social_percent<=25:
                            count_social_25 = count_social_25 + 1
                        if total_social_percent<=50 and total_social_percent>=26:
                            count_social_50 = count_social_50 + 1
                        if total_social_percent<=75 and total_social_percent>=51:
                            count_social_75 = count_social_75 + 1
                        if total_social_percent<=100 and total_social_percent>=76:
                            count_social_100 = count_social_100 + 1
                            
                        if total_kiny_percent<=25:
                            count_kiny_25 = count_kiny_25 + 1
                        if total_kiny_percent<=50 and total_kiny_percent>=26:
                            count_kiny_50 = count_kiny_50 + 1
                        if total_kiny_percent<=75 and total_kiny_percent>=51:
                            count_kiny_75 = count_kiny_75 + 1
                        if total_kiny_percent<=100 and total_kiny_percent>=76:
                            count_kiny_100 = count_kiny_100 + 1 
                            
                        if total_engl_percent<=25:
                            count_engl_25 = count_engl_25 + 1
                        if total_engl_percent<=50 and total_engl_percent>=26:
                            count_engl_50 = count_engl_50 + 1
                        if total_engl_percent<=75 and total_engl_percent>=51:
                            count_engl_75 = count_engl_75 + 1
                        if total_engl_percent<=100 and total_engl_percent>=76:
                            count_engl_100 = count_engl_100 + 1 
                            
                        
            

    context = {'count_student_year1':count_student_year1,'count_student_year2':count_student_year2,'year1Searched':year1Searched,'year2Searched':year2Searched,'school':school,'sector':sector,'district':district,
                'count_math_25':count_math_25,'count_math_50':count_math_50,'count_math_75':count_math_75,'count_math_100':count_math_100,
                'count_est_25':count_est_25,'count_est_50':count_est_50,'count_est_75':count_est_75,'count_est_100':count_est_100,
                'count_social_25':count_social_25,'count_social_50':count_social_50,'count_social_75':count_social_75,'count_social_100':count_social_100,
                'count_kiny_25':count_kiny_25,'count_kiny_50':count_kiny_50,'count_kiny_75':count_kiny_75,'count_kiny_100':count_kiny_100,
                'count_engl_25':count_engl_25,'count_engl_50':count_engl_50,'count_engl_75':count_engl_75,'count_engl_100':count_engl_100,
                'count_math_year1_25':count_math_year1_25,'count_math_year1_50':count_math_year1_50,'count_math_year1_75':count_math_year1_75,'count_math_year1_100':count_math_year1_100,
                'count_est_year1_25':count_est_year1_25,'count_est_year1_50':count_est_year1_50,'count_est_year1_75':count_est_year1_75,'count_est_year1_100':count_est_year1_100,
                'count_social_year1_25':count_social_year1_25,'count_social_year1_50':count_social_year1_50,'count_social_year1_75':count_social_year1_75,'count_social_year1_100':count_social_year1_100,
                'count_kiny_year1_25':count_kiny_year1_25,'count_kiny_year1_50':count_kiny_year1_50,'count_kiny_year1_75':count_kiny_year1_75,'count_kiny_year1_100':count_kiny_year1_100,
                'count_engl_year1_25':count_engl_year1_25,'count_engl_year1_50':count_engl_year1_50,'count_engl_year1_75':count_engl_year1_75,'count_engl_year1_100':count_engl_year1_100}       
    
    html = template.render(context)
    pdf= render_to_pdf('schoolPages/schoolTwoYearReport.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "School_%s Comparison between %s in %s" %(school, year1Searched, year2Searched)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary']) 
def schoolQuaterReport(request):
    template = get_template('schoolPages/schoolQuaterReport.html')
    math_school1_25 = 0
    math_school1_50 = 0
    math_school1_75 = 0
    math_school1_100 = 0
    
    est_school1_25 = 0
    est_school1_50 = 0
    est_school1_75 = 0
    est_school1_100 = 0
    
    social_school1_25 = 0
    social_school1_50 = 0
    social_school1_75 = 0
    social_school1_100 = 0
    
    kiny_school1_25 = 0
    kiny_school1_50 = 0
    kiny_school1_75 = 0
    kiny_school1_100 = 0
    
    engl_school1_25 = 0
    engl_school1_50 = 0
    engl_school1_75 = 0
    engl_school1_100 = 0
    
    total_students = 0
    
    try:
        quater = request.GET.get('quater')
        year = request.GET.get('year')
    except:
        quater = None
        year = None
        
    if quater:
        quaterSearched = quater
        if year:
            yearSearched = year
            user = request.user
            school = School.objects.get(user=user)
            sector = school.sector
            district = sector.district 
            school_id = school.id
            classes = Classe.objects.filter(school=school_id)
            
            for classe in classes:
                students  = Student.objects.filter(classe=classe.id, year_reg=yearSearched)
                for student in students:
                    total_students = total_students + 1
                    for math_quater_school1 in student.student_course_set.filter(course=1, quater=quaterSearched):
                        total_math_quater_school1 = math_quater_school1.mid_marks + math_quater_school1.final_marks
                    for est_quater_school1 in student.student_course_set.filter(course=2, quater=quaterSearched):
                        total_est_quater_school1 = est_quater_school1.mid_marks + est_quater_school1.final_marks
                    for social_quater_school1 in student.student_course_set.filter(course=3, quater=quaterSearched):
                        total_social_quater_school1 = social_quater_school1.mid_marks + social_quater_school1.final_marks
                    for kiny_quater_school1 in student.student_course_set.filter(course=4, quater=quaterSearched):
                        total_kiny_quater_school1 = kiny_quater_school1.mid_marks + kiny_quater_school1.final_marks
                    for engl_quater_school1 in student.student_course_set.filter(course=5, quater=quaterSearched):
                        total_engl_quater_shool1 = engl_quater_school1.mid_marks + engl_quater_school1.final_marks
                        
                        total_math_quater_school1_percent = (total_math_quater_school1 * 100)/200
                        total_est_quater_school1_percent = (total_est_quater_school1 * 100)/200
                        total_social_quater_school1_percent = (total_social_quater_school1 * 100)/200
                        total_kiny_quater_school1_percent = (total_kiny_quater_school1 * 100)/200
                        total_engl_quater_shool1_percent = (total_engl_quater_shool1 * 100)/200
                        
                        if total_math_quater_school1_percent<=25:
                            math_school1_25 = math_school1_25+1
                        if total_math_quater_school1_percent<=50 and total_math_quater_school1_percent>=26:
                            math_school1_50 = math_school1_50+1
                        if total_math_quater_school1_percent<=75 and total_math_quater_school1_percent>=51:
                            math_school1_75 = math_school1_75+1
                        if total_math_quater_school1_percent<=100 and total_math_quater_school1_percent>=76:
                            math_school1_100 = math_school1_100+1
                            
                        if total_est_quater_school1_percent<=25:
                            est_school1_25 = est_school1_25+1
                        if total_est_quater_school1_percent<=50 and total_est_quater_school1_percent>=26:
                            est_school1_50 = est_school1_50+1
                        if total_est_quater_school1_percent<=75 and total_est_quater_school1_percent>=51:
                            est_school1_75 = est_school1_75+1
                        if total_est_quater_school1_percent<=100 and total_est_quater_school1_percent>=76:
                            est_school1_100 = est_school1_100+1
                            
                        if total_social_quater_school1_percent<=25:
                            social_school1_25 = social_school1_25+1
                        if total_social_quater_school1_percent<=50 and total_social_quater_school1_percent>=26:
                            social_school1_50 = social_school1_50+1
                        if total_social_quater_school1_percent<=75 and total_social_quater_school1_percent>=51:
                            social_school1_75 = social_school1_75+1
                        if total_social_quater_school1_percent<=100 and total_social_quater_school1_percent>=76:
                            social_school1_100 = social_school1_100+1
                            
                        if total_kiny_quater_school1_percent<=25:
                            kiny_school1_25 = kiny_school1_25+1
                        if total_kiny_quater_school1_percent<=50 and total_kiny_quater_school1_percent>=26:
                            kiny_school1_50 = kiny_school1_50+1
                        if total_kiny_quater_school1_percent<=75 and total_kiny_quater_school1_percent>=51:
                            kiny_school1_75 = kiny_school1_75+1
                        if total_kiny_quater_school1_percent<=100 and total_kiny_quater_school1_percent>=76:
                            kiny_school1_100 = kiny_school1_100+1
                            
                        if total_engl_quater_shool1_percent<=25:
                            engl_school1_25 = engl_school1_25+1
                        if total_engl_quater_shool1_percent<=50 and total_engl_quater_shool1_percent>=26:
                            engl_school1_50 = engl_school1_50+1
                        if total_engl_quater_shool1_percent<=75 and total_engl_quater_shool1_percent>=51:
                            engl_school1_75 = engl_school1_75+1
                        if total_engl_quater_shool1_percent<=100 and total_engl_quater_shool1_percent>=76:
                            engl_school1_100 = engl_school1_100+1
        
        
        
    context = {'quaterSearched':quaterSearched,'yearSearched':yearSearched,'sector':sector,'district':district,'total_students':total_students,'school':school,
               'math_school1_25':math_school1_25,'math_school1_50':math_school1_50,'math_school1_75':math_school1_75,'math_school1_100':math_school1_100,
               'est_school1_25':est_school1_25,'est_school1_50':est_school1_50,'est_school1_75':est_school1_75,'est_school1_100':est_school1_100,
               'social_school1_25':social_school1_25,'social_school1_50':social_school1_50,'social_school1_75':social_school1_75,'social_school1_100':social_school1_100,
               'kiny_school1_25':kiny_school1_25,'kiny_school1_50':kiny_school1_50,'kiny_school1_75':kiny_school1_75,'kiny_school1_100':kiny_school1_100,
               'engl_school1_25':engl_school1_25,'engl_school1_50':engl_school1_50,'engl_school1_75':engl_school1_75,'engl_school1_100':engl_school1_100}
    
    html = template.render(context)
    pdf= render_to_pdf('schoolPages/schoolQuaterReport.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "School_%s Performance %s in %s" %(school, yearSearched, quaterSearched)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector']) 
def schoolReportFromSector(request):
    n_students = 0
    user = request.user.id
    sector = Sector.objects.get(user = user)
    sectorId = sector.id
    schools = School.objects.filter(sector=sectorId)
    
    for school in schools:
        classes = Classe.objects.filter(school=school.id)
        for classe in classes:
            students = Student.objects.filter(classe=classe.id)
            for student in students:
                n_students = n_students + 1
    
    now = datetime.datetime.now()
    year = now.year
    
    schools = School.objects.filter(sector = sectorId)
    
    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count, count(*) from student_student inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id inner join student_sector on student_sector.id=student_school.sector_id where student_student.year_reg=%s and student_sector.id=%s" %(year,sectorId)
    cursor.execute(male_female)
    answers2 = cursor.fetchall()
    
    
    context = {'sector':sector,'schools':schools,'answers2':answers2,'n_students':n_students}    
    
    return render(request, 'sectorPages/searchSchoolFromSector.html',context)


@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector']) 
def schoolReportFromSectorYear(request):
    
    template = get_template('sectorPages/schoolReportFromSectorYear.html')
    
    count_math_year1_25 = 0
    count_math_year1_50 = 0
    count_math_year1_75 = 0
    count_math_year1_100 = 0
    
    count_est_year1_25 = 0
    count_est_year1_50 = 0
    count_est_year1_75 = 0
    count_est_year1_100 = 0
    
    count_engl_year1_25 = 0
    count_engl_year1_50 = 0
    count_engl_year1_75 = 0
    count_engl_year1_100 = 0
    
    count_social_year1_25 = 0
    count_social_year1_50 = 0
    count_social_year1_75 = 0
    count_social_year1_100 = 0
    
    count_kiny_year1_25 = 0
    count_kiny_year1_50 = 0
    count_kiny_year1_75 = 0
    count_kiny_year1_100 = 0
    
    count_student_year1 = 0
    
    try:
        school = request.GET.get('school')
        year = request.GET.get('year')
    except:
        school = None
        year = None
        
    if school:
        schoolSearched = school
        if year:
            yearSearched = year
            school = School.objects.get(id=schoolSearched)
            sector = school.sector
            district = sector.district
            school_id = school
            classes = Classe.objects.filter(school=school_id)
            for classe in classes:
                students_year1 = Student.objects.filter(classe=classe.id,year_reg=yearSearched)
                for student in students_year1:
                    count_student_year1 = count_student_year1+1
                    for math_quater1_year1 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                        total_math_quater1_year1 = math_quater1_year1.mid_marks + math_quater1_year1.final_marks
                    for est_quater1_year1 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                        total_est_quater1_year1 = est_quater1_year1.mid_marks + est_quater1_year1.final_marks
                    for social_quater1_year1 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                        total_social_quater1_year1 = social_quater1_year1.mid_marks + social_quater1_year1.final_marks
                    for kiny_quater1_year1 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                        total_kiny_quater1_year1 = kiny_quater1_year1.mid_marks + kiny_quater1_year1.final_marks
                    for engl_quater1_year1 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                        total_engl_quater1_year1 = engl_quater1_year1.mid_marks + engl_quater1_year1.final_marks
                        
                    for math_quater2_year1 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                        total_math_quater2_year1 = math_quater2_year1.mid_marks + math_quater2_year1.final_marks
                    for est_quater2_year1 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                        total_est_quater2_year1 = est_quater2_year1.mid_marks + est_quater2_year1.final_marks
                    for social_quater2_year1 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                        total_social_quater2_year1 = social_quater2_year1.mid_marks + social_quater2_year1.final_marks
                    for kiny_quater2_year1 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                        total_kiny_quater2_year1 = kiny_quater2_year1.mid_marks + kiny_quater2_year1.final_marks
                    for engl_quater2_year1 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                        total_engl_quater2_year1 = engl_quater2_year1.mid_marks + engl_quater2_year1.final_marks
                    
                    for math_quater3_year1 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                        total_math_quater3_year1 = math_quater3_year1.mid_marks + math_quater3_year1.final_marks
                    for est_quater3_year1 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                        total_est_quater3_year1 = est_quater3_year1.mid_marks + est_quater3_year1.final_marks
                    for social_quater3_year1 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                        total_social_quater3_year1 = social_quater3_year1.mid_marks + social_quater3_year1.final_marks
                    for kiny_quater3_year1 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                        total_kiny_quater3_year1 = kiny_quater3_year1.mid_marks + kiny_quater3_year1.final_marks
                    for engl_quater3_year1 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                        total_engl_quater3_year1 = engl_quater3_year1.mid_marks + engl_quater3_year1.final_marks
                        
                        total_math_year1 = total_math_quater1_year1 +total_math_quater2_year1 + total_math_quater3_year1
                        total_est_year1 = total_est_quater1_year1 + total_est_quater2_year1 + total_est_quater3_year1
                        total_social_year1 = total_social_quater1_year1 + total_social_quater2_year1 + total_social_quater3_year1
                        total_kiny_year1 = total_kiny_quater1_year1 + total_kiny_quater2_year1 + total_kiny_quater3_year1
                        total_engl_year1 = total_engl_quater1_year1 + total_engl_quater2_year1 + total_engl_quater3_year1
                        
                        total_math_year1_percent = (total_math_year1 * 100)/600
                        total_est_year1_percent = (total_est_year1 * 100)/600
                        total_social_year1_percent = (total_social_year1 * 100)/600
                        total_kiny_year1_percent = (total_kiny_year1 * 100)/600
                        total_engl_year1_percent = (total_engl_year1 * 100)/600
                        
                        if total_math_year1_percent<=25:
                            count_math_year1_25 = count_math_year1_25 + 1
                        if total_math_year1_percent<=50 and total_math_year1_percent>=26:
                            count_math_year1_50 = count_math_year1_50 + 1
                        if total_math_year1_percent<=75 and total_math_year1_percent>=51:
                            count_math_year1_75 = count_math_year1_75 + 1
                        if total_math_year1_percent<=100 and total_math_year1_percent>=76:
                            count_math_year1_100 = count_math_year1_100 + 1 
                            
                        if total_est_year1_percent<=25:
                            count_est_year1_25 = count_est_year1_25 + 1
                        if total_est_year1_percent<=50 and total_est_year1_percent>=26:
                            count_est_year1_50 = count_est_year1_50 + 1
                        if total_est_year1_percent<=75 and total_est_year1_percent>=51:
                            count_est_year1_75 = count_est_year1_75 + 1
                        if total_est_year1_percent<=100 and total_est_year1_percent>=76:
                            count_est_year1_100 = count_est_year1_100 + 1 
                            
                        if total_social_year1_percent<=25:
                            count_social_year1_25 = count_social_year1_25 + 1
                        if total_social_year1_percent<=50 and total_social_year1_percent>=26:
                            count_social_year1_50 = count_social_year1_50 + 1
                        if total_social_year1_percent<=75 and total_social_year1_percent>=51:
                            count_social_year1_75 = count_social_year1_75 + 1
                        if total_social_year1_percent<=100 and total_social_year1_percent>=76:
                            count_social_year1_100 = count_social_year1_100 + 1
                            
                        if total_kiny_year1_percent<=25:
                            count_kiny_year1_25 = count_kiny_year1_25 + 1
                        if total_kiny_year1_percent<=50 and total_kiny_year1_percent>=26:
                            count_kiny_year1_50 = count_kiny_year1_50 + 1
                        if total_kiny_year1_percent<=75 and total_kiny_year1_percent>=51:
                            count_kiny_year1_75 = count_kiny_year1_75 + 1
                        if total_kiny_year1_percent<=100 and total_kiny_year1_percent>=76:
                            count_kiny_year1_100 = count_kiny_year1_100 + 1 
                            
                        if total_engl_year1_percent<=25:
                            count_engl_year1_25 = count_engl_year1_25 + 1
                        if total_engl_year1_percent<=50 and total_engl_year1_percent>=26:
                            count_engl_year1_50 = count_engl_year1_50 + 1
                        if total_engl_year1_percent<=75 and total_engl_year1_percent>=51:
                            count_engl_year1_75 = count_engl_year1_75 + 1
                        if total_engl_year1_percent<=100 and total_engl_year1_percent>=76:
                            count_engl_year1_100 = count_engl_year1_100 + 1
            
    
    context = {'schoolSearched':schoolSearched, 'yearSearched':yearSearched,'school':school,'count_student_year1':count_student_year1,'school':school,'sector':sector,'district':district,
               'count_math_year1_25':count_math_year1_25,'count_math_year1_50':count_math_year1_50,'count_math_year1_75':count_math_year1_75,'count_math_year1_100':count_math_year1_100,
               'count_est_year1_25':count_est_year1_25,'count_est_year1_50':count_est_year1_50,'count_est_year1_75':count_est_year1_75,'count_est_year1_100':count_est_year1_100,
               'count_social_year1_25':count_social_year1_25,'count_social_year1_50':count_social_year1_50,'count_social_year1_75':count_social_year1_75,'count_social_year1_100':count_social_year1_100,
               'count_kiny_year1_25':count_kiny_year1_25,'count_kiny_year1_50':count_kiny_year1_50,'count_kiny_year1_75':count_kiny_year1_75,'count_kiny_year1_100':count_kiny_year1_100,
               'count_engl_year1_25':count_engl_year1_25,'count_engl_year1_50':count_engl_year1_50,'count_engl_year1_75':count_engl_year1_75,'count_engl_year1_100':count_engl_year1_100}
            
    
    html = template.render(context)
    pdf= render_to_pdf('sectorPages/schoolReportFromSectorYear.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "School_%s Report in Year of %s" %(school, yearSearched)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector']) 
def schoolReportFromSectorQuater(request):
    
    template = get_template('sectorPages/schoolReportFromSectorQuater.html')
    
    n_students_school1 = 0
    
    math_school1_25 = 0
    math_school1_50 = 0
    math_school1_75 = 0
    math_school1_100 = 0
    
    est_school1_25 = 0
    est_school1_50 = 0
    est_school1_75 = 0
    est_school1_100 = 0
    
    social_school1_25 = 0
    social_school1_50 = 0
    social_school1_75 = 0
    social_school1_100 = 0
    
    kiny_school1_25 = 0
    kiny_school1_50 = 0
    kiny_school1_75 = 0
    kiny_school1_100 = 0
    
    engl_school1_25 = 0
    engl_school1_50 = 0
    engl_school1_75 = 0
    engl_school1_100 = 0
    
    
    try:
        school = request.GET.get('school')
        quater = request.GET.get('quater')
        year = request.GET.get('year')
    except:
        school = None
        quater = None
        year = None
        
    if school:
        schoolSearched = school
        if quater:
            quaterSearched = quater
            if year:
                yearSearched = year
                school = School.objects.get(id=schoolSearched)
                sector = school.sector
                district = sector.district
                school_id = school.id
                classes = Classe.objects.filter(school=school_id)
                
                for classe in classes:
                    students  = Student.objects.filter(classe=classe.id, year_reg=yearSearched)
                    for student in students:
                        n_students_school1 = n_students_school1+1
                        for math_quater_school1 in student.student_course_set.filter(course=1, quater=quaterSearched):
                            total_math_quater_school1 = math_quater_school1.mid_marks + math_quater_school1.final_marks
                        for est_quater_school1 in student.student_course_set.filter(course=2, quater=quaterSearched):
                            total_est_quater_school1 = est_quater_school1.mid_marks + est_quater_school1.final_marks
                        for social_quater_school1 in student.student_course_set.filter(course=3, quater=quaterSearched):
                            total_social_quater_school1 = social_quater_school1.mid_marks + social_quater_school1.final_marks
                        for kiny_quater_school1 in student.student_course_set.filter(course=4, quater=quaterSearched):
                            total_kiny_quater_school1 = kiny_quater_school1.mid_marks + kiny_quater_school1.final_marks
                        for engl_quater_school1 in student.student_course_set.filter(course=5, quater=quaterSearched):
                            total_engl_quater_shool1 = engl_quater_school1.mid_marks + engl_quater_school1.final_marks
                            
                            total_math_quater_school1_percent = (total_math_quater_school1 * 100)/200
                            total_est_quater_school1_percent = (total_est_quater_school1 * 100)/200
                            total_social_quater_school1_percent = (total_social_quater_school1 * 100)/200
                            total_kiny_quater_school1_percent = (total_kiny_quater_school1 * 100)/200
                            total_engl_quater_shool1_percent = (total_engl_quater_shool1 * 100)/200
                            
                            if total_math_quater_school1_percent<=25:
                                math_school1_25 = math_school1_25+1
                            if total_math_quater_school1_percent<=50 and total_math_quater_school1_percent>=26:
                                math_school1_50 = math_school1_50+1
                            if total_math_quater_school1_percent<=75 and total_math_quater_school1_percent>=51:
                                math_school1_75 = math_school1_75+1
                            if total_math_quater_school1_percent<=100 and total_math_quater_school1_percent>=76:
                                math_school1_100 = math_school1_100+1
                                
                            if total_est_quater_school1_percent<=25:
                                est_school1_25 = est_school1_25+1
                            if total_est_quater_school1_percent<=50 and total_est_quater_school1_percent>=26:
                                est_school1_50 = est_school1_50+1
                            if total_est_quater_school1_percent<=75 and total_est_quater_school1_percent>=51:
                                est_school1_75 = est_school1_75+1
                            if total_est_quater_school1_percent<=100 and total_est_quater_school1_percent>=76:
                                est_school1_100 = est_school1_100+1
                                
                            if total_social_quater_school1_percent<=25:
                                social_school1_25 = social_school1_25+1
                            if total_social_quater_school1_percent<=50 and total_social_quater_school1_percent>=26:
                                social_school1_50 = social_school1_50+1
                            if total_social_quater_school1_percent<=75 and total_social_quater_school1_percent>=51:
                                social_school1_75 = social_school1_75+1
                            if total_social_quater_school1_percent<=100 and total_social_quater_school1_percent>=76:
                                social_school1_100 = social_school1_100+1
                                
                            if total_kiny_quater_school1_percent<=25:
                                kiny_school1_25 = kiny_school1_25+1
                            if total_kiny_quater_school1_percent<=50 and total_kiny_quater_school1_percent>=26:
                                kiny_school1_50 = kiny_school1_50+1
                            if total_kiny_quater_school1_percent<=75 and total_kiny_quater_school1_percent>=51:
                                kiny_school1_75 = kiny_school1_75+1
                            if total_kiny_quater_school1_percent<=100 and total_kiny_quater_school1_percent>=76:
                                kiny_school1_100 = kiny_school1_100+1
                                
                            if total_engl_quater_shool1_percent<=25:
                                engl_school1_25 = engl_school1_25+1
                            if total_engl_quater_shool1_percent<=50 and total_engl_quater_shool1_percent>=26:
                                engl_school1_50 = engl_school1_50+1
                            if total_engl_quater_shool1_percent<=75 and total_engl_quater_shool1_percent>=51:
                                engl_school1_75 = engl_school1_75+1
                            if total_engl_quater_shool1_percent<=100 and total_engl_quater_shool1_percent>=76:
                                engl_school1_100 = engl_school1_100+1
                    
                
    context = {'schoolSearched':schoolSearched,'quaterSearched':quaterSearched,'yearSearched':yearSearched,'school':school,'sector':sector,'district':district,'n_students_school1':n_students_school1,
               'math_school1_25':math_school1_25,'math_school1_50':math_school1_50,'math_school1_75':math_school1_75,'math_school1_100':math_school1_100,
               'est_school1_25':est_school1_25,'est_school1_50':est_school1_50,'est_school1_75':est_school1_75,'est_school1_100':est_school1_100,
               'social_school1_25':social_school1_25,'social_school1_50':social_school1_50,'social_school1_75':social_school1_75,'social_school1_100':social_school1_100,
               'kiny_school1_25':kiny_school1_25,'kiny_school1_50':kiny_school1_50,'kiny_school1_75':kiny_school1_75,'kiny_school1_100':kiny_school1_100,
               'engl_school1_25':engl_school1_25,'engl_school1_50':engl_school1_50,'engl_school1_75':engl_school1_75,'engl_school1_100':engl_school1_100}
        
    html = template.render(context)
    pdf= render_to_pdf('sectorPages/schoolReportFromSectorQuater.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "School_%s Report in Year of %s %s" %(school, yearSearched, quaterSearched)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"
@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector']) 
def schoolsComparisonFromSector(request):
    
    template = get_template('sectorPages/schoolsComparisonFromSector.html')
    
    n_student_school1 = 0
    n_student_school2 = 0
    
    math_school125 = 0
    math_school150 = 0
    math_school175 = 0
    math_school1100 = 0
    
    est_school125 = 0
    est_school150 = 0
    est_school175 = 0
    est_school1100 = 0
    
    social_school125 = 0
    social_school150 = 0
    social_school175 = 0
    social_school1100 = 0
    
    kiny_school125 = 0
    kiny_school150 = 0
    kiny_school175 = 0
    kiny_school1100 = 0
    
    engl_school125 = 0
    engl_school150 = 0
    engl_school175 = 0
    engl_school1100 = 0
    
    
    
    math_school225 = 0
    math_school250 = 0
    math_school275 = 0
    math_school2100 = 0
    
    est_school225 = 0
    est_school250 = 0
    est_school275 = 0
    est_school2100 = 0
    
    social_school225 = 0
    social_school250 = 0
    social_school275 = 0
    social_school2100 = 0
    
    kiny_school225 = 0
    kiny_school250 = 0
    kiny_school275 = 0
    kiny_school2100 = 0
    
    engl_school225 = 0
    engl_school250 = 0
    engl_school275 = 0
    engl_school2100 = 0

    try:
        school1 = request.GET.get('school1')
        school2 = request.GET.get('school2')
        year = request.GET.get('year')
    except:
        school1 = None
        school2 = None
        year = None
    
    if school1:
        school1Searched = school1
        school11 = School.objects.get(id=school1Searched)
        if school2:
            school2Searched = school2
            school22 = School.objects.get(id=school2Searched)
            if year:
                yearSearched = year
                
                classesSchool1 = Classe.objects.filter(school=school1Searched)
                classesSchool2 = Classe.objects.filter(school=school2Searched)
                
                for classe in classesSchool1:
                    students = Student.objects.filter(classe=classe.id, year_reg=year)
                    for student in students:
                        n_student_school1 = n_student_school1 + 1
                        for math_quater1_school1 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                            total_math_quater1_school1 = math_quater1_school1.mid_marks + math_quater1_school1.final_marks
                        for est_quater1_school1 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                            total_est_quater1_school1 = est_quater1_school1.mid_marks + est_quater1_school1.final_marks
                        for social_quater1_school1 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                            total_social_quater1_school1 = social_quater1_school1.mid_marks + social_quater1_school1.final_marks
                        for kiny_quater1_school1 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                            total_kiny_quater1_school1 = kiny_quater1_school1.mid_marks + kiny_quater1_school1.final_marks
                        for engl_quater1_school1 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                            total_engl_quater1_school1 = engl_quater1_school1.mid_marks + engl_quater1_school1.final_marks
                            
                        for math_quater2_school1 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                            total_math_quater2_school1 = math_quater2_school1.mid_marks + math_quater2_school1.final_marks
                        for est_quater2_school1 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                            total_est_quater2_school1 = est_quater2_school1.mid_marks + est_quater2_school1.final_marks
                        for social_quater2_school1 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                            total_social_quater2_school1 = social_quater2_school1.mid_marks + social_quater2_school1.final_marks
                        for kiny_quater2_school1 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                            total_kiny_quater2_school1 = kiny_quater2_school1.mid_marks + kiny_quater2_school1.final_marks
                        for engl_quater2_school1 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                            total_engl_quater2_school1 = engl_quater2_school1.mid_marks + engl_quater2_school1.final_marks
                            
                        for math_quater3_school1 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                            total_math_quater3_school1 = math_quater3_school1.mid_marks + math_quater3_school1.final_marks
                        for est_quater3_school1 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                            total_est_quater3_school1 = est_quater3_school1.mid_marks + est_quater3_school1.final_marks
                        for social_quater3_school1 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                            total_social_quater3_school1 = social_quater3_school1.mid_marks + social_quater3_school1.final_marks
                        for kiny_quater3_school1 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                            total_kiny_quater3_school1 = kiny_quater3_school1.mid_marks + kiny_quater3_school1.final_marks
                        for engl_quater3_school1 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                            total_engl_quater3_school1 = engl_quater3_school1.mid_marks + engl_quater3_school1.final_marks
                            
                            total_math_school1 = total_math_quater1_school1 + total_math_quater2_school1 + total_math_quater3_school1
                            total_est_school1 = total_est_quater1_school1 + total_est_quater2_school1 + total_est_quater3_school1
                            total_social_school1 = total_social_quater1_school1 + total_social_quater2_school1 + total_social_quater3_school1
                            total_kiny_school1 = total_kiny_quater1_school1 + total_kiny_quater2_school1 + total_kiny_quater3_school1
                            total_engl_school1 = total_engl_quater1_school1 + total_engl_quater2_school1 + total_engl_quater3_school1
                            
                            total_math_school1_percent = (total_math_school1 * 100)/600
                            total_est_school1_percent = (total_est_school1 * 100)/600
                            total_social_school1_percent = (total_social_school1 * 100)/600
                            total_kiny_school1_percent = (total_kiny_school1 * 100)/600
                            total_engl_school1_percent = (total_engl_school1 * 100)/600
                                  
                            if total_math_school1_percent <= 25:
                                math_school125 = math_school125 + 1
                            if total_math_school1_percent<=50 and total_math_school1_percent>=26:
                                math_school150 = math_school150 + 1
                            if total_math_school1_percent<=75 and total_math_school1_percent>=51:
                                  math_school175 = math_school175 + 1
                            if total_math_school1_percent<=100 and total_math_school1_percent>=76:
                                  math_school1100 = math_school1100 + 1
                                  
                            if total_est_school1_percent <= 25:
                                est_school125 = est_school125 + 1
                            if total_est_school1_percent<=50 and total_est_school1_percent>=26:
                                est_school150 = est_school150 + 1
                            if total_est_school1_percent<=75 and total_est_school1_percent>=51:
                                  est_school175 = est_school175 + 1
                            if total_est_school1_percent<=100 and total_est_school1_percent>=76:
                                  est_school1100 = est_school1100 + 1
                                  
                            if total_social_school1_percent <= 25:
                                social_school125 = social_school125 + 1
                            if total_social_school1_percent<=50 and total_social_school1_percent>=26:
                                social_school150 = social_school150 + 1
                            if total_social_school1_percent<=75 and total_social_school1_percent>=51:
                                social_school175 = social_school175 + 1
                            if total_social_school1_percent<=100 and total_social_school1_percent>=76:
                                social_school1100 = social_school1100 + 1
                                
                            if total_kiny_school1_percent <= 25:
                                kiny_school125 = kiny_school125 + 1
                            if total_kiny_school1_percent<=50 and total_kiny_school1_percent>=26:
                                kiny_school150 = kiny_school150 + 1
                            if total_kiny_school1_percent<=75 and total_kiny_school1_percent>=51:
                                kiny_school175 = kiny_school175 + 1
                            if total_kiny_school1_percent<=100 and total_kiny_school1_percent>=76:
                                kiny_school1100 = kiny_school1100 + 1
                                
                            if total_engl_school1_percent <= 25:
                                engl_school125 = engl_school125 + 1
                            if total_engl_school1_percent<=50 and total_engl_school1_percent>=26:
                                engl_school150 = engl_school150 + 1
                            if total_engl_school1_percent<=75 and total_engl_school1_percent>=51:
                                engl_school175 = engl_school175 + 1
                            if total_engl_school1_percent<=100 and total_engl_school1_percent>=76:
                                engl_school1100 = engl_school1100 + 1
                
                
                
                for classe in classesSchool2:
                    students = Student.objects.filter(classe=classe.id, year_reg=year)
                    for student in students:
                        n_student_school2 = n_student_school2 + 1
                        for math_quater1_school2 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                            total_math_quater1_school2 = math_quater1_school2.mid_marks + math_quater1_school2.final_marks
                        for est_quater1_school2 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                            total_est_quater1_school2 = est_quater1_school2.mid_marks + est_quater1_school2.final_marks
                        for social_quater1_school2 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                            total_social_quater1_school2 = social_quater1_school2.mid_marks + social_quater1_school2.final_marks
                        for kiny_quater1_school2 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                            total_kiny_quater1_school2 = kiny_quater1_school2.mid_marks + kiny_quater1_school2.final_marks
                        for engl_quater1_school2 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                            total_engl_quater1_school2 = engl_quater1_school2.mid_marks + engl_quater1_school2.final_marks
                            
                        for math_quater2_school2 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                            total_math_quater2_school2 = math_quater2_school2.mid_marks + math_quater2_school2.final_marks
                        for est_quater2_school2 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                            total_est_quater2_school2 = est_quater2_school2.mid_marks + est_quater2_school2.final_marks
                        for social_quater2_school2 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                            total_social_quater2_school2 = social_quater2_school2.mid_marks + social_quater2_school2.final_marks
                        for kiny_quater2_school2 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                            total_kiny_quater2_school2 = kiny_quater2_school2.mid_marks + kiny_quater2_school2.final_marks
                        for engl_quater2_school2 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                            total_engl_quater2_school2 = engl_quater2_school2.mid_marks + engl_quater2_school2.final_marks
                            
                        for math_quater3_school2 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                            total_math_quater3_school2 = math_quater3_school2.mid_marks + math_quater3_school2.final_marks
                        for est_quater3_school2 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                            total_est_quater3_school2 = est_quater3_school2.mid_marks + est_quater3_school2.final_marks
                        for social_quater3_school2 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                            total_social_quater3_school2 = social_quater3_school2.mid_marks + social_quater3_school2.final_marks
                        for kiny_quater3_school2 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                            total_kiny_quater3_school2 = kiny_quater3_school2.mid_marks + kiny_quater3_school2.final_marks
                        for engl_quater3_school2 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                            total_engl_quater3_school2 = engl_quater3_school2.mid_marks + engl_quater3_school2.final_marks
                            
                            total_math_school2 = total_math_quater1_school2 + total_math_quater2_school2 + total_math_quater3_school2
                            total_est_school2 = total_est_quater1_school2 + total_est_quater2_school2 + total_est_quater3_school2
                            total_social_school2 = total_social_quater1_school2 + total_social_quater2_school2 + total_social_quater3_school2
                            total_kiny_school2 = total_kiny_quater1_school2 + total_kiny_quater2_school2 + total_kiny_quater3_school2
                            total_engl_school2 = total_engl_quater1_school2 + total_engl_quater2_school2 + total_engl_quater3_school2
                            
                            total_math_school2_percent = (total_math_school2 * 100)/600
                            total_est_school2_percent = (total_est_school2 * 100)/600
                            total_social_school2_percent = (total_social_school2 * 100)/600
                            total_kiny_school2_percent = (total_kiny_school2 * 100)/600
                            total_engl_school2_percent = (total_engl_school2 * 100)/600
                                  
                            if total_math_school2_percent <= 25:
                                math_school225 = math_school225 + 1
                            if total_math_school2_percent<=50 and total_math_school2_percent>=26:
                                math_school250 = math_school250 + 1
                            if total_math_school2_percent<=75 and total_math_school2_percent>=51:
                                  math_school275 = math_school275 + 1
                            if total_math_school2_percent<=100 and total_math_school2_percent>=76:
                                  math_school2100 = math_school2100 + 1
                                  
                            if total_est_school2_percent <= 25:
                                est_school225 = est_school225 + 1
                            if total_est_school2_percent<=50 and total_est_school2_percent>=26:
                                est_school250 = est_school250 + 1
                            if total_est_school2_percent<=75 and total_est_school2_percent>=51:
                                  est_school275 = est_school275 + 1
                            if total_est_school2_percent<=100 and total_est_school2_percent>=76:
                                  est_school2100 = est_school2100 + 1
                                  
                            if total_social_school2_percent <= 25:
                                social_school225 = social_school225 + 1
                            if total_social_school2_percent<=50 and total_social_school2_percent>=26:
                                social_school250 = social_school250 + 1
                            if total_social_school2_percent<=75 and total_social_school2_percent>=51:
                                social_school275 = social_school275 + 1
                            if total_social_school2_percent<=100 and total_social_school2_percent>=76:
                                social_school2100 = social_school2100 + 1
                                
                            if total_kiny_school2_percent <= 25:
                                kiny_school225 = kiny_school225 + 1
                            if total_kiny_school2_percent<=50 and total_kiny_school2_percent>=26:
                                kiny_school250 = kiny_school250 + 1
                            if total_kiny_school2_percent<=75 and total_kiny_school2_percent>=51:
                                kiny_school275 = kiny_school275 + 1
                            if total_kiny_school2_percent<=100 and total_kiny_school2_percent>=76:
                                kiny_school2100 = kiny_school2100 + 1
                                
                            if total_engl_school2_percent <= 25:
                                engl_school225 = engl_school225 + 1
                            if total_engl_school2_percent<=50 and total_engl_school2_percent>=26:
                                engl_school250 = engl_school250 + 1
                            if total_engl_school2_percent<=75 and total_engl_school2_percent>=51:
                                engl_school275 = engl_school275 + 1
                            if total_engl_school2_percent<=100 and total_engl_school2_percent>=76:
                                engl_school2100 = engl_school2100 + 1
                
                
            
    context = {'school1Searched':school1Searched,'school2Searched':school2Searched,'yearSearched':yearSearched,'school11':school11,'school22':school22,'n_student_school1':n_student_school1,'n_student_school2':n_student_school2,
               'math_school125':math_school125,'math_school150':math_school150,'math_school175':math_school175,'math_school1100':math_school1100,
               'est_school125':est_school125,'est_school150':est_school150,'est_school175':est_school175,'est_school1100':est_school1100,
               'social_school125':social_school125,'social_school150':social_school150,'social_school175':social_school175,'social_school1100':social_school1100,
               'kiny_school125':kiny_school125,'kiny_school150':kiny_school150,'kiny_school175':kiny_school175,'kiny_school1100':kiny_school1100,
               'engl_school125':engl_school125,'engl_school150':engl_school150,'engl_school175':engl_school175,'engl_school1100':engl_school1100,
               'math_school225':math_school225,'math_school250':math_school250,'math_school275':math_school275,'math_school2100':math_school2100,
               'est_school225':est_school225,'est_school250':est_school250,'est_school275':est_school275,'est_school2100':est_school2100,
               'social_school225':social_school225,'social_school250':social_school250,'social_school275':social_school275,'social_school2100':social_school2100,
               'kiny_school225':kiny_school225,'kiny_school250':kiny_school250,'kiny_school275':kiny_school275,'kiny_school2100':kiny_school2100,
               'engl_school225':engl_school225,'engl_school250':engl_school250,'engl_school275':engl_school275,'engl_school2100':engl_school2100}
    
    html = template.render(context)
    pdf= render_to_pdf('sectorPages/schoolsComparisonFromSector.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "School_%s and %s Performance Comparison in %s" %(school11, school22, yearSearched)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector']) 
def schoolYearComparisonFromSector(request):
    
    template = get_template('sectorPages/schoolYearComparisonFromSector.html')
    
    count_math_25 = 0
    count_math_50 = 0
    count_math_75 = 0
    count_math_100 = 0
    
    count_est_25 = 0
    count_est_50 = 0
    count_est_75 = 0
    count_est_100 = 0
    
    count_engl_25 = 0
    count_engl_50 = 0
    count_engl_75 = 0
    count_engl_100 = 0
    
    count_social_25 = 0
    count_social_50 = 0
    count_social_75 = 0
    count_social_100 = 0
    
    count_kiny_25 = 0
    count_kiny_50 = 0
    count_kiny_75 = 0
    count_kiny_100 = 0
    
    
    
    count_math_year1_25 = 0
    count_math_year1_50 = 0
    count_math_year1_75 = 0
    count_math_year1_100 = 0
    
    count_est_year1_25 = 0
    count_est_year1_50 = 0
    count_est_year1_75 = 0
    count_est_year1_100 = 0
    
    count_engl_year1_25 = 0
    count_engl_year1_50 = 0
    count_engl_year1_75 = 0
    count_engl_year1_100 = 0
    
    count_social_year1_25 = 0
    count_social_year1_50 = 0
    count_social_year1_75 = 0
    count_social_year1_100 = 0
    
    count_kiny_year1_25 = 0
    count_kiny_year1_50 = 0
    count_kiny_year1_75 = 0
    count_kiny_year1_100 = 0
  

    count_student_year1 = 0
    count_student_year2 = 0
    
    
    try:
        school = request.GET.get('school')
        year1 = request.GET.get('year1')
        year2 = request.GET.get('year2')
    except:
        school = None
        year1 = None
        year2 = None
        
    if school:
        schoolSearched = school
        if year1:
            year1Searched = year1
            if year2:
                year2Searched = year2
                schooll = School.objects.get(id=schoolSearched)
                sector = schooll.sector
                district = sector.district
                school_id= schooll.id
                classes = Classe.objects.filter(school=school_id)
                number_of_classes = classes.count()
                for classe in classes:
                    students_year1 = Student.objects.filter(classe=classe.id,year_reg=year1Searched)
                    for student in students_year1:
                        count_student_year1 = count_student_year1+1
                        for math_quater1_year1 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                            total_math_quater1_year1 = math_quater1_year1.mid_marks + math_quater1_year1.final_marks
                        for est_quater1_year1 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                            total_est_quater1_year1 = est_quater1_year1.mid_marks + est_quater1_year1.final_marks
                        for social_quater1_year1 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                            total_social_quater1_year1 = social_quater1_year1.mid_marks + social_quater1_year1.final_marks
                        for kiny_quater1_year1 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                            total_kiny_quater1_year1 = kiny_quater1_year1.mid_marks + kiny_quater1_year1.final_marks
                        for engl_quater1_year1 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                            total_engl_quater1_year1 = engl_quater1_year1.mid_marks + engl_quater1_year1.final_marks
                            
                        for math_quater2_year1 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                            total_math_quater2_year1 = math_quater2_year1.mid_marks + math_quater2_year1.final_marks
                        for est_quater2_year1 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                            total_est_quater2_year1 = est_quater2_year1.mid_marks + est_quater2_year1.final_marks
                        for social_quater2_year1 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                            total_social_quater2_year1 = social_quater2_year1.mid_marks + social_quater2_year1.final_marks
                        for kiny_quater2_year1 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                            total_kiny_quater2_year1 = kiny_quater2_year1.mid_marks + kiny_quater2_year1.final_marks
                        for engl_quater2_year1 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                            total_engl_quater2_year1 = engl_quater2_year1.mid_marks + engl_quater2_year1.final_marks
                        
                        for math_quater3_year1 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                            total_math_quater3_year1 = math_quater3_year1.mid_marks + math_quater3_year1.final_marks
                        for est_quater3_year1 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                            total_est_quater3_year1 = est_quater3_year1.mid_marks + est_quater3_year1.final_marks
                        for social_quater3_year1 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                            total_social_quater3_year1 = social_quater3_year1.mid_marks + social_quater3_year1.final_marks
                        for kiny_quater3_year1 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                            total_kiny_quater3_year1 = kiny_quater3_year1.mid_marks + kiny_quater3_year1.final_marks
                        for engl_quater3_year1 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                            total_engl_quater3_year1 = engl_quater3_year1.mid_marks + engl_quater3_year1.final_marks
                            
                            total_math_year1 = total_math_quater1_year1 +total_math_quater2_year1 + total_math_quater3_year1
                            total_est_year1 = total_est_quater1_year1 + total_est_quater2_year1 + total_est_quater3_year1
                            total_social_year1 = total_social_quater1_year1 + total_social_quater2_year1 + total_social_quater3_year1
                            total_kiny_year1 = total_kiny_quater1_year1 + total_kiny_quater2_year1 + total_kiny_quater3_year1
                            total_engl_year1 = total_engl_quater1_year1 + total_engl_quater2_year1 + total_engl_quater3_year1
                            
                            total_math_year1_percent = (total_math_year1 * 100)/600
                            total_est_year1_percent = (total_est_year1 * 100)/600
                            total_social_year1_percent = (total_social_year1 * 100)/600
                            total_kiny_year1_percent = (total_kiny_year1 * 100)/600
                            total_engl_year1_percent = (total_engl_year1 * 100)/600
                            
                            if total_math_year1_percent<=25:
                                count_math_year1_25 = count_math_year1_25 + 1
                            if total_math_year1_percent<=50 and total_math_year1_percent>=26:
                                count_math_year1_50 = count_math_year1_50 + 1
                            if total_math_year1_percent<=75 and total_math_year1_percent>=51:
                                count_math_year1_75 = count_math_year1_75 + 1
                            if total_math_year1_percent<=100 and total_math_year1_percent>=76:
                                count_math_year1_100 = count_math_year1_100 + 1 
                                
                            if total_est_year1_percent<=25:
                                count_est_year1_25 = count_est_year1_25 + 1
                            if total_est_year1_percent<=50 and total_est_year1_percent>=26:
                                count_est_year1_50 = count_est_year1_50 + 1
                            if total_est_year1_percent<=75 and total_est_year1_percent>=51:
                                count_est_year1_75 = count_est_year1_75 + 1
                            if total_est_year1_percent<=100 and total_est_year1_percent>=76:
                                count_est_year1_100 = count_est_year1_100 + 1 
                                
                            if total_social_year1_percent<=25:
                                count_social_year1_25 = count_social_year1_25 + 1
                            if total_social_year1_percent<=50 and total_social_year1_percent>=26:
                                count_social_year1_50 = count_social_year1_50 + 1
                            if total_social_year1_percent<=75 and total_social_year1_percent>=51:
                                count_social_year1_75 = count_social_year1_75 + 1
                            if total_social_year1_percent<=100 and total_social_year1_percent>=76:
                                count_social_year1_100 = count_social_year1_100 + 1
                                
                            if total_kiny_year1_percent<=25:
                                count_kiny_year1_25 = count_kiny_year1_25 + 1
                            if total_kiny_year1_percent<=50 and total_kiny_year1_percent>=26:
                                count_kiny_year1_50 = count_kiny_year1_50 + 1
                            if total_kiny_year1_percent<=75 and total_kiny_year1_percent>=51:
                                count_kiny_year1_75 = count_kiny_year1_75 + 1
                            if total_kiny_year1_percent<=100 and total_kiny_year1_percent>=76:
                                count_kiny_year1_100 = count_kiny_year1_100 + 1 
                                
                            if total_engl_year1_percent<=25:
                                count_engl_year1_25 = count_engl_year1_25 + 1
                            if total_engl_year1_percent<=50 and total_engl_year1_percent>=26:
                                count_engl_year1_50 = count_engl_year1_50 + 1
                            if total_engl_year1_percent<=75 and total_engl_year1_percent>=51:
                                count_engl_year1_75 = count_engl_year1_75 + 1
                            if total_engl_year1_percent<=100 and total_engl_year1_percent>=76:
                                count_engl_year1_100 = count_engl_year1_100 + 1
                            
                            
                    students_year2 = Student.objects.filter(classe=classe.id, year_reg=year2Searched)
                    for studentt in students_year2:
                        count_student_year2 = count_student_year2+1
                        for math_quater1 in studentt.student_course_set.filter(course=1, quater = 'QUATER1'):
                            total_math_quater1_year2 = math_quater1.mid_marks + math_quater1.final_marks 
                        for est_quater1 in studentt.student_course_set.filter(course=2, quater = 'QUATER1'):
                            total_est_quater1_year2 = est_quater1.mid_marks + est_quater1.final_marks  
                        for social_quater1 in studentt.student_course_set.filter(course=3, quater = 'QUATER1'):
                            total_social_quater1_year2 = social_quater1.mid_marks + social_quater1.final_marks
                        for kiny_quater1 in studentt.student_course_set.filter(course=4, quater = 'QUATER1'):
                            total_kiny_quater1_year2 = kiny_quater1.mid_marks + kiny_quater1.final_marks 
                        for engl_quater1 in studentt.student_course_set.filter(course=5, quater = 'QUATER1'):
                            total_engl_quater1_year2 = engl_quater1.mid_marks + engl_quater1.final_marks  
                            
                        for math_quater2 in studentt.student_course_set.filter(course=1, quater = 'QUATER2'):
                            total_math_quater2_year2 = math_quater2.mid_marks + math_quater2.final_marks
                        for est_quater2 in studentt.student_course_set.filter(course=2, quater = 'QUATER2'):
                            total_est_quater2_year2 = est_quater2.mid_marks + est_quater2.final_marks
                        for social_quater2 in studentt.student_course_set.filter(course=3, quater = 'QUATER2'):
                            total_social_quater2_year2 = social_quater2.mid_marks + social_quater2.final_marks
                        for kiny_quater2 in studentt.student_course_set.filter(course=4, quater = 'QUATER2'):
                            total_kiny_quater2_year2 = kiny_quater2.mid_marks + kiny_quater2.final_marks
                        for engl_quater2 in studentt.student_course_set.filter(course=5, quater = 'QUATER2'):
                            total_engl_quater2_year2 = engl_quater2.mid_marks + engl_quater2.final_marks     
                        
                        for math_quater3 in studentt.student_course_set.filter(course=1, quater = 'QUATER3'):
                            total_math_quater3_year2 = math_quater3.mid_marks + math_quater3.final_marks
                        for est_quater3 in studentt.student_course_set.filter(course=2, quater = 'QUATER3'):
                            total_est_quater3_year2 = est_quater3.mid_marks + est_quater3.final_marks 
                        for social_quater3 in studentt.student_course_set.filter(course=3, quater = 'QUATER3'):
                            total_social_quater3_year2 = social_quater3.mid_marks + social_quater3.final_marks
                        for kiny_quater3 in studentt.student_course_set.filter(course=4, quater = 'QUATER3'):
                            total_kiny_quater3_year2 = kiny_quater3.mid_marks + kiny_quater3.final_marks 
                        for engl_quater3 in studentt.student_course_set.filter(course=5, quater = 'QUATER3'):
                            total_engl_quater3_year2 = engl_quater3.mid_marks + engl_quater3.final_marks

                                
                            total_math = total_math_quater1_year2 + total_math_quater2_year2 + total_math_quater3_year2
                            total_est = total_est_quater1_year2 + total_est_quater2_year2 + total_est_quater3_year2
                            total_social = total_social_quater1_year2 + total_social_quater2_year2 + total_social_quater3_year2
                            total_kiny = total_kiny_quater1_year2 + total_kiny_quater2_year2 + total_kiny_quater3_year2
                            total_engl = total_engl_quater1_year2 + total_engl_quater2_year2 + total_engl_quater3_year2
                            
                            
                            
                            total_math_percent = (total_math * 100)/600
                            total_est_percent = (total_est * 100)/600
                            total_social_percent = (total_social * 100)/600
                            total_kiny_percent = (total_kiny * 100)/600
                            total_engl_percent = (total_engl * 100)/600
                            
                            
                            if total_math_percent<=25:
                                count_math_25 = count_math_25 + 1
                            if total_math_percent<=50 and total_math_percent>=26:
                                count_math_50 = count_math_50 + 1
                            if total_math_percent<=75 and total_math_percent>=51:
                                count_math_75 = count_math_75 + 1
                            if total_math_percent<=100 and total_math_percent>=76:
                                count_math_100 = count_math_100 + 1   
                                
                            if total_est_percent<=25:
                                count_est_25 = count_est_25 + 1
                            if total_est_percent<=50 and total_est_percent>=26:
                                count_est_50 = count_est_50 + 1
                            if total_est_percent<=75 and total_est_percent>=51:
                                count_est_75 = count_est_75 + 1
                            if total_est_percent<=100 and total_est_percent>=76:
                                count_est_100 = count_est_100 + 1 
                                
                            if total_social_percent<=25:
                                count_social_25 = count_social_25 + 1
                            if total_social_percent<=50 and total_social_percent>=26:
                                count_social_50 = count_social_50 + 1
                            if total_social_percent<=75 and total_social_percent>=51:
                                count_social_75 = count_social_75 + 1
                            if total_social_percent<=100 and total_social_percent>=76:
                                count_social_100 = count_social_100 + 1
                                
                            if total_kiny_percent<=25:
                                count_kiny_25 = count_kiny_25 + 1
                            if total_kiny_percent<=50 and total_kiny_percent>=26:
                                count_kiny_50 = count_kiny_50 + 1
                            if total_kiny_percent<=75 and total_kiny_percent>=51:
                                count_kiny_75 = count_kiny_75 + 1
                            if total_kiny_percent<=100 and total_kiny_percent>=76:
                                count_kiny_100 = count_kiny_100 + 1 
                                
                            if total_engl_percent<=25:
                                count_engl_25 = count_engl_25 + 1
                            if total_engl_percent<=50 and total_engl_percent>=26:
                                count_engl_50 = count_engl_50 + 1
                            if total_engl_percent<=75 and total_engl_percent>=51:
                                count_engl_75 = count_engl_75 + 1
                            if total_engl_percent<=100 and total_engl_percent>=76:
                                count_engl_100 = count_engl_100 + 1 
                                
                            
                

    context = {'count_student_year1':count_student_year1,'count_student_year2':count_student_year2,'schooll':schooll,'sector':sector,'district':district,'year1Searched':year1Searched,'year2Searched':year2Searched,'count_math_25':count_math_25,'count_math_50':count_math_50,'count_math_75':count_math_75,'count_math_100':count_math_100,
               'count_est_25':count_est_25,'count_est_50':count_est_50,'count_est_75':count_est_75,'count_est_100':count_est_100,
               'count_social_25':count_social_25,'count_social_50':count_social_50,'count_social_75':count_social_75,'count_social_100':count_social_100,
               'count_kiny_25':count_kiny_25,'count_kiny_50':count_kiny_50,'count_kiny_75':count_kiny_75,'count_kiny_100':count_kiny_100,
               'count_engl_25':count_engl_25,'count_engl_50':count_engl_50,'count_engl_75':count_engl_75,'count_engl_100':count_engl_100,
               'count_math_year1_25':count_math_year1_25,'count_math_year1_50':count_math_year1_50,'count_math_year1_75':count_math_year1_75,'count_math_year1_100':count_math_year1_100,
               'count_est_year1_25':count_est_year1_25,'count_est_year1_50':count_est_year1_50,'count_est_year1_75':count_est_year1_75,'count_est_year1_100':count_est_year1_100,
               'count_social_year1_25':count_social_year1_25,'count_social_year1_50':count_social_year1_50,'count_social_year1_75':count_social_year1_75,'count_social_year1_100':count_social_year1_100,
               'count_kiny_year1_25':count_kiny_year1_25,'count_kiny_year1_50':count_kiny_year1_50,'count_kiny_year1_75':count_kiny_year1_75,'count_kiny_year1_100':count_kiny_year1_100,
               'count_engl_year1_25':count_engl_year1_25,'count_engl_year1_50':count_engl_year1_50,'count_engl_year1_75':count_engl_year1_75,'count_engl_year1_100':count_engl_year1_100}        

    html = template.render(context)
    pdf= render_to_pdf('sectorPages/schoolYearComparisonFromSector.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "School_%s Report Comparison between %s and %s" %(schooll, year1Searched, year2Searched)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"


@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector']) 
def viewSchoolReport(request):
    quater1_math25=0
    quater1_math50=0
    quater1_math75=0
    quater1_math100=0
    
    quater1_engl25=0
    quater1_engl50=0
    quater1_engl75=0
    quater1_engl100=0
    
    quater1_set25=0
    quater1_set50=0
    quater1_set75=0
    quater1_set100=0
    
    quater1_social25=0
    quater1_social50=0
    quater1_social75=0
    quater1_social100=0
    
    quater1_kiny25=0
    quater1_kiny50=0
    quater1_kiny75=0
    quater1_kiny100=0
    
    try:
        searched = request.GET.get('sch')
    except:
        searched = None
    if searched:
        school = School.objects.get(id=searched)
        school_id = school.id
        classes = Classe.objects.filter(school=school_id)
        
        for classe in classes:
            students = Student.objects.filter(classe=classe.id)
            for student in students:
                for st in student.student_course_set.filter(course=1, quater='QUATER1'):
                    total_math = st.mid_marks + st.final_marks
                    total_math_percent = (total_math*100)/200
                    if total_math_percent<=25:
                        quater1_math25 = quater1_math25+1
                    if total_math_percent<=50 and total_math_percent>=26:
                        quater1_math50 = quater1_math50+1
                    if total_math_percent<=75 and total_math_percent>=51:
                        quater1_math75 = quater1_math75+1
                    if total_math_percent<=100 and total_math_percent>=76:
                        quater1_math100 = quater1_math100+1
                        
                for engl in student.student_course_set.filter(course=5, quater='QUATER1'):
                    total_engl = engl.mid_marks+engl.final_marks
                    total_engl_percent = (total_engl*100)/200
                    if total_engl_percent<=25:
                        quater1_engl25 = quater1_engl25+1
                    if total_engl_percent<=50 and total_engl_percent>=26:
                        quater1_engl50 = quater1_engl50+1
                    if total_engl_percent<=75 and total_engl_percent>=51:
                        quater1_engl75 = quater1_engl75+1
                    if total_engl_percent<=100 and total_engl_percent>=76:
                        quater1_engl100 = quater1_engl100+1
                    
                for est in student.student_course_set.filter(course=2, quater='QUATER1'):
                    total_set = est.mid_marks+est.final_marks
                    total_set_percent = (total_set*100)/200
                    if total_set_percent<=25:
                        quater1_set25 = quater1_set25+1
                    if total_set_percent<=50 and total_set_percent>=26:
                        quater1_set50 = quater1_set50+1
                    if total_set_percent<=75 and total_set_percent>=51:
                        quater1_set75 = quater1_set75+1
                    if total_set_percent<=100 and total_set_percent>=76:
                        quater1_set100 = quater1_set100+1
                    
                for social in student.student_course_set.filter(course=3, quater='QUATER1'):
                    total_social = social.mid_marks+social.final_marks
                    total_social_percent = (total_social*100)/200
                    if total_social_percent<=25:
                        quater1_social25 = quater1_social25+1
                    if total_social_percent<=50 and total_social_percent>=26:
                        quater1_social50 = quater1_social50+1
                    if total_social_percent<=75 and total_social_percent>=51:
                        quater1_social75 = quater1_social75+1
                    if total_social_percent<=100 and total_social_percent>=76:
                        quater1_social100 = quater1_social100+1
                    
                for kiny in student.student_course_set.filter(course=4, quater='QUATER1'):
                    total_kiny = kiny.mid_marks+kiny.final_marks
                    total_kiny_percent = (total_kiny*100)/200
                    if total_kiny_percent<=25:
                        quater1_kiny25 = quater1_kiny25+1
                    if total_kiny_percent<=50 and total_kiny_percent>=26:
                        quater1_kiny50 = quater1_kiny50+1
                    if total_kiny_percent<=75 and total_kiny_percent>=51:
                        quater1_kiny75 = quater1_kiny75+1
                    if total_kiny_percent<=100 and total_kiny_percent>=76:
                        quater1_kiny100 = quater1_kiny100+1
        
        
        
        context = {'school':school,'quater1_math25':quater1_math25,'quater1_math50':quater1_math50,'quater1_math75':quater1_math75,'quater1_math100':quater1_math100,
               'quater1_engl25':quater1_engl25,'quater1_engl50':quater1_engl50,'quater1_engl75':quater1_engl75,'quater1_engl100':quater1_engl100,
               'quater1_set25':quater1_set25,'quater1_set50':quater1_set50,'quater1_set75':quater1_set75,'quater1_set100':quater1_set100,
               'quater1_social25':quater1_social25,'quater1_social50':quater1_social50,'quater1_social75':quater1_social75,'quater1_social100':quater1_social100,
               'quater1_kiny25':quater1_kiny25,'quater1_kiny50':quater1_kiny50,'quater1_kiny75':quater1_kiny75,'quater1_kiny100':quater1_kiny100}
        
    template = 'sectorPages/searchedschool.html'
    return render(request, template,context) 

# def tryinlineformsetlist(request):
#     students = Student.objects.filter(classe=4)
#      Student_CourseFormSet = inlineformset_factory(Student, fields=('f_name','l_name','dob','year_reg'),max_num=5)
#      if request.method == 'POST':
#         #form = StudentCourseForm(request.POST)
#         formSet = StudentFormSet(request.POST)
#         if formSet.is_valid():
#             formSet.save()
#             messages.success(request, 'The Student has been given marks successfully')
#             return redirect('class')
#     context = {'formSet':formSet,'studentt':studentt}
#     context = {'students':students}
#     return render(request, 'inlineformset.html', context)

def goToLogin(request):
    return render(request, 'login.html')

@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary']) 
def studentbulletin(request,pk_student):
        
    template = get_template('schoolPages/studentbulletin.html')
    grade = ""
    try: 
        quater = request.GET.get('quater')
    except:
        quater = None
    if quater:
        student = Student.objects.get(id=pk_student)

        classe =  student.classe
        school = classe.school
        sector = school.sector
        students = Student.objects.filter(classe=classe)
        n_of_students = students.count()

        

        student_marks = student.student_course_set.all()
        
        quater1_math = Student_Course.objects.get(quater=quater, course=1, student=student)
        quater1_est = Student_Course.objects.get(quater=quater, course=2, student=student)
        quater1_social = Student_Course.objects.get(quater=quater, course=3, student=student)
        quater1_kiny = Student_Course.objects.get(quater=quater, course=4, student=student)
        quater1_engl = Student_Course.objects.get(quater=quater, course=5, student=student)
        
        total_quater1_math = quater1_math.mid_marks + quater1_math.final_marks
        total_quater1_est = quater1_est.mid_marks + quater1_est.final_marks
        total_quater1_social = quater1_social.mid_marks + quater1_social.final_marks
        total_quater1_kiny = quater1_kiny.mid_marks + quater1_kiny.final_marks
        total_quater1_engl = quater1_engl.mid_marks + quater1_engl.final_marks
        
        total_quater1 = total_quater1_math+total_quater1_est+total_quater1_social+total_quater1_kiny+total_quater1_engl

        total_percent = (total_quater1 * 100)/1000
        if(total_percent>=80):
            grade = "A"
        elif(total_percent<80 and total_percent>=60):
            grade = "B"
        elif(total_percent<60 and total_percent>=50):
            grade = "C"
        elif(total_percent<50 and total_percent>=40):
            grade = "D"
        else:
            grade = "F"
    
    

        
            
    context = {'student':student,'quater1_math':quater1_math,'quater1_est':quater1_est,'grade':grade,
            'quater1_social':quater1_social,'quater1_kiny':quater1_kiny,'quater1_engl':quater1_engl,'total_quater1_math':total_quater1_math,
            'total_quater1_est':total_quater1_est,'total_quater1_social':total_quater1_social,'total_quater1_kiny':total_quater1_kiny,
            'total_quater1_engl':total_quater1_engl,'total_quater1':total_quater1,'total_percent':total_percent,'classe':classe,'school':school,
            'sector':sector,'n_of_students':n_of_students}
    
    
    
    html = template.render(context)
    pdf= render_to_pdf('schoolPages/studentbulletin.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "Student_%s %s in %s" %(student.f_name, student.l_name, classe)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"


@login_required(login_url='/login')
@allowed_users(allowed_roles=['secretary']) 
def studentbulletinForYear(request, pk_student):
    template = get_template('yearBulletin.html')
    promotion = ""
    student = Student.objects.get(id=pk_student)

    classe =  student.classe
    school = classe.school
    sector = school.sector
    students = Student.objects.filter(classe=classe)
    n_of_students = students.count()


    student_marks = student.student_course_set.all()
    
    quater1_math = Student_Course.objects.get(quater='QUATER1', course=1, student=student)
    
    math_mid_q1 = quater1_math.mid_marks
    math_final_q1 = quater1_math.final_marks
    
    quater2_math = Student_Course.objects.get(quater='QUATER2', course=1, student=student)
    
    math_mid_q2 = quater2_math.mid_marks
    math_final_q2 = quater2_math.final_marks
    
    quater3_math = Student_Course.objects.get(quater='QUATER3', course=1, student=student)
    
    math_mid_q3 = quater3_math.mid_marks
    math_final_q3 = quater3_math.final_marks
    
    
    quater1_est = Student_Course.objects.get(quater='QUATER1', course=2, student=student)
    
    est_mid_q1 = quater1_est.mid_marks
    est_final_q1 = quater1_est.final_marks
    
    quater2_est = Student_Course.objects.get(quater='QUATER2', course=2, student=student)
    
    est_mid_q2 = quater2_est.mid_marks
    est_final_q2 = quater2_est.final_marks
    
    quater3_est = Student_Course.objects.get(quater='QUATER3', course=2, student=student)
    
    est_mid_q3 = quater3_est.mid_marks
    est_final_q3 = quater3_est.final_marks
    
    
    
    quater1_social = Student_Course.objects.get(quater='QUATER1', course=3, student=student)
    
    social_mid_q1 = quater1_social.mid_marks
    social_final_q1 = quater1_social.final_marks
    
    quater2_social = Student_Course.objects.get(quater='QUATER2', course=3, student=student)
    
    social_mid_q2 = quater2_social.mid_marks
    social_final_q2 = quater2_social.final_marks
    
    quater3_social = Student_Course.objects.get(quater='QUATER3', course=3, student=student)
    
    social_mid_q3 = quater3_social.mid_marks
    social_final_q3 = quater3_social.final_marks
    
    
    
    quater1_kiny = Student_Course.objects.get(quater='QUATER1', course=4, student=student)
    
    kiny_mid_q1 = quater1_kiny.mid_marks
    kiny_final_q1 = quater1_kiny.final_marks
    
    quater2_kiny = Student_Course.objects.get(quater='QUATER2', course=4, student=student)
    
    kiny_mid_q2 = quater2_kiny.mid_marks
    kiny_final_q2 = quater2_kiny.final_marks
    
    quater3_kiny = Student_Course.objects.get(quater='QUATER3', course=4, student=student)
    
    kiny_mid_q3 = quater3_kiny.mid_marks
    kiny_final_q3 = quater3_kiny.final_marks
    
    
    
    quater1_engl = Student_Course.objects.get(quater='QUATER1', course=5, student=student)
    
    engl_mid_q1 = quater1_engl.mid_marks
    engl_final_q1 = quater1_engl.final_marks
    
    quater2_engl = Student_Course.objects.get(quater='QUATER2', course=5, student=student)
    
    engl_mid_q2 = quater2_engl.mid_marks
    engl_final_q2 = quater2_engl.final_marks
    
    quater3_engl = Student_Course.objects.get(quater='QUATER3', course=5, student=student)
    
    engl_mid_q3 = quater3_engl.mid_marks
    engl_final_q3 = quater3_engl.final_marks
    
    
    total_quater1_math = quater1_math.mid_marks + quater1_math.final_marks
    total_quater2_math = quater2_math.mid_marks + quater2_math.final_marks
    total_quater3_math = quater3_math.mid_marks + quater3_math.final_marks
    
    
    total_quater1_est = quater1_est.mid_marks + quater1_est.final_marks
    total_quater2_est = quater2_est.mid_marks + quater2_est.final_marks
    total_quater3_est = quater3_est.mid_marks + quater3_est.final_marks
    
    total_quater1_social = quater1_social.mid_marks + quater1_social.final_marks
    total_quater2_social = quater2_social.mid_marks + quater2_social.final_marks
    total_quater3_social = quater3_social.mid_marks + quater3_social.final_marks
    
    
    total_quater1_kiny = quater1_kiny.mid_marks + quater1_kiny.final_marks
    total_quater2_kiny = quater2_kiny.mid_marks + quater2_kiny.final_marks
    total_quater3_kiny = quater3_kiny.mid_marks + quater3_kiny.final_marks
    
    total_quater1_engl = quater1_engl.mid_marks + quater1_engl.final_marks
    total_quater2_engl = quater2_engl.mid_marks + quater2_engl.final_marks
    total_quater3_engl = quater3_engl.mid_marks + quater3_engl.final_marks
    
    
    total_quater1 = total_quater1_math+total_quater1_est+total_quater1_social+total_quater1_kiny+total_quater1_engl
    total_quater2 = total_quater2_math+total_quater2_est+total_quater2_social+total_quater2_kiny+total_quater2_engl
    total_quater3 = total_quater3_math+total_quater3_est+total_quater3_social+total_quater3_kiny+total_quater3_engl

   

    total_quater1_percent = (total_quater1 * 100)/1000
    total_quater2_percent = (total_quater2 * 100)/1000
    total_quater3_percent = (total_quater3 * 100)/1000
    
    total_year = total_quater1 + total_quater2 + total_quater3
    total_year_percent = format((total_year*100)/3000, '.2f')
    total_percentage_with_floats = (total_year*100)/3000
    if (total_percentage_with_floats>=50):
        promotion = "PASS"
    else:
        promotion = "REPEAT"


    context = {'classe':classe,'school':school,'sector':sector,'n_of_students':n_of_students,'quater1_math':quater1_math,'quater2_math':quater2_math,'quater3_math':quater1_math,'promotion':promotion,'student':student,
               'quater1_est':quater1_est,'quater2_est':quater2_est,'quater3_est':quater3_est,'quater1_social':quater1_social,'quater2_social':quater2_social,'quater3_social':quater3_social,
               'quater1_kiny':quater1_kiny,'quater2_kiny':quater2_kiny,'quater3_kiny':quater3_kiny,'quater1_engl':quater1_engl,'quater2_engl':quater2_engl,'quater3_engl':quater3_engl,
               'quater1_engl':quater1_engl,'quater2_engl':quater2_engl,'quater3_engl':quater3_engl,'total_quater1_math':total_quater1_math,'total_quater2_math':total_quater2_math,'total_quater3_math':total_quater2_math,
               'total_quater1_est':total_quater1_est,'total_quater2_est':total_quater1_est,'total_quater3_est':total_quater1_est,'total_quater1_social':total_quater1_social,'total_quater2_social':total_quater2_social,'total_quater3_social':total_quater1_social,
               'total_quater1_kiny':total_quater1_kiny,'total_quater2_kiny':total_quater2_kiny,'total_quater3_kiny':total_quater1_kiny,'total_quater1_engl':total_quater1_engl,'total_quater2_engl':total_quater2_engl,'total_quater3_engl':total_quater3_engl,
               'math_mid_q1':math_mid_q1,'math_final_q1':math_final_q1,'math_mid_q2':math_mid_q2,'math_final_q2':math_final_q2,'math_mid_q3':math_mid_q3,'math_final_q3':math_final_q3,'est_mid_q1':est_mid_q1,'est_final_q1':est_final_q1,
               'est_mid_q2':est_mid_q2,'est_final_q2':est_final_q2,'est_mid_q3':est_mid_q3,'est_final_q3':est_final_q3,'social_mid_q1':social_mid_q1,'social_final_q1':social_final_q1,
               'social_mid_q2':social_mid_q2,'social_final_q2':social_final_q2,'social_mid_q3':social_mid_q3,'social_final_q3':social_final_q3,'kiny_mid_q1':kiny_mid_q1,'kiny_final_q1':kiny_final_q1,
               'kiny_mid_q2':kiny_mid_q2,'kiny_final_q2':kiny_final_q1,'kiny_mid_q3':kiny_mid_q3,'kiny_final_q3':kiny_final_q3,'engl_mid_q1':engl_mid_q1,'engl_final_q1':engl_final_q1,'engl_mid_q2':engl_mid_q2,'engl_final_q2':engl_final_q1,
               'engl_mid_q3':engl_mid_q3,'engl_final_q3':engl_final_q3,'total_quater1':total_quater1,'total_quater1_percent':total_quater1_percent,'total_quater2':total_quater2,'total_quater2_percent':total_quater2_percent,
               'total_quater3':total_quater3,'total_quater3_percent':total_quater3_percent,'total_year':total_year,'total_year_percent':total_year_percent}

    html = template.render(context)
    pdf= render_to_pdf('yearBulletin.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "Student_%s %s in %s" %(student.f_name, student.l_name, classe)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"







def buletinOption(request, pk_student):
    
    student = Student.objects.get(id=pk_student)
    context = {'student':student}
    
    return render(request, 'schoolPages/buletinOption.html', context)

def schoolUser(request):
    user = request.user.id
    school = School.objects.get(user=user)
    schoolId = school.id
    
    classes = Classe.objects.filter(school=schoolId)
    
    context = {'user':user, 'school':school,"schoolId":schoolId,'classes':classes}
    return render(request, 'schoolUser.html', context)
@login_required(login_url='/login')
@allowed_users(allowed_roles=['district']) 
def SearchSchoolFromDistrict(request):
    no_students = 0
    now = datetime.datetime.now()
    year = now.year
    
    user = request.user.id
    district = District.objects.get(user = user)
    districtId = district.id
    
    sectors =  Sector.objects.filter(district=districtId)
    for sector in sectors:
        schools = School.objects.filter(sector=sector.id)
        for school in schools:
            classes = Classe.objects.filter(school=school.id)
            for classe in classes:
                students = Student.objects.filter(classe=classe.id)
                for student in students:
                    no_students = no_students + 1
    
    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count, count(*) from student_student inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id inner join student_sector on student_sector.id=student_school.sector_id inner join student_district on student_sector.district_id=student_district.id where student_student.year_reg=%s and student_district.id=%s" %(year, districtId)
    cursor.execute(male_female)
    answers = cursor.fetchall()
    
    sectors = Sector.objects.filter(district = districtId)
    
    context = {'sectors':sectors,'answers':answers,'district':district,'no_students':no_students}
    
    return render(request, 'districtPages/searchSchoolFromDistrict.html', context)


@login_required(login_url='/login')

def schoolReportFromDistrict(request):
    
    quater1_math25=0
    quater1_math50=0
    quater1_math75=0
    quater1_math100=0
    
    quater1_engl25=0
    quater1_engl50=0
    quater1_engl75=0
    quater1_engl100=0
    
    quater1_set25=0
    quater1_set50=0
    quater1_set75=0
    quater1_set100=0
    
    quater1_social25=0
    quater1_social50=0
    quater1_social75=0
    quater1_social100=0
    
    quater1_kiny25=0
    quater1_kiny50=0
    quater1_kiny75=0
    quater1_kiny100=0
    n_student = 0
    
    criterion1 = Q(course = 1)
    criterion2 = Q(quater='QUATER1')
    criterion3 = Q(quater='QUATER2')
    
    template = get_template('districtPages/searchedSchool.html')
    try:
        year = request.GET.get('year')
        school = request.GET.get('school')
    except:
        year= None
        school = None
    if year:
        yearToSearch = year
        if school:
            schooll = School.objects.get(id=school)
            school_id = schooll.id
            sector = schooll.sector
            district = sector.district
            classes = Classe.objects.filter(school=school_id)
            
            for classe in classes:
                students = Student.objects.filter(classe=classe.id, year_reg=year)
                for student in students:
                    n_student = n_student + 1
                    for st in student.student_course_set.filter(criterion1 & criterion2):
                        total_math = st.mid_marks + st.final_marks
                        total_math_percent = (total_math*100)/200
                        if total_math_percent<=25:
                            quater1_math25 = quater1_math25+1
                        if total_math_percent<=50 and total_math_percent>=26:
                            quater1_math50 = quater1_math50+1
                        if total_math_percent<=75 and total_math_percent>=51:
                            quater1_math75 = quater1_math75+1
                        if total_math_percent<=100 and total_math_percent>=76:
                            quater1_math100 = quater1_math100+1
                            
                    for engl in student.student_course_set.filter(course=5, quater='QUATER1'):
                        total_engl = engl.mid_marks+engl.final_marks
                        total_engl_percent = (total_engl*100)/200
                        if total_engl_percent<=25:
                            quater1_engl25 = quater1_engl25+1
                        if total_engl_percent<=50 and total_engl_percent>=26:
                            quater1_engl50 = quater1_engl50+1
                        if total_engl_percent<=75 and total_engl_percent>=51:
                            quater1_engl75 = quater1_engl75+1
                        if total_engl_percent<=100 and total_engl_percent>=76:
                            quater1_engl100 = quater1_engl100+1
                        
                    for est in student.student_course_set.filter(course=2, quater='QUATER1'):
                        total_set = est.mid_marks+est.final_marks
                        total_set_percent = (total_set*100)/200
                        if total_set_percent<=25:
                            quater1_set25 = quater1_set25+1
                        if total_set_percent<=50 and total_set_percent>=26:
                            quater1_set50 = quater1_set50+1
                        if total_set_percent<=75 and total_set_percent>=51:
                            quater1_set75 = quater1_set75+1
                        if total_set_percent<=100 and total_set_percent>=76:
                            quater1_set100 = quater1_set100+1
                        
                    for social in student.student_course_set.filter(course=3, quater='QUATER1'):
                        total_social = social.mid_marks+social.final_marks
                        total_social_percent = (total_social*100)/200
                        if total_social_percent<=25:
                            quater1_social25 = quater1_social25+1
                        if total_social_percent<=50 and total_social_percent>=26:
                            quater1_social50 = quater1_social50+1
                        if total_social_percent<=75 and total_social_percent>=51:
                            quater1_social75 = quater1_social75+1
                        if total_social_percent<=100 and total_social_percent>=76:
                            quater1_social100 = quater1_social100+1
                        
                    for kiny in student.student_course_set.filter(course=4, quater='QUATER1'):
                        total_kiny = kiny.mid_marks+kiny.final_marks
                        total_kiny_percent = (total_kiny*100)/200
                        if total_kiny_percent<=25:
                            quater1_kiny25 = quater1_kiny25+1
                        if total_kiny_percent<=50 and total_kiny_percent>=26:
                            quater1_kiny50 = quater1_kiny50+1
                        if total_kiny_percent<=75 and total_kiny_percent>=51:
                            quater1_kiny75 = quater1_kiny75+1
                        if total_kiny_percent<=100 and total_kiny_percent>=76:
                            quater1_kiny100 = quater1_kiny100+1
                    
        
            templates = 'districtPages/searchedSchool.html'
            context = {'yearToSearch':yearToSearch,'n_student':n_student,'students':students,'district':district,'sector':sector,'schooll':schooll,'quater1_math25':quater1_math25,'quater1_math50':quater1_math50,'quater1_math75':quater1_math75,'quater1_math100':quater1_math100,
                    'quater1_engl25':quater1_engl25,'quater1_engl50':quater1_engl50,'quater1_engl75':quater1_engl75,'quater1_engl100':quater1_engl100,
                    'quater1_set25':quater1_set25,'quater1_set50':quater1_set50,'quater1_set75':quater1_set75,'quater1_set100':quater1_set100,
                    'quater1_social25':quater1_social25,'quater1_social50':quater1_social50,'quater1_social75':quater1_social75,'quater1_social100':quater1_social100,
                    'quater1_kiny25':quater1_kiny25,'quater1_kiny50':quater1_kiny50,'quater1_kiny75':quater1_kiny75,'quater1_kiny100':quater1_kiny100}
            html = template.render(context)
            pdf= render_to_pdf('districtPages/searchedSchool.html', context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                file_name = "School%s %s in %s" %(schooll.id, schooll.school_name, sector)
                content = "inline; filename='%s'" %(file_name)
                download = request.GET.get("download")
                if download:
                    content = "attachment; filename='%s'" %(file_name)
                response['Content-Disposition'] = content
                return response
            return HttpResponse*"Not found"
    else:
        template = 'searchSchoolFromDistrict.html'
    return render(request, templates, context)
@login_required(login_url='/login')
@allowed_users(allowed_roles=['district']) 
def dataSchool(request):
    user = request.user.id
    district = District.objects.get(user = user)
    districtId = district.id

    sectors = Sector.objects.filter(district = districtId)
    
    sector = request.GET.get('sector')
   
    schools=School.objects.filter(sector=sector)
           
    print(schools)
    context = {'user':user,'districtId':districtId,'district':district,'sectors':sectors, 'schools':schools}
    return render(request, 'schoolData.html', context)

def dataSchool2(request):
    
    sector = request.GET.get('sector')
    
    # sector = Sector.objects.get(id=8)
    
    schools = School.objects.filter(sector=sector)
    print(schools)
    
    context = {'schools':schools}
    
    return render(request, 'schoolData2.html', context)

def dataDistrict(request):
    
    districts = District.objects.all()
    
    district = request.GET.get('district')
    sectors = Sector.objects.filter(district=district)
    
    context = {'sectors':sectors}
    
    return render(request, 'rebPages/districtData.html',context)

@login_required(login_url='/login')
@allowed_users(allowed_roles=['district']) 
def twoYearSchoolComparisonReport(request):
    n_student = 0
    try:
        school = request.GET.get('school')
        year1 = request.GET.get('year1')
        year2 = request.GET.get('year2')
    except:
        school = None
        year1 = None
        year2 = None
    if school:
        if year1:
            year1searched = year1
            if year2:
                year2searched = year2
                schooll = School.objects.get(id=school)
                school_id = schooll.id
                sector = schooll.sector
                district = sector.district
                classes = Classe.objects.filter(school=school_id)
                for classe in classes:
                    students = Student.objects.filter(classe=classe.id,year_reg=year2searched)
                
                    
                
                
                template = 'districtPages/twoYearSchoolComparison.html'
                context = {'classes':classes,'school_id':school_id,'schooll':schooll,'students':students}
    else:
        template = 'districtPages/searchSchoolFromDistrict.html'
        context = {}
                   
            
    return render(request, template, context)

def yearMark(request):
    template = get_template('yearMark.html')
    count_math_25 = 0
    count_math_50 = 0
    count_math_75 = 0
    count_math_100 = 0
    
    count_est_25 = 0
    count_est_50 = 0
    count_est_75 = 0
    count_est_100 = 0
    
    count_engl_25 = 0
    count_engl_50 = 0
    count_engl_75 = 0
    count_engl_100 = 0
    
    count_social_25 = 0
    count_social_50 = 0
    count_social_75 = 0
    count_social_100 = 0
    
    count_kiny_25 = 0
    count_kiny_50 = 0
    count_kiny_75 = 0
    count_kiny_100 = 0
    
    
    
    count_math_year1_25 = 0
    count_math_year1_50 = 0
    count_math_year1_75 = 0
    count_math_year1_100 = 0
    
    count_est_year1_25 = 0
    count_est_year1_50 = 0
    count_est_year1_75 = 0
    count_est_year1_100 = 0
    
    count_engl_year1_25 = 0
    count_engl_year1_50 = 0
    count_engl_year1_75 = 0
    count_engl_year1_100 = 0
    
    count_social_year1_25 = 0
    count_social_year1_50 = 0
    count_social_year1_75 = 0
    count_social_year1_100 = 0
    
    count_kiny_year1_25 = 0
    count_kiny_year1_50 = 0
    count_kiny_year1_75 = 0
    count_kiny_year1_100 = 0
  

    count_student_year1 = 0
    count_student_year2 = 0
    try:
        school = request.GET.get('school')
        year1 = request.GET.get('year1')
        year2 = request.GET.get('year2')
    except:
        school = None
        year1 = None
        year2 = None
        
        
        
    if year1:
        year1Searched = year1
        if year2:
            year2Searched = year2
            if school:
                schooll = School.objects.get(id=school)
                sector = schooll.sector
                district = sector.district
                school_id= schooll.id
                classes = Classe.objects.filter(school=school_id)
                number_of_classes = classes.count()
                for classe in classes:
                    students_year1 = Student.objects.filter(classe=classe.id,year_reg=year1Searched)
                    for student in students_year1:
                        count_student_year1 = count_student_year1+1
                        for math_quater1_year1 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                            total_math_quater1_year1 = math_quater1_year1.mid_marks + math_quater1_year1.final_marks
                        for est_quater1_year1 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                            total_est_quater1_year1 = est_quater1_year1.mid_marks + est_quater1_year1.final_marks
                        for social_quater1_year1 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                            total_social_quater1_year1 = social_quater1_year1.mid_marks + social_quater1_year1.final_marks
                        for kiny_quater1_year1 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                            total_kiny_quater1_year1 = kiny_quater1_year1.mid_marks + kiny_quater1_year1.final_marks
                        for engl_quater1_year1 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                            total_engl_quater1_year1 = engl_quater1_year1.mid_marks + engl_quater1_year1.final_marks
                            
                        for math_quater2_year1 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                            total_math_quater2_year1 = math_quater2_year1.mid_marks + math_quater2_year1.final_marks
                        for est_quater2_year1 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                            total_est_quater2_year1 = est_quater2_year1.mid_marks + est_quater2_year1.final_marks
                        for social_quater2_year1 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                            total_social_quater2_year1 = social_quater2_year1.mid_marks + social_quater2_year1.final_marks
                        for kiny_quater2_year1 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                            total_kiny_quater2_year1 = kiny_quater2_year1.mid_marks + kiny_quater2_year1.final_marks
                        for engl_quater2_year1 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                            total_engl_quater2_year1 = engl_quater2_year1.mid_marks + engl_quater2_year1.final_marks
                        
                        for math_quater3_year1 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                            total_math_quater3_year1 = math_quater3_year1.mid_marks + math_quater3_year1.final_marks
                        for est_quater3_year1 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                            total_est_quater3_year1 = est_quater3_year1.mid_marks + est_quater3_year1.final_marks
                        for social_quater3_year1 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                            total_social_quater3_year1 = social_quater3_year1.mid_marks + social_quater3_year1.final_marks
                        for kiny_quater3_year1 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                            total_kiny_quater3_year1 = kiny_quater3_year1.mid_marks + kiny_quater3_year1.final_marks
                        for engl_quater3_year1 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                            total_engl_quater3_year1 = engl_quater3_year1.mid_marks + engl_quater3_year1.final_marks
                            
                            total_math_year1 = total_math_quater1_year1 +total_math_quater2_year1 + total_math_quater3_year1
                            total_est_year1 = total_est_quater1_year1 + total_est_quater2_year1 + total_est_quater3_year1
                            total_social_year1 = total_social_quater1_year1 + total_social_quater2_year1 + total_social_quater3_year1
                            total_kiny_year1 = total_kiny_quater1_year1 + total_kiny_quater2_year1 + total_kiny_quater3_year1
                            total_engl_year1 = total_engl_quater1_year1 + total_engl_quater2_year1 + total_engl_quater3_year1
                            
                            total_math_year1_percent = (total_math_year1 * 100)/600
                            total_est_year1_percent = (total_est_year1 * 100)/600
                            total_social_year1_percent = (total_social_year1 * 100)/600
                            total_kiny_year1_percent = (total_kiny_year1 * 100)/600
                            total_engl_year1_percent = (total_engl_year1 * 100)/600
                            
                            if total_math_year1_percent<=25:
                                count_math_year1_25 = count_math_year1_25 + 1
                            if total_math_year1_percent<=50 and total_math_year1_percent>=26:
                                count_math_year1_50 = count_math_year1_50 + 1
                            if total_math_year1_percent<=75 and total_math_year1_percent>=51:
                                count_math_year1_75 = count_math_year1_75 + 1
                            if total_math_year1_percent<=100 and total_math_year1_percent>=76:
                                count_math_year1_100 = count_math_year1_100 + 1 
                                
                            if total_est_year1_percent<=25:
                                count_est_year1_25 = count_est_year1_25 + 1
                            if total_est_year1_percent<=50 and total_est_year1_percent>=26:
                                count_est_year1_50 = count_est_year1_50 + 1
                            if total_est_year1_percent<=75 and total_est_year1_percent>=51:
                                count_est_year1_75 = count_est_year1_75 + 1
                            if total_est_year1_percent<=100 and total_est_year1_percent>=76:
                                count_est_year1_100 = count_est_year1_100 + 1 
                                
                            if total_social_year1_percent<=25:
                                count_social_year1_25 = count_social_year1_25 + 1
                            if total_social_year1_percent<=50 and total_social_year1_percent>=26:
                                count_social_year1_50 = count_social_year1_50 + 1
                            if total_social_year1_percent<=75 and total_social_year1_percent>=51:
                                count_social_year1_75 = count_social_year1_75 + 1
                            if total_social_year1_percent<=100 and total_social_year1_percent>=76:
                                count_social_year1_100 = count_social_year1_100 + 1
                                
                            if total_kiny_year1_percent<=25:
                                count_kiny_year1_25 = count_kiny_year1_25 + 1
                            if total_kiny_year1_percent<=50 and total_kiny_year1_percent>=26:
                                count_kiny_year1_50 = count_kiny_year1_50 + 1
                            if total_kiny_year1_percent<=75 and total_kiny_year1_percent>=51:
                                count_kiny_year1_75 = count_kiny_year1_75 + 1
                            if total_kiny_year1_percent<=100 and total_kiny_year1_percent>=76:
                                count_kiny_year1_100 = count_kiny_year1_100 + 1 
                                
                            if total_engl_year1_percent<=25:
                                count_engl_year1_25 = count_engl_year1_25 + 1
                            if total_engl_year1_percent<=50 and total_engl_year1_percent>=26:
                                count_engl_year1_50 = count_engl_year1_50 + 1
                            if total_engl_year1_percent<=75 and total_engl_year1_percent>=51:
                                count_engl_year1_75 = count_engl_year1_75 + 1
                            if total_engl_year1_percent<=100 and total_engl_year1_percent>=76:
                                count_engl_year1_100 = count_engl_year1_100 + 1
                            
                            
                    students_year2 = Student.objects.filter(classe=classe.id, year_reg=year2Searched)
                    for studentt in students_year2:
                        count_student_year2 = count_student_year2+1
                        for math_quater1 in studentt.student_course_set.filter(course=1, quater = 'QUATER1'):
                            total_math_quater1_year2 = math_quater1.mid_marks + math_quater1.final_marks 
                        for est_quater1 in studentt.student_course_set.filter(course=2, quater = 'QUATER1'):
                            total_est_quater1_year2 = est_quater1.mid_marks + est_quater1.final_marks  
                        for social_quater1 in studentt.student_course_set.filter(course=3, quater = 'QUATER1'):
                            total_social_quater1_year2 = social_quater1.mid_marks + social_quater1.final_marks
                        for kiny_quater1 in studentt.student_course_set.filter(course=4, quater = 'QUATER1'):
                            total_kiny_quater1_year2 = kiny_quater1.mid_marks + kiny_quater1.final_marks 
                        for engl_quater1 in studentt.student_course_set.filter(course=5, quater = 'QUATER1'):
                            total_engl_quater1_year2 = engl_quater1.mid_marks + engl_quater1.final_marks  
                            
                        for math_quater2 in studentt.student_course_set.filter(course=1, quater = 'QUATER2'):
                            total_math_quater2_year2 = math_quater2.mid_marks + math_quater2.final_marks
                        for est_quater2 in studentt.student_course_set.filter(course=2, quater = 'QUATER2'):
                            total_est_quater2_year2 = est_quater2.mid_marks + est_quater2.final_marks
                        for social_quater2 in studentt.student_course_set.filter(course=3, quater = 'QUATER2'):
                            total_social_quater2_year2 = social_quater2.mid_marks + social_quater2.final_marks
                        for kiny_quater2 in studentt.student_course_set.filter(course=4, quater = 'QUATER2'):
                            total_kiny_quater2_year2 = kiny_quater2.mid_marks + kiny_quater2.final_marks
                        for engl_quater2 in studentt.student_course_set.filter(course=5, quater = 'QUATER2'):
                            total_engl_quater2_year2 = engl_quater2.mid_marks + engl_quater2.final_marks     
                        
                        for math_quater3 in studentt.student_course_set.filter(course=1, quater = 'QUATER3'):
                            total_math_quater3_year2 = math_quater3.mid_marks + math_quater3.final_marks
                        for est_quater3 in studentt.student_course_set.filter(course=2, quater = 'QUATER3'):
                            total_est_quater3_year2 = est_quater3.mid_marks + est_quater3.final_marks 
                        for social_quater3 in studentt.student_course_set.filter(course=3, quater = 'QUATER3'):
                            total_social_quater3_year2 = social_quater3.mid_marks + social_quater3.final_marks
                        for kiny_quater3 in studentt.student_course_set.filter(course=4, quater = 'QUATER3'):
                            total_kiny_quater3_year2 = kiny_quater3.mid_marks + kiny_quater3.final_marks 
                        for engl_quater3 in studentt.student_course_set.filter(course=5, quater = 'QUATER3'):
                            total_engl_quater3_year2 = engl_quater3.mid_marks + engl_quater3.final_marks

                                
                            total_math = total_math_quater1_year2 + total_math_quater2_year2 + total_math_quater3_year2
                            total_est = total_est_quater1_year2 + total_est_quater2_year2 + total_est_quater3_year2
                            total_social = total_social_quater1_year2 + total_social_quater2_year2 + total_social_quater3_year2
                            total_kiny = total_kiny_quater1_year2 + total_kiny_quater2_year2 + total_kiny_quater3_year2
                            total_engl = total_engl_quater1_year2 + total_engl_quater2_year2 + total_engl_quater3_year2
                            
                            
                            
                            total_math_percent = (total_math * 100)/600
                            total_est_percent = (total_est * 100)/600
                            total_social_percent = (total_social * 100)/600
                            total_kiny_percent = (total_kiny * 100)/600
                            total_engl_percent = (total_engl * 100)/600
                            
                            
                            if total_math_percent<=25:
                                count_math_25 = count_math_25 + 1
                            if total_math_percent<=50 and total_math_percent>=26:
                                count_math_50 = count_math_50 + 1
                            if total_math_percent<=75 and total_math_percent>=51:
                                count_math_75 = count_math_75 + 1
                            if total_math_percent<=100 and total_math_percent>=76:
                                count_math_100 = count_math_100 + 1   
                                
                            if total_est_percent<=25:
                                count_est_25 = count_est_25 + 1
                            if total_est_percent<=50 and total_est_percent>=26:
                                count_est_50 = count_est_50 + 1
                            if total_est_percent<=75 and total_est_percent>=51:
                                count_est_75 = count_est_75 + 1
                            if total_est_percent<=100 and total_est_percent>=76:
                                count_est_100 = count_est_100 + 1 
                                
                            if total_social_percent<=25:
                                count_social_25 = count_social_25 + 1
                            if total_social_percent<=50 and total_social_percent>=26:
                                count_social_50 = count_social_50 + 1
                            if total_social_percent<=75 and total_social_percent>=51:
                                count_social_75 = count_social_75 + 1
                            if total_social_percent<=100 and total_social_percent>=76:
                                count_social_100 = count_social_100 + 1
                                
                            if total_kiny_percent<=25:
                                count_kiny_25 = count_kiny_25 + 1
                            if total_kiny_percent<=50 and total_kiny_percent>=26:
                                count_kiny_50 = count_kiny_50 + 1
                            if total_kiny_percent<=75 and total_kiny_percent>=51:
                                count_kiny_75 = count_kiny_75 + 1
                            if total_kiny_percent<=100 and total_kiny_percent>=76:
                                count_kiny_100 = count_kiny_100 + 1 
                                
                            if total_engl_percent<=25:
                                count_engl_25 = count_engl_25 + 1
                            if total_engl_percent<=50 and total_engl_percent>=26:
                                count_engl_50 = count_engl_50 + 1
                            if total_engl_percent<=75 and total_engl_percent>=51:
                                count_engl_75 = count_engl_75 + 1
                            if total_engl_percent<=100 and total_engl_percent>=76:
                                count_engl_100 = count_engl_100 + 1 
                                
                            
                

    context = {'count_student_year1':count_student_year1,'count_student_year2':count_student_year2,'schooll':schooll,'sector':sector,'district':district,'year1Searched':year1Searched,'year2Searched':year2Searched,'count_math_25':count_math_25,'count_math_50':count_math_50,'count_math_75':count_math_75,'count_math_100':count_math_100,
               'count_est_25':count_est_25,'count_est_50':count_est_50,'count_est_75':count_est_75,'count_est_100':count_est_100,
               'count_social_25':count_social_25,'count_social_50':count_social_50,'count_social_75':count_social_75,'count_social_100':count_social_100,
               'count_kiny_25':count_kiny_25,'count_kiny_50':count_kiny_50,'count_kiny_75':count_kiny_75,'count_kiny_100':count_kiny_100,
               'count_engl_25':count_engl_25,'count_engl_50':count_engl_50,'count_engl_75':count_engl_75,'count_engl_100':count_engl_100,
               'count_math_year1_25':count_math_year1_25,'count_math_year1_50':count_math_year1_50,'count_math_year1_75':count_math_year1_75,'count_math_year1_100':count_math_year1_100,
               'count_est_year1_25':count_est_year1_25,'count_est_year1_50':count_est_year1_50,'count_est_year1_75':count_est_year1_75,'count_est_year1_100':count_est_year1_100,
               'count_social_year1_25':count_social_year1_25,'count_social_year1_50':count_social_year1_50,'count_social_year1_75':count_social_year1_75,'count_social_year1_100':count_social_year1_100,
               'count_kiny_year1_25':count_kiny_year1_25,'count_kiny_year1_50':count_kiny_year1_50,'count_kiny_year1_75':count_kiny_year1_75,'count_kiny_year1_100':count_kiny_year1_100,
               'count_engl_year1_25':count_engl_year1_25,'count_engl_year1_50':count_engl_year1_50,'count_engl_year1_75':count_engl_year1_75,'count_engl_year1_100':count_engl_year1_100}
    
    html = template.render(context)
    pdf= render_to_pdf('yearMark.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "School_%s %s in %s" %(schooll, sector, district)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

def twoSchoolComparisonSameYear(request):
    template = get_template('districtPages/twoSchoolComparison.html')
    n_student_school1 = 0
    n_student_school2 = 0
    
    math_school125 = 0
    math_school150 = 0
    math_school175 = 0
    math_school1100 = 0
    
    est_school125 = 0
    est_school150 = 0
    est_school175 = 0
    est_school1100 = 0
    
    social_school125 = 0
    social_school150 = 0
    social_school175 = 0
    social_school1100 = 0
    
    kiny_school125 = 0
    kiny_school150 = 0
    kiny_school175 = 0
    kiny_school1100 = 0
    
    engl_school125 = 0
    engl_school150 = 0
    engl_school175 = 0
    engl_school1100 = 0
    
    
    
    math_school225 = 0
    math_school250 = 0
    math_school275 = 0
    math_school2100 = 0
    
    est_school225 = 0
    est_school250 = 0
    est_school275 = 0
    est_school2100 = 0
    
    social_school225 = 0
    social_school250 = 0
    social_school275 = 0
    social_school2100 = 0
    
    kiny_school225 = 0
    kiny_school250 = 0
    kiny_school275 = 0
    kiny_school2100 = 0
    
    engl_school225 = 0
    engl_school250 = 0
    engl_school275 = 0
    engl_school2100 = 0
    
    try:
        school1 = request.GET.get('school1')
        school2 = request.GET.get('school2')
        year = request.GET.get('year')
    except:
        school1 = None
        school2 = None
        year = None
        
    if school1:
        school1Searched = school1
        school11 = School.objects.get(id=school1Searched)
        if school2:
            school2Searched = school2
            school22 = School.objects.get(id=school2Searched)
            if year:
                yearSearched = year
                
                classesSchool1 = Classe.objects.filter(school=school1Searched)
                classesSchool2 = Classe.objects.filter(school=school2Searched)
                
                for classe in classesSchool1:
                    students = Student.objects.filter(classe=classe.id, year_reg=year)
                    for student in students:
                        n_student_school1 = n_student_school1 + 1
                        for math_quater1_school1 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                            total_math_quater1_school1 = math_quater1_school1.mid_marks + math_quater1_school1.final_marks
                        for est_quater1_school1 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                            total_est_quater1_school1 = est_quater1_school1.mid_marks + est_quater1_school1.final_marks
                        for social_quater1_school1 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                            total_social_quater1_school1 = social_quater1_school1.mid_marks + social_quater1_school1.final_marks
                        for kiny_quater1_school1 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                            total_kiny_quater1_school1 = kiny_quater1_school1.mid_marks + kiny_quater1_school1.final_marks
                        for engl_quater1_school1 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                            total_engl_quater1_school1 = engl_quater1_school1.mid_marks + engl_quater1_school1.final_marks
                            
                        for math_quater2_school1 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                            total_math_quater2_school1 = math_quater2_school1.mid_marks + math_quater2_school1.final_marks
                        for est_quater2_school1 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                            total_est_quater2_school1 = est_quater2_school1.mid_marks + est_quater2_school1.final_marks
                        for social_quater2_school1 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                            total_social_quater2_school1 = social_quater2_school1.mid_marks + social_quater2_school1.final_marks
                        for kiny_quater2_school1 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                            total_kiny_quater2_school1 = kiny_quater2_school1.mid_marks + kiny_quater2_school1.final_marks
                        for engl_quater2_school1 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                            total_engl_quater2_school1 = engl_quater2_school1.mid_marks + engl_quater2_school1.final_marks
                            
                        for math_quater3_school1 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                            total_math_quater3_school1 = math_quater3_school1.mid_marks + math_quater3_school1.final_marks
                        for est_quater3_school1 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                            total_est_quater3_school1 = est_quater3_school1.mid_marks + est_quater3_school1.final_marks
                        for social_quater3_school1 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                            total_social_quater3_school1 = social_quater3_school1.mid_marks + social_quater3_school1.final_marks
                        for kiny_quater3_school1 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                            total_kiny_quater3_school1 = kiny_quater3_school1.mid_marks + kiny_quater3_school1.final_marks
                        for engl_quater3_school1 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                            total_engl_quater3_school1 = engl_quater3_school1.mid_marks + engl_quater3_school1.final_marks
                            
                            total_math_school1 = total_math_quater1_school1 + total_math_quater2_school1 + total_math_quater3_school1
                            total_est_school1 = total_est_quater1_school1 + total_est_quater2_school1 + total_est_quater3_school1
                            total_social_school1 = total_social_quater1_school1 + total_social_quater2_school1 + total_social_quater3_school1
                            total_kiny_school1 = total_kiny_quater1_school1 + total_kiny_quater2_school1 + total_kiny_quater3_school1
                            total_engl_school1 = total_engl_quater1_school1 + total_engl_quater2_school1 + total_engl_quater3_school1
                            
                            total_math_school1_percent = (total_math_school1 * 100)/600
                            total_est_school1_percent = (total_est_school1 * 100)/600
                            total_social_school1_percent = (total_social_school1 * 100)/600
                            total_kiny_school1_percent = (total_kiny_school1 * 100)/600
                            total_engl_school1_percent = (total_engl_school1 * 100)/600
                                  
                            if total_math_school1_percent <= 25:
                                math_school125 = math_school125 + 1
                            if total_math_school1_percent<=50 and total_math_school1_percent>=26:
                                math_school150 = math_school150 + 1
                            if total_math_school1_percent<=75 and total_math_school1_percent>=51:
                                  math_school175 = math_school175 + 1
                            if total_math_school1_percent<=100 and total_math_school1_percent>=76:
                                  math_school1100 = math_school1100 + 1
                                  
                            if total_est_school1_percent <= 25:
                                est_school125 = est_school125 + 1
                            if total_est_school1_percent<=50 and total_est_school1_percent>=26:
                                est_school150 = est_school150 + 1
                            if total_est_school1_percent<=75 and total_est_school1_percent>=51:
                                  est_school175 = est_school175 + 1
                            if total_est_school1_percent<=100 and total_est_school1_percent>=76:
                                  est_school1100 = est_school1100 + 1
                                  
                            if total_social_school1_percent <= 25:
                                social_school125 = social_school125 + 1
                            if total_social_school1_percent<=50 and total_social_school1_percent>=26:
                                social_school150 = social_school150 + 1
                            if total_social_school1_percent<=75 and total_social_school1_percent>=51:
                                social_school175 = social_school175 + 1
                            if total_social_school1_percent<=100 and total_social_school1_percent>=76:
                                social_school1100 = social_school1100 + 1
                                
                            if total_kiny_school1_percent <= 25:
                                kiny_school125 = kiny_school125 + 1
                            if total_kiny_school1_percent<=50 and total_kiny_school1_percent>=26:
                                kiny_school150 = kiny_school150 + 1
                            if total_kiny_school1_percent<=75 and total_kiny_school1_percent>=51:
                                kiny_school175 = kiny_school175 + 1
                            if total_kiny_school1_percent<=100 and total_kiny_school1_percent>=76:
                                kiny_school1100 = kiny_school1100 + 1
                                
                            if total_engl_school1_percent <= 25:
                                engl_school125 = engl_school125 + 1
                            if total_engl_school1_percent<=50 and total_engl_school1_percent>=26:
                                engl_school150 = engl_school150 + 1
                            if total_engl_school1_percent<=75 and total_engl_school1_percent>=51:
                                engl_school175 = engl_school175 + 1
                            if total_engl_school1_percent<=100 and total_engl_school1_percent>=76:
                                engl_school1100 = engl_school1100 + 1
                
                
                
                for classe in classesSchool2:
                    students = Student.objects.filter(classe=classe.id, year_reg=year)
                    for student in students:
                        n_student_school2 = n_student_school2 + 1
                        for math_quater1_school2 in student.student_course_set.filter(course=1, quater = 'QUATER1'):
                            total_math_quater1_school2 = math_quater1_school2.mid_marks + math_quater1_school2.final_marks
                        for est_quater1_school2 in student.student_course_set.filter(course=2, quater = 'QUATER1'):
                            total_est_quater1_school2 = est_quater1_school2.mid_marks + est_quater1_school2.final_marks
                        for social_quater1_school2 in student.student_course_set.filter(course=3, quater = 'QUATER1'):
                            total_social_quater1_school2 = social_quater1_school2.mid_marks + social_quater1_school2.final_marks
                        for kiny_quater1_school2 in student.student_course_set.filter(course=4, quater = 'QUATER1'):
                            total_kiny_quater1_school2 = kiny_quater1_school2.mid_marks + kiny_quater1_school2.final_marks
                        for engl_quater1_school2 in student.student_course_set.filter(course=5, quater = 'QUATER1'):
                            total_engl_quater1_school2 = engl_quater1_school2.mid_marks + engl_quater1_school2.final_marks
                            
                        for math_quater2_school2 in student.student_course_set.filter(course=1, quater = 'QUATER2'):
                            total_math_quater2_school2 = math_quater2_school2.mid_marks + math_quater2_school2.final_marks
                        for est_quater2_school2 in student.student_course_set.filter(course=2, quater = 'QUATER2'):
                            total_est_quater2_school2 = est_quater2_school2.mid_marks + est_quater2_school2.final_marks
                        for social_quater2_school2 in student.student_course_set.filter(course=3, quater = 'QUATER2'):
                            total_social_quater2_school2 = social_quater2_school2.mid_marks + social_quater2_school2.final_marks
                        for kiny_quater2_school2 in student.student_course_set.filter(course=4, quater = 'QUATER2'):
                            total_kiny_quater2_school2 = kiny_quater2_school2.mid_marks + kiny_quater2_school2.final_marks
                        for engl_quater2_school2 in student.student_course_set.filter(course=5, quater = 'QUATER2'):
                            total_engl_quater2_school2 = engl_quater2_school2.mid_marks + engl_quater2_school2.final_marks
                            
                        for math_quater3_school2 in student.student_course_set.filter(course=1, quater = 'QUATER3'):
                            total_math_quater3_school2 = math_quater3_school2.mid_marks + math_quater3_school2.final_marks
                        for est_quater3_school2 in student.student_course_set.filter(course=2, quater = 'QUATER3'):
                            total_est_quater3_school2 = est_quater3_school2.mid_marks + est_quater3_school2.final_marks
                        for social_quater3_school2 in student.student_course_set.filter(course=3, quater = 'QUATER3'):
                            total_social_quater3_school2 = social_quater3_school2.mid_marks + social_quater3_school2.final_marks
                        for kiny_quater3_school2 in student.student_course_set.filter(course=4, quater = 'QUATER3'):
                            total_kiny_quater3_school2 = kiny_quater3_school2.mid_marks + kiny_quater3_school2.final_marks
                        for engl_quater3_school2 in student.student_course_set.filter(course=5, quater = 'QUATER3'):
                            total_engl_quater3_school2 = engl_quater3_school2.mid_marks + engl_quater3_school2.final_marks
                            
                            total_math_school2 = total_math_quater1_school2 + total_math_quater2_school2 + total_math_quater3_school2
                            total_est_school2 = total_est_quater1_school2 + total_est_quater2_school2 + total_est_quater3_school2
                            total_social_school2 = total_social_quater1_school2 + total_social_quater2_school2 + total_social_quater3_school2
                            total_kiny_school2 = total_kiny_quater1_school2 + total_kiny_quater2_school2 + total_kiny_quater3_school2
                            total_engl_school2 = total_engl_quater1_school2 + total_engl_quater2_school2 + total_engl_quater3_school2
                            
                            total_math_school2_percent = (total_math_school2 * 100)/600
                            total_est_school2_percent = (total_est_school2 * 100)/600
                            total_social_school2_percent = (total_social_school2 * 100)/600
                            total_kiny_school2_percent = (total_kiny_school2 * 100)/600
                            total_engl_school2_percent = (total_engl_school2 * 100)/600
                                  
                            if total_math_school2_percent <= 25:
                                math_school225 = math_school225 + 1
                            if total_math_school2_percent<=50 and total_math_school2_percent>=26:
                                math_school250 = math_school250 + 1
                            if total_math_school2_percent<=75 and total_math_school2_percent>=51:
                                  math_school275 = math_school275 + 1
                            if total_math_school2_percent<=100 and total_math_school2_percent>=76:
                                  math_school2100 = math_school2100 + 1
                                  
                            if total_est_school2_percent <= 25:
                                est_school225 = est_school225 + 1
                            if total_est_school2_percent<=50 and total_est_school2_percent>=26:
                                est_school250 = est_school250 + 1
                            if total_est_school2_percent<=75 and total_est_school2_percent>=51:
                                  est_school275 = est_school275 + 1
                            if total_est_school2_percent<=100 and total_est_school2_percent>=76:
                                  est_school2100 = est_school2100 + 1
                                  
                            if total_social_school2_percent <= 25:
                                social_school225 = social_school225 + 1
                            if total_social_school2_percent<=50 and total_social_school2_percent>=26:
                                social_school250 = social_school250 + 1
                            if total_social_school2_percent<=75 and total_social_school2_percent>=51:
                                social_school275 = social_school275 + 1
                            if total_social_school2_percent<=100 and total_social_school2_percent>=76:
                                social_school2100 = social_school2100 + 1
                                
                            if total_kiny_school2_percent <= 25:
                                kiny_school225 = kiny_school225 + 1
                            if total_kiny_school2_percent<=50 and total_kiny_school2_percent>=26:
                                kiny_school250 = kiny_school250 + 1
                            if total_kiny_school2_percent<=75 and total_kiny_school2_percent>=51:
                                kiny_school275 = kiny_school275 + 1
                            if total_kiny_school2_percent<=100 and total_kiny_school2_percent>=76:
                                kiny_school2100 = kiny_school2100 + 1
                                
                            if total_engl_school2_percent <= 25:
                                engl_school225 = engl_school225 + 1
                            if total_engl_school2_percent<=50 and total_engl_school2_percent>=26:
                                engl_school250 = engl_school250 + 1
                            if total_engl_school2_percent<=75 and total_engl_school2_percent>=51:
                                engl_school275 = engl_school275 + 1
                            if total_engl_school2_percent<=100 and total_engl_school2_percent>=76:
                                engl_school2100 = engl_school2100 + 1
                
                
    context = {'n_student_school2':n_student_school2,'school11':school11,'school22':school22,'n_student_school1':n_student_school1,'n_student_school1':n_student_school1,'school1Searched':school1Searched,'school2Searched':school2Searched,'math_school125':math_school125,'math_school150':math_school150,'math_school175':math_school175,'math_school1100':math_school1100,'yearSearched':yearSearched,
               'est_school125':est_school125,'est_school150':est_school150,'est_school175':est_school175,'est_school1100':est_school1100,
               'social_school125':social_school125,'social_school150':social_school150,'social_school175':social_school175,'social_school1100':social_school1100,
               'kiny_school125':kiny_school125,'kiny_school150':kiny_school150,'kiny_school175':kiny_school175,'kiny_school1100':kiny_school1100,
               'engl_school125':engl_school125,'engl_school150':engl_school150,'engl_school175':engl_school175,'engl_school1100':engl_school1100,
               'math_school225':math_school225,'math_school250':math_school250,'math_school275':math_school275,'math_school2100':math_school2100,
               'est_school225':est_school225,'est_school250':est_school250,'est_school275':est_school275,'est_school2100':est_school2100,
               'social_school225':social_school225,'social_school250':social_school250,'social_school275':social_school275,'social_school2100':social_school2100,
               'kiny_school225':kiny_school225,'kiny_school250':kiny_school250,'kiny_school275':kiny_school275,'kiny_school2100':kiny_school2100,
               'engl_school225':engl_school225,'engl_school250':engl_school250,'engl_school275':engl_school275,'engl_school2100':engl_school2100}
    
    
    html = template.render(context)
    pdf= render_to_pdf('districtPages/twoSchoolComparison.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "School_%s and %s in %s" %(school11, school22, yearSearched)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

def twoSchoolComparisonSameYearQuater(request):
    template = get_template('districtPages/twoSchoolComparisonSameYearQuater.html')
    n_students_school1 = 0
    n_students_school2 = 0
    
    math_school1_25 = 0
    math_school1_50 = 0
    math_school1_75 = 0
    math_school1_100 = 0
    
    est_school1_25 = 0
    est_school1_50 = 0
    est_school1_75 = 0
    est_school1_100 = 0
    
    social_school1_25 = 0
    social_school1_50 = 0
    social_school1_75 = 0
    social_school1_100 = 0
    
    kiny_school1_25 = 0
    kiny_school1_50 = 0
    kiny_school1_75 = 0
    kiny_school1_100 = 0
    
    engl_school1_25 = 0
    engl_school1_50 = 0
    engl_school1_75 = 0
    engl_school1_100 = 0
    
    
    math_school2_25 = 0
    math_school2_50 = 0
    math_school2_75 = 0
    math_school2_100 = 0
    
    est_school2_25 = 0
    est_school2_50 = 0
    est_school2_75 = 0
    est_school2_100 = 0
    
    social_school2_25 = 0
    social_school2_50 = 0
    social_school2_75 = 0
    social_school2_100 = 0
    
    kiny_school2_25 = 0
    kiny_school2_50 = 0
    kiny_school2_75 = 0
    kiny_school2_100 = 0
    
    engl_school2_25 = 0
    engl_school2_50 = 0
    engl_school2_75 = 0
    engl_school2_100 = 0
    
    try:
        school1 = request.GET.get('school1')
        school2 = request.GET.get('school2')
        year = request.GET.get('year')
        quater = request.GET.get('quater')
    except:
        school1 = None
        school2 = None
        year = None
        quater = None
        
    if school1:
        school1Searched = School.objects.get(id=school1)
        classes1 = Classe.objects.filter(school=school1)
        if school2:
            school2Searched = School.objects.get(id=school2)
            classes2 = Classe.objects.filter(school=school2)
            if year:
                yearSearched = year
                if quater:
                    quaterSearched = quater
                    
                    for classe in classes1:
                        students  = Student.objects.filter(classe=classe.id, year_reg=yearSearched)
                        for student in students:
                            n_students_school1 = n_students_school1+1
                            for math_quater_school1 in student.student_course_set.filter(course=1, quater=quaterSearched):
                                total_math_quater_school1 = math_quater_school1.mid_marks + math_quater_school1.final_marks
                            for est_quater_school1 in student.student_course_set.filter(course=2, quater=quaterSearched):
                                total_est_quater_school1 = est_quater_school1.mid_marks + est_quater_school1.final_marks
                            for social_quater_school1 in student.student_course_set.filter(course=3, quater=quaterSearched):
                                total_social_quater_school1 = social_quater_school1.mid_marks + social_quater_school1.final_marks
                            for kiny_quater_school1 in student.student_course_set.filter(course=4, quater=quaterSearched):
                                total_kiny_quater_school1 = kiny_quater_school1.mid_marks + kiny_quater_school1.final_marks
                            for engl_quater_school1 in student.student_course_set.filter(course=5, quater=quaterSearched):
                                total_engl_quater_shool1 = engl_quater_school1.mid_marks + engl_quater_school1.final_marks
                                
                                total_math_quater_school1_percent = (total_math_quater_school1 * 100)/200
                                total_est_quater_school1_percent = (total_est_quater_school1 * 100)/200
                                total_social_quater_school1_percent = (total_social_quater_school1 * 100)/200
                                total_kiny_quater_school1_percent = (total_kiny_quater_school1 * 100)/200
                                total_engl_quater_shool1_percent = (total_engl_quater_shool1 * 100)/200
                                
                                if total_math_quater_school1_percent<=25:
                                    math_school1_25 = math_school1_25+1
                                if total_math_quater_school1_percent<=50 and total_math_quater_school1_percent>=26:
                                    math_school1_50 = math_school1_50+1
                                if total_math_quater_school1_percent<=75 and total_math_quater_school1_percent>=51:
                                    math_school1_75 = math_school1_75+1
                                if total_math_quater_school1_percent<=100 and total_math_quater_school1_percent>=76:
                                    math_school1_100 = math_school1_100+1
                                    
                                if total_est_quater_school1_percent<=25:
                                    est_school1_25 = est_school1_25+1
                                if total_est_quater_school1_percent<=50 and total_est_quater_school1_percent>=26:
                                   est_school1_50 = est_school1_50+1
                                if total_est_quater_school1_percent<=75 and total_est_quater_school1_percent>=51:
                                    est_school1_75 = est_school1_75+1
                                if total_est_quater_school1_percent<=100 and total_est_quater_school1_percent>=76:
                                    est_school1_100 = est_school1_100+1
                                    
                                if total_social_quater_school1_percent<=25:
                                    social_school1_25 = social_school1_25+1
                                if total_social_quater_school1_percent<=50 and total_social_quater_school1_percent>=26:
                                   social_school1_50 = social_school1_50+1
                                if total_social_quater_school1_percent<=75 and total_social_quater_school1_percent>=51:
                                    social_school1_75 = social_school1_75+1
                                if total_social_quater_school1_percent<=100 and total_social_quater_school1_percent>=76:
                                    social_school1_100 = social_school1_100+1
                                    
                                if total_kiny_quater_school1_percent<=25:
                                    kiny_school1_25 = kiny_school1_25+1
                                if total_kiny_quater_school1_percent<=50 and total_kiny_quater_school1_percent>=26:
                                   kiny_school1_50 = kiny_school1_50+1
                                if total_kiny_quater_school1_percent<=75 and total_kiny_quater_school1_percent>=51:
                                    kiny_school1_75 = kiny_school1_75+1
                                if total_kiny_quater_school1_percent<=100 and total_kiny_quater_school1_percent>=76:
                                    kiny_school1_100 = kiny_school1_100+1
                                    
                                if total_engl_quater_shool1_percent<=25:
                                    engl_school1_25 = engl_school1_25+1
                                if total_engl_quater_shool1_percent<=50 and total_engl_quater_shool1_percent>=26:
                                   engl_school1_50 = engl_school1_50+1
                                if total_engl_quater_shool1_percent<=75 and total_engl_quater_shool1_percent>=51:
                                    engl_school1_75 = engl_school1_75+1
                                if total_engl_quater_shool1_percent<=100 and total_engl_quater_shool1_percent>=76:
                                    engl_school1_100 = engl_school1_100+1
                                
                                
                                
                                
                    for classe in classes2:
                        students  = Student.objects.filter(classe=classe.id, year_reg=yearSearched)
                        for student in students:
                            n_students_school2 = n_students_school2+1
                            for math_quater_school2 in student.student_course_set.filter(course=1, quater=quaterSearched):
                                total_math_quater_school2 = math_quater_school2.mid_marks + math_quater_school2.final_marks
                            for est_quater_school2 in student.student_course_set.filter(course=2, quater=quaterSearched):
                                total_est_quater_school2 = est_quater_school2.mid_marks + est_quater_school2.final_marks
                            for social_quater_school2 in student.student_course_set.filter(course=3, quater=quaterSearched):
                                total_social_quater_school2 = social_quater_school2.mid_marks + social_quater_school2.final_marks
                            for kiny_quater_school2 in student.student_course_set.filter(course=4, quater=quaterSearched):
                                total_kiny_quater_school2 = kiny_quater_school2.mid_marks + kiny_quater_school2.final_marks
                            for engl_quater_school2 in student.student_course_set.filter(course=5, quater=quaterSearched):
                                total_engl_quater_school2 = engl_quater_school2.mid_marks + engl_quater_school2.final_marks
                            
                            
                                total_math_quater_school2_percent = (total_math_quater_school2 * 100)/200
                                total_est_quater_school2_percent = (total_est_quater_school2 * 100)/200
                                total_social_quater_school2_percent = (total_social_quater_school2 * 100)/200
                                total_kiny_quater_school2_percent = (total_kiny_quater_school2 * 100)/200
                                total_engl_quater_shool2_percent = (total_engl_quater_school2 * 100)/200
                                
                                if total_math_quater_school2_percent<=25:
                                    math_school2_25 = math_school2_25+1
                                if total_math_quater_school2_percent<=50 and total_math_quater_school2_percent>=26:
                                    math_school2_50 = math_school2_50+1
                                if total_math_quater_school2_percent<=75 and total_math_quater_school2_percent>=51:
                                    math_school2_75 = math_school2_75+1
                                if total_math_quater_school2_percent<=100 and total_math_quater_school2_percent>=76:
                                    math_school2_100 = math_school2_100+1
                                    
                                if total_est_quater_school2_percent<=25:
                                    est_school2_25 = est_school2_25+1
                                if total_est_quater_school2_percent<=50 and total_est_quater_school2_percent>=26:
                                   est_school2_50 = est_school2_50+1
                                if total_est_quater_school2_percent<=75 and total_est_quater_school2_percent>=51:
                                    est_school2_75 + est_school2_75+1
                                if total_est_quater_school2_percent<=100 and total_est_quater_school2_percent>=76:
                                    est_school2_100 = est_school2_100+1
                                    
                                if total_social_quater_school2_percent<=25:
                                    social_school2_25 = social_school2_25+1
                                if total_social_quater_school2_percent<=50 and total_social_quater_school2_percent>=26:
                                   social_school2_50 = social_school2_50+1
                                if total_social_quater_school2_percent<=75 and total_social_quater_school2_percent>=51:
                                    social_school2_75 = social_school2_75+1
                                if total_social_quater_school2_percent<=100 and total_social_quater_school2_percent>=76:
                                    social_school2_100 = social_school2_100+1
                                    
                                if total_kiny_quater_school2_percent<=25:
                                    kiny_school2_25 = kiny_school2_25+1
                                if total_kiny_quater_school2_percent<=50 and total_kiny_quater_school2_percent>=26:
                                   kiny_school2_50 = kiny_school2_50+1
                                if total_kiny_quater_school2_percent<=75 and total_kiny_quater_school2_percent>=51:
                                    kiny_school2_75 = kiny_school2_75+1
                                if total_kiny_quater_school2_percent<=100 and total_kiny_quater_school2_percent>=76:
                                    kiny_school2_100 = kiny_school2_100+1
                                    
                                if total_engl_quater_shool2_percent<=25:
                                    engl_school2_25 = engl_school2_25+1
                                if total_engl_quater_shool2_percent<=50 and total_engl_quater_shool2_percent>=26:
                                   engl_school2_50 = engl_school2_50+1
                                if total_engl_quater_shool2_percent<=75 and total_engl_quater_shool2_percent>=51:
                                    engl_school2_75 = engl_school2_75+1
                                if total_engl_quater_shool2_percent<=100 and total_engl_quater_shool2_percent>=76:
                                    engl_school2_100 = engl_school2_100+1
                    
    context = {'n_students_school1':n_students_school1,'n_students_school2':n_students_school2,'classes1':classes1,'classes2':classes2,'school1Searched':school1Searched,'school2Searched':school2Searched,'yearSearched':yearSearched,'quaterSearched':quaterSearched,
               'math_school1_25':math_school1_25,'math_school1_50':math_school1_50,'math_school1_75':math_school1_75,'math_school1_100':math_school1_100,
               'est_school1_25':est_school1_25,'est_school1_50':est_school1_50,'est_school1_75':est_school1_75,'est_school1_100':est_school1_100,
               'social_school1_25':social_school1_25,'social_school1_50':social_school1_50,'social_school1_75':social_school1_75,'social_school1_100':social_school1_100,
               'kiny_school1_25':kiny_school1_25,'kiny_school1_50':kiny_school1_50,'kiny_school1_75':kiny_school1_75,'kiny_school1_100':kiny_school1_100,
               'engl_school1_25':engl_school1_25,'engl_school1_50':engl_school1_50,'engl_school1_75':engl_school1_75,'engl_school1_100':engl_school1_100,
               'math_school2_25':math_school2_25,'math_school2_50':math_school2_50,'math_school2_75':math_school2_75,'math_school2_100':math_school2_100,
               'est_school2_25':est_school2_25,'est_school2_50':est_school2_50,'est_school2_75':est_school2_75,'est_school2_100':est_school2_100,
               'social_school2_25':social_school2_25,'social_school2_50':social_school2_50,'social_school2_75':social_school2_75,'social_school2_100':social_school2_100,
               'kiny_school2_25':kiny_school2_25,'kiny_school2_50':kiny_school2_50,'kiny_school2_75':kiny_school2_75,'kiny_school2_100':kiny_school2_100,
               'engl_school2_25':engl_school2_25,'engl_school2_50':engl_school2_50,'engl_school2_75':engl_school2_75,'engl_school2_100':engl_school2_100}
    
    html = template.render(context)
    pdf= render_to_pdf('districtPages/twoSchoolComparisonSameYearQuater.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "School_%s and %s in %s at %s" %(school1Searched, school1Searched, yearSearched, quaterSearched)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"


def accountSchoolSettings(request):
    school = request.user.school
    form = SchoolForm(instance=school)
    
    if request.method == 'POST':
        form = SchoolForm(request.POST, request.FILES, instance=school)
        if form.is_valid:
            form.save()
    
    context = {'form':form}
    return render(request, 'schoolPages/accountSchoolSettings.html', context)

def accountSectorSettings(request):
    sector = request.user.sector
    form = SectorForm(instance=sector)
    
    if request.method == 'POST':
        form = SectorForm(request.POST, request.FILES, instance=sector)
        if form.is_valid:
            form.save()
    
    context = {'form':form}
    return render(request, 'sectorPages/accountSectorSettings.html', context)

def accountDistrictSettings(request):
    district = request.user.district
    form = DistrictForm(instance=district)
    
    if request.method == 'POST':
        form = SectorForm(request.POST, request.FILES, instance=district)
        if form.is_valid:
            form.save()
    
    context = {'form':form}
    return render(request, 'districtPages/accountDistrictSettings.html', context)

@unauthenticated_user
def addSchoolUser(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            messages.success(request,'Account has been Created Successfully of ' +username)
            
            # send_mail(
            #     'Subject here',
            #     'Here is the message.',
            #     'pndungutse1@gmail.com',
            #     ['pndungutse1@gmail.com'],
            #     fail_silently=False,
            # )
             #  log the user in
            # school_create(request, user)
            return redirect('school_create')
    else:
        form = RegistrationForm()
    return render(request, 'sectorPages/signupSchoolUser.html', { 'form': form })

@unauthenticated_user
def addSectorUser(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,'Account has been Created Successfully of ' +username)
             #  log the user in
            # sector_create(request, user)
            return redirect('sector_create')
    else:
        form = RegistrationForm()
    return render(request, 'districtPages/signupSectorUser.html', { 'form': form })

@unauthenticated_user
def addDistrictUser(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,'Account has been Created Successfully of ' +username)
             #  log the user in
            # sector_create(request, user)
            return redirect('district_create')
    else:
        form = RegistrationForm()
    return render(request, 'rebPages/signupDistrictUser.html', { 'form': form })  

def enterMarks(request):
    
    Student_CourseFormSet = inlineformset_factory(Student.objects.filter(classe=4), Student_Course, fields=('student','course','quater','mid_marks','final_marks'),max_num=Student.objects.filter(classe=4).count(), extra=Student.objects.filter(classe=4).count())
    formset = Student_CourseFormSet(instance=Student.objects.filter(classe=4))
    if request.method == 'POST':
        form = StudentCourseForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('home_school')
    
    context = {'formset':formset}
    
    
    return render(request,'schoolPages/enterMarks.html',context)

def schoolAvgMarkFormSector(request):

    template = get_template('sectorPages/schoolAvgMark.html')
    user = request.user
    sector = Sector.objects.get(user=user)
    sector_id = sector.id
    
    try:
        year = request.GET.get("year")
    except:
        year = None
        
    if year:
        yearSearched = year
        cursor = connection.cursor()
        course_marks = "select student_school.school_name, avg(student_student_course.final_marks), sum(student_student_course.final_marks) as final_exam, sum(student_student_course.mid_marks) as mid_exam from student_student_course inner join student_student on student_student.id=student_student_course.student_id inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id where student_school.sector_id=%s and student_student.year_reg=%s group by student_school.school_name order by avg(student_student_course.final_marks) desc " %(sector_id, yearSearched)
        cursor.execute(course_marks)
        answers = cursor.fetchall()

    context = {'course_marks':course_marks,'answers':answers,'sector':sector,'yearSearched':yearSearched}
    html = template.render(context)
    pdf= render_to_pdf('sectorPages/schoolAvgMark.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "Schools_List Bases on Performance in %s year %s" %(sector, yearSearched)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

def schoolAvgMarkFormDistrict(request):
    template = get_template('districtPages/schoolAvgMarkFromDistrict.html')
    user = request.user
    district = District.objects.get(user=user)
    district_id = district.id
    
    try:
        year = request.GET.get("year")
    except:
        year = None
        
    if year:
        yearSearched = year
        cursor = connection.cursor()
        course_marks = "select student_school.school_name, avg(student_student_course.final_marks), sum(student_student_course.final_marks) as final_exam, sum(student_student_course.mid_marks) as mid_exam from student_student_course inner join student_student on student_student.id=student_student_course.student_id inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id inner join student_sector on student_sector.id=student_school.sector_id inner join student_district on student_district.id=student_sector.district_id where student_district.id=%s and student_student.year_reg=%s group by student_school.school_name order by avg(student_student_course.final_marks) desc" %(district_id, yearSearched)
        cursor.execute(course_marks)
        answers = cursor.fetchall()

    context = {'course_marks':course_marks,'answers':answers,'yearSearched':yearSearched,'district':district}
    html = template.render(context)
    pdf= render_to_pdf('districtPages/schoolAvgMarkFromDistrict.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "Schools_List Bases on Performance in %s year %s" %(district, yearSearched)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector'])
def male_femeleSectorPdf(request):
    template = get_template('sectorPages/male_femaleSectorPdf.html')
    n_students = 0
    user = request.user
    sector = Sector.objects.get(user=user)
    sectorId = sector.id
    schools = School.objects.filter(sector=sectorId)

    now = datetime.datetime.now()
    year = now.year

    for school in schools:
        classes = Classe.objects.filter(school=school.id)
        for classe in classes:
            students = Student.objects.filter(classe=classe.id, year_reg=year)
            for student in students:
                n_students = n_students + 1

    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count from student_student inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id inner join student_sector on student_sector.id=student_school.sector_id where student_student.year_reg=%s and student_sector.id=%s" %(year,sectorId)
    cursor.execute(male_female)
    answers = cursor.fetchall()

    context = {'answers':answers,'sector':sector,'n_students':n_students}
    html = template.render(context)
    pdf= render_to_pdf('sectorPages/male_femaleSectorPdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "Sector %s Male and Female Participating" %(sector)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

@login_required(login_url='/login')
@allowed_users(allowed_roles=['sector'])
def physicalSectorPdf(request):
    template = get_template('sectorPages/physicalSectorPdf.html')
    n_students = 0
    user = request.user
    sector = Sector.objects.get(user=user)
    sectorId = sector.id
    schools = School.objects.filter(sector=sectorId)

    now = datetime.datetime.now()
    year = now.year

    for school in schools:
        classes = Classe.objects.filter(school=school.id)
        for classe in classes:
            students = Student.objects.filter(classe=classe.id, year_reg=year)
            for student in students:
                n_students = n_students + 1

    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count from student_student inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id inner join student_sector on student_sector.id=student_school.sector_id where student_student.year_reg=%s and student_sector.id=%s" %(year,sectorId)
    cursor.execute(male_female)
    answers = cursor.fetchall()

    context = {'answers':answers,'sector':sector,'n_students':n_students}
    html = template.render(context)
    pdf= render_to_pdf('sectorPages/physicalSectorPdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "Sector %s Physical Disability and Physical Ability Participating" %(sector)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

@login_required(login_url='/login')
@allowed_users(allowed_roles=['district']) 
def male_femaleDistrict(request):
    template = get_template('districtPages/male_femaleDistrict.html')

    no_students = 0
    now = datetime.datetime.now()
    year = now.year
    
    user = request.user.id
    district = District.objects.get(user = user)
    districtId = district.id
    
    sectors =  Sector.objects.filter(district=districtId)
    for sector in sectors:
        schools = School.objects.filter(sector=sector.id)
        for school in schools:
            classes = Classe.objects.filter(school=school.id)
            for classe in classes:
                students = Student.objects.filter(classe=classe.id, year_reg=year)
                for student in students:
                    no_students = no_students + 1
    
    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count, count(*) from student_student inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id inner join student_sector on student_sector.id=student_school.sector_id inner join student_district on student_sector.district_id=student_district.id where student_student.year_reg=%s and student_district.id=%s" %(year, districtId)
    cursor.execute(male_female)
    answers = cursor.fetchall()
    
    sectors = Sector.objects.filter(district = districtId)
    
    context = {'sectors':sectors,'answers':answers,'district':district,'no_students':no_students}
    html = template.render(context)
    pdf= render_to_pdf('districtPages/male_femaleDistrict.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "District %s Male and Female Participating" %(district)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

@login_required(login_url='/login')
@allowed_users(allowed_roles=['district']) 
def physicalDistrict(request):
    template = get_template('districtPages/physicalDistrict.html')

    no_students = 0
    now = datetime.datetime.now()
    year = now.year
    
    user = request.user.id
    district = District.objects.get(user = user)
    districtId = district.id
    
    sectors =  Sector.objects.filter(district=districtId)
    for sector in sectors:
        schools = School.objects.filter(sector=sector.id)
        for school in schools:
            classes = Classe.objects.filter(school=school.id)
            for classe in classes:
                students = Student.objects.filter(classe=classe.id, year_reg=year)
                for student in students:
                    no_students = no_students + 1
    
    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count, count(*) from student_student inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id inner join student_sector on student_sector.id=student_school.sector_id inner join student_district on student_sector.district_id=student_district.id where student_student.year_reg=%s and student_district.id=%s" %(year, districtId)
    cursor.execute(male_female)
    answers = cursor.fetchall()
    
    sectors = Sector.objects.filter(district = districtId)
    
    context = {'sectors':sectors,'answers':answers,'district':district,'no_students':no_students}
    html = template.render(context)
    pdf= render_to_pdf('districtPages/physicalDistrict.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "District %s Male and Female Participating" %(district)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

@login_required(login_url='/login')
@user_passes_test(lambda u: u.is_superuser)
def male_femaleReb(request):
    template = get_template('rebPages/male_femaleReb.html')

    no_students = 0
    now = datetime.datetime.now()
    year = now.year
    

    
    districts = District.objects.all()
    for district in districts:
        sectors = Sector.objects.filter(district=district.id)
        for sector in sectors:
            schools = School.objects.filter(sector=sector)
            for school in schools:
                classes = Classe.objects.filter(school=school.id)
                for classe in classes:
                    students = Student.objects.filter(classe=classe.id, year_reg=year)
                    for student in students:
                        no_students = no_students + 1
    
    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count, count(*) from student_student where student_student.year_reg=%s" %year
    cursor.execute(male_female)
    answers = cursor.fetchall()
    
    context = {'answers':answers,'districts':districts,'no_students':no_students}
    html = template.render(context)
    pdf= render_to_pdf('rebPages/male_femaleReb.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "REB Male and Female Participating"
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

@login_required(login_url='/login')
@user_passes_test(lambda u: u.is_superuser)
def physicalReb(request):
    template = get_template('rebPages/physicalReb.html')

    no_students = 0
    now = datetime.datetime.now()
    year = now.year
    

    
    districts = District.objects.all()
    for district in districts:
        sectors = Sector.objects.filter(district=district.id)
        for sector in sectors:
            schools = School.objects.filter(sector=sector)
            for school in schools:
                classes = Classe.objects.filter(school=school.id)
                for classe in classes:
                    students = Student.objects.filter(classe=classe.id, year_reg=year)
                    for student in students:
                        no_students = no_students + 1
    
    
    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count, count(*) from student_student where student_student.year_reg=%s" %year
    cursor.execute(male_female)
    answers = cursor.fetchall()
    
    context = {'answers':answers,'districts':districts, 'no_students':no_students}
    html = template.render(context)
    pdf= render_to_pdf('rebPages/physicalReb.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "REB Male and Female Participating"
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"

def testChart(request):
    
    context = {}
    return render(request, 'testChart.html',context)


def testHighCharts(request):
    
    context = {}
    return render(request, 'testHighCharts.html', context)

def schoolGenderPdf(request):
    template = get_template('schoolPages/schoolGenderPdf.html')
    n_students = 0
    user = request.user
    school = School.objects.get(user = user)
    school_id = school.id
    classes = Classe.objects.filter(school=school_id)

    now = datetime.datetime.now()
    year = now.year

    for classe in classes:
        students = Student.objects.filter(classe=classe.id, year_reg=year)
        for student in students:
            n_students = n_students + 1

    
    
    courses = Course.objects.all()

    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count, count(*) as n_students from student_student inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id where student_student.year_reg=%s and student_school.id=%s" %(year, school_id)
    cursor.execute(male_female)
    answers2 = cursor.fetchall()
    context= {'answers2':answers2, 'school':school,'n_students':n_students}

    html = template.render(context)
    pdf= render_to_pdf('schoolPages/schoolGenderPdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "School %s Male and Female Participating" %(school)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"
    
def schoolPhysicalPdf(request):
    template = get_template('schoolPages/schoolPhysicalPdf.html')
    n_students = 0
    user = request.user
    school = School.objects.get(user = user)
    school_id = school.id
    classes = Classe.objects.filter(school=school_id)

    now = datetime.datetime.now()
    year = now.year

    for classe in classes:
        students = Student.objects.filter(classe=classe.id, year_reg=year)
        for student in students:
            n_students = n_students + 1

 

    cursor = connection.cursor()
    male_female = "select sum(case when gender='M' then 1 else 0 end) as male_count,sum(case when gender='F' then 1 else 0 end) as female_count, sum(case when physical_disability='YES' then 1 else 0 end) as disability_count,sum(case when physical_disability='NO' then 1 else 0 end) as no_disability_count, count(*) as n_students from student_student inner join student_classe on student_classe.id=student_student.classe_id inner join student_school on student_school.id=student_classe.school_id where student_student.year_reg=%s and student_school.id=%s" %(year, school_id)
    cursor.execute(male_female)
    answers2 = cursor.fetchall()
    context= {'answers2':answers2, 'school':school,'n_students':n_students}

    html = template.render(context)
    pdf= render_to_pdf('schoolPages/schoolPhysicalPdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = "School %s Physical Disability and Physical Ability Participating" %(school)
        content = "inline; filename='%s'" %(file_name)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(file_name)
        response['Content-Disposition'] = content
        return response
    return HttpResponse*"Not found"
    