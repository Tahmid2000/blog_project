from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from .models import Blog, UserProfileInfo, Comment, Notification, Friend
from django.urls import reverse_lazy, reverse, path
from django.contrib.auth.forms import UserCreationForm
from .forms import UserForm, UserProfileForm, BlogForm, CommentForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, views
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .decorators import unauthenticated_user, login_excluded
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
import datetime
from django.contrib.auth.models import User
import json
from django.template import RequestContext
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from hitcount.views import HitCountDetailView
from django.db.models import Count
from notifications.signals import notify


class HomeView(generic.ListView):
    template_name = 'blogs/home.html'
    context_object_name = 'all_blogs'

    def get_context_data(self, **kwargs):
        context = super(generic.ListView, self).get_context_data(**kwargs)
        context.update({
            'user_profiles': UserProfileInfo.objects.all()
        })
        return context

    def get_queryset(self):
        if self.request.user.is_authenticated:
            following_created_by = Friend.objects.filter(
                follower=self.request.user).values('following')
            following_created_by_id = following_created_by.values('id')
        if self.request.user.is_authenticated:
            if Blog.objects.filter(posted=1).filter(Q(created_by__in=following_created_by) | Q(likes__in=following_created_by)).exclude(created_by=self.request.user).distinct().count() > 0:
                return Blog.objects.filter(posted=1).filter(Q(created_by__in=following_created_by) | Q(likes__in=following_created_by)).exclude(created_by=self.request.user).distinct().order_by('-pub_date')
            else:
                return Blog.objects.filter(posted=1).order_by('-pub_date')
        else:
            return Blog.objects.filter(posted=1).order_by('-pub_date')


@login_required(login_url='login')
def author_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('blogs:login'))


