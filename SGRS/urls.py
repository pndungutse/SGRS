"""SGRS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

from student.views import physicalReb,male_femaleReb,physicalDistrict,male_femaleDistrict,physicalSectorPdf,schoolPhysicalPdf,schoolGenderPdf,testHighCharts,testChart,male_femeleSectorPdf,class_delete,classWithQuaterMarks,schoolAvgFromSchool,schoolAvgMarkFormDistrict,dataSchool2,schoolAvgMarkFormSector,enterMarks,addDistrictUser,addSectorUser,dataDistrict,rebStatisticalReport,district_delete,district_create,district_update,districtList,rebPage,addSchoolUser,course_update,school_update,school_create,classeList,schoolList,sectorList,courseList,studentList,schoolYearComparisonFromSector,schoolsComparisonFromSector,schoolReportFromSectorQuater,schoolReportFromSectorYear,schoolQuaterReport,schoolTwoYearReport,schoolStatisticalReportYear,schoolStatisticalReport,twoSchoolComparisonSameYearQuater,twoSchoolComparisonSameYear,studentbulletinForYear,loginOrg,accountDistrictSettings,accountSectorSettings,accountSchoolSettings,yearMark,twoYearSchoolComparisonReport,schoolReportFromDistrict,dataSchool,SearchSchoolFromDistrict,schoolUser,buletinOption,studentbulletin,goToLogin,viewSchoolReport,schoolReportFromSector,schoolPage,districtPage,sectorPage,searchClass,view401,sector_create,sector_delete,school_create,school_delete,classe_create,class_update,student_create,student_update,student_delete,course_create,home_view, login_view,logout_view,signup_view,school,classe,student,createStudentCourse,student_course_update,student_course_delete,createClass
urlpatterns = [
    path('admin/', admin.site.urls), 
    # path('', home_view, name='home'),
    path('', login_view, name='login_view'),
    path('401', view401, name='401'),
    # path('dashboard',dashboard, name='dashboard'),
    path('district_create', district_create, name="district_create"),
    path('sector_create', sector_create, name='sector_create'),
    path('sectorList',sectorList,name='sectorList'),
    path('sector_update/<int:id>/', sector_create, name='sector_update'),
    path('sector_delete/<int:id>/', sector_delete, name='sector_delete'),
    path('school_delete/<int:id>/', school_delete, name='school_delete'),
    path('school_create', school_create, name='school_create'),
    path('school_update/<str:pk_school>', school_update, name='school_update'),
    path('classe_create', classe_create, name='classe_create'),
    path('class_update/<str:pk_class>',class_update, name='class_update'),
    path('class_delete/<str:id>',class_delete, name='class_delete'),

    
    path('student_create', student_create, name='student_create'),
    path('studentList',studentList,name='studentList'),
    path('courseList',courseList,name='courseList'),
    path('class/student_update/<str:pk_student>',student_update, name='student_update'),
    path('student_delete/<str:pk_student>',student_delete, name='student_delete'),
    path('course_create', course_create, name='course_create'),
    path('course_update/<str:pk_course>',course_update,name='course_update'),
    # path('student_course_list', student_course_list, name='student_course_list')
    # path('signup/', views.signup_view, name='signup'),
    path('login', login_view, name="login"),
    path('logout', logout_view, name='logout'),
    path('signup', signup_view, name='signup'),
    path('school/<str:pk_school>',school, name='school'),
    path('schoolList',schoolList,name='schoolList'),
    path('class/<str:pk_class>',classe, name='class'),
    
    path('classeList',classeList, name='classeList'),
    
    path('searchClass/',searchClass,name='searchClass'),
    path('search/student/<str:pk_student>',student,name='student'),
    path('createStudentCourse/<str:pk_student>', createStudentCourse, name='createStudentCourse'),
    path('student_course_update/<str:pk_student_course>', student_course_update, name='student_course_update'),
    path('student_course_delete/<str:pk_student_course>',student_course_delete,name='student_course_delete'),
    path('createClass/<str:pk_class>', createClass, name='createClass'),
    
    path('sectorPage',sectorPage, name='sectorPage'),
    
    path('districtPage',districtPage,name='districtPage'),
    
    path('schoolPage',schoolPage,name='schoolPage'),
    path('schoolStatisticalReport',schoolStatisticalReport, name='schoolStatisticalReport'),
    
    # path('studentbulletinnn/<str:pk_student>',studentbulletinnn, name='studentbulletinnn'),
    path('sectorSchoolReport',schoolReportFromSector, name='sectorSchoolReport'),
    path('schoolReportFromSectorYear',schoolReportFromSectorYear,name='schoolReportFromSectorYear'),
    path('schoolReportFromSectorQuater',schoolReportFromSectorQuater,name='schoolReportFromSectorQuater'),
    path('schoolsComparisonFromSector',schoolsComparisonFromSector,name='schoolsComparisonFromSector'),
    path('schoolYearComparisonFromSector',schoolYearComparisonFromSector,name='schoolYearComparisonFromSector'),
    
    path('viewSchoolReport/',viewSchoolReport, name='viewSchoolReport'),
    # path('tryinlineformsetlist',tryinlineformsetlist, name='tryinlineformsetlist'),
    path('goToLogin',goToLogin, name='goToLogin'),
    path('studentbulletin/<str:pk_student>', studentbulletin, name='studentbulletin'),
    path('class/student/buletinOption/<str:pk_student>', buletinOption, name='buletinOption'),
    path('schoolUser', schoolUser, name='schoolUser'),
    path('SearchSchoolFromDistrict', SearchSchoolFromDistrict, name='SearchSchoolFromDistrict'),
    path('schoolReportFromDistrict', schoolReportFromDistrict, name='schoolReportFromDistrict'),
    path('dataSchool',dataSchool, name='dataSchool'),
    path('dataSchool2',dataSchool2, name='dataSchool2'),
    path('twoYearSchoolComparisonReport',twoYearSchoolComparisonReport, name='twoYearSchoolComparisonReport'),
    path('yearMark',yearMark, name='yearMark'),
    path('schoolPages/accountSchoolSettings',accountSchoolSettings,name='accountSchoolSettings'),
    path('accountSectorSettings',accountSectorSettings, name='accountSectorSettings'),
    path('accountDistrictSettings', accountDistrictSettings, name='accountDistrictSettings'),
    path('loginOrg',loginOrg, name='loginOrg'),
    
    path('studentbulletinForYear/<str:pk_student>',studentbulletinForYear, name='studentbulletinForYear'),
    path('twoSchoolComparisonSameYear',twoSchoolComparisonSameYear,name='twoSchoolComparisonSameYear'),
    path('twoSchoolComparisonSameYearQuater',twoSchoolComparisonSameYearQuater,name='twoSchoolComparisonSameYearQuater'),
    path('schoolStatisticalReportYear',schoolStatisticalReportYear,name='schoolStatisticalReportYear'),
    path('schoolTwoYearReport',schoolTwoYearReport,name='schoolTwoYearReport'),
    path('schoolQuaterReport',schoolQuaterReport,name='schoolQuaterReport'),
    path('addSchoolUser',addSchoolUser,name='addSchoolUser'),
    
    path('rebPage',rebPage, name='rebPage'),
    path('districtList',districtList,name='districtList'),
    path('district_update/<str:pk_district>',district_update,name='district_update'),
    path('district_delete/<str:id>',district_delete,name='district_delete'),
    path('rebStatisticalReport',rebStatisticalReport,name='rebStatisticalReport'),
    path('dataDistrict',dataDistrict,name='dataDistrict'),
    path('addSectorUser',addSectorUser,name='addSectorUser'),
    path('addDistrictUser',addDistrictUser,name='addDistrictUser'),
    path('enterMarks',enterMarks,name='enterMarks'),
    
    path('schoolAvgMarkFormSector',schoolAvgMarkFormSector,name='schoolAvgMarkFormSector'),
    path('schoolAvgMarkFormDistrict',schoolAvgMarkFormDistrict,name='schoolAvgMarkFormDistrict'),
    path('schoolAvgFromSchool',schoolAvgFromSchool,name='schoolAvgFromSchool'),
    
    path('classWithQuaterMarks',classWithQuaterMarks,name='classWithQuaterMarks'),
    path('male_femeleSectorPdf',male_femeleSectorPdf,name='male_femeleSectorPdf'),
    path('testChart',testChart,name='testChart'), 
    
    path('schoolGenderPdf',schoolGenderPdf, name='schoolGenderPdf'),
    path('schoolPhysicalPdf',schoolPhysicalPdf, name='schoolPhysicalPdf'),
    path('physicalSectorPdf', physicalSectorPdf, name='physicalSectorPdf'),
    path('male_femaleDistrict',male_femaleDistrict, name='male_femaleDistrict'),
    path('physicalDistrict',physicalDistrict,name='physicalDistrict'),
    path('male_femaleReb',male_femaleReb,name='male_femaleReb'),
    path('physicalReb',physicalReb,name='physicalReb'),
    
    
    # Pasword Reset Patterns and Views
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(template_name="account/password_reset.html"), 
         name="reset_password"),
    path('reset_password_sent/', 
         auth_views.PasswordResetDoneView.as_view(template_name="account/password_reset_sent.html"), 
         name="password_reset_done"),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="account/password_reset_form.html"), 
         name="password_reset_confirm"),
    path('reset_password_complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="account/password_reset_done.html"), 
         name="password_reset_complete"),
    path('testHighCharts', testHighCharts, name='testHighCharts')

]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
