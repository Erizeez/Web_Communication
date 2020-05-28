from django.shortcuts import render, get_object_or_404, reverse
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from bubbleworld.models import User, Navigation, Section, Post, PostPart, AdminApply, PostPartComment, Comment, CommentReport
from bubbleworld.form import *
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.db.models import Q
from django.utils.timezone import now, timedelta
from datetime import datetime
from django.core.cache import cache
from bubbleworld.captcha import create_captcha
from django.utils import timezone
import datetime
from io import BytesIO

import logging
# Create your views here.

logger = logging.getLogger(__name__)
PAGE_NUM = 50


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

def modify_password(request, template_name = 'show_accounts.html'):
    if request.method == 'POST':
        user = request.user
        user.set_password(request.POST.get('password'))
        user.save()
        return render(
        request,
        'show_accounts.html'
        )
    else:
        return render(
        request,
        'show_accounts.html'
        )

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
                
        except Exception:
            logger.error(u'[BaseMixin]加载基本信息出错')
        return context
        
#首页
class IndexView(BaseMixin, ListView):
    model = Post
    queryset = Post.objects.all()
    template_name = 'index.html'
    context_object_name = 'post_list'

    def get_context_data(self, **kwargs):
        kwargs['foruminfo'] = get_forum_info()
        kwargs['hot_topics'] = Section.objects.all().filter(section_type=7).order_by("-updated_at")[0:4]
        kwargs['hot_books'] = Section.objects.all().filter(section_type=5).order_by("-updated_at")[0:4]
        kwargs['hot_films'] = Section.objects.all().filter(section_type=6).order_by("-updated_at")[0:4]
        kwargs['hot_comments'] = Comment.objects.all().order_by("-updated_at")[0:4]
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
    sections_new= section_obj.section_parent_section.all().order_by('-created_at')[0:10]
    sections_hot= section_obj.section_parent_section.all().order_by('-content_number')[0:10]
    section_users = section_obj.users.all()
    if section_obj.section_type == 1 or section_obj.section_type == 2:
        uni_obj = Comment.objects.all().filter(type_comment=section_obj.section_type).order_by('like_user')[0:10]
    else:
        uni_obj = Post.objects.all().filter(type_post=section_obj.section_type).order_by('content_number')[0:10]
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
        if Section.objects.all().filter(pk = kwargs['section'])[0].users.all().filter(pk = self.request.user.pk):
            kwargs['hasuser'] = True
        else:
            kwargs['hasuser'] = False
        if Section.objects.all().filter(pk = kwargs['section'])[0].admins.all().filter(pk = self.request.user.pk):
            kwargs['hasadmin'] = True
        else:
            kwargs['hasadmin'] = False
        return super(SectionView, self).get_context_data(**kwargs)

    def get_queryset(self):
        section = self.request.GET.get('section_pk', '')
        section_instance = Section.objects.all().filter(pk = section)[0]
        if section_instance.section_type == 5 or section_instance.section_type == 6:
            uni_list = section_instance.comment_section.all()[0:20]
            if not uni_list.exists():
                return [section_instance,]
            else:
                return uni_list
        else:
            tmp_list = []
            tmp_list.extend(section_instance.post_section.all().filter(upper_placed=True).order_by("-updated_at"))
            tmp_list.extend(section_instance.post_section.all().filter(upper_placed=False).order_by("-updated_at"))
            uni_list = tmp_list[0:30]
            if len(uni_list) == 0:
                return [section_instance,]
            else:
                return uni_list
        
