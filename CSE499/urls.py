"""
URL configuration for CSE499 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from plagiarism import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login),
    path('accounts/', include('allauth.urls')),
    path('home/',views.Profile, name='profile'),
    path('input/', views.InputText, name='input_text'),
    path('preprocess/', views.Preprocess, name='preprocess'),
    re_path(r'^accounts/profile/about/$', views.about, name='about'),
    path('embedding/', views.embedding, name='embedding'),
    path('search/', views.search_q, name='search'),
    path('scrape/', views.scrape, name='scrape'),
    path('reload/', views.reload_page, name='reload_page'),
    path('accounts/logout/', views.logout, name='log_out'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('upload/', views.upload, name='upload'),
    path('delete_file/<pk>', views.delete_file, name='delete_file'),
    path('aboutus/', views.aboutus, name='aboutus'),
    
]
