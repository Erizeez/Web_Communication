#coding:utf-8
from django import forms
from forum.models import User, Post, PostPart, Comment, CommentReport, Message


class LoginUserForm(forms.ModelForm):
    error_messages = {
            'mismatch_password':u'两次输入的密码不一致',
            'duplicate_username':u'此用户已存在',
            'duplicate_email':u'此邮箱已被注册'
            }
    
    username = forms.RegexField(
            max_length = 25,
            regex = r'[\w?!.@+-]+$',
            error_messages = {
                    'invalid':u'只能包含字母、数字和字符?!.@+-',
                    'required':u'用户名不能为空'
                    }
            )
    
    email = forms.EmailField(
            error_messages = {
                    'invalid':u'邮箱格式错误',
                    'required':u'邮箱不能为空'
                    }
            )
    
    password = forms.CharField(
            widget=forms.PasswordInput,
            error_messages={
                    'required': u"密码不能为空"
                    }
            )
    
    confirm_password = forms.CharField(
            widget=forms.PasswordInput,
            error_messages={
                    'required': u"密码不能为空"
                    }
            )
    
    class Meta:
        model = User
        fields = (
                'username',
                'email'
                )
        
    #clean_xxxx 读取处理相应值
    
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User._default_manager.get(username = username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicat_username'])
        
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password and password and confirm_password


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = (
                'content'
                )
        
class 