def section_details(request, section_pk):
    section_pk = int(section_pk)
    section = Section.objects.get(pk=section_pk)
    navigation_list = Navigation.objects.all()
    context = {}
    context['section'] = request.GET.get('section_pk', '')
    if Section.objects.all().filter(pk = section_pk)[0].users.all().filter(pk = request.user.pk):
        context['hasuser'] = True
    else:
        context['hasuser'] = False
    if Section.objects.all().filter(pk = section_pk)[0].admins.all().filter(pk = request.user.pk):
        context['hasadmin'] = True
    else:
        context['hasadmin'] = False
    if section.section_type == 5 or section.section_type == 6:
        uni_list = section.comment_section.all()[0:20]
        if not uni_list.exists():
            context['uni_list'] = [section,]
        else:
            context['uni_list'] = uni_list
    else:
        tmp_list = []
        tmp_list.extend(section.post_section.all().filter(upper_placed=True).order_by("-updated_at"))
        tmp_list.extend(section.post_section.all().filter(upper_placed=False).order_by("-updated_at"))
        uni_list = tmp_list[0:30]
        if len(uni_list) == 0:
            context['uni_list'] = [section,]
        else:
            context['uni_list'] = uni_list


    return render(
        request,
        'section_detail.html',context)
    
#评论详细界面

def comment_detail(request, comment_pk):
    comment_pk = int(comment_pk)
    comment = Comment.objects.get(pk=comment_pk)
    navigation_list = Navigation.objects.all()
    return render(
        request,
        'comment_detail.html', {
            'comment': comment,
            'navigation_list': navigation_list,
            'like_number': comment.like_number,
            'dislike_number': comment.dislike_number,
        }) 
def like_comment(request, comment_pk):
    comment_pk = int(comment_pk)
    comment = Comment.objects.get(pk=comment_pk)
    user = User.objects.get(username = request.user.username)
    if not comment.like_user.all().filter(pk=user.pk):
        if comment.dislike_user.all().filter(pk=user.pk):
            comment.dislike_user.remove(user)
        comment.like_user.add(user)
        comment.like_number = comment.like_user.all().count()
        comment.dislike_number = comment.dislike_user.all().count()
        comment.save()
    return HttpResponseRedirect(
        reverse('comment_detail', args=(str(comment_pk)))
        )

def dislike_comment(request, comment_pk):
    comment_pk = int(comment_pk)
    comment = Comment.objects.get(pk=comment_pk)
    user = User.objects.get(username = request.user.username)
    if not comment.dislike_user.all().filter(pk=user.pk):
        if comment.like_user.all().filter(pk=user.pk):
            comment.like_user.remove(user)
        comment.dislike_user.add(user)
        comment.like_number = comment.like_user.all().count()
        comment.dislike_number = comment.dislike_user.all().count()
        comment.save()
    return HttpResponseRedirect(
        reverse('comment_detail', args=(str(comment_pk)))
        )


#帖子详细界面
def post_detail(request, post_pk):
    post_pk = int(post_pk)
    post = Post.objects.get(pk=post_pk)
    navigation_list = Navigation.objects.all()
    #间帖列表
    postpart_list = post.post.all().order_by("created_at")
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
    
class SectionCreate(BaseMixin, CreateView):
    model = Section
    template_name = 'section_create.html'
    form_class = SectionForm
    def form_valid(self, form):
        captcha = self.request.POST.get('captcha', None)
        formdata = form.cleaned_data
        section_instance = Section.objects.get(pk = self.request.GET.get('section_pk', ''))
        if self.request.session.get('captcha', None).upper() != captcha.upper():
            messages.success(self.request, "验证码错误")
            return HttpResponseRedirect("/bubbleworld/section_create/?section_pk=" + str(section_instance.pk))
        user = User.objects.get(username = self.request.user.username)
        
        if user.privilege == 1 and admin_check(user, section_instance):
            messages.success(self.request, "您已被封禁")
            return HttpResponseRedirect("/bubbleworld/section_create/?section_pk=" + str(section_instance.pk))
        formdata['parent_section'] = section_instance
        if section_instance.section_type == 3:
            formdata['section_type'] = 7
        else:
            formdata['section_type'] = 8
        section_obj = Section(**formdata)
        section_obj.save()
        section_obj.admins.add(user)
        section_obj.users.add(user)
        section_instance.content_number += 1
        section_instance.save()
        messages.success(self.request, "发布成功")
        return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(section_obj.pk))

