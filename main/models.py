from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=200)
    roll_no = models.CharField(max_length=20, unique=True)
    mobile = models.CharField(max_length=15)
    college = models.CharField(max_length=100)
    dob = models.DateField()
    photo = models.ImageField(upload_to='student_photos/')
    date = models.CharField(max_length=15, null=True)
    exam_time=models.CharField(max_length=25, null=True)
    reporting_time=models.CharField(max_length=15, null=True)
    exam_date=models.CharField(max_length=15, null=True)
    category=models.CharField(max_length=15, null=True)
    gender=models.CharField(max_length=15, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.roll_no})"

class Subject(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    marks = models.IntegerField(null=True, blank=True)  # NEW

    def __str__(self):
        return f"{self.subject_name} - {self.student.roll_no}"




class StudentAssignment(models.Model):
    entry_user = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.entry_user.username} → {self.student.roll_no}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('entry', 'Entry User')])