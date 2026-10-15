"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from http.client import HTTPResponse

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
import zoneinfo
import json
import io

# from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
#                      Lecture, QRCodeUpload, is_instructor, is_student,
#                      getUploadsForCourse)


def time_view(request):
    """Return the current time in Http"""

    now = datetime.now(tz=zoneinfo.ZoneInfo("America/Chicago"))
    return HttpResponse(now.strftime('%H:%M'), content_type='text/plain')

def sum_view(request):
    """Return the sum of two numbers in JSON format."""
    try:
        data = json.load(request.body)
        a = data.get('a')
        b = data.get('b')
        if a is None or b is None:
            return HttpResponseBadRequest("Missing required fields")
        result = a + b
        return JsonResponse({'result': result})
    except (json.JSONDecodeError, TypeError):
        return HttpResponseBadRequest("Invalid JSON")

def index(request):
    """Render the home page (index.html)."""

    context = {}
    return render(request, 'app/index.html', context)



# ---------------------------------------------------------------------------
# HW4  — user creation
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



