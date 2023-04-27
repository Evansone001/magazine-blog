from django.conf import settings
from django.db import models
from django.utils.timezone import now

from blog.models import Article


# Create your models here.

class Comment(models.Model):
    body = models.TextField('text', max_length=300)
    created_time = models.DateTimeField('creation time', default=now)
    last_mod_time = models.DateTimeField('Change the time', default=now)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='author',
        on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article,
        verbose_name='article',
        on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(
        'self',
        verbose_name="superior comments",
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    is_enable = models.BooleanField(
        'whether to display', default=True, blank=False, null=False)

    class Meta:
        ordering = ['-id']
        verbose_name = "Comment"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def __str__(self):
        return self.body

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
