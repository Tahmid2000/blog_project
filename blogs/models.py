from django.db import models
import datetime
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
import os
from django.utils.deconstruct import deconstructible
from ckeditor.fields import RichTextField
from hitcount.models import HitCountMixin, HitCount
from django.contrib.contenttypes.fields import GenericRelation
# Create your models here.


@deconstructible
class FileRename(object):
    def __init__(self, sub_path, the_type):
        self.the_path = sub_path
        self.the_type = the_type

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # get filename
        if self.the_type == 'blog':
            filename = '{}.{}.{}'.format(
                instance.created_by, instance.title, ext)
        elif self.the_type == 'profile':
            filename = '{}.{}'.format(
                instance.created_by, ext)
        return os.path.join(self.the_path, filename)


profile_pic_rename = FileRename('images/profile_pics/', 'profile')


class UserProfileInfo(models.Model):
    created_by = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField()
    interests = models.CharField(max_length=256)
    profile_pic = models.ImageField(
        upload_to=profile_pic_rename, default="blogs/images/home-bg.jpg")
    github = models.URLField(default=None, null=True,
                             blank=True, max_length=256)
    twitter = models.URLField(default=None, null=True,
                              blank=True, max_length=256)
    portfolio = models.URLField(
        default=None, null=True, blank=True, max_length=256)
    linkedin = models.URLField(
        default=None, null=True, blank=True, max_length=256)

    def __str__(self):
        return self.created_by.username

    def get_absolute_url(self):
        return reverse("blogs:profile", kwargs={"pk": self.pk})


blog_file_rename = FileRename('images/blogs/', 'blog')


class Blog(models.Model):
    class Meta:
        ordering = ['-pub_date']
    title = models.CharField(max_length=256, unique=True)
    subject = models.CharField(max_length=256, null=True)
    body = RichTextField()
    pub_date = models.DateTimeField()
    updated_date = models.DateTimeField(null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    blog_image = models.ImageField(
        upload_to=blog_file_rename, default='blogs/images/post-bg.jpg')
    posted = models.BooleanField(default=1)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='likes')
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')

    def __str__(self):
        return self.title

    def was_published_recently(self):
        return timezone.now() >= self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def get_absolute_url(self):
        return reverse('blogs:detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    """  class Meta:
         ordering = ['-pub_date'] """
    blog = models.ForeignKey(
        Blog, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)
    comment_likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='comment_likes')
    parent = models.ForeignKey(
        'self', null=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.created_by)


class Notification(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, related_name='sender')
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, related_name='receiver')
    blog = models.ForeignKey(
        Blog, on_delete=models.CASCADE, related_name='notifications', null=True)
    content = models.CharField(max_length=256, null=True)

    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class Friend(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, related_name='follower')
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, related_name='following')
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.follower.username + ' follows ' + self.following.username
