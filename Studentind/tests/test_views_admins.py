from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from Studentind.models import CustomUser, Teacher, Student, Subject, Aplication
from datetime import datetime
import json
User = get_user_model()

class AdminViewsTestCase(TestCase):

    def setUp(self):
        # Tworzenie testowego administratora
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@edu.pl',
            password='Haslo123'
        )
        self.client.login(username='admin', password='Haslo123')
        self.teacher = Teacher.objects.create(
            teacherIndex='2002',
            name='Jan',
            surname='Narcyz',
            email='2002@edu.pl',
            pesel='00011122233',
            phone_nr='987654321',
            city='Warsaw',
            street='Main Street',
            home_nr="1",
            flat_nr='2B'
        )

        self.subject = Subject.objects.create(
            subjectName='Analiza 3',
            ects=5,
            teacher=self.teacher
        )

        self.student = Student.objects.create(
            studentIndex='500500',
            name='Adam',
            surname='Nowak',
            email='500500@edu.pl',
            pesel='22233344455',
            phone_nr='123456789',
            city='Warsaw',
            street='Main Street',
            home_nr="1",
            flat_nr='2A',
            course='CS',
            year="2"
        )

        self.application = Aplication.objects.create(
            student=self.student,
            text='Application text',
            status='In Progress',
            typ='Absence',
            date_added = datetime(2024, 10, 15, 10, 30),
        )

    def test_admins_view(self):
        # Test widoku administratorskiego
        response = self.client.get(reverse('admins_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admins.html')
        self.assertContains(response, self.admin_user.username)

    def test_add_admin_success(self):
        # Test udanego dodania administratora
        response = self.client.post(reverse('add_admin'), {
            'username': 'host_new',
            'email': 'host_new@edu.pl',
            'password': 'Haslo123',
            'password2': 'Haslo123'
        })
        self.assertTrue(User.objects.filter(username='host_new').exists())
        self.assertTrue(User.objects.filter(email='host_new@edu.pl').exists())

    def test_add_admin_username_exists(self):
        # Test przypadku, gdy nazwa użytkownika już istnieje
        User.objects.create_user(username='admin1', email='admin1@edu.pl', password='Haslo12345')
        response = self.client.post(reverse('add_admin'), {
            'username': 'admin1',
            'email': 'krk@edu.pl',
            'password': 'Haslo123',
            'password2': 'Haslo123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nazwa juz istnieje')

    def test_add_admin_email_exists(self):
        # Test przypadku, gdy email już istnieje
        User.objects.create_user(username='host1', email='host1@edu.pl', password='Haslo123')
        response = self.client.post(reverse('add_admin'), {
            'username': 'host2',
            'email': 'host1@edu.pl',
            'password': 'Haslo123',
            'password2': 'Haslo123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email juz istieje')

    def test_add_admin_password_mismatch(self):
        # Test przypadku, gdy hasła nie są zgodne
        response = self.client.post(reverse('add_admin'), {
            'username': 'admin1',
            'email': 'admin1@edu.pl',
            'password': 'Haslo123',
            'password2': 'Abcdef'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hasla musza byc takie same')

    def test_delete_admin_success(self):
        # Test udanego usunięcia administratora
        admin_to_delete = User.objects.create_superuser(
            username='admin1',
            email='admin1@edu.pl',
            password='Haslo123'
        )
        response = self.client.post(reverse('delete_admin', args=[admin_to_delete.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Administrator został usunięty!'})
        self.assertFalse(User.objects.filter(id=admin_to_delete.id).exists())


    def test_change_values_admin_success(self):
        # Test udanej zmiany wartości administratora
        admin_to_change = User.objects.create_superuser(
            username='admin1',
            email='admin1@edu.pl',
            password='Haslo123'
        )
        response = self.client.post(reverse('change_values_admin', args=[admin_to_change.id]), {
            'username': 'host1',
            'email': 'host1@edu.pl'
        })
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Dane administratora zostały zaktualizowane!'})
        admin_to_change.refresh_from_db()
        self.assertEqual(admin_to_change.username, 'host1')
        self.assertEqual(admin_to_change.email, 'host1@edu.pl')

    def test_change_values_admin_username_exists(self):
        # Test przypadku, gdy nowa nazwa użytkownika już istnieje
        admin_user = User.objects.create_superuser(
            username='admin1',
            email='admin1@edu.pl',
            password='Haslo123'
        )
        admin_to_change = User.objects.create_superuser(
            username='admin2',
            email='admin2@edu.pl',
            password='Haslo123'
        )
        response = self.client.post(reverse('change_values_admin', args=[admin_to_change.id]), {
            'username': 'admin1',  # Używamy istniejącej nazwy użytkownika
            'email': 'adminn@edu.pl'
        })
        self.assertEqual(response.json(), {'status': 'error', 'message': 'Nazwa użytkownika jest już zajęta.'})

    def test_change_values_admin_email_exists(self):
        # Test przypadku, gdy nowy email już istnieje
        admin_user = User.objects.create_superuser(
            username='admin1',
            email='admin1@edu.pl',
            password='Haslo123'
        )
        admin_to_change = User.objects.create_superuser(
            username='admin2',
            email='admin2@edu.pl',
            password='Haslo123'
        )
        response = self.client.post(reverse('change_values_admin', args=[admin_to_change.id]), {
            'username': 'adminN',
            'email': 'admin1@edu.pl'  # Używamy istniejącego emaila
        })
        self.assertEqual(response.json(), {'status': 'error', 'message': 'Adres email jest już używany.'})

    def test_teachers_info(self):
        # Test widoku teachers_info
        Teacher.objects.create(
            teacherIndex='1001',
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
        response = self.client.get(reverse('teachers_info'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teachers_info.html')
      

    def test_students_info(self):
        # Test widoku students_info
        Student.objects.create(
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
        response = self.client.get(reverse('students_info'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students_info.html')
    



    def test_update_teacher_info(self):
    # Test aktualizacji danych nauczyciela
        teacher = Teacher.objects.create(
            teacherIndex='1001',
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
        
        response = self.client.post(reverse('update_teacher_info'), json.dumps({
            'id': teacher.id,
            'teacherData': {
                'name': 'Adam',
                'surname': 'Nowak',  # Zmieniamy nazwisko na 'Nowak'
                'index': '1001',
                'email': "1001@edu.pl",  # Zachowujemy ten sam e-mail
                'pesel': "12345678901",
                'phone_nr': "987654321",
                'city': "Warsaw",
                'street': "Marszalkowska",
                'home_nr': "1",
                'flat_nr': "2B",
            }
        }), content_type='application/json')

        self.assertEqual(response.json(), {'status': 'success', 'message': 'Zaktualizowano'})
        
        # Odświeżenie instancji nauczyciela, aby pobrać zaktualizowane dane
        teacher.refresh_from_db()
        self.assertEqual(teacher.surname, 'Nowak')



   
    def test_update_student_info(self):
        # Test aktualizacji danych studenta
        student = Student.objects.create(
            studentIndex="112233",
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
        
        response = self.client.post(reverse('update_student_info'), json.dumps({
            'id': student.id,  # Przekazujemy ID jako część danych
            'studentData': {
                'name': 'Adam',
                'surname': 'Nowak',  # Zmieniamy nazwisko na 'Nowak'
                'index': '112233',
                'email': "112233@edu.pl",  # Zachowujemy ten sam e-mail
                'pesel': "12345678901",
                'phone_nr': "987654321",
                'city': "Warsaw",
                'street': "Marszalkowska",
                'home_nr': "1",
                'flat_nr': "2B",
                'course': "CS",
                'year': "2",
            }
        }), content_type='application/json')  # Określamy typ zawartości jako JSON

        self.assertEqual(response.json(), {'status': 'success', 'message': 'Zaktualizowano'})
        
        # Odświeżenie instancji studenta, aby pobrać zaktualizowane dane
        student.refresh_from_db()
        self.assertEqual(student.surname, 'Nowak')
    def test_subjects_info(self):
        response = self.client.get(reverse('subjects_info'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subjects_info.html')
        self.assertIn('subjects', response.context)
        self.assertEqual(len(response.context['subjects']), 1)



    
    def test_delete_subject(self):
        response = self.client.post(reverse('delete_subject'), {
            'id': self.subject.id
        })

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Subject deleted successfully'})
        self.assertEqual(Subject.objects.count(), 0)  # Sprawdzamy, czy przedmiot został usunięty

    def test_aplications_info(self):
        response = self.client.get(reverse('aplications_info'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_info.html')
        self.assertIn('applications', response.context)
        self.assertEqual(len(response.context['applications']), 1)





    def test_get_teachers(self):
        response = self.client.get(reverse('get_teachers'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [{
            'id': self.teacher.id,
            'name': 'Jan',
            'surname': 'Narcyz'
        }])

