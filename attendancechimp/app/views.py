"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""



from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
from django.utils import timezone
import zoneinfo

from django.views.decorators.http import require_GET, require_POST
from .models import InstructorProfile, StudentProfile

import uuid
from .models import (InstructorProfile, StudentProfile)
from .models import Course, Lecture, QRCodeUpload

"""from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
                      Lecture, QRCodeUpload, is_instructor, is_student,
                      getUploadsForCourse)
"""


def time_view(request):
    """Return the current time in Http"""

    now = datetime.now(tz=zoneinfo.ZoneInfo("America/Chicago"))
    return HttpResponse(now.strftime('%H:%M'), content_type='text/plain')

def sum_view(request):
    """Return the sum of two numbers as HTML."""
    data = request.POST if request.method == 'POST' else request.GET
    a = data.get('n1')
    b = data.get('n2')
    if a is None or b is None:
        return HttpResponseBadRequest("Missing required fields")

    try:
        result = round(float(a) + float(b), 10)
    except ValueError:
        return HttpResponseBadRequest("Is Invalid numbers")

    if result == int(result):
        result = int(result)  # 1+2 -> "3", not "3.0"
    return HttpResponse(f"<p>{result}</p>")

def index(request):
    """Render the home page (index.html)."""

    now = datetime.now(tz=zoneinfo.ZoneInfo("America/Chicago"))
    context = {'current_time': now.strftime('%H:%M')}
    return render(request, 'app/index.html', context)
@require_GET
def new(request):
    """Render the sign-up form. GET only."""
    return render(request, 'app/new.html')


@csrf_exempt
@require_POST
def createUser(request):
    """Create a user + profile, log them in. POST only."""
    email = request.POST.get('email')
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    is_student = request.POST.get('is_student')

    if not all([email, user_name, password, is_student]):
        return HttpResponseBadRequest("Missing required fields")

    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest("Email already registered")

    user = User.objects.create_user(username=user_name, email=email,
                                    password=password)

    if is_student == '1':
        StudentProfile.objects.create(user=user, student_name=user_name)
    else:
        InstructorProfile.objects.create(user=user, instructor_name=user_name)

    user = authenticate(request, username=user_name, password=password)
    login(request, user)
    return HttpResponse("User created")

# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------
def _instructor_profile(user):
    if not user.is_authenticated:
        return None
    return InstructorProfile.objects.filter(user=user).first()


def _student_profile(user):
    if not user.is_authenticated:
        return None
    return StudentProfile.objects.filter(user=user).first()


# ---- form pages (GET) ----
@require_GET
def new_course(request):
    return render(request, 'app/new_course.html')


@require_GET
def new_lecture(request):
    return render(request, 'app/new_lecture.html',
                  {'courses': Course.objects.all()})


@require_GET
def new_qr_upload(request):
    return render(request, 'app/new_qr_upload.html')


# ---- API endpoints ----
@csrf_exempt
@require_POST
def createCourse(request):
    instructor = _instructor_profile(request.user)
    if instructor is None:
        return HttpResponse("Unauthorized", status=401)

    name = request.POST.get('course-name')
    start = request.POST.get('start-time')
    end = request.POST.get('end-time')
    if not all([name, start, end]):
        return HttpResponseBadRequest("Missing required fields")

    # Checkboxes are only submitted when checked
    days = [label for field, label in [
        ('day-mon', 'Mon'), ('day-tue', 'Tue'), ('day-wed', 'Wed'),
        ('day-thu', 'Thu'), ('day-fri', 'Fri')] if field in request.POST]
    schedule = f"{','.join(days)} {start}-{end}"

    # Course names are unique, so reuse an existing row instead of duplicating
    Course.objects.get_or_create(
        course_name=name,
        defaults={'instructor': instructor, 'meeting_schedule': schedule},
    )
    return HttpResponse("Course created")


@csrf_exempt
@require_POST
def createLecture(request):
    if _instructor_profile(request.user) is None:
        return HttpResponse("Unauthorized", status=401)

    course = Course.objects.filter(course_name=request.POST.get('choice')).first()
    if course is None:
        return HttpResponseBadRequest("Unknown course")

    Lecture.objects.create(
        course=course,
        date=timezone.now(),
        qr_identifier=uuid.uuid4().hex,   # 32 chars, matches max_length=32
    )
    return HttpResponse("Lecture created")


@csrf_exempt
@require_POST
def createQRCodeUpload(request):
    student = _student_profile(request.user)
    if student is None:
        return HttpResponse("Unauthorized", status=401)

    image = request.FILES.get('imageUpload')
    if image is None:
        return HttpResponseBadRequest("Missing imageUpload")

    # upload_time is auto_now_add, so it is set automatically
    QRCodeUpload.objects.create(student=student, image=image)
    return HttpResponse("Upload saved")


@require_GET
def dumpUploads(request):
    if _instructor_profile(request.user) is None:
        return HttpResponse("Unauthorized", status=401)

    data = []
    for u in QRCodeUpload.objects.select_related('student__user'):
        t = u.upload_time
        if timezone.is_aware(t):
            t = timezone.localtime(t)
        data.append({
            "username": u.student.user.username,
            "upload_time": t.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return JsonResponse(data, safe=False)

# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



