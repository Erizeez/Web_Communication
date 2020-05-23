#coding:utf-8
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from bubbleworld import views

admin.autodiscover()

urlpatterns = [
    url(r'^accounts/login/$', views.user_login, name='user_login'),
    url(r'^accounts/logout/$', views.user_logout, name='user_logout'),
    url(r'^accounts/register/$',
        views.user_register,
        name='user_register'),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^section/$', views.section_index_all, name='section_index_all'),
    url(r'^section/(?P<section_pk>\d+)/$',
        views.section_index_detail,
        name='section_index_detail'),
    url(r'^section_detail/$',
        views.SectionView.as_view(),
        name='section_detail'),
    url(r'^post_detail/(?P<post_pk>\d+)/$',
        views.post_detail,
        name='post_detail'),
   # url(r'^makefriend/(?P<sender>\w+)/(?P<receiver>\w+)/$',
   #     'forum.views.makefriend',
   #     name='make_friend'),
  #  url(r'^makecomment/$', 'forum.views.makecomment', name='make_comment'),
 #   url(r'^user/postlist/$', UserPostView.as_view(), name='user_post'),
    url(r'^user/post_create/$',
        login_required(views.PostCreate.as_view()),
        name='post_create'),
 #   url(r'^user/post_update/(?P<pk>\d+)/$',
 #       login_required(views.PostUpdate.as_view()),
  #      name='post_update'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^validate/$', 
        views.captcha, 
        name='captcha'),
     ]