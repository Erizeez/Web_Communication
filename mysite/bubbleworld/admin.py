from django.contrib import admin
from bubbleworld.models import User, Navigation, Section, Post, PostPart, PostPartComment, Comment, CommentReport

# Register your models here.
admin.site.register(User)
admin.site.register(Navigation)
admin.site.register(Section)
admin.site.register(Post)
admin.site.register(PostPart)
admin.site.register(PostPartComment)
admin.site.register(Comment)
admin.site.register(CommentReport)