def show_accounts(request):
    return render(
        request,
        'show_accounts.html'
        )



def section_join(request, section_pk):
    section_instance = Section.objects.all().filter(pk=section_pk)[0]
    section_instance.users.add(request.user)
    section_instance.save()
    return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(section_pk))

def section_admin(request, section_pk):
    if not AdminApply.objects.all().filter(section=Section.objects.all().filter(pk=section_pk)[0], user=request.user):        
        adminapply_instance = AdminApply(section=Section.objects.all().filter(pk=section_pk)[0], user=request.user)
        adminapply_instance.save()
    return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(section_pk))

class CommentCreate(BaseMixin, CreateView):
    model = Comment
    template_name = 'post_create.html'
    form_class = CommentForm
    def form_valid(self, form):
        captcha = self.request.POST.get('captcha', None)
        formdata = form.cleaned_data
        section_instance = Section.objects.get(pk = self.request.GET.get('section_pk', ''))
        if self.request.session.get('captcha', None).upper() != captcha.upper():
            messages.success(self.request, "验证码错误")
            return HttpResponseRedirect("/bubbleworld/comment_create/?section_pk=" + str(section_instance.pk))
        user = User.objects.get(username = self.request.user.username)
        
        if user.privilege == 1 and admin_check(user, section_instance):
            messages.success(self.request, "您已被封禁")
            return HttpResponseRedirect("/bubbleworld/comment_create/?section_pk=" + str(section_instance.pk))
        if len(formdata['content']) < 25:
            messages.success(self.request, "内容长度不得小于25")
            return HttpResponseRedirect("/bubbleworld/comment_create/?section_pk=" + str(section_instance.pk))
        formdata['section'] = section_instance
        formdata['author'] = user
        comment_obj = Comment(**formdata)
        comment_obj.save()
        section_instance.star = (section_instance.star*section_instance.content_number + formdata['star']) / (section_instance.content_number+1)
        section_instance.updated_at = datetime.datetime.now()
        section_instance.content_number+=1
        section_instance.save()
        messages.success(self.request, "发布成功")
        return HttpResponseRedirect(
            reverse_lazy('comment_detail', kwargs={"comment_pk": comment_obj.pk}))
class CommentReportCreate(BaseMixin, CreateView):
    model = Comment
    template_name = 'post_create.html'
    form_class = CommentReportForm
    def form_valid(self, form):
        captcha = self.request.POST.get('captcha', None)
        formdata = form.cleaned_data
        comment_instance = Comment.objects.get(pk = self.request.GET.get('comment_pk', ''))
        if self.request.session.get('captcha', None).upper() != captcha.upper():
            messages.success(self.request, "验证码错误")
            return HttpResponseRedirect(
            reverse_lazy('comment_detail', kwargs={"comment_pk": comment_instance.pk}))
        user = User.objects.get(username = self.request.user.username)  
        if user.privilege == 1:
            messages.success(self.request, "您已被封禁")
            return HttpResponseRedirect(
            reverse_lazy('comment_detail', kwargs={"comment_pk": comment_instance.pk}))
        if len(formdata['content']) < 15:
            messages.success(self.request, "内容长度不得小于25")
            return HttpResponseRedirect(
            reverse_lazy('comment_detail', kwargs={"comment_pk": comment_instance.pk}))
        formdata['comment'] = comment_instance
        formdata['author'] = user
        commentreport_obj = CommentReport(**formdata)
        commentreport_obj.save()
        messages.success(self.request, "举报成功")
        return HttpResponseRedirect(
            reverse_lazy('comment_detail', kwargs={"comment_pk": comment_instance.pk}))


