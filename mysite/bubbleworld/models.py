#coding:utf-8
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields
from django.db.models import signals
import datetime

# Create your models here.

class Permission(models.Model):
    name = models.CharField(
            max_length = 30,
            unique = True
            )
    access_permission = models.BooleanField(
            default = False
            )
    add_permission = models.BooleanField(
            default = False
            )
    modify_permission = models.BooleanField(
            default = False
            )
    delete_permission = models.BooleanField(
            default = False
            )
    created_time = models.DateTimeField(
            u'创建时间',
            default = datetime.datetime.now
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
            'Permission',
            blank = True,
          #  null = True,
            related_name = 'permissions'
            )
    created_time = models.DateTimeField(
            u'创建时间',
            default = datetime.datetime.now
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
    #权限默认为0，即已注册用户,1为管理员，2为被封禁，-1为游客
    privilege = models.CharField(
            max_length = 200,
            default = 0,
            verbose_name = u'权限'
            )
    follow_to = models.ManyToManyField(
            'self',
            blank = True,
        #   null = True,
            related_name = 'followto'
            )    
    
    groups = models.ManyToManyField(
            'Group',
            blank = True,
         #   null = True,
            related_name = 'groups'
            )
    black_list = models.ManyToManyField(
            'self',
            blank = True,
         #   null = True,
            related_name = 'black_list'
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


class Follow(models.Model):
    sender = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete = models.CASCADE,
            related_name = 'sender',
            )
    receiver = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete = models.CASCADE,
            related_name = 'receiver',
            )
    #0-不允许 1-允许 
    status = models.IntegerField(
            default=1
            )
    created_at = models.DateTimeField(
            auto_now_add=True
            )
    updated_at = models.DateTimeField(
            auto_now=True
            )
    
    class Meta:
        db_table = 'follow'
        verbose_name = u'关注'
        verbose_name_plural = u'关注'
    
    def description(self):
        return u' %s 关注了 %s' % (self.follow_from, self.follow_to)

    
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
            default = datetime.datetime.now
            )
    
    class Meta:
        db_table = 'navigation'
        verbose_name = u'导航'
        verbose_name_plural = u'导航'
        ordering = ['-created_time']
    
    def __unicode__(self):
        return self.name
    
    
class Tag(models.Model):
    name = models.CharField(
            max_length = 20
            )
    created_time = models.DateTimeField(
            u'创建时间',
            default = datetime.datetime.now
            )
    
    class Meta:
        db_table = 'tag'
        verbose_name = u'标签'
        verbose_name_plural = u'标签'
        ordering = ['-created_time']
    
    def __unicode__(self):
        return self.name
    
    
class Section(models.Model):
    name = models.CharField(
            max_length = 20
            )
    users = models.ManyToManyField(
            'User',
            blank = True,
     #       null = True,
            related_name = 'users'
            )
    parent_section = models.ForeignKey(
            'self',
            blank = True,
            null = True,
            on_delete = models.CASCADE,
            related_name = 'section_parent_section',
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
    
    tags = models.ManyToManyField(
            'Tag',
            blank = True,
      #      null = True,
            related_name = 'tags'
            )
    
    created_at = models.DateTimeField(
            auto_now_add = True
            )
    updated_at = models.DateTimeField(
            auto_now = True
            )

    class Meta:
        db_table = 'section'
        verbose_name = u'区块'
        verbose_name_plural = u'区块'
        ordering = ['-content_number']
    
    def __unicode__(self):
        return self.name
    
    
class Post(models.Model):
    title = models.CharField(
            max_length = 20
            )
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete = models.CASCADE,
            related_name = 'post_author',
            )
    section = models.ForeignKey(
            Section,
            on_delete = models.CASCADE,
            related_name = 'post_section',
            )
    view_times = models.IntegerField(
            default = 0
            )
    content_number = models.IntegerField(
            default = 1
            )
    last_response = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete = models.CASCADE,
            related_name = 'last_responce',
            )
    
    upper_placed = models.BooleanField(
            default = False
            )
    #是否加精
    essence = models.BooleanField(
            default = False
            )
    
    tags = models.ManyToManyField(
            'Tag',
            blank = True,
       #     null = True,
            related_name = 'post_tags'
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
    
    
class PostPart(models.Model):
    post = models.ForeignKey(
            Post,
            related_name = 'post',
            on_delete = models.CASCADE
            )
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'postpart_author',
            on_delete = models.CASCADE
            )
    content = models.TextField()
    
    content_number = models.IntegerField(
            default = 1
            )
    last_response = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete = models.CASCADE,
            related_name = 'last_responce',
            )
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

