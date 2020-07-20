from django.contrib import admin
from .models import Blog, UserProfileInfo, Comment, Notification
# Register your models here.
admin.site.register(Blog)
admin.site.register(UserProfileInfo)
admin.site.register(Comment)
admin.site.register(Notification)
