"""shittyNews URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,re_path
from . import views

urlpatterns = [
    re_path(r'^$',views.index,name="index"),
    re_path(r'^results',views.results,name="search results"),
    re_path(r'^teams/?$',views.teamIndex,name="team index"),
    re_path(r'^teams/\d+$',views.team,name="team"),
    re_path(r'^news/\d+$',views.news,name="news"),
    re_path(r'^spider/?$',views.spider,name="spider"),
    path('admin/', admin.site.urls),
]
