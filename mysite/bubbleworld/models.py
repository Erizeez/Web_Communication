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
    
    
class Article(models.Model):
    title = models.CharField(
            max_length = 30
            )
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'article_author'
            )
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    