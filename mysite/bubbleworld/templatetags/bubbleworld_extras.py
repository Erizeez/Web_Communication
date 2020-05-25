from django import template
from bubbleworld.models import User, Tag, Section, Post, PostPart, PostPartComment, Comment, CommentReport, Message

register = template.Library()

@register.simple_tag(takes_context=False)
def modeltype(context):
    if isinstance(context, Section):
        typ = 0
    elif isinstance(context, Comment):
        typ = 1
    elif isinstance(context, Post):
        typ = 2
    elif isinstance(context, PostPart):
        typ = 3
    elif isinstance(context, PostPartComment):
        typ = 4
    else:
        typ = -1
    return {'type':typ}
    
