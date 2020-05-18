from django.contrib import admin
from bubbleworld.models import User, Follow, Navigation, Tag, Section, Post, PostPart, PostPartComment, Comment, CommentReport, Notice, Message

# Register your models here.
admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Navigation)
admin.site.register(Tag)
admin.site.register(Section)
admin.site.register(Post)
admin.site.register(PostPart)
admin.site.register(PostPartComment)
admin.site.register(Comment)
admin.site.register(CommentReport)
admin.site.register(Notice)
admin.site.register(Message)