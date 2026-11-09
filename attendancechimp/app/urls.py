from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('index.html', views.index, name='index_html'),
    re_path(r'^time/?$', views.time_view, name='time'),
    re_path(r'^sum/?$', views.sum_view, name='sum'),
    re_path(r'^new/?$', views.new, name='new'),
    re_path(r'^createUser/?$', views.createUser, name='createUser'),
    re_path(r'^new_course/?$', views.new_course, name='new_course'),
    re_path(r'^new_lecture/?$', views.new_lecture, name='new_lecture'),
    re_path(r'^new_qr_upload/?$', views.new_qr_upload, name='new_qr_upload'),
    re_path(r'^createCourse/?$', views.createCourse, name='createCourse'),
    re_path(r'^createLecture/?$', views.createLecture, name='createLecture'),
    re_path(r'^createQRCodeUpload/?$', views.createQRCodeUpload, name='createQRCodeUpload'),
    re_path(r'^dumpUploads/?$', views.dumpUploads, name='dumpUploads'),
]