class RegisterAuthor(generic.edit.CreateView):
    template_name = "registration/register.html"
    form_class = UserForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('blogs:home')
        return super(RegisterAuthor, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Welcome!')
        return reverse('blogs:login')


class IndexView(generic.ListView):
    paginate_by = 5
    template_name = 'blogs/index.html'
    context_object_name = 'all_blogs'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Blog.objects.filter(posted=1).filter(Q(title__icontains=query) | Q(subject__icontains=query) | Q(body__icontains=query) | Q(created_by__username__icontains=query)).order_by('-pub_date')
        return Blog.objects.filter(posted=1).order_by('-pub_date')


class SearchView(generic.ListView):
    paginate_by = 5
    template_name = 'blogs/search.html'
    context_object_name = 'all_blogs'

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        if query:
            context.update({
                'users': User.objects.all().filter(Q(username__icontains=query)),
            })
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Blog.objects.filter(posted=1).filter(Q(title__icontains=query) | Q(subject__icontains=query) | Q(body__icontains=query) | Q(created_by__username__icontains=query)).order_by('-pub_date')
        else:
            return Blog.objects.none()


@method_decorator(login_required, name='post')
class DetailView(HitCountDetailView, generic.edit.FormMixin):
    model = Blog
    template_name = 'blogs/detail.html'
    form_class = CommentForm
    count_hit = True

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().created_by != self.request.user and self.get_object().posted == 0:
            return redirect('blogs:home')
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blogs:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context.update({
            'comments': Comment.objects.filter(blog=self.kwargs['pk'], parent=None).order_by('-pub_date'),
            'like_count': self.get_object().likes.all().count,
            'likedpost': self.get_object().likes.filter(pk=self.request.user.id).exists()
        })
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('blogs:login')
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        f = form.save(commit=False)
        f.blog = self.get_object()
        parentID = self.request.POST.get('parent_id')
        if parentID:
            f.parent = get_object_or_404(Comment, pk=parentID)
        f.created_by = self.request.user
        f.pub_date = datetime.datetime.now()
        f.save()
        if self.request.user != f.blog.created_by:
            notif = Notification(
                sender=self.request.user, receiver=f.blog.created_by, blog=f.blog, content="commented on your post")
            notif.save()
        if f.parent:
            if self.request.user != f.parent.created_by:
                notif = Notification(
                    sender=self.request.user, receiver=f.parent.created_by, blog=f.blog, content="replied to your comment on")
                notif.save()
        return super().form_valid(form)


@login_required
def likeBlog(request, *args, **kwargs):
    user = request.user
    blog = get_object_or_404(Blog, pk=kwargs['pk'])
    response_data = {}
    if blog.likes.filter(pk=user.id).exists():
        blog.likes.remove(request.user)
        response_data['status'] = 'unliked'
        response_data['likedpost'] = False
        response_data['like_change'] = -1
    else:
        blog.likes.add(request.user)
        response_data['status'] = 'liked'
        response_data['likedpost'] = True
        response_data['like_change'] = 1
        if request.user != blog.created_by:
            notif = Notification(
                sender=request.user, receiver=blog.created_by, blog=blog, content="liked your post")
            notif.save()

    return JsonResponse(response_data, safe=False)


@login_required
def likeComment(request, *args, **kwargs):
    user = request.user
    comment = get_object_or_404(
        Comment, pk=kwargs['id'])
    response_data = {}
    if comment.comment_likes.filter(pk=user.id).exists():
        comment.comment_likes.remove(user)
        response_data['status'] = 'unliked'
        response_data['likedpost'] = False
        response_data['like_change'] = -1
    else:
        comment.comment_likes.add(user)
        response_data['status'] = 'liked'
        response_data['likedpost'] = True
        response_data['like_change'] = 1
        if request.user != comment.created_by:
            notif = Notification(
                sender=request.user, receiver=comment.created_by, blog=comment.blog, content="liked your comment on")
            notif.save()
    return JsonResponse(response_data, safe=False)


@login_required
def deleteComment(request, *args, **kwargs):
    comment = get_object_or_404(Comment, pk=kwargs['id'])
    if request.user == comment.created_by:
        blog = comment.blog
        comment.delete()
        print(blog.comments.count())
        return JsonResponse({'deleted': True, 'count': blog.comments.count()})
    return redirect('blogs:detail', kwargs['pk'])


@login_required
def deleteNotif(request, *args, **kwargs):
    notif = get_object_or_404(Notification, pk=kwargs['pk'])
    if notif.receiver == request.user:
        notif.delete()
        return JsonResponse({'deleted': True}, safe=False)
    else:
        return redirect('blogs:profile', request.user.pk)


@ method_decorator(login_required, name='dispatch')
class BlogCreate(generic.edit.CreateView):
    model = Blog
    template_name = 'blogs/blog_create.html'
    form_class = BlogForm

    def form_valid(self, form):
        f = form.save(commit=False)
        f.created_by = self.request.user
        f.pub_date = datetime.datetime.now()
        f.save()
        return super().form_valid(form)


@ method_decorator(login_required, name='dispatch')
class BlogUpdate(UserPassesTestMixin, generic.edit.UpdateView):
    def test_func(self):
        return self.request.user == self.get_object().created_by

    def handle_no_permission(self):
        return redirect('blogs:profile', self.request.user.pk)
    model = Blog
    template_name = 'blogs/blog_update.html'
    form_class = BlogForm

    def form_valid(self, form):
        f = form.save(commit=False)
        if self.get_object().posted != f.posted:
            f.pub_date = datetime.datetime.now()
        else:
            f.updated_date = datetime.datetime.now()
        f.save()
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class BlogDelete(UserPassesTestMixin, generic.edit.DeleteView):
    def test_func(self):
        return self.request.user == self.get_object().created_by

    def handle_no_permission(self):
        return redirect('blogs:profile', self.request.user.pk)
    model = Blog
    template_name = 'blogs/blog_delete.html'

    def get_success_url(self):
        return reverse_lazy('blogs:profile', kwargs={'pk': self.request.user.pk})


@ method_decorator(login_required, name='dispatch')
class ProfileView(generic.ListView):
    paginate_by = 5
    template_name = 'blogs/profile.html'
    context_object_name = 'all_blogs'

    def get_context_data(self, **kwargs):
        context = super(generic.ListView, self).get_context_data(**kwargs)
        context.update({
            'user_profile': UserProfileInfo.objects.filter(created_by=self.request.user).first(),
            'drafts': Blog.objects.all().filter(created_by=self.request.user, posted=0).order_by('-pub_date'),
            'likes': Blog.objects.all().filter(likes__in=[self.request.user], posted=1).order_by('-pub_date'),
            'like_count': Blog.objects.all().filter(created_by=self.request.user, posted=1, likes__isnull=False).values('likes').count(),
            'blogs_count': Blog.objects.all().filter(created_by=self.request.user, posted=1).count(),
            'notifs': Notification.objects.filter(receiver=self.request.user).order_by('-pub_date'),
            'followers': Friend.objects.filter(following=self.request.user).order_by('-pub_date'),
            'following': Friend.objects.filter(follower=self.request.user).order_by('-pub_date'),
        })
        return context

    def get_queryset(self):
        return Blog.objects.all().filter(created_by=self.request.user, posted=1).order_by('-pub_date')


class ProfileDetail(UserPassesTestMixin, generic.ListView):
    def test_func(self):
        return self.request.user != User.objects.filter(pk=self.kwargs['pk']).first()

    def handle_no_permission(self):
        return redirect('blogs:profile', self.request.user.pk)
    paginate_by = 5
    template_name = 'profiles/profile_detail.html'
    context_object_name = 'all_blogs'
    model = User

    def get_context_data(self, **kwargs):
        context = super(generic.ListView, self).get_context_data(**kwargs)
        context.update({
            'user_detail': User.objects.filter(pk=self.kwargs['pk']).first(),
            'user_profile': UserProfileInfo.objects.filter(created_by=self.kwargs['pk']).first(),
            'user_name': User.objects.filter(pk=self.kwargs['pk']).first().username,
            'like_count': Blog.objects.all().filter(created_by=self.kwargs['pk'], posted=1, likes__isnull=False).values('likes').count(),
            'blogs_count': Blog.objects.all().filter(created_by=self.kwargs['pk'], posted=1).count(),
            'followers': Friend.objects.filter(following=self.kwargs['pk']).order_by('-pub_date'),
            'following': Friend.objects.filter(follower=self.kwargs['pk']).order_by('-pub_date'),
        })
        return context

    def get_queryset(self):
        return Blog.objects.all().filter(created_by=self.kwargs['pk'], posted=1).order_by('-pub_date')


@ method_decorator(login_required, name='dispatch')
class ProfileCreate(generic.edit.CreateView):
    model = UserProfileInfo
    template_name = 'profiles/profile_create.html'
    form_class = UserProfileForm

    def form_valid(self, form):
        f = form.save(commit=False)
        f.created_by = self.request.user
        f.save()
        return super().form_valid(form)


@ method_decorator(login_required, name='dispatch')
class ProfileUpdate(UserPassesTestMixin, generic.edit.UpdateView):
    def test_func(self):
        return self.request.user == self.get_object().created_by

    def handle_no_permission(self):
        return redirect('blogs:profile', self.request.user.pk)
    model = UserProfileInfo
    template_name = 'profiles/profile_update.html'
    form_class = UserProfileForm


@login_required
def follow(request, *args, **kwargs):
    follower = request.user
    following = get_object_or_404(User, pk=kwargs['following'])
    response_data = {}
    if follower != following:
        if Friend.objects.filter(follower=follower, following=following).count() > 0:
            response_data['status'] = 0
            Friend.objects.filter(
                follower=follower, following=following).delete()
        else:
            f = Friend(follower=follower, following=following)
            f.save()
            notif = Notification(
                sender=follower, receiver=following, blog=None, content="followed you")
            notif.save()
            response_data['status'] = 1
    return JsonResponse(response_data)


""" @method_decorator(login_required, name='dispatch')
class ProfileDelete(UserPassesTestMixin, generic.edit.DeleteView):
    def test_func(self):
        return self.request.user == self.get_object().created_by

    def handle_no_permission(self):
        return redirect('blogs:profile')
    model = UserProfileInfo
    template_name = 'profiles/profile_delete.html'
    success_url = reverse_lazy('blogs:profile') """
