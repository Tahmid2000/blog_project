from django import template

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
