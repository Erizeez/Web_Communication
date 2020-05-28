#coding:utf-8
from django.conf.urls import include, url
from django.contrib import admin
from jump import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
admin.autodiscover()

urlpatterns = [
    url(r'^$', views.jump_index, name='jump_index'),
     ]
urlpatterns += staticfiles_urlpatterns()