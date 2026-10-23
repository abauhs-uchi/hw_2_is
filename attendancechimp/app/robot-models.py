"""

LLM Generation Details
#####################

LLM Name: Gemini 3.6 Thinking

Prompt:
"Please complete the AI section described in part 5 of the attached pdf"
"""

import uuid
from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    """
    Profile extension for student users in AttendanceChimp.
    
    Separated from InstructorProfile to encapsulate student-specific metadata
    (e.g., student ID, major) and simplify role-based permissions.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_profile'
    )
    student_id = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="University student identification number"
    )
    major = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"Student: {full_name if full_name else self.user.username} ({self.student_id})"


class InstructorProfile(models.Model):
    """
    Profile extension for instructor users in AttendanceChimp.
    
    Separated from StudentProfile to manage faculty-specific details
    such as department association and office hours.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='instructor_profile'
    )
    department = models.CharField(max_length=100, blank=True)
    office_hours = models.CharField(
        max_length=200, 
        blank=True, 
        help_text="e.g., Mon/Wed 2:00 PM - 4:00 PM"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"Instructor: Prof. {full_name if full_name else self.user.username}"


class Course(models.Model):
    """
    Represents an academic course taught by an instructor.
    """
    name = models.CharField(
        max_length=200, 
        help_text="Course title (e.g., Data Model Design)"
    )
    course_code = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Unique course code (e.g., DATA13600)"
    )
    instructor = models.ForeignKey(
        InstructorProfile, 
        on_delete=models.CASCADE, 
        related_name='courses'
    )
    meeting_schedule = models.CharField(
        max_length=200, 
        help_text="Days and time schedule (e.g., MWF 10:00 AM - 11:15 AM)"
    )
    students = models.ManyToManyField(
        StudentProfile, 
        through='Enrollment', 
        related_name='courses'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_code}: {self.name}"


class Enrollment(models.Model):
    """
    Explicit junction model representing a student's enrollment in a course.
    """
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.student} enrolled in {self.course.course_code}"


class Lecture(models.Model):
    """
    Represents an individual class meeting for a course, associated with a QR code identifier.
    """
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='lectures'
    )
    title = models.CharField(
        max_length=200, 
        blank=True, 
        help_text="Optional lecture topic or session name"
    )
    date = models.DateTimeField(help_text="Scheduled date and start time of the lecture")
    qr_identifier = models.CharField(
        max_length=255, 
        unique=True, 
        default=uuid.uuid4, 
        help_text="Unique identifier/token embedded in the generated lecture QR code"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Flag indicating whether attendance submission for this lecture is open"
    )

    def __str__(self):
        return f"{self.course.course_code} - Lecture on {self.date.strftime('%Y-%m-%d %H:%M')}"


class QRCodeUpload(models.Model):
    """
    Represents a student's submission of a QR code image to record attendance.
    
    Includes analytics and security metadata (decoded payload, status, IP, coordinates)
    to support robust verification and cheat detection.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE, 
        related_name='qr_uploads'
    )
    lecture = models.ForeignKey(
        Lecture, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='qr_uploads',
        help_text="Optional until QR decoding and lecture matching complete"
    )
    image = models.ImageField(
        upload_to='qr_uploads/%Y/%m/%d/', 
        help_text="Uploaded photo of the QR code"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    decoded_code = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Decoded text extracted from the QR code image"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Anti-cheating & Analytics metadata
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True, 
        help_text="IP address at time of submission"
    )
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True, 
        help_text="GPS latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True, 
        help_text="GPS longitude coordinate"
    )

    def __str__(self):
        lecture_str = f"Lecture #{self.lecture.id}" if self.lecture else "Unmatched Lecture"
        return f"QR Upload by {self.student.user.username} - {lecture_str} ({self.get_status_display()})"