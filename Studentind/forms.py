from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import CustomUser, Aplication, Teacher, Student



class CustomUserCreationForm(UserCreationForm):
    Name = forms.CharField(max_length=100, required=True, label='Imię:')
    surname = forms.CharField(max_length=100, required=True, label='Nazwisko:')
    index = forms.CharField(max_length=20, required=True, label='Numer indeksu:')
    email = forms.EmailField(required=True, label='Email:')
    pesel = forms.CharField(max_length=11, required=True, label='PESEL:')
    phone_number = forms.CharField(max_length=15, required=True, label='Numer telefonu:')
    city = forms.CharField(max_length=100, required=True, label='Miasto:')
    street = forms.CharField(max_length=100, required=True, label='Ulica:')
    home_nr = forms.CharField(max_length=10, required=True, label='Numer domu:')
    flat_nr = forms.CharField(max_length=10, required=False, label='Numer mieszkania:')
    course = forms.CharField(max_length=10, required=False, label='Kierunek:')
    year = forms.CharField(max_length=10, required=False, label='Rok:')
    role = forms.ChoiceField(
        choices=[('Teacher', 'Teacher'), ('Student', 'Student')],
        required=True,
        label='Rola:'
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@edu.pl'):
            raise forms.ValidationError("Email musi być w domenie 'edu.pl'.")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Użytkownik z takim adresem email już istnieje.")
        return email
    def clean_pesel(self):
        pesel = self.cleaned_data.get('pesel')

        if Teacher.objects.filter(pesel=pesel).exists() or Student.objects.filter(pesel=pesel).exists():  
            raise forms.ValidationError("Użytkownik z takim peselem już istnieje.")

        if not len(pesel) == 11:
            raise forms.ValidationError("Pesel musi mieć 11 znaków.")
        return pesel
    def clean_index(self):
        index = self.cleaned_data.get('index')
        if CustomUser.objects.filter(username=index).exists():  # `username` może przechowywać `index` jak w twoim kodzie
            raise forms.ValidationError("Użytkownik z takim numerem indeksu już istnieje.")
        return index
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not len(phone_number) == 9:
            raise forms.ValidationError("Nr telefonu musi mieć 9 znaków.")
        return phone_number
    class Meta:
        model = CustomUser
        fields = (
            'Name', 'surname', 'index', 'email', 
            'password1', 'password2', 
            'pesel', 'phone_number', 
            'city', 'street', 'home_nr', 'flat_nr', 'role'
        )

class PasswordChangeWithLoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Login")
    old_password = forms.CharField(widget=forms.PasswordInput, label="Stare hasło")
    new_password = forms.CharField(widget=forms.PasswordInput, label="Nowe hasło")

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')

        user = authenticate(username=username, password=old_password)
        if user is None:
            raise forms.ValidationError("Nieprawidłowy login lub stare hasło.")

        self.user = user
        return cleaned_data

    def save(self, commit=True):
        new_password = self.cleaned_data['new_password']
        user = self.user
        user.set_password(new_password)
        if commit:
            user.save()
        return user
class ApplicationForm(forms.ModelForm):

    typ = forms.ChoiceField(
    choices=[('Group change', 'Podanie o zmiane grupy'),
        ('Subject pass', 'Podanie o przepisanie przedmiotu'),
        ('Absence', 'Podanie o urlop zdrowotny'),
        ('Removal', 'Wykreslenie z listy studentów'),
        ('Overall', 'Podanie ogólne'),],
        required=True,
        label='Typ podania:'
        )
    text = forms.CharField(max_length=600, required=True, label='Wprowadź opis i uzasadnienie')
    class Meta:
        model = Aplication
        fields = (
            'typ', 'text'
        )        
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise forms.ValidationError('To pole nie może być puste.')
        return text
    