from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from bubbleworld.models import Permission, Group, User, Follow, Navigation, Tag, Section, Post, PostPart, Comment, CommentReport, Notice
from bubbleworld.form import UserForm, TagForm, SectionForm, PostForm, PostPartForm, CommentForm, CommentReportForm, MessageForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
#from django.contrib.sites.models import get_current_site
from django.core.mail import send_mail
from django.db.models import Q
from django.utils.timezone import now, timedelta
from datetime import datetime
from django.core.cache import cache
from bubbleworld.captcha import create_captcha
from io import StringIO
import logging
# Create your views here.

logger = logging.getLogger(__name__)
PAGE_NUM = 50



#用户登录
def user_login(request, template_name = 'login.html'):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        next = request.POST['next']
        
        user = authenticate(
                username = username,
                password = password
                )
        if user is not None:
            login(request, user)
        return HttpResponseRedirect(next)
    else:
        next = request.GET.get('next', None)
        if next is None:
            next = reverse_lazy('index')
        return render(
                template_name, 
                {'next':next}
                )

#用户注销
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('index'))

#用户注册
def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        email = request.POST.get('email', '')
        
        form = UserForm(request.POST)
        errors = []
        if form.is_valid():
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            title = u'欢迎来到%s' % site_name
            message = u'你好！%s！\n\n' % username + \
                u'请记录以下信息：\n' + \
                u'    用户名：%s\n' % username + \
                u'    密码：%s\n' % password
            from_email = None
            try:
                send_mail(
                        title,
                        message,
                        from_email,
                        [email]
                        )
            except Exception as e:
                logger.error(
                        u'[USER]用户注册邮件发送失败：[%s] [%s]' % (username, email)
                        )
                return HttpResponse(
                        u'邮件发送失败\n注册失败',
                        status = 500
                        )
            new_user = form.save()
            user = authenticate(
                    username = username,
                    password = password
                    )
            login(request, user)
        else:
            for k, v in form.errors.items():
                errors.append(v.as_text())
        return render(
                'user_ok.html', 
                {'errors':errors}
                )
    else:
        return render('register.html')
    

        

















