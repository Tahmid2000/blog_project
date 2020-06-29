from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from .models import Blog, UserProfileInfo
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import UserCreationForm
from .forms import UserForm, UserProfileForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, views
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.


class HomeView(generic.ListView):
    template_name = 'blogs/home.html'
    context_object_name = 'all_blogs'

    def get_queryset(self):
        return Blog.objects.order_by('-pub_date')[:5]


@login_required(login_url='login')
def author_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('blogs:login'))


class RegisterAuthor(generic.edit.CreateView):
    template_name = "registration/register.html"
    form_class = UserForm

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Author created.')
        return reverse('blogs:login')


class IndexView(generic.ListView):
    template_name = 'blogs/index.html'
    context_object_name = 'all_blogs'

    def get_queryset(self):
        return Blog.objects.order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Blog
    template_name = 'blogs/detail.html'


@method_decorator(login_required, name='dispatch')
class ProfileView(generic.ListView):
    template_name = 'blogs/profile.html'
    context_object_name = 'all_blogs'

    def get_queryset(self):
        return Blog.objects.all().filter(created_by=self.request.user)


@method_decorator(login_required, name='dispatch')
class BlogCreate(generic.edit.CreateView):
    model = Blog
    template_name = 'blogs/blog_create.html'
    fields = ['title', 'subject', 'body', 'pub_date']

    def form_valid(self, form):
        f = form.save(commit=False)
        f.created_by = self.request.user
        f.save()
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class BlogUpdate(generic.edit.UpdateView):
    model = Blog
    template_name = 'blogs/blog_create.html'
    fields = ['title', 'subject', 'body', 'pub_date']


@method_decorator(login_required, name='dispatch')
class BlogDelete(generic.edit.DeleteView):
    model = Blog
    #template_name = 'blogs/blog_create.html'
    success_url = reverse_lazy('Blog-list')


class AboutView(generic.TemplateView):
    template_name = 'blogs/about.html'


class ContactView(generic.TemplateView):
    template_name = 'blogs/contact.html'
