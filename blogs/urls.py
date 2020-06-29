from django.urls import path, include
from . import views

app_name = 'blogs'
urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('author/', include('django.contrib.auth.urls')),
    path('author/register/', views.RegisterAuthor.as_view(), name="register"),
    path('all/', views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name="about"),
    path('contact/', views.ContactView.as_view(), name="contact"),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('author/profile/', views.ProfileView.as_view(), name='profile'),
    path('add/', views.BlogCreate.as_view(), name='blog-add'),
    path('<int:pk>/', views.BlogUpdate.as_view(), name='blog-update'),
    path('<int:pk>/delete/', views.BlogDelete.as_view(), name='blog-delete'),
]
""" path('author/login/', views.LoginAuthor.as_view(), name="login"),
path('author/register/', views.RegisterAuthor.as_view(), name="register"),
path('author/logout/', views.author_logout, name="logout"), """
