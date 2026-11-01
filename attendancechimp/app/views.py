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
import zoneinfo

from django.views.decorators.http import require_GET, require_POST
from .models import InstructorProfile, StudentProfile


from .models import (InstructorProfile, StudentProfile)

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



# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



