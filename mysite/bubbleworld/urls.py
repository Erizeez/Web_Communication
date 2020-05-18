#coding:utf-8
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from bubbleworld.views import BaseMixin, IndexView, UserPostView, PostCreate, PostUpdate, PostDelete, SearchView
#from bubbleworld.manager_delete_decorator import delete_permission

admin.autodiscover()

urlpatterns = [
   url(r'^accounts/login/$', 'forum.views.user_login', name='user_login'),
    url(r'^accounts/logout/$', 'forum.views.user_logout', name='user_logout'),
    url(r'^accounts/register/$',
        'forum.views.user_register',
        name='user_register'),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^columns/$', 'forum.views.section_all', name='section_all'),
    url(r'^column/(?P<column_pk>\d+)/$',
        'forum.views.section_detail',
        name='section_detail'),
    url(r'^postdetail/(?P<post_pk>\d+)/$',
        'forum.views.postdetail',
        name='post_detail'),
    url(r'^makefriend/(?P<sender>\w+)/(?P<receiver>\w+)/$',
        'forum.views.makefriend',
        name='make_friend'),
    url(r'^makecomment/$', 'forum.views.makecomment', name='make_comment'),
    url(r'^user/postlist/$', UserPostView.as_view(), name='user_post'),
    url(r'^user/post_create/$',
        login_required(PostCreate.as_view()),
        name='post_create'),
    url(r'^user/post_update/(?P<pk>\d+)/$',
        login_required(PostUpdate.as_view()),
        name='post_update'),
    
   # url(r'^validate/$', 
    #    'bubbleworld.views.captcha', 
    #    name='captcha'),
    ]