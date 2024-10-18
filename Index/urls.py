"""
URL configuration for Index project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from Studentind.views import CustomLoginView, admin_dashboard, home_view, change_password_with_login, register_user, filter_grades, oceny_view, obecnosc_view, podania_view, sprawdziany_view, nowe_podanie_view, filter_absences, teacher_oceny_view, teacher_update_grade, teacher_filter_grades,add_grade, get_subjects_for_teacher, search_students, delete_grade, filter_tests
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView
from Studentind.views import teacher_filter_tests, teacher_update_test, add_test, delete_test, teacher_tests_view, teacher_absences_view, add_absence, teacher_filter_absences, teacher_update_absences, delete_teacher, delete_student, delete_applications, filter_user_list
from Studentind.views import  get_teachers, students_info, teachers_info, aplications_info, subjects_info, filter_student_info, update_student_info, filter_teacher_info, update_teacher_info, admins_view,add_admin, delete_admin, change_values_admin, add_subject, update_subject, delete_subject, change_application_status, filter_applications, change_password, user_list
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('login/', CustomLoginView.as_view(next_page = 'home'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('password/change_with_login/', change_password_with_login, name='change_password_with_login'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('register_user/', register_user, name='register_user'),
    path('student/oceny/', oceny_view, name='oceny'),
    path('student/sprawdziany/', sprawdziany_view, name='sprawdziany'),
    path('student/sprawdziany/filter_tests', filter_tests, name='filter_tests'),
    path('student/podania/', podania_view, name='podania'),
    path('student/obecnosc/', obecnosc_view, name='obecnosc'),
    path('filter_grades/', filter_grades, name='filter_grades'),
    path('student/podania/nowe_podanie/', nowe_podanie_view, name='nowe_podanie'),
    path('filter_absences/', filter_absences, name='filter_absences'),
    path('teacher/oceny/', teacher_oceny_view, name='teacher_oceny'),
    path('teacher/sprawdziany/', teacher_tests_view, name='teacher_sprawdziany'),
    path('teacher/obecnosc/', teacher_absences_view, name='teacher_obecnosc'),
    path('teacher/oceny/teacher_update_grade/', teacher_update_grade, name='teacher_update_grade'),
    path('teacher/oceny/teacher_filter_grades/', teacher_filter_grades, name='teacher_filter_grades'),
    path('teacher/oceny/add_grade/', add_grade, name='add_grade'),
    path('teacher/search_students/', search_students, name='search_students'),
    path('teacher/get_subjects_for_teacher/', get_subjects_for_teacher, name='get_subjects_for_teacher'),
    path('teacher/oceny/delete_grade/', delete_grade, name='delete_grade'),
    path('teacher/sprawdziany/teacher_update_test/', teacher_update_test, name='teacher_update_test'),
    path('teacher/sprawdziany/teacher_filter_tests/', teacher_filter_tests, name='teacher_filter_tests'),
    path('teacher/sprawdziany/add_test/', add_test, name='add_test'),
    path('teacher/sprawdziany/delete_test/', delete_test, name='delete_test'),
    path('teacher/obecnosc/teacher_update_absence/', teacher_update_absences, name='teacher_update_absences'),
    path('teacher/obecnosc/teacher_filter_absence/', teacher_filter_absences, name='teacher_filter_absences'),
    path('teacher/obecnosc/add_absence/', add_absence, name='add_absence'),
    path('admin_dashboard/students_info', students_info, name='students_info'),
    path('admin_dashboard/teachers_info', teachers_info, name='teachers_info'),
    path('admin_dashboard/filter_student_info', filter_student_info, name='filter_students_info'),
    path('admin_dashboard/update_student_info', update_student_info, name='update_student_info'),
    path('admin_dashboard/filter_teacher_info', filter_teacher_info, name='filter_teachers_info'),
    path('admin_dashboard/update_teacher_info', update_teacher_info, name='update_teacher_info'),
    path('admin_dashboard/admins', admins_view, name='admins_view'),
    path('admin_dashboard/admins/add_admin', add_admin, name='add_admin'),
    path('change_values_admin/<int:admin_id>/', change_values_admin, name='change_values_admin'),
    path('delete_admin/<int:admin_id>/', delete_admin, name='delete_admin'),  # Edytowanie danych
    path('admin_dashboard/subjects_info/delete/', delete_subject, name='delete_subject'),
    path('admin_dashboard/aplication/', aplications_info, name='aplications_info'),
    path('admin_dashboard/change_application_status/', change_application_status, name='change_application_status'),
    path('admin_dashboard/filter_applications/', filter_applications, name='filter_applications'),  # Nowa trasa do filtrowania
    path('admin_dashboard/subjects_info/', subjects_info , name='subjects_info'),
    path('admin_dashboard/subjects_info/get_teachers/', get_teachers, name='get_teachers'),
    path('admin_dashboard/subjects_info/add/', add_subject, name='add_subject'),
    path('admin_dashboard/subjects_info/update/', update_subject, name='update_subject'),
    path('admin_dashboard/students_info/delete/', delete_student, name='delete_student'),
    path('admin_dashboard/teachers_info/delete/', delete_teacher, name='delete_teacher'),
    path('admin_dashboard/aplication/delete', delete_applications, name='delete_applications'),
    path('admin_dashboard/aplication/delete', delete_applications, name='delete_applications'),
    path('users/', user_list, name='user_list'),
    path('change-password/<int:user_id>/', change_password, name='change_password'),
    path('filter_users/', filter_user_list, name='filter_user_list'),

]
