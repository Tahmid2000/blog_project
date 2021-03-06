"""blog_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import blogs.views
from django.conf import settings  # add this
from django.conf.urls.static import static  # add this
import notifications.urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', blogs.views.HomeView.as_view(), name="home"),
    path('blogs/', include('blogs.urls'), name='blogs'),
    path('hitcount/', include(('hitcount.urls', 'hitcount'), namespace='hitcount')),
    path('inbox/notifications/',
         include(notifications.urls, namespace='notifications'))
]

if settings.DEBUG:  # add this
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
