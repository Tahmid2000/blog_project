from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from .models import Blog, UserProfileInfo
from django.urls import reverse_lazy, reverse, path
from django.contrib.auth.forms import UserCreationForm
from .forms import UserForm, UserProfileForm, BlogForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, views
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .decorators import unauthenticated_user, login_excluded
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
import datetime
from django.contrib.auth.models import User
# Create your views here.


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
        return Blog.objects.order_by('-pub_date')[:5]


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
        return Blog.objects.order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Blog
    template_name = 'blogs/detail.html'


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class BlogUpdate(UserPassesTestMixin, generic.edit.UpdateView):
    def test_func(self):
        return self.request.user == self.get_object().created_by

    def handle_no_permission(self):
        return redirect('blogs:profile', self.request.user.pk)
    model = Blog
    template_name = 'blogs/blog_update.html'
    form_class = BlogForm


@method_decorator(login_required, name='dispatch')
class BlogDelete(UserPassesTestMixin, generic.edit.DeleteView):
    def test_func(self):
        return self.request.user == self.get_object().created_by

    def handle_no_permission(self):
        return redirect('blogs:profile', self.request.user.pk)
    model = Blog
    template_name = 'blogs/blog_delete.html'

    def get_success_url(self):
        return reverse_lazy('blogs:home')


@method_decorator(login_required, name='dispatch')
class ProfileView(generic.ListView):
    paginate_by = 5
    template_name = 'blogs/profile.html'
    context_object_name = 'all_blogs'

    def get_context_data(self, **kwargs):
        context = super(generic.ListView, self).get_context_data(**kwargs)
        context.update({
            'user_profile': UserProfileInfo.objects.filter(created_by=self.request.user).first()
        })
        return context

    def get_queryset(self):
        return Blog.objects.all().filter(created_by=self.request.user).order_by('-pub_date')


class ProfileDetail(generic.ListView):
    paginate_by = 5
    template_name = 'profiles/profile_detail.html'
    context_object_name = 'all_blogs'
    model = User

    def get_context_data(self, **kwargs):
        context = super(generic.ListView, self).get_context_data(**kwargs)
        context.update({
            'user_profile': UserProfileInfo.objects.filter(created_by=self.kwargs['pk']).first(),
            'user_name': str(Blog.objects.all().filter(created_by=self.kwargs['pk']).first().created_by)
        })
        return context

    def get_queryset(self):
        return Blog.objects.all().filter(created_by=self.kwargs['pk']).order_by('-pub_date')


@method_decorator(login_required, name='dispatch')
class ProfileCreate(generic.edit.CreateView):
    model = UserProfileInfo
    template_name = 'profiles/profile_create.html'
    form_class = UserProfileForm

    def form_valid(self, form):
        f = form.save(commit=False)
        f.created_by = self.request.user
        f.save()
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
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
