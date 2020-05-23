from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from bubbleworld.models import User, Follow, Navigation, Tag, Section, Post, PostPart, PostPartComment, Comment, CommentReport, Notice
from bubbleworld.form import UserForm, TagForm, SectionForm, PostForm, PostPartForm, CommentForm, CommentReportForm, MessageForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.db.models import Q
from django.utils.timezone import now, timedelta
from datetime import datetime
from django.core.cache import cache
from bubbleworld.captcha import create_captcha
from io import BytesIO
import logging
# Create your views here.

logger = logging.getLogger(__name__)
PAGE_NUM = 50

def get_online_ips_count():
    online_ips = cache.get('online_ips', [])
    if online_ips:
        online_ips = cache.get_many(online_ips).keys()
        return len(online_ips)
    return 0


def admin_check(user, section):
        while section.parent_section != "self":
            if user in section.users.all():
                return True
            section = section.parent_section
        return False

def get_forum_info():
    one_day = timedelta(days=1)
    today = now().date()
    last_day = today - one_day
    today_end = today + one_day
    post_number = Post.objects.count()
    account_number = User.objects.count()

    lastday_post_number = cache.get('lastday_post_number', None)
    today_post_number = cache.get('today_post_number', None)

    if lastday_post_number is None:
        lastday_post_number = Post.objects.filter(
            created_at__range=[last_day, today]).count()
        cache.set('lastday_post_number', lastday_post_number, 60 * 60)

    if today_post_number is None:
        today_post_number = Post.objects.filter(
            created_at__range=[today, today_end]).count()
        cache.set('today_post_number', today_post_number, 60 * 60)

    info = {
        "post_number": post_number,
        "account_number": account_number,
        "lastday_post_number": lastday_post_number,
        "today_post_number": today_post_number
    }
    return info


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
            messages.success(request, "登录失败")
            return render(
                request,
                'login.html'
                )
        
    else:
        next = request.GET.get('next', None)
        if next is None:
            next = reverse_lazy('index')
        return render(
                request,
                template_name, 
                {'next': next}
                )

#用户注销
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('index'))

#用户注册
def user_register(request, template_name = 'register.html'):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        form = UserForm(request.POST)
        errors = []
        if form.is_valid():
            current_site = request.build_absolute_uri
           
            new_user = form.save()
            user = authenticate(
                    username = username,
                    password = password
                    )
            login(request, user)
            return HttpResponseRedirect(reverse_lazy('index'))
        else:
            for k, v in form.errors.items():
                messages.success(request, v.as_text())
                return render(
                    request,
                    'register.html'
                    )
    else:
        return render(request, 'register.html')
  
#基本信息
class BaseMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(BaseMixin, self).get_context_data(**kwargs)
        try:
            context['navigation_list'] = Navigation.objects.all()
            context['section_list'] = Section.objects.all()
            context['last_comments'] = Comment.objects.all().order_by(
                '-created_at')[0:10]
            context['last_posts'] = Post.objects.all().order_by(
                'created_at')[0:10]
            if self.request.user.is_authenticated:
                k = Notice.objects.filter(
                    receiver=self.request.user, status=False).count()
                context['message_number'] = k
                
        except Exception:
            logger.error(u'[BaseMixin]加载基本信息出错')
        return context
        
#首页
class IndexView(BaseMixin, ListView):
    model = Post
    queryset = Post.objects.all()
    template_name = 'index.html'
    context_object_name = 'post_list'
    #分页-每页数目
    paginate_by = PAGE_NUM  

    def get_context_data(self, **kwargs):
        kwargs['foruminfo'] = get_forum_info()
        kwargs['online_ips_count'] = get_online_ips_count()
        kwargs['hot_posts'] = self.queryset.order_by("-last_response")[0:10]
        kwargs['hot_comments'] = self.queryset.order_by("-updated_at")[0:10]
        return super(IndexView, self).get_context_data(**kwargs)

#所有版块

def section_index_all(request):
    section_list = Section.objects.all()
    return render(
        'section_list.html', {'section_list': section_list},
        context_instance=RequestContext(request))     

#单个板块
def section_index_detail(request, section_pk):
    section_obj = Section.objects.get(pk=section_pk)
    sections_new= section_obj.section_parent_section.all().order_by('created_at')
    sections_hot= section_obj.section_parent_section.all().order_by('content_number')
    section_users = section_obj.users.all()
    if section_obj.section_type == 1 or section_obj.section_type == 2:
        uni_obj = Comment.objects.all().filter(type_comment=section_obj.section_type).order_by('like_number')
    else:
        uni_obj = Post.objects.all().filter(type_post=section_obj.section_type).order_by('content_number')
    return render(
        request,
        'section_index_detail.html', {
            'navigation_list': Navigation.objects.all(),
            'section_obj': section_obj,
            'sections_new': sections_new,
            'sections_hot': sections_hot,
            'uni_obj': uni_obj,
            'section_users': section_users
        }) 

