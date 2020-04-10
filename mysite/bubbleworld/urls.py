#coding:utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from bubbleworld.views import * 
from bubbleworld.manager_delete_decorator import delete_permission

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^accounts/login/$', 'forum.views.userlogin', name='user_login'),
    url(r'^accounts/logout/$', 'forum.views.userlogout', name='user_logout'),
    url(r'^accounts/register/$',
        'forum.views.userregister',
        name='user_register'),
    
    url(r'^validate/$', 'bubbleworld.views.captcha', name='captcha'),
    )