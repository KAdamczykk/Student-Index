from django.contrib import admin
from .models import Student, Teacher, Grade, Absences, Subject, CustomUser, Tests, Aplication
admin.site.register(CustomUser)

# Register your models here.
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Grade)
admin.site.register(Absences)
admin.site.register(Subject)
admin.site.register(Tests)
admin.site.register(Aplication)