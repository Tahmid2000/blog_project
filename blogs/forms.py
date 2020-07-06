from django import forms
from django.core import validators
from django.forms import ModelForm
from .models import UserProfileInfo, Blog
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'rows': 5, 'cols': 20}))
    interests = forms.CharField(required=False)
    profile_pic = forms.ImageField(required=False, error_messages={
        'invalid': ("Image files only")}, widget=forms.FileInput)
    twitter = forms.URLField(required=False)
    portfolio = forms.URLField(required=False)

    class Meta:
        model = UserProfileInfo
        fields = ['bio', 'interests', 'profile_pic', 'twitter', 'portfolio']


class BlogForm(forms.ModelForm):
    blog_image = forms.ImageField(required=False, error_messages={
                                  'invalid': ("Image files only")}, widget=forms.FileInput)

    class Meta:
        model = Blog
        fields = ['title', 'subject', 'body', 'blog_image']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10, 'cols': 59}),
        }
