from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from Studentind.models import Student, Subject, Grade, Tests, Absences, Teacher

User = get_user_model()

class TeacherViewsTestCase(TestCase):

    def setUp(self):
        # Tworzenie nauczyciela
        self.teacher_user = User.objects.create_user(username='1001', password='Haslo123', is_superuser=False)
        
        # Tworzenie superużytkownika (jeśli potrzebne)
        self.super_user = User.objects.create_user(username='admin', password='Haslo123', is_superuser=True)
        
        # Tworzenie studenta
        self.student = Student.objects.create(
            studentIndex='112233',
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
        self.teacher = Teacher.objects.create(
            teacherIndex=self.teacher_user.username,
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

        # Tworzenie przedmiotu
        self.subject = Subject.objects.create(
            subjectName="Analiza 1",
            teacher=self.teacher,
            ects=6
        )
        self.subject2 = Subject.objects.create(
            subjectName="Analiza 2",
            teacher=self.teacher,
            ects=5
        )
        self.test = Tests.objects.create(
            student=self.student,
            subject=self.subject,
            test_number=1,
            points=8,
            max_points=10
        )

        # Tworzenie ocen
        self.grade = Grade.objects.create(student=self.student, subject=self.subject, grade=4.0)

        # Logowanie nauczyciela
        self.client.login(username='1001', password='Haslo123')



    def test_teacher_oceny_view(self):
        response = self.client.get(reverse('teacher_oceny'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_grades.html')
        self.assertIn('grades', response.context)
        self.assertEqual(len(response.context['grades']), 1)  # Sprawdź, czy ocena została załadowana

    def test_teacher_filter_grades(self):
        response = self.client.get(reverse('teacher_filter_grades'), {'surname_filter': 'Kowalski'})
        self.assertEqual(response.status_code, 200)
       

    def test_teacher_update_grade(self):
        response = self.client.post(reverse('teacher_update_grade'), {'grade_id': self.grade.id, 'new_grade': 5.0})
        self.assertJSONEqual(response.content, {'success': True})
        self.grade.refresh_from_db()
        self.assertEqual(self.grade.grade, 5.0)

    def test_add_grade(self):
        response = self.client.post(reverse('add_grade'), {'student_index': '112233', 'subject_id': self.subject2.id, 'new_grade': 4.5})
        self.assertJSONEqual(response.content, {'message': 'Grade added successfully!'})
        self.assertEqual(Grade.objects.count(), 2)  # Sprawdzenie, czy dodano nową ocenę

    def test_delete_grade(self):
        response = self.client.post(reverse('delete_grade'), {'grade_id': self.grade.id})
        self.assertJSONEqual(response.content, {'success': True})
        self.assertEqual(Grade.objects.count(), 0)  # Ocena powinna być usunięta

    def test_teacher_absences_view(self):
        response = self.client.get(reverse('teacher_obecnosc'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_absences.html')

    def test_teacher_update_absences(self):
        # Tworzenie przykładowych nieobecności
        absence = Absences.objects.create(student=self.student, subject=self.subject, count=1)
        response = self.client.post(reverse('teacher_update_absences'), {'absence_id': absence.id, 'count': 2})
        self.assertJSONEqual(response.content, {'success': True})
        absence.refresh_from_db()
        self.assertEqual(absence.count, 2)

    def test_teacher_filter_absences(self):
        Absences.objects.create(student=self.student, subject=self.subject, count=3)
        response = self.client.get(reverse('teacher_filter_absences'), {'surname_filter': 'Kowalski'})
        self.assertEqual(response.status_code, 200)
        

    def test_add_absence(self):
        response = self.client.post(reverse('add_absence'), {'student_index': '112233', 'subject_id': self.subject.id})
        self.assertJSONEqual(response.content, {'message': 'Absence added successfully!'})
        self.assertEqual(Absences.objects.count(), 1)  # Sprawdzenie, czy dodano nową nieobecność
    
    def test_teacher_tests_view(self):
        response = self.client.get(reverse('teacher_sprawdziany'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_tests.html')
        self.assertIn('tests', response.context)
        self.assertEqual(len(response.context['tests']), 1)  # Sprawdź, czy test został załadowany

    def test_teacher_update_test(self):
        response = self.client.post(reverse('teacher_update_test'), {'test_id': self.test.id, 'points': 90})
        self.assertJSONEqual(response.content, {'success': True})
        self.test.refresh_from_db()
        self.assertEqual(self.test.points, 90)

    def test_teacher_update_test_not_found(self):
        response = self.client.post(reverse('teacher_update_test'), {'test_id': 9999, 'points': 90})
        self.assertJSONEqual(response.content, {'error': 'Test not found'})

    def test_teacher_filter_tests(self):
        response = self.client.get(reverse('teacher_filter_tests'), {'surname_filter': 'Kowalski'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [{
            'id': self.test.id,
            'student_name': self.student.name,
            'student_surname': self.student.surname,
            'student_index': self.student.studentIndex,
            'teacher_index': self.teacher.teacherIndex,
            'subject': self.subject.subjectName,
            'test_number': self.test.test_number,
            'points': self.test.points,
            'max_points': self.test.max_points,
        }])

    def test_teacher_filter_tests_empty(self):
        response = self.client.get(reverse('teacher_filter_tests'), {'surname_filter': 'Nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [])

    def test_add_test(self):
        response = self.client.post(reverse('add_test'), {
            'student_index': '112233',
            'subject_id': self.subject.id,
            'points': 14,
            'max_points': 20,
            'test_number': 2
        })
        self.assertJSONEqual(response.content, {'message': 'Test added successfully!'})
        self.assertEqual(Tests.objects.count(), 2)  # Sprawdzenie, czy dodano nowy test


    def test_delete_test(self):
        response = self.client.post(reverse('delete_test'), {'test_id': self.test.id})
        self.assertJSONEqual(response.content, {'success': True})
        self.assertEqual(Tests.objects.count(), 0)  # Test powinien być usunięty

    def test_delete_test_not_found(self):
        response = self.client.post(reverse('delete_test'), {'test_id': 9999})
        self.assertJSONEqual(response.content, {'error': 'Test not found'})
    
    


