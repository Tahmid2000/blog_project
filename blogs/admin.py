from django.contrib import admin
from .models import Blog, UserProfileInfo, Comment, Notification, Friend
# Register your models here.
admin.site.register(Blog)
admin.site.register(UserProfileInfo)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(Friend)
