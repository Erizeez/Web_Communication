from django.contrib import admin
from forum.models import User, Navigation, Section, Post, PostPart, Comment, Notice

# Register your models here.
admin.site.register(User)
admin.site.register(Navigation)
admin.site.register(Section)
admin.site.register(Post)
admin.site.register(PostPart)
admin.site.register(Comment)
admin.site.register(Notice)