class PostCommennt(models.Model):
    postpart =  models.ForeignKey(
            PostPart,
            related_name = 'postpart',
            on_delete = models.CASCADE
            )
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'postpart_author',
            on_delete = models.CASCADE
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
        verbose_name = u'间贴评论'
        verbose_name_plural = u'间贴评论'
        ordering = ['-created_at']
    
    def __unicode__(self):
        return self.title
    
    def description(self):
        return u' %s 回复了帖子（%s）： %s' % (
                self.author, self.postpart.post, 
                self.content)

class Comment(models.Model):
    section = models.ForeignKey(
            Section,
            related_name = 'comment_section',
            on_delete = models.CASCADE
            )
    star = models.IntegerField(
            default = 3
            )
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'comment_author',
            on_delete = models.CASCADE
            )
    content = models.TextField()
    
    like_number = models.IntegerField(
            default = 0
            )
    dislike_number = models.IntegerField(
            default = 0
            )
    
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
    
    
class CommentReport(models.Model):
    comment = models.ForeignKey(
            Comment,
            related_name = 'commentreport_comment',
            on_delete = models.CASCADE
            )
    status = models.BooleanField(
            default = False
            )
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'commentreport_author',
            on_delete = models.CASCADE
            )
    title = models.CharField(
            max_length = 40
            )
    reason = models.TextField()
    
    created_at = models.DateTimeField(
            auto_now_add = True
            )
    updated_at = models.DateTimeField(
            auto_now = True
            )
    
    class Meta:
        db_table = 'commentreport'
        verbose_name = u'评论举报'
        verbose_name_plural = u'评论举报'
        ordering = ['-created_at']
    
    def __unicode__(self):
        return self.title


#私信
class Message(models.Model):  
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='message_sender',
        on_delete = models.CASCADE
        )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='message_receiver',
        on_delete = models.CASCADE
        )
    content = models.TextField()
    created_at = models.DateTimeField(
            auto_now_add=True
            )
    updated_at = models.DateTimeField(
            auto_now=True
            )

    def description(self):
        return u'%s 向你发送了信息 %s' % (self.sender, self.content)

    class Meta:
        db_table = 'message'
        verbose_name = u'信息'
        verbose_name_plural = u'信息'     
    
class Notice(models.Model):
    sender = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'notice_sender',
            on_delete = models.CASCADE
            )
    receiver = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name = 'notice_receiver',
            on_delete = models.CASCADE
            )
    content_type = models.ForeignKey(
            ContentType,
            related_name = 'content_type',
            on_delete = models.CASCADE
            )
    object_id = models.PositiveIntegerField()
    event = fields.GenericForeignKey(
            'content_type','object_id'
            )
    status = models.BooleanField(
            default = False
            )
    #通知类型：0-系统通知 1-评论 2-follow相关通知 3-私信
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
        if self.event:
            return self.event
        else:
            return "No event"
    
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
    
def follow_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    event = Notice(
            sender = entity.sender,
            receiver = entity.receiver,
            event = entity,
            type = 2
            )
    event.save()
    
def message_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    event = Notice(
        sender = entity.sender,
        receiver = entity.receiver,
        event = entity,
        type = 3
        )
    event.save()
    
#注册消息响应函数
signals.post_save.connect(comment_save, sender=Comment)
signals.post_delete.connect(comment_delete, sender=Comment)
signals.post_save.connect(follow_save, sender=Follow)
signals.post_save.connect(post_save, sender=Post)
signals.post_delete.connect(post_delete, sender=Post)
signals.post_save.connect(postpart_save, sender=PostPart)
signals.post_delete.connect(postpart_delete, sender=PostPart)
signals.post_save.connect(message_save, sender=Message)
    
    
    
    
    
    
    
    
    
    