class BookCreate(BaseMixin, CreateView):
    model = Section
    template_name = 'section_create.html'
    form_class = BookForm
    def form_valid(self, form):
        captcha = self.request.POST.get('captcha', None)
        formdata = form.cleaned_data
        section_instance = Section.objects.get(pk = self.request.GET.get('section_pk', ''))
        if self.request.session.get('captcha', None).upper() != captcha.upper():
            messages.success(self.request, "验证码错误")
            return HttpResponseRedirect("/bubbleworld/book_create/?section_pk=" + str(section_instance.pk))
        user = User.objects.get(username = self.request.user.username)
        
        if user.privilege == 1 and admin_check(user, section_instance):
            messages.success(self.request, "您已被封禁")
            return HttpResponseRedirect("/bubbleworld/book_create/?section_pk=" + str(section_instance.pk))
        formdata['parent_section'] = section_instance
        formdata['section_type'] = 5
        section_obj = Section(**formdata)
        section_obj.save()
        section_obj.users.add(user)
        section_instance.content_number += 1
        section_instance.save()
        messages.success(self.request, "发布成功")
        return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(section_obj.pk))


class FilmCreate(BaseMixin, CreateView):
    model = Section
    template_name = 'section_create.html'
    form_class = FilmForm
    def form_valid(self, form):
        captcha = self.request.POST.get('captcha', None)
        formdata = form.cleaned_data
        section_instance = Section.objects.get(pk = self.request.GET.get('section_pk', ''))
        if self.request.session.get('captcha', None).upper() != captcha.upper():
            messages.success(self.request, "验证码错误")
            return HttpResponseRedirect("/bubbleworld/film_create/?section_pk=" + str(section_instance.pk))
        user = User.objects.get(username = self.request.user.username)
        
        if user.privilege == 1 and admin_check(user, section_instance):
            messages.success(self.request, "您已被封禁")
            return HttpResponseRedirect("/bubbleworld/film_create/?section_pk=" + str(section_instance.pk))
        formdata['parent_section'] = section_instance
        formdata['section_type'] = 6
        section_obj = Section(**formdata)
        section_obj.save()
        section_obj.users.add(user)
        section_instance.content_number += 1
        section_instance.save()
        messages.success(self.request, "发布成功")
        return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(section_obj.pk))
    
#发帖

class PostCreate(BaseMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm
    def form_valid(self, form):
        captcha = self.request.POST.get('captcha', None)
        formdata = form.cleaned_data
        section_instance = Section.objects.get(pk = self.request.GET.get('section_pk', ''))
        if self.request.session.get('captcha', None).upper() != captcha.upper():
            messages.success(self.request, "验证码错误")
            return HttpResponseRedirect("/bubbleworld/post_create/?section_pk=" + str(section_instance.pk))
        author = User.objects.get(username = self.request.user.username)
        
        if author.privilege == 1:
            messages.success(self.request, "您已被封禁")
            return HttpResponseRedirect("/bubbleworld/post_create/?section_pk=" + str(section_instance.pk))
        if not section_instance.users.all().filter(pk=author.pk):
            messages.success(self.request, "您需要先加入小组")
            return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(section_instance.pk))
        formdata['section'] = section_instance
        formdata['author'] = author
        formdata['last_response'] = author
        formdata['type_post'] = section_instance.section_type
        post_instance = Post(**formdata)
        post_instance.save()
        section_instance.content_number += 1
        section_instance.updated_at = datetime.datetime.now()
        section_instance.save()
        messages.success(self.request, "发布成功")
        return HttpResponseRedirect(
            reverse_lazy('post_detail', kwargs={"post_pk": post_instance.pk}))   

    
#删帖
def post_delete(request, post_pk):
    post_obj = Post.objects.all().filter(pk=post_pk)[0]
    section_pk = post_obj.section.pk
    post_obj.delete()
    section_obj = Section.objects.all().filter(pk=section_pk)[0]
    section_obj.content_number -= 1
    return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(section_pk))
        
#置顶
def post_top(request, post_pk):
    post_obj = Post.objects.all().filter(pk=post_pk)[0]
    post_obj.upper_placed = True
    post_obj.save()
    return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(post_obj.section.pk))

