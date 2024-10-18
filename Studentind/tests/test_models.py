from django.test import TestCase
from Studentind.models import Student, Teacher, Grade, Subject, Absences, Tests, Aplication, CustomUser

class StudentModelTest(TestCase):

    def setUp(self):
        self.student = Student.objects.create(
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

    def test_student_creation(self):
        self.assertEqual(self.student.name, "Adam")
        self.assertEqual(self.student.surname, "Kowalski")
        self.assertEqual(self.student.pesel, "12345678901")
        self.assertEqual(self.student.studentIndex, "112233")
        self.assertEqual(self.student.phone_nr, "987654321")
        self.assertEqual(self.student.email, "112233@edu.pl")
        self.assertEqual(self.student.city, "Warsaw")
        self.assertEqual(self.student.street, "Marszalkowska")
        self.assertEqual(self.student.home_nr, "1")
        self.assertEqual(self.student.flat_nr, "2B")
        self.assertEqual(self.student.course, "CS")
        self.assertEqual(self.student.year, "2")

    

class TeacherModelTest(TestCase):

    def setUp(self):
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

    def test_teacher_creation(self):
        self.assertEqual(self.teacher.name, "Adam")
        self.assertEqual(self.teacher.surname, "Kowalski")
        self.assertEqual(self.teacher.pesel, "12345678901")
        self.assertEqual(self.teacher.teacherIndex, "1001")
        self.assertEqual(self.teacher.phone_nr, "987654321")
        self.assertEqual(self.teacher.email, "1001@edu.pl")
        self.assertEqual(self.teacher.city, "Warsaw")
        self.assertEqual(self.teacher.street, "Marszalkowska")
        self.assertEqual(self.teacher.home_nr, "1")
        self.assertEqual(self.teacher.flat_nr, "2B")

    

class SubjectModelTest(TestCase):

    def setUp(self):
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
        self.subject = Subject.objects.create(
            subjectName="Statystyka",
            teacher=self.teacher,
            ects=5
        )

    def test_subject_creation(self):
        self.assertEqual(self.subject.subjectName, "Statystyka")
        self.assertEqual(self.subject.ects, 5)
        self.assertEqual(self.subject.teacher.name, "Adam")
        self.assertEqual(self.subject.teacher.surname, "Kowalski")
        self.assertEqual(self.subject.teacher.pesel, "12345678901")
        self.assertEqual(self.subject.teacher.teacherIndex, "1001")
        self.assertEqual(self.subject.teacher.phone_nr, "987654321")
        self.assertEqual(self.subject.teacher.email, "1001@edu.pl")
        self.assertEqual(self.subject.teacher.city, "Warsaw")
        self.assertEqual(self.subject.teacher.street, "Marszalkowska")
        self.assertEqual(self.subject.teacher.home_nr, "1")
        self.assertEqual(self.subject.teacher.flat_nr, "2B")
        

    

class GradeModelTest(TestCase):

    def setUp(self):
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
        self.student = Student.objects.create(
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
        self.subject = Subject.objects.create(
            subjectName="Analiza 1",
            teacher=self.teacher,
            ects=6
        )
        self.grade = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            grade=4.5
        )

    def test_grade_creation(self):
        self.assertEqual(self.grade.grade, 4.5)
        self.assertEqual(self.grade.student.name, "Adam")
        self.assertEqual(self.grade.subject.subjectName, "Analiza 1")

   

class AbsencesModelTest(TestCase):

    def setUp(self):
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
        self.student = Student.objects.create(
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
        self.subject = Subject.objects.create(
            subjectName="Logika",
            teacher=self.teacher,
            ects=4
        )
        self.absences = Absences.objects.create(
            student=self.student,
            subject=self.subject,
            count=2
        )

    def test_absences_creation(self):
        self.assertEqual(self.absences.count, 2)
        self.assertEqual(self.absences.student.name, "Adam")
        self.assertEqual(self.absences.subject.subjectName, "Logika")

class TestsModelTest(TestCase):

    def setUp(self):
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
        self.student = Student.objects.create(
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
        self.subject = Subject.objects.create(
            subjectName="Logika",
            teacher=self.teacher,
            ects=4
        )
        self.test = Tests.objects.create(
            student=self.student,
            subject=self.subject,
            points=80,
            max_points=100,
            test_number=1
        )

    def test_test_creation(self):
        self.assertEqual(self.test.points, 80)
        self.assertEqual(self.test.max_points, 100)
        self.assertEqual(self.test.student.name, "Adam")
        self.assertEqual(self.test.subject.subjectName, "Logika")

    
