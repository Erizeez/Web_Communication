#coding:utf-8
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from bubbleworld.views import user_login, user_logout, user_register
#from bubbleworld.manager_delete_decorator import delete_permission

admin.autodiscover()

urlpatterns = [
    '',
    url(r'^accounts/login/$', 
        user_login, 
        name='user_login'
        ),
    url(r'^accounts/logout/$', 
        user_logout, 
        name='user_logout'
        ),
    url(r'^accounts/register/$',
        user_register,
        name='user_register'),
    
   # url(r'^validate/$', 
    #    'bubbleworld.views.captcha', 
    #    name='captcha'),
    ]