class SectionView(BaseMixin, ListView):
    template_name = 'section_detail.html'
    context_object_name = 'uni_list'
    paginate_by = PAGE_NUM

    def get_context_data(self, **kwargs):
        kwargs['section'] = self.request.GET.get('section_pk', '')
        return super(SectionView, self).get_context_data(**kwargs)

    def get_queryset(self):
        section = self.request.GET.get('section_pk', '')
        section_instance = Section.objects.all().filter(pk = section)[0]
        if section_instance.section_type == 5 and section_instance.section_type == 6:
            uni_list = section_instance.comment_section.all()
        else:
            uni_list = section_instance.post_section.all()
            
        return uni_list

def section_detail(request, section_pk, args):
    section_obj = Section.objects.get(pk=section_pk)
    sections = section_obj.section_parent_section.all().order_by('created_at')

    return render(
        request,
        'section_index_detail.html', {
            'section_obj': section_obj,
            'sections': sections
        }) 
    
#评论详细界面
def comment_detail(request, comment_pk):
    comment_pk = int(comment_pk)
    comment = Comment.objects.get(pk=comment_pk)
    comment_list = Comment.comment_set.all()
    if request.user.is_authenticated():
        k = Notice.objects.filter(receiver=request.user, status=False).count()
    else:
        k = 0
    return render(
        'comment_detail.html', {
            'comment': comment,
            'comment_list': comment_list,
            'message_number': k
        },
        context_instance=RequestContext(request))
    
    
    
#帖子详细界面
def post_detail(request, post_pk):
    post_pk = int(post_pk)
    post = Post.objects.get(pk=post_pk)
    navigation_list = Navigation.objects.all()
    #间帖列表
    postpart_list = post.post.all().order_by("created_at")
    #统计帖子的访问访问次数
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    title = post.title
    visited_ips = cache.get(title, [])

    if ip not in visited_ips:
        post.view_times += 1
        post.save()
        visited_ips.append(ip)
    cache.set(title, visited_ips, 15 * 60)
    return render(
        request,
        'post_detail.html', {
            'post': post,
            'postpart_list': postpart_list,
            'navigation_list': navigation_list
        })
    
    
#消息通知
@login_required(login_url=reverse_lazy('user_login'))
def show_notice(request):
    notice_list = Notice.objects.filter(receiver=request.user, status=False)
    followtos = User.objects.get(username=request.user).follow_to.all()
    return render(
        'notice_list.html', {
            'notice_list': notice_list,
            'followtos': followtos
        },
        context_instance=RequestContext(request))      
    
#具体通知
def notice_detail(request, pk):
    pk = int(pk)
    notice = Notice.objects.get(pk=pk)
    notice.status = True
    notice.save()
    if notice.type == 1:  
        post_id = notice.event.post.id
        return HttpResponseRedirect(
            reverse_lazy('post_detail', kwargs={"post_pk": post_id}))
    elif notice.type == 2:
        follow_id = notice.event.follow.id
        return HttpResponseRedirect(
            reverse_lazy('follow_detail', kwargs={"follow_pk": follow_id}))
    elif notice.type == 3:
        message_id = notice.event.message.id
        return HttpResponseRedirect(
            reverse_lazy('message_detail', kwargs={"message_pk": message_id}))
    else:
        notice_id = notice.event.id  
        return HttpResponseRedirect(
            reverse_lazy('notice_detail', kwargs={"pk": notice_id}))

#已发帖子
class UserPostView(ListView):
    template_name = 'user_posts.html'
    context_object_name = 'user_posts'
    paginate_by = PAGE_NUM

    def get_queryset(self):
        user_posts = Post.objects.filter(author=self.request.user)
        return user_posts        
    

    
#发帖

