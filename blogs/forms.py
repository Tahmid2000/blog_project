from django import forms
from django.core import validators
from django.forms import ModelForm
from .models import UserProfileInfo, Blog, Comment
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for fieldname in ['interests', 'twitter', 'portfolio']:
            self.fields[fieldname].required = False
    bio = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'rows': 5, 'cols': 20}))
    profile_pic = forms.ImageField(required=False, error_messages={
        'invalid': ("Image files only")}, widget=forms.FileInput)



    class Meta:
        model = UserProfileInfo
        fields = ['bio', 'interests', 'profile_pic', 'twitter', 'portfolio']


class BlogForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlogForm, self).__init__(*args, **kwargs)
        self.fields['subject'].required = False
    blog_image = forms.ImageField(required=False, error_messages={
                                  'invalid': ("Image files only")}, widget=forms.FileInput)

    class Meta:
        model = Blog
        fields = ['title', 'subject', 'body', 'blog_image', 'posted']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10, 'cols': 59}),
        }


class CommentForm(forms.ModelForm):
    body = forms.CharField(label='<strong>Comment</strong>', widget=forms.Textarea(
        attrs={'rows': 5, 'cols': 15}))

    class Meta:
        model = Comment
        fields = ['body']
