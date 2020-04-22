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
from django.contrib.sites.models import get_current_site
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

def get_online_ips_count():
    online_ips = cache.get('online_ips', [])
    if online_ips:
        online_ips = cache.get_many(online_ips).keys()
        return len(online_ips)
    return 0


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
            except Exception:
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
  
#基本信息
class BaseMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(BaseMixin, self).get_context_data(**kwargs)
        try:
            context['navigation_list'] = Navigation.objects.all()
            context['section_list'] = Section.objects.all()[0:5]
            context['last_comments'] = Comment.objects.all().order_by(
                '-created_at')[0:10]
            context['last_posts'] = Post.objects.all().order_by(
                'created_at')[0:10]
            if self.request.user.is_authenticated():
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
    
    
#评论详细界面
def commentdetail(request, comment_pk):
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
def postdetail(request, post_pk):
    post_pk = int(post_pk)
    post = Post.objects.get(pk=post_pk)
    comment_list = post.comment_set.all()
    if request.user.is_authenticated():
        k = Notice.objects.filter(receiver=request.user, status=False).count()
    else:
        k = 0
        
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
        'post_detail.html', {
            'post': post,
            'comment_list': comment_list,
            'message_number': k
        },
        context_instance=RequestContext(request))
    
    
#消息通知
@login_required(login_url=reverse_lazy('user_login'))
def shownotice(request):
    notice_list = Notice.objects.filter(receiver=request.user, status=False)
    followtos = User.objects.get(username=request.user).follow_to.all()
    return render(
        'notice_list.html', {
            'notice_list': notice_list,
            'followtos': followtos
        },
        context_instance=RequestContext(request))      
    
#具体通知
def noticedetail(request, pk):
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

#已发帖
class UserPostView(ListView):
    template_name = 'user_posts.html'
    context_object_name = 'user_posts'
    paginate_by = PAGE_NUM

    def get_queryset(self):
        user_posts = Post.objects.filter(author=self.request.user)
        return user_posts        
    

    
#发帖
class PostCreate(CreateView):
    model = Post
    template_name = 'form.html'
    form_class = PostForm
    success_url = reverse_lazy('user_post')

    def form_valid(self, form):
        validate = self.request.POST.get('validate', None)
        formdata = form.cleaned_data
        if self.request.session.get('validate', None) != validate:
            return HttpResponse("验证码错误！<a href='/'>返回</a>")
        user = User.objects.get(username=self.request.user.username)
        formdata['author'] = user
        formdata['last_response'] = user
        p = Post(**formdata)
        p.save()
        return HttpResponse("发贴成功！<a href='/'>返回</a>")     
    
#编辑贴
class PostUpdate(UpdateView):
    model = Post
    template_name = 'form.html'
    success_url = reverse_lazy('user_post')

    
#删帖
class PostDelete(DeleteView):
    model = Post
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('user_post')      
    
#评论


#回帖
    

    
#所有版块
def sectionall(request):
    section_list = Section.objects.all()
    return render(
        'section_list.html', {'section_list': section_list},
        context_instance=RequestContext(request))     

#单个板块(需要细化)
def sectiondetail(request, section_pk):
    section_obj = Section.objects.get(pk=section_pk)
    section_posts = section_obj.post_set.all()

    return render(
        'section_detail.html', {
            'section_obj': section_obj,
            'section_posts': section_posts
        },
        context_instance=RequestContext(request))    

    
#搜索（需要细化）
class SearchView(ListView):
    template_name = 'search_result.html'
    context_object_name = 'post_list'
    paginate_by = PAGE_NUM

    def get_context_data(self, **kwargs):
        kwargs['q'] = self.request.GET.get('srchtxt', '')
        return super(SearchView, self).get_context_data(**kwargs)

    def get_queryset(self):
        q = self.request.GET.get('srchtxt', '')
        post_list = Post.objects.only(
            'title',
            'content').filter(Q(title__icontains=q) | Q(content__icontains=q))
        return post_list        
    
#验证码
def captcha(request):
    mstream = StringIO.StringIO()
    captcha = create_captcha()
    img = captcha[0]
    img.save(mstream, "GIF")
    request.session['captcha'] = captcha[1]
    return HttpResponse(mstream.getvalue(), "image/gif")
    


















