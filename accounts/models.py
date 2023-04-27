from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from djangoblog.utils import get_current_site


# Create your models here.

class BlogUser(AbstractUser):
    nickname = models.CharField('Nick name', max_length=100, blank=True)
    created_time = models.DateTimeField('creation time', default=now)
    last_mod_time = models.DateTimeField('Change the time', default=now)
    source = models.CharField("create source", max_length=100, blank=True)

    def get_absolute_url(self):
        return reverse(
            'blog:author_detail', kwargs={
                'author_name': self.username})

    def __str__(self):
        return self.email

    def get_full_url(self):
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site,
                                            path=self.get_absolute_url())
        return url

    class Meta:
        ordering = ['-id']
        verbose_name = "user"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
