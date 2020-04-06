#coding:utf-8
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import signals
import datetime

# Create your models here.

class Permission(models.Model):
    name = models.Model(
            max_length = 30,
            unique = True
            )
    created_time = models.DateTimeField(
            u'创建时间',
            default = datetime.datetime.now,
            auto_now_add = True
            )
    
    class Meta:
        db_table = 'permission'
        verbose_name = u'权限'
        verbose_name_plural = u'权限'
        ordering = ['-created_time']
    
    def __unicode__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(
            max_length = 20,
            unique = True
            )
    permissions = models.ManyToManyField(
            'Permission'
            )
    created_time = models.DateTimeField(
            u'创建时间',
            default = datetime.datetime.now,
            auto_now_add = True
            )
    
    class Meta:
        db_table = 'group'
        verbose_name = u'用户组'
        verbose_name_plural = u'用户组'
        ordering = ['-created_time']
    
    def __unicode__(self):
        return self.name


class User(AbstractUser):
    avatar = models.CharField(
            max_length = 200,
            default = '/static/avatar/default.jpg',
            verbose_name = u'头像'
            )
    #权限默认为0，即已注册用户
    privilege = models.CharField(
            max_length = 200,
            default = 0,
            verbose_name = u'权限'
            )
    #表示无小组，其他序号后续添加
    groups = models.ManyToManyField(
            'Group'
            )
    ip_address = models.GenericIPAddressField()
    
    class Meta:
        db_table = 'user'
        #可读性名字（及其复数形式）
        verbose_name = u'用户'
        verbose_name_plural = u'用户'
        ordering = ['-date_joined']
    
    #无需重写__str__，会自动生成
    def __unicode__(self):
        return self.get_username()

    
class Navigation(models.Model):
    name = models.CharField(
            max_length = 30,
            verbose_name = u'导航'
            )
    url = models.CharField(
            max_length = 250,
            verbose_name = u'地址'
            )
    
    created_time = models.DateTimeField(
            u'创建时间',
            default = datetime.datetime.now,
            auto_now_add = True
            )
    
    class Meta:
        db_table = 'section'
        verbose_name = u'导航'
        verbose_name_plural = u'导航'
        ordering = ['-created_time']
    
    def __unicode__(self):
        return self.name
    
    
class Section(models.Model):
    name = models.CharField(
            max_length = 20
            )
    manager = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'section_manager'
            )
    parent_section = models.ForeignKey(
            'self',
            blank = True,
            null = True,
            related_name = 'child_section'
            )
    description = models.CharField(
            max_length = 200,
            verbose_name = u'描述'
            )
    img = models.CharField(
            max_length = 200,
            default = '/static/avatar/default.jpg',
            verbose_name = u'图标'
            )
    content_number = models.IntegerField(
            default = 0
            )
    created_at = models.DateTimeField(
            auto_now_add = True
            )
    updated_at = models.DateTimeField(
            auto_run = True
            )

    class Meta:
        db_table = 'section'
        verbose_name = u'区块'
        verbose_name_plural = u'区块'
        ordering = ['-content_number']
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('section_detail', (), {'section_pk' : self.pk})
    
    
class Post(models.Model):
    title = models.CharField(
            max_length = 20
            )
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'post_author'
            )
    section = models.ForeignKey(
            Section
            )
    view_times = models.IntegerField(
            default = 0
            )
    content_number = models.IntegerField(
            default = 1
            )
    last_response = models.ForeignKey(
            settings.AUTH_USER_MODEL
            )
    created_at = models.DateTimeField(
            auto_now_add = True
            )
    updated_at = models.DateTimeField(
            auto_now = True
            )
    
    class Meta:
        db_table = 'post'
        verbose_name = u'主题帖'
        verbose_name_plural = u'主题帖'
        ordering = ['-created_at']
    
    def __unicode__(self):
        return self.title
    
    def description(self):
        return u' %s 发表了主题帖 %s' % (self.author, self.title)
    
    @models.permalink
    def get_absolute_url(self):
        return ('post_detail', (), {'post_pk' : self.pk})
    
    
class PostPart(models.Model):
    post = models.ForeignKey(
            Post
            )
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'postpart_author'
            )
    parent_postpart = models.ForeignKey(
            'self',
            blank = True,
            null = True,
            related_name = 'child_postpart'
            )
    content = models.TextField()
    created_at = models.DateTimeField(
            auto_now_add = True
            )
    updated_at = models.DateTimeField(
            auto_now = True
            )
    
    class Meta:
        db_table = 'postpart'
        verbose_name = u'间贴'
        verbose_name_plural = u'间贴'
        ordering = ['-created_at']
    
    def __unicode__(self):
        return self.title
    
    def description(self):
        return u' %s 回复了帖子（%s）： %s' % (
                self.author, self.post, 
                self.content)
    
    @models.permalink
    def get_absolute_url(self):
        return ('post_detail', (), {'post_pk' : self.pk})
    

class Comment(models.Model):
    section = models.ForeignKey(
            Section
            )
    star = models.IntegerField(
            default = 3
            )
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'comment_author'
            )
    content = models.TextField()
    created_at = models.DateTimeField(
            auto_now_add = True
            )
    updated_at = models.DateTimeField(
            auto_now = True
            )
    
    class Meta:
        db_table = 'comment'
        verbose_name = u'评论'
        verbose_name_plural = u'评论'
        ordering = ['-created_at']
    
    def __unicode__(self):
        return self.title
    
    def description(self):
        return u' %s 添加了评论（%s）： %s' % (
                self.author, self.section, 
                self.content)
    
    @models.permalink
    def get_absolute_url(self):
        return ('author_detail', (), {'author_pk' : self.pk})
    
    
class Notice(models.Model):
    sender = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'notice_sender'
            )
    receiver = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'notice_receiver'
            )
    content_type = models.ForeignKey(
            ContentType
            )
    object_id = models.PositiveIntegerField()
    event = generic.GenericForeignKey(
            'content_type','object_id'
            )
    status = models.BooleanField(
            default = False
            )
    type = models.IntegerField()
    created_at = models.DateTimeField(
            auto_now_add = True
            )
    updated_at = models.DateTimeField(
            auto_now = True
            )
    class Meta:
        db_table = 'notice'
        verbose_name = u'通知'
        verbose_name_plural = u'通知'
        ordering = ['-created_at']
    
    def __unicode__(self):
        return u' %s 的消息： %s' % (
                self.sender, self.description
                )
    
    def description(self):
        return self.event
    
    def read(self):
       if not self.status:
           self.status = True
    
    
def post_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    section = entity.section
    section.content_number += 1
    section.save()
    
def post_delete(sender, instance, signal, *args, **kwargs):
    entity = instance
    section = entity.section
    section.content_number -= 1
    section.save()

def postpart_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    post = entity.post
    post.content_number += 1
    post.save()
    
def postpart_delete(sender, instance, signal, *args, **kwargs):
    entity = instance
    post = entity.post
    post.content_number -= 1
    post.save()

def comment_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    section = entity.section
    section.content_number += 1
    section.save()
    
def comment_delete(sender, instance, signal, *args, **kwargs):
    entity = instance
    section = entity.section
    section.content_number -= 1
    section.save()
    
def notice_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    event = Notice(
            entity.sender,
            entity.receiver,
            entity,
            0
            )
    event.save()
    
    
    
    
    
    
    
    
    
    
    
    
    
    