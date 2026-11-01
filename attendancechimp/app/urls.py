from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('index.html', views.index, name='index_html'),
    re_path(r'^time/?$', views.time_view, name='time'),
    re_path(r'^sum/?$', views.sum_view, name='sum'),
    re_path(r'^new/?$', views.new, name='new'),
    re_path(r'^createUser/?$', views.createUser, name='createUser'),
]

