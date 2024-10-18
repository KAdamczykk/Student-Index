# Generated by Django 4.2.16 on 2024-10-05 15:41

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('studentIndex', models.CharField(editable=False, max_length=6, unique=True)),
                ('name', models.CharField(max_length=20)),
                ('surname', models.CharField(max_length=20)),
                ('email', models.CharField(max_length=35)),
                ('pesel', models.IntegerField(max_length=11, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('phone_nr', models.IntegerField(max_length=9)),
                ('city', models.CharField(max_length=20)),
                ('street', models.CharField(max_length=20)),
                ('home_nr', models.IntegerField(max_length=4)),
                ('flat_nr', models.CharField(blank=True, max_length=7, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacherIndex', models.CharField(editable=False, max_length=4, unique=True)),
                ('name', models.CharField(max_length=20)),
                ('surname', models.CharField(max_length=20)),
                ('email', models.CharField(max_length=35)),
                ('pesel', models.IntegerField(max_length=11, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('phone_nr', models.IntegerField(max_length=9)),
                ('city', models.CharField(max_length=20)),
                ('street', models.CharField(max_length=20)),
                ('home_nr', models.IntegerField(max_length=4)),
                ('flat_nr', models.CharField(blank=True, max_length=7, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ects', models.IntegerField(max_length=2)),
                ('teacherID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Studentind.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Deleted_Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(max_length=500)),
                ('studentID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Studentind.student')),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('student', 'Student'), ('teacher', 'Teacher')], default='student', max_length=10)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='customuser_set', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='customuser_set', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.DecimalField(decimal_places=2, max_digits=3)),
                ('studentID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Studentind.student')),
                ('subjectID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Studentind.subject')),
                ('teacherID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Studentind.teacher')),
            ],
            options={
                'unique_together': {('studentID', 'subjectID')},
            },
        ),
        migrations.CreateModel(
            name='Absences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=0, max_length=2)),
                ('studentID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Studentind.student')),
                ('subjectID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Studentind.subject')),
                ('teacherID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Studentind.teacher')),
            ],
            options={
                'unique_together': {('studentID', 'subjectID')},
            },
        ),
    ]
