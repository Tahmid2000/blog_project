from django import template
from blogs.models import Notification, Friend
register = template.Library()


@register.simple_tag
def is_liked(comment, userID):
    return comment.comment_likes.filter(pk=userID).exists()


@register.simple_tag
def liked_this_blog(blog, userID):
    return blog.likes.filter(pk=userID).exists()


@register.simple_tag
def commented_this_blog(blog, user):
    return blog.comments.filter(created_by=user).count() > 0


@register.simple_tag
def notif_count(user):
    return Notification.objects.filter(receiver=user).count()
# blogs/profile/delete/notif/16


@register.simple_tag
def isFollowing(user1, user2):
    return Friend.objects.filter(follower=user1, following=user2).count() > 0
