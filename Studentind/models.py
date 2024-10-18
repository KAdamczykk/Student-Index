from django.db import models
from django.contrib.auth.models import AbstractUser

class Student(models.Model):
    studentIndex = models.CharField(max_length=6, editable=False, unique=True)
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    email = models.CharField(max_length=35)
    pesel = models.CharField(max_length=11, unique = True)
    phone_nr = models.CharField(max_length=9)
    city = models.CharField(max_length = 20)
    street = models.CharField(max_length = 20)
    home_nr = models.CharField(max_length = 4)
    flat_nr = models.CharField(max_length = 7, null = True, blank = True)
    course = models.CharField(max_length = 10, default='IAD')
    year = models.CharField(default='1')
    def __str__(self) -> str:
        return "" + self.studentIndex +" "+ self.name +" "+self.surname +" "+self.email +" "+str(self.pesel)  +" "+str(self.phone_nr) +" "+self.city +" "+self.street +" "+str(self.home_nr) +" "+self.flat_nr

    

class Teacher(models.Model):
    teacherIndex = models.CharField(max_length=4, editable=False, unique=True)
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    email = models.CharField(max_length=35)
    pesel = models.CharField(max_length=11, unique = True)
    phone_nr = models.CharField(max_length=9)
    city = models.CharField(max_length = 20)
    street = models.CharField(max_length = 20)
    home_nr = models.CharField(max_length = 4)
    flat_nr = models.CharField(max_length = 7, null = True, blank = True)
    def __str__(self) -> str:
        return "" + self.teacherIndex +" "+ self.name +" "+self.surname +" "+self.email +" "+str(self.pesel)  +" "+str(self.phone_nr) +" "+self.city +" "+self.street +" "+str(self.home_nr) +" "+self.flat_nr
    
class Subject(models.Model):
    subjectName = models.CharField(max_length=25, default="-")
    teacher = models.ForeignKey(Teacher, on_delete = models.CASCADE, db_constraint=False)
    ects = models.IntegerField(max_length=2)
    def __str__(self) -> str:
        return "" + self.subjectName + " " + str(self.ects) + " " +self.teacher.surname + " " +self.teacher.name + + " " +self.teacher.teacherIndex



class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)  
    class Meta:
        unique_together = (('student', 'subject'),)   
    def __str__(self) -> str:
        return "" + self.student.name + " " + self.student.surname + " " + self.student.studentIndex + " " + self.subject.subjectName + " " + str(self.subject.ects) + " " + str(self.grade)

class Absences(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    count = models.IntegerField(max_length=2, default=1)  
    class Meta:
        unique_together = (('student', 'subject'),)  
 
class Tests(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)  
    max_points = models.IntegerField(default=0)  
    test_number = models.IntegerField(default=0) 
    class Meta:
        unique_together = (('student', 'subject', 'test_number'),) 
    def __str__(self) -> str:
        return "" + self.student.name + " " + self.student.surname + " " + self.student.studentIndex + " " + self.subject.subjectName + " "+ str(self.test_number) +" "+ str(self.points) + " " + str(self.max_points)

class Aplication(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    text = models.TextField(max_length=600, default='-')
    date_added = models.DateTimeField()

    STATUS = (
        ('Accepted', 'Accepted'),
        ('In progress', 'In progress'),
        ('Rejected', 'Rejected'),
    )
    TYPE = (
        ('Group change', 'Podanie o zmiane grupy'),
        ('Subject pass', 'Podanie o przepisanie przedmiotu'),
        ('Absence', 'Podanie o urlop zdrowotny'),
        ('Removal', 'Wykreslenie z listy studentów'),
        ('Overall', 'Podanie ogólne'),
    )
    status = models.CharField(max_length=15, choices=STATUS, default='In progress')
    typ = models.CharField(max_length=100, choices=TYPE, default='Overall')
    
    def __str__(self) -> str:
        return "" + self.student.name + " " + self.student.surname + " " + self.student.studentIndex + " " + self.text + "    " + self.status

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Student', 'Student'),
        ('Teacher', 'Teacher'),
        ('Admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    def __str__(self):
        return f'{self.username} ({self.email}), Role: {self.role}'


