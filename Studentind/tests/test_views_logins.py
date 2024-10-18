from django.test import TestCase
from django.urls import reverse
from Studentind.models import CustomUser, Student


############ Testy rejestracji ############
class ViewsTestCase(TestCase):
    def setUp(self):
        # Tworzenie użytkowników testowych
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@edu.pl',
            password='Haslo123',
            role='Teacher',
            is_superuser=True
        )

        self.student_user = CustomUser.objects.create_user(
            username='000002',
            email='000002@edu.pl',
            password='Haslo123',
            role='Student'
        )

        self.teacher_user = CustomUser.objects.create_user(
            username='0002',
            email='0002@edu.pl',
            password='Haslo123',
            role='Teacher'
        )

    # Test widoku home_view
    def test_home_view_authenticated(self):
        self.client.login(username='000002', password='Haslo123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_anonymous(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    # Test widoku admin_dashboard
    def test_admin_dashboard_access_by_admin(self):
        self.client.login(username='admin', password='Haslo123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')

    def test_admin_dashboard_access_by_student(self):
        self.client.login(username='000002', password='Haslo123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Użytkownik nie ma dostępu, więc zwracamy 403

    # Test widoku register_user
    def test_register_user_post_valid(self):
        self.client.login(username='admin', password='Haslo123')
        form_data = {
            'Name': 'Jan',
            'surname': 'Kowalski',
            'index': '123456',
            'email': '123456@edu.pl',
            'pesel': '12345678901',
            'phone_number': '123456789',
            'city': 'Warszawa',
            'street': 'Polna',
            'home_nr': '12',
            'flat_nr': '5',
            'password1': 'Haslo123',
            'password2': 'Haslo123',
            'role': 'Student'
        }
        response = self.client.post(reverse('register_user'), data=form_data)
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertTrue(CustomUser.objects.filter(username='123456').exists())
        self.assertTrue(Student.objects.filter(studentIndex='123456').exists())

    def test_register_user_post_invalid(self):
        self.client.login(username='admin', password='Haslo123')
        form_data = {
            'Name': 'Jan',
            'surname': 'Kowalski',
            'index': '123456',
            'email': 'email',
            'pesel': '12345678901',
            'phone_number': '123456789',
            'city': 'Warszawa',
            'street': 'Polna',
            'home_nr': '12',
            'flat_nr': '5',
            'password1': 'Haslo123',
            'password2': 'Haslo123',
            'role': 'Student'
        }
        response = self.client.post(reverse('register_user'), data=form_data)
        self.assertEqual(response.status_code, 200)  # Zostajemy na stronie rejestracji, bo formularz nie przeszedł
        self.assertContains(response, 'Enter a valid email address.')
        self.assertFalse(CustomUser.objects.filter(username='123456').exists())  # Użytkownik nie został utworzony

    # Test widoku zmiany hasła
    def test_change_password_with_login_valid(self):
        self.client.login(username='000002', password='Haslo123')
        form_data = {
            'username': '000002',
            'old_password': 'Haslo123',
            'new_password': 'Haslo12345'
        }
        response = self.client.post(reverse('change_password_with_login'), data=form_data)
        self.assertRedirects(response, reverse('change_password_with_login'))
        self.student_user.refresh_from_db()
        self.assertTrue(self.student_user.check_password('Haslo12345'))

    def test_change_password_with_login_invalid(self):
        self.client.login(username='000002', password='Haslo123')
        form_data = {
            'username': '000002',
            'old_password': 'Abcdef',
            'new_password': 'Haslo12345'
        }
        response = self.client.post(reverse('change_password_with_login'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nieprawidłowy login lub stare hasło.')

    # Test widoku logowania
    def test_login_view_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'Haslo123'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))

 