#加精
def post_useful(request, post_pk):
    post_obj = Post.objects.all().filter(pk=post_pk)[0]
    post_obj.essence = True
    post_obj.save()
    return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(post_obj.section.pk))
    
#取消置顶
def cancel_post_top(request, post_pk):
    post_obj = Post.objects.all().filter(pk=post_pk)[0]
    post_obj.upper_placed = False
    post_obj.save()
    return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(post_obj.section.pk))

#取消加精
def cancel_post_useful(request, post_pk):
    post_obj = Post.objects.all().filter(pk=post_pk)[0]
    post_obj.essence = False
    post_obj.save()
    return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(post_obj.section.pk))

#回帖
class PostPartCreate(BaseMixin, CreateView):
    model = PostPart
    template_name = 'postpart_create.html'
    form_class = PostPartForm

    def form_valid(self, form):
        captcha = self.request.POST.get('captcha', None)
        formdata = form.cleaned_data
        post_instance = Post.objects.get(pk = self.request.GET.get('post_pk', ''))
        section_instance = post_instance.section
        if self.request.session.get('captcha', None).upper() != captcha.upper():
            messages.success(self.request, "验证码错误")
            return HttpResponseRedirect("/bubbleworld/postpart_create/?post_pk=" + str(post_instance.pk))
        author = User.objects.get(username = self.request.user.username)
        
        if author.privilege == 1 and admin_check(author, post_instance):
            messages.success(self.request, "您已被封禁")
            return HttpResponseRedirect("/bubbleworld/postpart_create/?post_pk=" + str(post_instance.pk))
        if not section_instance.users.all().filter(pk=author.pk):
            messages.success(self.request, "您需要先加入小组")
            return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(section_instance.pk))
        if len(formdata['content']) < 25:
            messages.success(self.request, "内容长度不得小于25")
            return HttpResponseRedirect("/bubbleworld/postpart_create/?post_pk=" + str(post_instance.pk))
        
        formdata['post'] = post_instance
        formdata['author'] = author
        formdata['last_response'] = author
        formdata['type_postpart'] = post_instance.type_post
        postpart_instance = PostPart(**formdata)
        postpart_instance.save()
        post_instance.content_number += 1
        post_instance.save()
        section_instance.content_number += 1
        section_instance.updated_at = datetime.datetime.now()
        section_instance.save()
        messages.success(self.request, "发布成功")
        return HttpResponseRedirect(
            reverse_lazy('post_detail', kwargs={"post_pk": post_instance.pk}))   

    
#删除回帖
@login_required(login_url=reverse_lazy('user_login'))
class PostPartDelete(DeleteView):
    model = PostPart
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('user_postpart')
   
#间帖评论
class PostPartCommentCreate(BaseMixin, CreateView):
    model = PostPartComment
    template_name = 'postpartcomment_create.html'
    form_class = PostPartCommentForm

    def form_valid(self, form):
        captcha = self.request.POST.get('captcha', None)
        formdata = form.cleaned_data
        postpart_instance = PostPart.objects.get(pk = self.request.GET.get('postpart_pk', ''))
        section_instance = postpart_instance.post.section
        if self.request.session.get('captcha', None).upper() != captcha.upper():
            messages.success(self.request, "验证码错误")
            return HttpResponseRedirect("/bubbleworld/postpartcomment_create/?postpart_pk=" + str(postpart_instance.pk))
        author = User.objects.get(username = self.request.user.username)
        
        if author.privilege == 1 and admin_check(author, postpart_instance):
            messages.success(self.request, "您已被封禁")
            return HttpResponseRedirect("/bubbleworld/postpartcomment_create/?postpart_pk=" + str(postpart_instance.pk))
        if not section_instance.users.all().filter(pk=author.pk):
            messages.success(self.request, "您需要先加入小组")
            return HttpResponseRedirect("/bubbleworld/section_detail/?section_pk=" + str(section_instance.pk))
        formdata['postpart'] = postpart_instance
        formdata['author'] = author
        formdata['type_postpartcomment'] = postpart_instance.type_postpart
        postpartcomment_instance = PostPartComment(**formdata)
        postpartcomment_instance.save()
        post_instance = postpart_instance.post
        post_instance.content_number += 1
        post_instance.save()
        postpart_instance.content_number += 1
        postpart_instance.save()
        section_instance.content_number += 1
        section_instance.updated_at = datetime.datetime.now()
        section_instance.save()
        messages.success(self.request, "发布成功")
        return HttpResponseRedirect(
            reverse_lazy('post_detail', kwargs={"post_pk": postpart_instance.post.pk}))   

    
