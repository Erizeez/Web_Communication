#coding:utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from forum.manager_delete_decorator import delete_permission

admin.autodiscover()