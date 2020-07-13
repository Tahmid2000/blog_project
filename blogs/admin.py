from django.contrib import admin
from .models import Blog, UserProfileInfo, Comment
# Register your models here.
admin.site.register(Blog)
admin.site.register(UserProfileInfo)
admin.site.register(Comment)