#删除间帖评论
@login_required(login_url=reverse_lazy('user_login'))
class PostPartCommentDelete(DeleteView):
    model = PostPart
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('user_postpart')
   
#搜索

class SearchView(BaseMixin, ListView):
    template_name = 'search_result.html'
    context_object_name = 'target_list'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        kwargs['q'] = self.request.GET.get('q', '')
        kwargs['scope'] = int(self.request.GET.get('scope', ''))
        return super(SearchView, self).get_context_data(**kwargs)

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        scope = int(self.request.GET.get('scope', ''))
        a=[]
        if scope == 0:
            section_list = Section.objects.all(
                ).filter(Q(section_type__gt = 4)
                         & (Q(name__icontains=q) 
                         | Q(author__icontains=q)
                         | Q(director__icontains=q)
                         | Q(actor__icontains=q)
                         | Q(author_description__icontains=q)
                         | Q(description__icontains=q)
                         )
                         ).order_by("-content_number")
            comment_list = Comment.objects.all(
                ).filter(Q(title__icontains=q)
                         | Q(content__icontains=q)
                         )
            post_list = Post.objects.all(
                ).filter(Q(title__icontains=q)
                         ).order_by("-content_number")
            postpart_list = PostPart.objects.all(
                ).filter(Q(content__icontains=q)
                         ).order_by("-content_number")
            postpartcomment_list = PostPart.objects.all(
                ).filter(Q(content__icontains=q)
            ).order_by("-updated_at")
            a.extend(section_list)
            a.extend(comment_list)
            a.extend(post_list)
            a.extend(postpart_list)
            a.extend(postpartcomment_list)
        elif scope == 1 or scope == 2:
            section_list = Section.objects.all(
                ).filter((Q(name__icontains=q) 
                         | Q(author__icontains=q)
                         | Q(director__icontains=q)
                         | Q(actor__icontains=q)
                         | Q(author_description__icontains=q)
                         | Q(description__icontains=q))
                         & Q(section_type__exact=(scope+4)
                         )
                         ).order_by("-content_number")
            comment_list = Comment.objects.all(
                ).filter(Q(title__icontains=q)
                         | Q(content__icontains=q)
                         & Q(type_comment__exact=scope)
                         )
            a.extend(section_list)
            a.extend(comment_list)
        else:
            section_list = Section.objects.all(
                ).filter((Q(name__icontains=q) 
                         | Q(author__icontains=q)
                         | Q(director__icontains=q)
                         | Q(actor__icontains=q)
                         | Q(author_description__icontains=q)
                         | Q(description__icontains=q))
                         & Q(section_type__exact=(scope+4)
                         )
                         ).order_by("-content_number")
            post_list = Post.objects.all(
                ).filter(Q(title__icontains=q)
                         & Q(type_post__exact=scope)
                         ).order_by("-content_number")
            postpart_list = PostPart.objects.all(
                ).filter(Q(content__icontains=q)
                         & Q(type_postpart__exact=scope)
                         ).order_by("-content_number")
            postpartcomment_list = PostPartComment.objects.all(
                ).filter(Q(content__icontains=q)
                         & Q(type_postpartcomment__exact=scope)
            ).order_by("-updated_at")
            a.extend(section_list)
            a.extend(post_list)
            a.extend(postpart_list)
            a.extend(postpartcomment_list)
        return a

