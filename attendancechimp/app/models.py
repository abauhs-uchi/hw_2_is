"""
See ERD in app/docs/my-data-model.png
"""

from django.db import models
from django.contrib.auth.models import User


class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    instructor_name = models.CharField(max_length=200)


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=200)


class Course(models.Model):
    course_name = models.CharField(max_length=200)
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE)
    meeting_schedule = models.CharField(max_length=200)


class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')


class Lecture(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField()
    qr_identifier = models.CharField(max_length=32, unique=True)


class QRCodeUpload(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, null=True, blank=True,
                                on_delete=models.SET_NULL)
    image = models.FileField(upload_to='qr_uploads/')
    upload_time = models.DateTimeField(auto_now_add=True)