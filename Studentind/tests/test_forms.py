from django.test import TestCase
from Studentind.forms import CustomUserCreationForm, PasswordChangeWithLoginForm, ApplicationForm
from Studentind.models import CustomUser, Student
from django.contrib.auth import get_user_model  
from datetime import datetime


class CustomUserCreationFormTest(TestCase):

    def setUp(self):
        # Zamiast User.objects.create_user, używamy get_user_model()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username='tester', password='Haslo321')
        self.student = Student.objects.create(
            studentIndex="112233",
            name="Adam",
            surname="Kowalski",
            email="112233@edu.pl",
            pesel="12345678901",
            phone_nr="987654321",  # Make sure this matches your form
            city="Warsaw",
            street="Marszalkowska",
            home_nr="1",
            flat_nr="2B",
            course="CS",
            year="2"
        )
        self.student_user = self.user_model.objects.create_user(username="112233", email="112233@edu.pl", password="Haslo123", role= "Student")

    def test_valid_form(self):
        form_data = {
            'Name': 'Jan',
            'surname': 'Kowalski',
            'index': '123456',
            'email': '123456@edu.pl',
            'pesel': '12345678902',
            'phone_number': '123456789',
            'city': 'Warszawa',
            'street': 'Polna',
            'home_nr': '12',
            'flat_nr': '5',
            'password1': 'Haslo123',
            'password2': 'Haslo123',
            'role': 'Student'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form_data = {
            'Name': 'Jan',
            'surname': 'Kowalski',
            'index': '123456',
            'email': 'mail@gmail.com',  # Niepoprawna domena
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
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
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
            'password2': 'InneHaslo123',  # Różne hasła
            'role': 'Student'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    def test_email_integrity(self):
        form_data = {
            'Name': 'Jan',
            'surname': 'Kowalski',
            'index': '123456',
            'email': '112233@edu.pl',  # Existing email
            'pesel': '12345678902',
            'phone_number': '123456789',  # Match with form
            'city': 'Warszawa',
            'street': 'Polna',
            'home_nr': '12',
            'flat_nr': '5',
            'password1': 'Haslo123',
            'password2': 'Haslo123',  # Match passwords
            'role': 'Student'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_index_integrity(self):
        form_data = {
            'Name': 'Jan',
            'surname': 'Kowalski',
            'index': '112233',  # Existing index
            'email': 'newemail@edu.pl',
            'pesel': '12345678902',
            'phone_number': '123456789',  # Match with form
            'city': 'Warszawa',
            'street': 'Polna',
            'home_nr': '12',
            'flat_nr': '5',
            'password1': 'Haslo123',
            'password2': 'Haslo123',  # Match passwords
            'role': 'Student'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('index', form.errors)

    def test_pesel_integrity(self):
        form_data = {
            'Name': 'Jan',
            'surname': 'Kowalski',
            'index': '123456',
            'email': 'newemail@edu.pl',
            'pesel': '12345678901',  # Existing PESEL
            'phone_number': '123456789',  # Match with form
            'city': 'Warszawa',
            'street': 'Polna',
            'home_nr': '12',
            'flat_nr': '5',
            'password1': 'Haslo123',
            'password2': 'Haslo123',  # Match passwords
            'role': 'Student'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('pesel', form.errors)
    def test_pesel_len(self):
        form_data = {
            'Name': 'Jan',
            'surname': 'Kowalski',
            'index': '123456',
            'email': '112233@edu.pl',
            'pesel': '142',
            'phone_number': '123456789',
            'city': 'Warszawa',
            'street': 'Polna',
            'home_nr': '12',
            'flat_nr': '5',
            'password1': 'Haslo123',
            'password2': 'Haslo123',  # Różne hasła
            'role': 'Student'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('pesel', form.errors)
    def test_phone_len(self):
        form_data = {
            'Name': 'Jan',
            'surname': 'Kowalski',
            'index': '123456',
            'email': '112233@edu.pl',
            'pesel': '12345678901',
            'phone_number': '123',
            'city': 'Warszawa',
            'street': 'Polna',
            'home_nr': '12',
            'flat_nr': '5',
            'password1': 'Haslo123',
            'password2': 'Haslo123',  # Różne hasła
            'role': 'Student'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)



class ApplicationFormTest(TestCase):

    def test_valid_application_form(self):
        form_data = {
            'typ': 'Group change',
            'text': 'Proszę o zmianę grupy.',
            'date_added': datetime(2024, 10, 15, 10, 30),
        }
        form = ApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_application_form_empty_text(self):
        form_data = {
            'typ': 'Group change',
            'text': '' ,
            'date_added': datetime(2024, 10, 15, 10, 30), 
        }
        form = ApplicationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)