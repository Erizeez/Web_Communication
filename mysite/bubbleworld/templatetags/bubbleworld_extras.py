from django import template
from bubbleworld.models import User, Section, Post, PostPart, PostPartComment, Comment, CommentReport
from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
register = template.Library()

@register.simple_tag(takes_context=False)
def modelcontent(context):
    if isinstance(context, Section):
        content = context.name
    elif isinstance(context, Comment):
        content = context.content
    elif isinstance(context, Post):
        content = context.title
    elif isinstance(context, PostPart):
        content = context.content
    elif isinstance(context, PostPartComment):
        content = context.content
    else:
        content = -1
    return content

@register.simple_tag(takes_context=False)
def modelurl(context):
    if isinstance(context, Section):
        url = "/bubbleworld/section_detail/?section_pk=" + str(context.pk)
    elif isinstance(context, Comment):
        url = reverse_lazy('comment_detail', kwargs={"comment_pk": context.pk})
    elif isinstance(context, Post):
        url = reverse_lazy('post_detail', kwargs={"post_pk": context.pk})
    elif isinstance(context, PostPart):
        url = reverse_lazy('post_detail', kwargs={"post_pk": context.post.pk})
    elif isinstance(context, PostPartComment):
        url = reverse_lazy('post_detail', kwargs={"post_pk": context.postpart.post.pk})
    else:
        url = -1
    return url


    
