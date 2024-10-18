from django.shortcuts import render, redirect, get_object_or_404

from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Teacher, Student, CustomUser, Grade, Tests, Aplication, Absences, Subject
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import update_session_auth_hash
from .forms import PasswordChangeWithLoginForm, ApplicationForm

from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
import json
from datetime import datetime

from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

############ Rejestracje ############
def home_view(request):


    # Ustalanie roli użytkownika
    role = getattr(request.user, 'role', None)
    
    context = {
        'is_authenticated': request.user.is_authenticated,
        'role': role
    }
    
    return render(request, 'home.html', context)
def check_admin(user):
    return user.is_superuser
@user_passes_test(check_admin)  
def admin_dashboard(request):
    context = None
    if request.user.is_authenticated:
        username = request.user.username
        context = {
            'username': username
        }
    return render(request, 'admin_dashboard.html', context)


@user_passes_test(check_admin)
def register_user(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        
        if user_form.is_valid():
            # Pobieranie danych z formularza
            login = user_form.cleaned_data['index']
            email = user_form.cleaned_data['email']
            password = user_form.cleaned_data['password1']
            role = user_form.cleaned_data['role']
            name = user_form.cleaned_data['Name']
            surname = user_form.cleaned_data['surname']
            pesel = user_form.cleaned_data['pesel']
            phone = user_form.cleaned_data['phone_number']
            city = user_form.cleaned_data['city']
            street = user_form.cleaned_data['street']
            home = user_form.cleaned_data['home_nr']
            flat = user_form.cleaned_data['flat_nr']
            course = user_form.cleaned_data['course']
            year = user_form.cleaned_data['year']
            try:
                # Tworzenie użytkownika
                user = CustomUser.objects.create_user(username=login, email=email, password=password, role=role)

                # Tworzenie obiektu Teacher lub Student
                if role == 'Teacher':
                    Teacher.objects.create(
                        teacherIndex=login,
                        name=name,
                        surname=surname,
                        email=email,
                        pesel=pesel,
                        phone_nr=phone,
                        city=city,
                        street=street,
                        home_nr=home,
                        flat_nr=flat
                    )
                elif role == 'Student':
                    Student.objects.create(
                        studentIndex=login,
                        name=name,
                        surname=surname,
                        email=email,
                        pesel=pesel,
                        phone_nr=phone,
                        city=city,
                        street=street,
                        home_nr=home,
                        flat_nr=flat,
                        course = course,
                        year = year
                    )
                else:
                    messages.error(request, "Nieznana rola użytkownika.")
                    return redirect('register_user')

                messages.success(request, "Użytkownik został pomyślnie zarejestrowany.")
                return redirect('admin_dashboard')

            except Exception as e:
                messages.error(request, f"Wystąpił błąd: {str(e)}")
                return redirect('register_user')
        else:
            messages.error(request, "Błąd przy wprowadzaniu danych")
    else:
        user_form = CustomUserCreationForm()

    return render(request, 'register_user.html', {'form': user_form})

def change_password_with_login(request):
    if request.method == 'POST':
        form = PasswordChangeWithLoginForm(request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('change_password_with_login')
    else:
        form = PasswordChangeWithLoginForm()

    return render(request, 'change_password_with_login.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy('admin_dashboard')
        else:
            return reverse_lazy('home')

############ Studenci ##############

# Widok dla strony "Oceny"
@login_required
def oceny_view(request):
    # Sprawdzamy, czy użytkownik jest zalogowany
    if request.user.is_authenticated:
        username = request.user.username  # Zakładam, że studentIndex to username

        # Pobranie wszystkich ocen dla zalogowanego użytkownika
        user_grades = Grade.objects.filter(
            student__studentIndex=username
        ).select_related('student', 'subject')  # Ładowanie związanych obiektów

        # Tworzymy listę słowników z danymi do zwrócenia
        grades_data = [
            {
                'student_index': grade.student.studentIndex,
                'subject': grade.subject.subjectName,
                'grade': grade.grade,
                'ects': grade.subject.ects,
                'username': username
            }
            for grade in user_grades
        ]
        
    else:
        grades_data = []  # Pusta lista, jeśli użytkownik nie jest zalogowany
   
    return render(request, 'grades.html', {'grades': grades_data}) 

def filter_grades(request):
    if request.method == 'GET' and request.user.is_authenticated:
        search_term = request.GET.get('search_term', '').strip().lower()
        grade_filter = request.GET.get('grade_filter', '')
        username = request.user.username  # Zakładam, że studentIndex to username

        # Filtrowanie ocen na podstawie studentIndex, nazwy przedmiotu oraz zakresu ocen
        user_grades = Grade.objects.filter(
            student__studentIndex=username,
            subject__subjectName__icontains=search_term,
        )

        # Dodatkowe filtrowanie według ocen
        if grade_filter == "2":
            user_grades = user_grades.filter(grade=2)
        elif grade_filter == "not_2":
            user_grades = user_grades.exclude(grade=2)


        # Sortowanie według ocen i ECTS
        sort_by = request.GET.get('sort_by', '')
        if sort_by == 'grade_asc':
            user_grades = user_grades.order_by('grade')
        elif sort_by == 'grade_desc':
            user_grades = user_grades.order_by('-grade')
        elif sort_by == 'ects_asc':
            user_grades = user_grades.order_by('subject__ects')
        elif sort_by == 'ects_desc':
            user_grades = user_grades.order_by('-subject__ects')

        user_grades = user_grades.select_related('student', 'subject')

        # Tworzymy listę słowników z danymi do zwrócenia
        grades_data = [
            {
                'student_index': grade.student.studentIndex,
                'subject': grade.subject.subjectName,
                'grade': grade.grade,
                'ects': grade.subject.ects,
            }
            for grade in user_grades
        ]

        return JsonResponse(grades_data, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
def sprawdziany_view(request):
        # Sprawdzamy, czy użytkownik jest zalogowany
    if request.user.is_authenticated:
        username = request.user.username  # Zakładam, że studentIndex to username

        # Pobranie wszystkich ocen dla zalogowanego użytkownika
        user_tests = Tests.objects.filter(
            student__studentIndex=username
        ).select_related('student', 'subject').order_by('subject__subjectName')  # Ładowanie związanych obiektów
        
        # Tworzymy listę słowników z danymi do zwrócenia
        tests_data = [
            {
                'student_index': test.student.studentIndex,
                'subject': test.subject.subjectName,
                'test_nr': test.test_number,
                'points': test.points,
                'max_points': test.max_points,
                'username': username,
            }
            for test in user_tests
        ]
    else:
        tests_data = []  # Pusta lista, jeśli użytkownik nie jest zalogowany

    return render(request, 'tests.html', {'tests': tests_data}) 

def filter_tests(request):
    if request.method == 'GET' and request.user.is_authenticated:
        search_term = request.GET.get('search_term', '').strip().lower()
        
        
        username = request.user.username  # Zakładam, że studentIndex to username

        # Filtrowanie obecności na podstawie studentIndex, nazwy przedmiotu oraz zakresu obecności
        user_tests = Tests.objects.filter(
            student__studentIndex=username,
            subject__subjectName__icontains=search_term,
           
        ).select_related('student', 'subject')  # Ładowanie związanych obiektów

        # Tworzymy listę słowników z danymi do zwrócenia
        tests_data = [
            {
                'student_index': test.student.studentIndex,
                'subject': test.subject.subjectName,
                'test_nr': test.test_number,
                'points': test.points,
                'max_points': test.max_points,
            }
            for test in user_tests
        ]

        return JsonResponse(tests_data, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
def podania_view(request):
    # Sprawdzamy, czy użytkownik jest zalogowany
    if request.user.is_authenticated:
        username = request.user.username  # Zakładam, że studentIndex to username

        # Pobranie wszystkich podań dla zalogowanego użytkownika
        user_aplications = Aplication.objects.filter(
            student__studentIndex=username
        ).select_related('student')  # Ładowanie związanych obiektów
        
        # Tworzymy listę słowników z danymi do zwrócenia
        aplications_data = [
            {
                'student_index': aplication.student.studentIndex,
                'text': aplication.text,
                'status': aplication.status,
                'typ': aplication.typ,
                'date_added': aplication.date_added,
                'username': username, 
            }
            for aplication in user_aplications
        ]
    else:
        aplications_data = []  

    return render(request, 'aplications.html', {'aplications': aplications_data})
# Widok do składania nowego podania
def nowe_podanie_view(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            username = request.user.username  
            status = 'In progress'
            student = Student.objects.get(studentIndex=username)  
            typ = form.cleaned_data['typ']
            text = form.cleaned_data['text']
            current_date = datetime.now()

            
            Aplication.objects.create(student = student, status = status, typ = typ, text = text, date_added = current_date)
            return redirect('podania')  # Przekierowanie na stronę z podaniami
    else:
        form = ApplicationForm()
    
    return render(request, 'new_aplication.html', {'form': form})

@login_required
def obecnosc_view(request):
    if request.user.is_authenticated:
        username = request.user.username  # Zakładam, że studentIndex to username

        # Pobranie wszystkich ocen dla zalogowanego użytkownika
        user_absences = Absences.objects.filter(
            student__studentIndex=username
        ).select_related('student', 'subject')  # Ładowanie związanych obiektów

        # Tworzymy listę słowników z danymi do zwrócenia
        absences_data = [
            {
                'student_index': absence.student.studentIndex,
                'subject': absence.subject.subjectName,
                'count': absence.count,
                'username': username, 
            }
            for absence in user_absences
        ]
    else:
        absences_data = []  # Pusta lista, jeśli użytkownik nie jest zalogowany

    return render(request, 'absences.html', {'absences': absences_data})

def filter_absences(request):
    if request.method == 'GET' and request.user.is_authenticated:
        search_term = request.GET.get('search_term', '').strip().lower()
        
        
        username = request.user.username  # Zakładam, że studentIndex to username

        # Filtrowanie obecności na podstawie studentIndex, nazwy przedmiotu oraz zakresu obecności
        user_absences = Absences.objects.filter(
            student__studentIndex=username,
            subject__subjectName__icontains=search_term,
           
        ).select_related('student', 'subject')  # Ładowanie związanych obiektów

        # Tworzymy listę słowników z danymi do zwrócenia
        absences_data = [
            {
                'student_index': absence.student.studentIndex,
                'subject': absence.subject.subjectName,
                'count': absence.count,
            }
            for absence in user_absences
        ]

        return JsonResponse(absences_data, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)


################## TEACHER ##################


@login_required
def teacher_oceny_view(request):
    if request.user.is_authenticated:
        teacher_username = request.user.username  # Zakładamy, że teacherIndex to username

        if request.user.is_superuser:
            # Pobranie wszystkich ocen dla wszystkich przedmiotów
            grades_by_teacher = Grade.objects.select_related('student', 'subject', 'subject__teacher')  # Optymalizacja zapytania
        else:
            # Pobranie wszystkich przedmiotów przypisanych do zalogowanego nauczyciela
            teacher_subjects = Subject.objects.filter(teacher__teacherIndex=teacher_username)

            # Pobranie wszystkich ocen dla przedmiotów, które prowadzi nauczyciel
            grades_by_teacher = Grade.objects.filter(
                subject__in=teacher_subjects
            ).select_related('student', 'subject', 'subject__teacher')  # Optymalizacja zapytania

        # Tworzymy listę słowników z danymi do wyświetlenia
        grades_data = [
            {
                'student_name': grade.student.name,
                'student_surname': grade.student.surname,
                'student_index': grade.student.studentIndex,
                'teacher_index': grade.subject.teacher.teacherIndex,  # Nauczyciel przedmiotu
                'subject': grade.subject.subjectName,
                'grade': grade.grade,
                'username': teacher_username, 
            }
            for grade in grades_by_teacher
        ]
    else:
        grades_data = []  # Pusta lista, jeśli użytkownik nie jest zalogowany

    return render(request, 'teacher_grades.html', {'grades': grades_data})

def teacher_filter_grades(request):
    if request.method == 'GET' and request.user.is_authenticated:
        surname_filter = request.GET.get('surname_filter', '').strip().lower()
        index_filter = request.GET.get('index_filter', '').strip().lower()
        teacher_username = request.user.username

        if request.user.is_superuser:
            # Jeśli to superuser, pobierz wszystkie oceny
            grades_by_teacher = Grade.objects.all()
        else:
            # Pobieranie przedmiotów prowadzonych przez nauczyciela
            teacher_subjects = Subject.objects.filter(teacher__teacherIndex=teacher_username)

            # Filtrowanie ocen po nazwisku i numerze indeksu
            grades_by_teacher = Grade.objects.filter(subject__in=teacher_subjects)

        if surname_filter:
            grades_by_teacher = grades_by_teacher.filter(student__surname__icontains=surname_filter)

        if index_filter:
            grades_by_teacher = grades_by_teacher.filter(student__studentIndex__icontains=index_filter)

        # Dane do zwrócenia w formacie JSON
        grades_data = [
            {
                'id': grade.id,
                'student_name': grade.student.name,
                'student_surname': grade.student.surname,
                'student_index': grade.student.studentIndex,
                'subject': grade.subject.subjectName,
                'grade': grade.grade,
                'ects': grade.subject.ects,
            }
            for grade in grades_by_teacher
        ]

        return JsonResponse(grades_data, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def teacher_update_grade(request):
    if request.method == 'POST' and request.user.is_authenticated:
        grade_id = request.POST.get('grade_id')
        new_grade = request.POST.get('new_grade')

        try:
            # Znajdujemy ocenę do edycji
            grade = Grade.objects.get(id=grade_id)
            grade.grade = new_grade  # Zmieniamy ocenę
            grade.save()  # Zapisujemy w bazie danych

            return JsonResponse({'success': True})

        except Grade.DoesNotExist:
            return JsonResponse({'error': 'Grade not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def add_grade(request):
    if request.method == 'POST':
        student_index = request.POST.get('student_index')
        subject_id = request.POST.get('subject_id')
        new_grade = request.POST.get('new_grade')

        # Znajdź studenta i przedmiot
        student = get_object_or_404(Student, studentIndex=student_index)
        subject = get_object_or_404(Subject, id=subject_id)

        # Dodaj nową ocenę
        grade, created = Grade.objects.get_or_create(student=student, subject=subject)
        grade.grade = new_grade
        grade.save()

        return JsonResponse({'message': 'Grade added successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def search_students(request):
    query = request.GET.get('query', '')
    students = Student.objects.filter(surname__icontains=query)  # Możesz też dodać wyszukiwanie po imieniu

    results = [{'name': student.name, 'surname': student.surname, 'studentIndex': student.studentIndex} for student in students]
    return JsonResponse(results, safe=False)
@login_required
def get_subjects_for_teacher(request):
    teacher_index = request.user.username  # Przyjmujemy, że username to teacherIndex

    if request.user.is_superuser:
        subjects = Subject.objects.all()  # Superuser widzi wszystkie przedmioty
    else:
        subjects = Subject.objects.filter(teacher__teacherIndex=teacher_index)  # Zwykły nauczyciel widzi tylko swoje przedmioty

    results = [{'id': subject.id, 'subjectName': subject.subjectName, 'ects': subject.ects} for subject in subjects]
    return JsonResponse(results, safe=False)
@login_required
def delete_grade(request):
    if request.method == 'POST' and request.user.is_authenticated:
        grade_id = request.POST.get('grade_id')

        try:
            grade = Grade.objects.get(id=grade_id)
            grade.delete()  # Usunięcie oceny z bazy danych
            return JsonResponse({'success': True})

        except Grade.DoesNotExist:
            return JsonResponse({'error': 'Grade not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def teacher_tests_view(request):
    if request.user.is_authenticated:
        teacher_username = request.user.username  # Zakładamy, że teacherIndex to username

        # Pobranie wszystkich przedmiotów
        if request.user.is_superuser:
            # Superuser widzi wszystkie przedmioty
            teacher_subjects = Subject.objects.all()
        else:
            # Pobranie wszystkich przedmiotów przypisanych do zalogowanego nauczyciela
            teacher_subjects = Subject.objects.filter(teacher__teacherIndex=teacher_username)

        # Pobranie wszystkich ocen dla przedmiotów, które prowadzi nauczyciel
        tests_by_teacher = Tests.objects.filter(
            subject__in=teacher_subjects
        ).select_related('student', 'subject', 'subject__teacher')  # Optymalizacja zapytania

        # Tworzymy listę słowników z danymi do wyświetlenia
        tests_data = [
            {
                'student_name': test.student.name,
                'student_surname': test.student.surname,
                'student_index': test.student.studentIndex,
                'teacher_index': test.subject.teacher.teacherIndex,  # Nauczyciel przedmiotu
                'subject': test.subject.subjectName,
                'test_number': test.test_number,
                'points': test.points,
                'max_points': test.max_points,
                'username': teacher_username,
            }
            for test in tests_by_teacher
        ]
    else:
        tests_data = []  # Pusta lista, jeśli użytkownik nie jest zalogowany

    return render(request, 'teacher_tests.html', {'tests': tests_data})


@login_required
def teacher_update_test(request):
    if request.method == 'POST' and request.user.is_authenticated:
        test_id = request.POST.get('test_id')
        new_points = request.POST.get('points')

        try:
            # Znajdujemy ocenę do edycji
            test = Tests.objects.get(id=test_id)
            test.points = new_points  # Zmieniamy ocenę
            test.save()  # Zapisujemy w bazie danych

            return JsonResponse({'success': True})

        except Tests.DoesNotExist:
            return JsonResponse({'error': 'Test not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def teacher_filter_tests(request):
    if request.method == 'GET' and request.user.is_authenticated:
        surname_filter = request.GET.get('surname_filter', '').strip().lower()
        index_filter = request.GET.get('index_filter', '').strip().lower()
        teacher_username = request.user.username

        # Pobieranie przedmiotów
        if request.user.is_superuser:
            # Superuser widzi wszystkie przedmioty
            teacher_subjects = Subject.objects.all()
        else:
            # Pobranie wszystkich przedmiotów prowadzonych przez nauczyciela
            teacher_subjects = Subject.objects.filter(teacher__teacherIndex=teacher_username)

        # Filtrowanie ocen po nazwisku i numerze indeksu
        tests_by_teacher = Tests.objects.filter(subject__in=teacher_subjects)

        if surname_filter:
            tests_by_teacher = tests_by_teacher.filter(student__surname__icontains=surname_filter)

        if index_filter:
            tests_by_teacher = tests_by_teacher.filter(student__studentIndex__icontains=index_filter)

        tests_data = [
            {
                'id': test.id,
                'student_name': test.student.name,
                'student_surname': test.student.surname,
                'student_index': test.student.studentIndex,
                'teacher_index': test.subject.teacher.teacherIndex,  # Nauczyciel przedmiotu
                'subject': test.subject.subjectName,
                'test_number': test.test_number,
                'points': test.points,
                'max_points': test.max_points,
            }
            for test in tests_by_teacher
        ]
        return JsonResponse(tests_data, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def add_test(request):
    if request.method == 'POST':
        student_index = request.POST.get('student_index')
        subject_id = request.POST.get('subject_id')
        points = request.POST.get('points')
        max_points = request.POST.get('max_points')
        test_number = request.POST.get('test_number')

        # Znajdź studenta i przedmiot
        student = get_object_or_404(Student, studentIndex=student_index)
        subject = get_object_or_404(Subject, id=subject_id)

        # Dodaj nową ocenę
        test, created = Tests.objects.get_or_create(student=student, subject=subject, test_number = test_number)
        test.points = points
        test.max_points = max_points
        test.test_number = test_number
        test.save()

        return JsonResponse({'message': 'Test added successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def delete_test(request):
    if request.method == 'POST' and request.user.is_authenticated:
        test_id = request.POST.get('test_id')

        try:
            test = Tests.objects.get(id=test_id)
            test.delete()  
            return JsonResponse({'success': True})

        except Tests.DoesNotExist:
            return JsonResponse({'error': 'Test not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
def teacher_absences_view(request):
    if request.user.is_authenticated:
        teacher_username = request.user.username  

        # Pobranie wszystkich przedmiotów
        if request.user.is_superuser:
            # Superuser widzi wszystkie przedmioty
            teacher_subjects = Subject.objects.all()
        else:
            # Pobranie wszystkich przedmiotów przypisanych do zalogowanego nauczyciela
            teacher_subjects = Subject.objects.filter(teacher__teacherIndex=teacher_username)

        absences_by_teacher = Absences.objects.filter(
            subject__in=teacher_subjects
        ).select_related('student', 'subject', 'subject__teacher')  # Optymalizacja zapytania

        # Tworzymy listę słowników z danymi do wyświetlenia
        absences_data = [
            {
                'student_name': absence.student.name,
                'student_surname': absence.student.surname,
                'student_index': absence.student.studentIndex,
                'teacher_index': absence.subject.teacher.teacherIndex,  # Nauczyciel przedmiotu
                'subject': absence.subject.subjectName,
                'count': absence.count,
                'username': teacher_username,
            }
            for absence in absences_by_teacher
        ]
    else:
        absences_data = []  # Pusta lista, jeśli użytkownik nie jest zalogowany

    return render(request, 'teacher_absences.html', {'absences': absences_data})


@login_required
def teacher_update_absences(request):
    if request.method == 'POST' and request.user.is_authenticated:
        absence_id = request.POST.get('absence_id')
        count = request.POST.get('count')

        try:
            absence = Absences.objects.get(id=absence_id)
            absence.count = count  
            absence.save()  

            return JsonResponse({'success': True})

        except Tests.DoesNotExist:
            return JsonResponse({'error': 'Absence not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def teacher_filter_absences(request):
    if request.method == 'GET' and request.user.is_authenticated:
        surname_filter = request.GET.get('surname_filter', '').strip().lower()
        index_filter = request.GET.get('index_filter', '').strip().lower()
        teacher_username = request.user.username

        # Pobranie wszystkich przedmiotów
        if request.user.is_superuser:
            # Superuser widzi wszystkie przedmioty
            teacher_subjects = Subject.objects.all()
        else:
            # Pobranie wszystkich przedmiotów prowadzonych przez nauczyciela
            teacher_subjects = Subject.objects.filter(teacher__teacherIndex=teacher_username)

        # Filtrowanie nieobecności
        absences_by_teacher = Absences.objects.filter(subject__in=teacher_subjects)

        if surname_filter:
            absences_by_teacher = absences_by_teacher.filter(student__surname__icontains=surname_filter)

        if index_filter:
            absences_by_teacher = absences_by_teacher.filter(student__studentIndex__icontains=index_filter)

        absences_data = [
            {
                'id': absence.id,
                'student_name': absence.student.name,
                'student_surname': absence.student.surname,
                'student_index': absence.student.studentIndex,
                'teacher_index': absence.subject.teacher.teacherIndex,  # Nauczyciel przedmiotu
                'subject': absence.subject.subjectName,
                'count': absence.count,
            }
            for absence in absences_by_teacher
        ]
        return JsonResponse(absences_data, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def add_absence(request):
    if request.method == 'POST':
        student_index = request.POST.get('student_index')
        subject_id = request.POST.get('subject_id')
       

        # Znajdź studenta i przedmiot
        student = get_object_or_404(Student, studentIndex=student_index)
        subject = get_object_or_404(Subject, id=subject_id)

        absence, created = Absences.objects.get_or_create(student=student, subject=subject)
        if absence.count == None:
            absence.count = 1


        absence.save()

        return JsonResponse({'message': 'Absence added successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)
############# ADMIN #############
@login_required
def admins_view(request):
    admins = CustomUser.objects.filter(is_superuser=True)
    return render(request, 'admins.html', {'admins': admins})
from django.shortcuts import render, redirect
from django.contrib import messages
@user_passes_test(check_admin) 
def add_admin(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if not username or not email or not password or not password2:
           return JsonResponse({'status':'error', 'message': 'Dane nie pelne'})
        elif password != password2:
            return JsonResponse({'status':'error','message':  'Hasla musza byc takie same'})
        elif CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'status':'error', 'message': 'Nazwa juz istnieje'})
        elif CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'status':'error', 'message':'Email juz istieje'})
        else:
            # Dodajemy nowego admina
            admin_user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='Admin'
            )
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            return JsonResponse({'success': True})
    return JsonResponse({'status':'error', 'message': 'Invalid request'}, status=400)


@user_passes_test(check_admin) 
def delete_admin(request, admin_id):
    if request.method == 'POST':
        admin = get_object_or_404(CustomUser, id=admin_id)
        if admin.is_superuser:
            admin.delete()
            return JsonResponse({'status': 'success', 'message': 'Administrator został usunięty!'})
        return JsonResponse({'status': 'error', 'message': 'Nie można usunąć tego użytkownika.'})
    return JsonResponse({'status': 'error', 'message': 'Nieprawidłowe żądanie.'})
@user_passes_test(check_admin) 
def change_values_admin(request, admin_id):
    if request.method == 'POST':
        # Pobierz administratora z bazy
        admin = get_object_or_404(CustomUser, id=admin_id)
        
        # Odbierz dane z formularza
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')

        # Walidacja danych (czy nowy username i email są unikalne)
        if CustomUser.objects.filter(username=new_username).exclude(id=admin_id).exists():
            return JsonResponse({'status': 'error', 'message': 'Nazwa użytkownika jest już zajęta.'})

        if CustomUser.objects.filter(email=new_email).exclude(id=admin_id).exists():
            return JsonResponse({'status': 'error', 'message': 'Adres email jest już używany.'})

        # Aktualizacja danych administratora
        admin.username = new_username
        admin.email = new_email
        admin.save()

        return JsonResponse({'status': 'success', 'message': 'Dane administratora zostały zaktualizowane!'})

    # Jeśli metoda nie jest POST
    return JsonResponse({'status': 'error', 'message': 'Nieprawidłowe żądanie.'})
@user_passes_test(check_admin) 
def teachers_info(request):
    teachers = Teacher.objects.all()
    teachers_data = [
            {
                'id': teacher.id,
                'name': teacher.name,
                'surname': teacher.surname,
                'index': teacher.teacherIndex,
                'email': teacher.email,  
                'pesel': teacher.pesel,
                'phone_nr': teacher.phone_nr,
                'city': teacher.city,  
                'street': teacher.street,
                'home_nr': teacher.home_nr,
                'flat_nr': teacher.flat_nr,  
            }
            for teacher in teachers
        ]
    return render(request, 'teachers_info.html', {'teachers': teachers_data})
@user_passes_test(check_admin) 
def filter_teacher_info(request):
    # Pobieramy parametry filtrów z zapytania GET
    surname_filter = request.GET.get('surnameFilter', '').strip().lower()  # poprawna nazwa klucza
    index_filter = request.GET.get('indexFilter', '').strip().lower()  # poprawna nazwa klucza
    sort_by = request.GET.get('sort_by', 'surname')
    sort_order = request.GET.get('sort_order', 'asc')

    teachers = Teacher.objects.all()

    # Filtracja
    if surname_filter:
        teachers = teachers.filter(surname__icontains=surname_filter)
    if index_filter:
        teachers = teachers.filter(teacherIndex__icontains=index_filter)
    if sort_by:
        teachers = teachers.order_by(f"{'' if sort_order == 'asc' else '-'}surname", f"{'' if sort_order == 'asc' else '-'}name")

    teachers_data = [
        {
            'id': teacher.id,
            'name': teacher.name,
            'surname': teacher.surname,
            'index': teacher.teacherIndex,
            'email': teacher.email,
            'pesel': teacher.pesel,
            'phone_nr': teacher.phone_nr,
            'city': teacher.city,
            'street': teacher.street,
            'home_nr': teacher.home_nr,
            'flat_nr': teacher.flat_nr,
           
        }
        for teacher in teachers
    ]

    return JsonResponse({'teachers': teachers_data}, safe=False)
@user_passes_test(check_admin) 
def update_teacher_info(request):
    if request.method == 'POST':

        # Parsowanie danych JSON
        data = json.loads(request.body)
        teacher_id = data.get('id')
        teacher_data = data.get('teacherData')

        teacher = Teacher.objects.get(pk=teacher_id)

        teacher.name = teacher_data.get('name', teacher.name)
        teacher.surname = teacher_data.get('surname', teacher.surname)
        teacher.teacherIndex = teacher_data.get('index', teacher.teacherIndex)
        teacher.email = teacher_data.get('email', teacher.email)
        teacher.pesel = teacher_data.get('pesel', teacher.pesel)
        teacher.phone_nr = teacher_data.get('phone_nr', teacher.phone_nr)
        teacher.city = teacher_data.get('city', teacher.city)
        teacher.street = teacher_data.get('street', teacher.street)
        teacher.home_nr = teacher_data.get('home_nr', teacher.home_nr)
        teacher.flat_nr = teacher_data.get('flat_nr', teacher.flat_nr)
        if not len(teacher.pesel) == 11:
            return JsonResponse({'status': 'error', 'message': 'Zły pesel'}) 

        if not len(teacher.phone_nr) == 9:
            return JsonResponse({'status': 'error', 'message': 'Zły nr telefonu'})

        # Zapisanie zmian w bazie danych
        teacher.save()

        return JsonResponse({'status': 'success', 'message': 'Zaktualizowano'})
       
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
@user_passes_test(check_admin) 
def delete_teacher(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacherId')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        teacher.delete()
        return JsonResponse({'message': 'Teacher deleted successfully'})
    return JsonResponse({'message': 'Something wrong'})
@user_passes_test(check_admin) 
def students_info(request):
    students = Student.objects.all()
    students_data = [
            {
                'id': student.id,
                'name': student.name,
                'surname': student.surname,
                'index': student.studentIndex,
                'email': student.email,  
                'pesel': student.pesel,
                'phone_nr': student.phone_nr,
                'city': student.city,  
                'street': student.street,
                'home_nr': student.home_nr,
                'flat_nr': student.flat_nr,  
                'course': student.course,
                'year': student.year,
            }
            for student in students
        ]
    return render(request, 'students_info.html', {'students': students_data})

@user_passes_test(check_admin) 
def filter_student_info(request):
    # Pobieramy parametry filtrów z zapytania GET
    surname_filter = request.GET.get('surnameFilter', '').strip().lower()  # poprawna nazwa klucza
    index_filter = request.GET.get('indexFilter', '').strip().lower()  # poprawna nazwa klucza
    sort_by = request.GET.get('sort_by', 'surname')
    sort_order = request.GET.get('sort_order', 'asc')

    students = Student.objects.all()

    # Filtracja
    if surname_filter:
        students = students.filter(surname__icontains=surname_filter)
    if index_filter:
        students = students.filter(studentIndex__icontains=index_filter)
    if sort_by == 'surname':
        students = students.order_by(f"{'' if sort_order == 'asc' else '-'}surname", f"{'' if sort_order == 'asc' else '-'}name")
    if sort_by == 'course':
        students = students.order_by(f"{'' if sort_order == 'asc' else '-'}course", f"{'' if sort_order == 'asc' else '-'}year")
    students_data = [
        {
            'id': student.id,
            'name': student.name,
            'surname': student.surname,
            'index': student.studentIndex,
            'email': student.email,
            'pesel': student.pesel,
            'phone_nr': student.phone_nr,
            'city': student.city,
            'street': student.street,
            'home_nr': student.home_nr,
            'flat_nr': student.flat_nr,
            'course': student.course,
            'year': student.year,
        }
        for student in students
    ]

    return JsonResponse({'students': students_data}, safe=False)
@user_passes_test(check_admin) 
def update_student_info(request):
    if request.method == 'POST':

        # Parsowanie danych JSON
        data = json.loads(request.body)
        student_id = data.get('id')
        student_data = data.get('studentData')

        # Znajdowanie studenta na podstawie ID
        student = Student.objects.get(pk=student_id)

        # Aktualizacja danych studenta
        student.name = student_data.get('name', student.name)
        student.surname = student_data.get('surname', student.surname)
        student.studentIndex = student_data.get('index', student.studentIndex)
        student.email = student_data.get('email', student.email)
        student.pesel = student_data.get('pesel', student.pesel)
        student.phone_nr = student_data.get('phone_nr', student.phone_nr)
        student.city = student_data.get('city', student.city)
        student.street = student_data.get('street', student.street)
        student.home_nr = student_data.get('home_nr', student.home_nr)
        student.flat_nr = student_data.get('flat_nr', student.flat_nr)
        student.course = student_data.get('course', student.course)
        student.year = student_data.get('year', student.year)
        if not len(student.pesel) == 11:
            return JsonResponse({'status': 'error', 'message': 'Zły pesel'}) 

        if not len(student.phone_nr) == 9:
            return JsonResponse({'status': 'error', 'message': 'Zły nr telefonu'})            
                
        student.save()

        return JsonResponse({'status': 'success', 'message': 'Zaktualizowano'})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
@user_passes_test(check_admin) 
def delete_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('studentId')
        student = get_object_or_404(Student, id=student_id)
        student.delete()
        return JsonResponse({'message': 'Student deleted successfully'})
    return JsonResponse({'message': 'Something wrong'})

def subjects_info(request):
    subjects = Subject.objects.all()

    subjects_data = [
        {
            'id': subject.id,
            'subjectName': subject.subjectName,
            'ects': subject.ects,
            'teacherID': subject.teacher,
            'teacherName': subject.teacher.name,
            'teacherSurname': subject.teacher.surname,
            'teacherIndex': subject.teacher.teacherIndex,
        }
        for subject in subjects
    ]
    
    return render(request, 'subjects_info.html', {'subjects': subjects_data})

def add_subject(request):
    if request.method == 'POST':
        subject_name = request.POST.get('subjectName')
        ects = request.POST.get('ects')
        teacher_id = request.POST.get('teacherId')  # Upewnij się, że to 'teacherId'

        teacher = get_object_or_404(Teacher, id=teacher_id)

        Subject.objects.create(
            subjectName=subject_name,
            ects=ects,
            teacher=teacher
        )
        return JsonResponse({'message': 'Subject added successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def update_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subjectId')  # Upewnij się, że to 'subjectId'
        subject = get_object_or_404(Subject, id=subject_id)

        subject.subjectName = request.POST.get('subjectName')
        subject.ects = request.POST.get('ects')
        teacher_id = request.POST.get('teacherId')
        subject.teacher = get_object_or_404(Teacher, id=teacher_id)

        subject.save()
        return JsonResponse({'message': 'Subject updated successfully'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def delete_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('id')
        subject = get_object_or_404(Subject, id=subject_id)
        subject.delete()
        return JsonResponse({'message': 'Subject deleted successfully'})


@user_passes_test(check_admin) 
def aplications_info(request):
    applications = Aplication.objects.all()

    # Przygotowanie danych do wyświetlenia
    applications_data = [
        {
            'id': application.id,
            'student_name': application.student.name,
            'student_surname': application.student.surname,
            'studentIndex': application.student.studentIndex,
            'text': application.text,
            'status': application.status,  # Zwraca przyjazną nazwę statusu
            'type': application.typ,      # Zwraca przyjazną nazwę typu
            'date_added': application.date_added, 
        }
        for application in applications
    ]

    return render(request, 'application_info.html', {'applications': applications_data})
@user_passes_test(check_admin) 
def change_application_status(request):
    if request.method == 'POST':
        application_id = request.POST.get('applicationId')  # Pobiera ID aplikacji z żądania
        new_status = request.POST.get('newStatus')  # Pobiera nowy status

        try:
            # Wyszukiwanie aplikacji na podstawie ID
            application = Aplication.objects.get(id=application_id)
            application.status = new_status  # Zmiana statusu
            application.save()

            return JsonResponse({'status': 'success', 'message': 'Status updated successfully'})
        except Aplication.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Application not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
@user_passes_test(check_admin) 
def filter_applications(request):
    if request.method == 'GET':
        surname_query = request.GET.get('surname', '')
        index_query = request.GET.get('index', '')

        # Filtrowanie aplikacji
        applications = Aplication.objects.all()
        if surname_query:
            applications = applications.filter(student__surname__icontains=surname_query)
        if index_query:
            applications = applications.filter(student__studentIndex__icontains=index_query)

        # Przygotowanie danych do wyświetlenia
        applications_data = [
            {
                'id': application.id,
                'student_name': application.student.name,
                'student_surname': application.student.surname,
                'studentIndex': application.student.studentIndex,
                'text': application.text,
                'status': application.get_status_display(),
                'type': application.get_typ_display(),
            }
            for application in applications
        ]

        return JsonResponse({'applications': applications_data})

@user_passes_test(check_admin)
def delete_applications(request):
    if request.method == 'POST':
        application_id = request.POST.get('applicationId')
        application = get_object_or_404(Aplication, id=application_id)
        application.delete()
        return JsonResponse({'message': 'Application deleted successfully'})
    return JsonResponse({'message': 'Someething get wrong'})
    
@user_passes_test(check_admin) 
def get_teachers(request):
    teachers = Teacher.objects.all()
    teachers_data = [
        {
            'id': teacher.id,
            'name': teacher.name,
            'surname': teacher.surname,
        }
        for teacher in teachers
    ]
    return JsonResponse(teachers_data, safe=False)
@user_passes_test(check_admin)
def filter_user_list(request):
    users = CustomUser.objects.all()
    search_query = request.GET.get('index', '').strip().lower()  # Zmienione z POST na GET
    if search_query:
        users = users.filter(username__icontains=search_query)
    users_data = [
        {
            'id': user.id,  # Dodaj id do danych użytkownika
            'index': user.username,
            'email': user.email,
            'role': user.role,
        }
        for user in users
    ]
    return JsonResponse({'applications': users_data})  # Upewnij się, że nazwa klucza jest spójna
@user_passes_test(check_admin) 
def user_list(request):
    users = CustomUser.objects.all()
    users_data = [
        {
            'index': user.username,
            'email': user.email,
            'role': user.role,
        }
        for user in users
    ]
    return render(request, 'user_list.html', {'users': users_data})
@user_passes_test(check_admin)
def change_password(request, user_id):
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(id=user_id)
            new_password = request.POST.get('new_password')
            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True})
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    
    return JsonResponse({'success': False}, status=400)