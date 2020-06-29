from django.db import models
import datetime
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.


class UserProfileInfo(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField()
    interests = models.TextField()

    def __str__(self):
        return self.user.username

    """ def get_absolute_url(self):
        return reverse("model_detail", kwargs={"pk": self.pk}) """


class Blog(models.Model):
    title = models.CharField(max_length=256)
    subject = models.CharField(max_length=256)
    body = models.TextField()
    pub_date = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.title

    def was_published_recently(self):
        return timezone.now() >= self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def get_absolute_url(self):
        return reverse('blogs:detail', kwargs={'pk': self.pk})
