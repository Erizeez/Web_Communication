#coding:utf-8
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import signals
import datetime

# Create your models here.

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
    group = models.CharField(
            max_length = 200,
            default = 0,
            verbose_name = u'小组'
            )
    
    class Meta:
        db_table = 'user'
        #可读性名字（及其复数形式）
        verbose_name = u'用户'
        verbose_name_plural = u'用户'
        ordering = ['-date_joined']
    
    #无需重写__str__，会自动生成
    def __unicode__(self):
        return self.get_username()
    
    
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
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_run = True)

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
    section = 
    view_times = models.IntegerField(
            default = 0
            )
    content_quantity = models.IntegerField(
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
        ordering = ['-created-at']
    
    def __unicode__(self):
        return self.title
    
    def description(self):
        return u' %s 发表了主题帖 %s' % (self.author, self.title)
    
    @models.permalink
    def get_absolute_url(self):
        return ('post_detail', (), {'post_pk' : self.pk})
    
    
class Comment(models.Model):
    
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'article_author'
            )
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    