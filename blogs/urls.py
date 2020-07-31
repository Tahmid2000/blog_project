from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
app_name = 'blogs'
urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('author/login/',
         auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('author/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('author/register/', views.RegisterAuthor.as_view(), name="register"),
    path('search/', views.SearchView.as_view(), name='search'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('author/profile/<int:pk>', views.ProfileView.as_view(), name='profile'),
    path('add/', views.BlogCreate.as_view(), name='blog-add'),
    path('<int:pk>/update/', views.BlogUpdate.as_view(), name='blog-update'),
    path('<int:pk>/delete/', views.BlogDelete.as_view(), name='blog-delete'),
    path('author/profile/<int:pk>/add/',
         views.ProfileCreate.as_view(), name='profile-add'),
    path('author/profile/<int:pk>/update/',
         views.ProfileUpdate.as_view(), name='profile-update'),
    path('author/profile/<int:pk>/view/',
         views.ProfileDetail.as_view(), name='profile-detail'),
    path('<int:pk>/like/', views.likeBlog, name='like-blog'),
    path('<int:pk>/like/comment/<int:id>/',
         views.likeComment, name='like-comment'),
    path(
        '<int:pk>/delete/comment/<int:id>', views.deleteComment, name='delete-comment'),
    path('profile/delete/notif/<int:pk>',
         views.deleteNotif, name='delete-notif'),
    path('user/<int:following>/follow/', views.follow, name='follow'),
]
""" path('all/', views.IndexView.as_view(), name='index'), """
