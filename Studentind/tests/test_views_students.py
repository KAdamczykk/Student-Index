from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from Studentind.models import Student, Grade, Tests, Aplication, Absences, Subject, Teacher
from datetime import datetime
User = get_user_model()

class StudentViewsTestCase(TestCase):

    def setUp(self):
        self.student_user = User.objects.create_user(username='112233', password='Haslo123', role='Student')

        # Tworzenie użytkownika studenckiego
        self.student = self.student = Student.objects.create(
            studentIndex=self.student_user.username,
            name="Adam",
            surname="Kowalski",
            email="112233@edu.pl",
            pesel="12345678901",
            phone_nr="987654321",
            city="Warsaw",
            street="Marszalkowska",
            home_nr="1",
            flat_nr="2B",
            course="CS",
            year="2"
        )
        self.client.login(username='112233', password='Haslo123')
        self.teacher = Teacher.objects.create(
            teacherIndex="1001",
            name="Adam",
            surname="Kowalski",
            email="1001@edu.pl",
            pesel="12345678901",
            phone_nr="987654321",
            city="Warsaw",
            street="Marszalkowska",
            home_nr="1",
            flat_nr="2B",
        )
        # Przykładowe dane
        self.subject = Subject.objects.create(
            subjectName="Analiza 1",
            teacher=self.teacher,
            ects=6
        )
        
        self.grade = Grade.objects.create(student=self.student, subject=self.subject, grade=4.0)
        self.test = Tests.objects.create(student=self.student, subject=self.subject, test_number=1, points=8, max_points=10)
        self.aplication = Aplication.objects.create(student=self.student, text='Prośba o urlop', status='In progress', typ='Absence', date_added= datetime(2024, 10, 15, 10, 30))
        self.absence = Absences.objects.create(student=self.student, subject=self.subject, count=1)



    def test_oceny_view_authenticated(self):
        response = self.client.get(reverse('oceny'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'grades.html')
        self.assertContains(response, self.grade.grade)

    def test_oceny_view_not_authenticated(self):
        self.client.logout()  # Wylogowanie studenta
        response = self.client.get(reverse('oceny'))
        self.assertEqual(response.status_code, 302)

    def test_sprawdziany_view_authenticated(self):
        response = self.client.get(reverse('sprawdziany'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tests.html')
        self.assertContains(response, self.test.test_number)

    def test_podania_view_authenticated(self):
        response = self.client.get(reverse('podania'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aplications.html')
        self.assertContains(response, self.aplication.text)

    def test_nowe_podanie_view_post(self):
        response = self.client.post(reverse('nowe_podanie'), {'text': 'Nowe podanie', 'typ': 'Overall'})
        self.assertEqual(response.status_code, 302)  # Oczekujemy przekierowania
        self.assertTrue(Aplication.objects.filter(text='Nowe podanie').exists())

    def test_obecnosc_view_authenticated(self):
        response = self.client.get(reverse('obecnosc'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'absences.html')
        self.assertContains(response, self.absence.count)

    def test_filter_grades_authenticated(self):
        response = self.client.get(reverse('filter_grades'), {'search_term': 'Analiza 2', 'grade_min': 3, 'grade_max': 5})
        self.assertEqual(response.status_code, 200)
       

    def test_filter_absences_authenticated(self):
        response = self.client.get(reverse('filter_absences'), {'search_term': 'Analiza 2', 'absence_min': 0, 'absence_max': 5})
        self.assertEqual(response.status_code, 200)
        