#功能主页搜索

class SectionSearchView(BaseMixin, ListView):
    template_name = 'section_search_result.html'
    context_object_name = 'target_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['q'] = self.request.GET.get('q', '')
        kwargs['scope'] = int(self.request.GET.get('scope', ''))
        kwargs['sort'] = str(self.request.GET.get('sort', ''))
        return super(SectionSearchView, self).get_context_data(**kwargs)

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        scope = int(self.request.GET.get('scope', ''))
        sort = str(self.request.GET.get('sort', ''))
        a=[]
        section_list = Section.objects.all(
                ).filter((Q(name__icontains=q) 
                         | Q(author__icontains=q)
                         | Q(director__icontains=q)
                         | Q(actor__icontains=q)
                         | Q(author_description__icontains=q)
                         | Q(description__icontains=q))
                         & Q(section_type__exact=(scope+4)
                         )
                         ).order_by(sort)
        a.extend(section_list)
        return a
    
class HandlePost(BaseMixin, ListView):
    template_name = 'handle_post.html'
    context_object_name = 'target_list'
    paginate_by = 20
    
    template_name = 'handle_post.html'
    context_object_name = 'target_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['q'] = self.request.GET.get('q', '')
        kwargs['sort'] = str(self.request.GET.get('sort', ''))
        return super(HandlePost, self).get_context_data(**kwargs)

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        sort = str(self.request.GET.get('sort', ''))
        user_tmp = User.objects.all().filter(username=q)
        a=[]
        if q:
            for section_obj in Section.objects.all().filter(section_type = 8):
                if self.request.user in section_obj.admins.all():
                    a.extend(section_obj.post_section.all().filter(
                            Q(title__icontains=q) 
                         
                         ).order_by(sort))
        else:
            for section_obj in Section.objects.all().filter(section_type = 8):
                if self.request.user in section_obj.admins.all():
                    a.extend(section_obj.post_section.all().order_by("-updated_at"))
        return a


        
 
    
class HandleApply(BaseMixin, ListView):
    template_name = 'handle_apply.html'
    context_object_name = 'target_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        return super(HandleApply, self).get_context_data(**kwargs)

    def get_queryset(self):
        a = []
        a.extend(AdminApply.objects.all().order_by("-created_at"))
        return a
    
class HandleReport(BaseMixin, ListView):
    template_name = 'handle_report.html'
    context_object_name = 'target_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        return super(HandleReport, self).get_context_data(**kwargs)

    def get_queryset(self):
        a = []
        a.extend(CommentReport.objects.all().order_by("-created_at"))
        return a

def pass_apply(request, adminapply_pk):
    adminapply_obj = AdminApply.objects.all().filter(pk=adminapply_pk)[0]
    section_obj = adminapply_obj.section
    section_obj.admins.add(adminapply_obj.user)
    section_obj.save()
    adminapply_obj.delete()
    return HttpResponseRedirect(reverse_lazy("handle_apply"))
    
def refuse_apply(request, adminapply_pk):
    adminapply_obj = AdminApply.objects.all().filter(pk=adminapply_pk)[0]
    adminapply_obj.delete()
    return HttpResponseRedirect(reverse_lazy("handle_apply"))

def pass_report(request, report_pk):
    commentreport_obj = CommentReport.objects.all().filter(pk=report_pk)[0]
    commentreport_obj.comment.delete()
    commentreport_obj.delete()
    return HttpResponseRedirect(reverse_lazy("handle_report"))
    
def refuse_report(request, report_pk):
    commentreport_obj = CommentReport.objects.all().filter(pk=report_pk)[0]
    commentreport_obj.delete()
    return HttpResponseRedirect(reverse_lazy("handle_report"))

#验证码
def captcha(request):
    mstream = BytesIO()
    captcha = create_captcha()
    img = captcha[0]
    img.save(mstream, "PNG")
    request.session['captcha'] = captcha[1]
    return HttpResponse(mstream.getvalue(), "image/gif")


