class PostCreate(BaseMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm

    def form_valid(self, form):
        captcha = self.request.POST.get('captcha', None)
        formdata = form.cleaned_data
        if self.request.session.get('captcha', None) != captcha:
            return HttpResponse("验证码错误！<a href='/'>返回</a>")
        user = User.objects.get(username = self.request.user.username)
        section_instance = Section.objects.get(name = formdata['section'])
        if user.privilege == 1 and admin_check(user, section_instance):
            return HttpResponse("您已被封禁！<a href='/'>返回</a>")
        formdata['author'] = user
        formdata['last_response'] = user
        post_instance = Post(**formdata)
        post_instance.save()
    
 
    
#编辑贴
@login_required(login_url=reverse_lazy('user_login'))
class PostUpdate(UpdateView):
    model = Post
    template_name = 'form.html'
    
    
#删帖
@login_required(login_url=reverse_lazy('user_login'))
class PostDelete(DeleteView):
    model = Post
    template_name = 'delete_confirm.html'   

#回帖
class PostPartCreate(BaseMixin, CreateView):
    model = PostPart
    template_name = 'postpart_create.html'
    form_class = PostPartForm

    def form_valid(self, form):
        captcha = self.request.POST.get('captcha', None)
        formdata = form.cleaned_data
        if self.request.session.get('captcha', None) != captcha:
            return HttpResponse("验证码错误！<a href='/'>返回</a>")
        user = User.objects.get(username = self.request.user.username)
        section_instance = Section.objects.get(name = formdata['section'])
        if user.privilege == 1 and admin_check(user, section_instance):
            return HttpResponse("您已被封禁！<a href='/'>返回</a>")
        formdata['author'] = user
        formdata['last_response'] = user
        postpart_instance = PostPart(**formdata)
        postpart_instance.save()
'''
    if request.method == 'POST':
        content = request.POST.get("comment", "")
        post_id = request.POST.get("post_id", "")
        user = User.objects.get(username=request.user)
        post_instance = Post.objects.get(pk=post_id)
        post_instance.concontent_number += 1
        post_instance.last_response = user

        p = PostPart(post=post_instance, author=user, content=content)
        p.save()
        post_instance.save()

    return HttpResponse("回复成功") 
'''
#编辑回帖
@login_required(login_url=reverse_lazy('user_login'))
class PostPartUpdate(UpdateView):
    model = PostPart
    template_name = 'form.html'
    success_url = reverse_lazy('user_postpart')
    
#删除回帖
@login_required(login_url=reverse_lazy('user_login'))
class PostPartDelete(DeleteView):
    model = PostPart
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('user_postpart')
   
#间帖评论
@login_required(login_url=reverse_lazy('user_login'))
def create_PostPartComment(request):
    if request.method == 'POST':
        content = request.POST.get("comment", "")
        postpart_id = request.POST.get("postpart_id", "")
        user = User.objects.get(username=request.user)
        postpart_instance = PostPart.objects.get(pk=postpart_id)
        postpart_instance.concontent_number += 1
        postpart_instance.last_response = user
        post_instance = postpart_instance.post
        post_instance.concontent_number += 1
        post_instance.last_response = user

        c = Comment(postpart=postpart_instance, author=user, content=content)
        c.save()
        post_instance.save()

    return HttpResponse("回复成功") 

#编辑间帖评论
@login_required(login_url=reverse_lazy('user_login'))
class PostPartCommentUpdate(UpdateView):
    model = PostPartComment
    template_name = 'form.html'
    success_url = reverse_lazy('user_postpart')
    
#删除间帖评论
@login_required(login_url=reverse_lazy('user_login'))
class PostPartCommentDelete(DeleteView):
    model = PostPart
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('user_postpart')
    


    
#搜索（需要细化）

class SearchView(ListView):
    template_name = 'search_result.html'
    context_object_name = 'target_list'
    paginate_by = PAGE_NUM

    def get_context_data(self, **kwargs):
        kwargs['q'] = self.request.GET.get('srchtxt', '')
        kwargs['section'] = self.request.GET.get('section', '')
        return super(SearchView, self).get_context_data(**kwargs)

    def get_queryset(self):
        q = self.request.GET.get('srchtxt', '')
        section = self.request.GET.get('section', '')
        
        if section == "all":
            post_list = Post.objects.only(
                'title',
                'content').filter(Q(title__icontains=q) | Q(content__icontains=q))
            comment_list = Comment.objects.only(
                'content').filter(Q(content__icontains=q))
        else:
            section_instance = Section.objects.get(name = section)
            section_list = section_instance.section_parent_section.all()
            post_list = Post.objects.only(
                'title',
                'section',
                'content').filter(Q(section in section_list) | Q(title__icontains=q) | Q(content__icontains=q))
            comment_list = Comment.objects.only(
                'section',
                'content').filter(Q(section in section_list) | Q(title__icontains=q) | Q(content__icontains=q))
            
        target_list = post_list + comment_list
        return target_list
    
#验证码
def captcha(request):
    mstream = BytesIO()
    captcha = create_captcha()
    img = captcha[0]
    img.save(mstream, "PNG")
    request.session['captcha'] = captcha[1]
    return HttpResponse(mstream.getvalue(), "image/gif")
    


















