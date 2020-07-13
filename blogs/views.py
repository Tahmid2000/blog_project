from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from .models import Blog, UserProfileInfo, Comment
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
        return Blog.objects.filter(posted=1).order_by('-pub_date')[:5]


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
        messages.add_message(self.request, messages.SUCCESS, 'Author created!')
        return reverse('blogs:login')


class IndexView(generic.ListView):
    paginate_by = 5
    template_name = 'blogs/index.html'
    context_object_name = 'all_blogs'

    def get_queryset(self):
        return Blog.objects.filter(posted=1).order_by('-pub_date')


@method_decorator(login_required, name='post')
class DetailView(generic.DetailView, generic.edit.FormMixin):
    model = Blog
    template_name = 'blogs/detail.html'
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().created_by != self.request.user and self.get_object().posted == 0:
            return redirect('blogs:home')
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blogs:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(generic.DetailView, self).get_context_data(**kwargs)
        context.update({
            'comments': Comment.objects.filter(blog=self.kwargs['pk']).order_by('-pub_date'),
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
        f.created_by = self.request.user
        f.pub_date = datetime.datetime.now()
        f.save()
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
    return JsonResponse(response_data, safe=False)


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
        """ if not self.get_object().posted:
            f.pub_date = datetime.datetime.now()
        else: """
        if self.get_object().posted != f.posted:
            f.pub_date = datetime.datetime.now()
        else:
            f.updated_date = datetime.datetime.now()
        f.save()
        return super().form_valid(form)


@ method_decorator(login_required, name='dispatch')
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
            'drafts': Blog.objects.all().filter(created_by=self.request.user, posted=0).order_by('-pub_date')
        })
        return context

    def get_queryset(self):
        return Blog.objects.all().filter(created_by=self.request.user, posted=1).order_by('-pub_date')


class ProfileDetail(generic.ListView):
    paginate_by = 5
    template_name = 'profiles/profile_detail.html'
    context_object_name = 'all_blogs'
    model = User

    def get_context_data(self, **kwargs):
        context = super(generic.ListView, self).get_context_data(**kwargs)
        context.update({
            'user_profile': UserProfileInfo.objects.filter(created_by=self.kwargs['pk']).first(),
            'user_name': str(Blog.objects.all().filter(created_by=self.kwargs['pk'], posted=1).first().created_by)
        })
        return context

    def get_queryset(self):
        return Blog.objects.all().filter(created_by=self.kwargs['pk']).order_by('-pub_date')


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


""" @method_decorator(login_required, name='dispatch')
class ProfileDelete(UserPassesTestMixin, generic.edit.DeleteView):
    def test_func(self):
        return self.request.user == self.get_object().created_by

    def handle_no_permission(self):
        return redirect('blogs:profile')
    model = UserProfileInfo
    template_name = 'profiles/profile_delete.html'
    success_url = reverse_lazy('blogs:profile') """
