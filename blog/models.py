import logging
from django.contrib.auth.models import User
from abc import abstractmethod
from accounts.models import BlogUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from mdeditor.fields import MDTextField
from uuslug import slugify

from djangoblog.utils import cache_decorator, cache
from djangoblog.utils import get_current_site

logger = logging.getLogger(__name__)


class LinkShowType(models.TextChoices):
    I = ('i', 'front page')
    L = ('l', 'List')
    P = ('p', 'article page')
    A = ('a', 'Full Site')
    S = ('s', 'Friendship Links Page')


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField('creation time', default=now)
    last_mod_time = models.DateTimeField('Change the time', default=now)

    def save(self, *args, **kwargs):
        is_update_views = isinstance(
            self,
            Article) and 'update_fields' in kwargs and kwargs['update_fields'] == ['views']
        if is_update_views:
            Article.objects.filter(pk=self.pk).update(views=self.views)
        else:
            if 'slug' in self.__dict__:
                slug = getattr(
                    self, 'title') if 'title' in self.__dict__ else getattr(
                    self, 'name')
                setattr(self, 'slug', slugify(slug))
            super().save(*args, **kwargs)

    def get_full_url(self):
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site,
                                            path=self.get_absolute_url())
        return url

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass


class Article(BaseModel):
    """article"""
    STATUS_CHOICES = (
        ('d', 'draft'),
        ('p', 'published'),
    )
    COMMENT_STATUS = (
        ('o', 'Open'),
        ('c', 'closure'),
    )
    TYPE = (
        ('a', 'article'),
        ('p', 'page'),
    )
    title = models.CharField('title', max_length=200, unique=True)
    body = MDTextField('text')
    pub_time = models.DateTimeField(
        'release time', blank=False, null=False, default=now)
    status = models.CharField(
        'article status',
        max_length=1,
        choices=STATUS_CHOICES,
        default='p')
    comment_status = models.CharField(
        'comment status',
        max_length=1,
        choices=COMMENT_STATUS,
        default='o')
    type = models.CharField('type', max_length=1, choices=TYPE, default='a')
    views = models.PositiveIntegerField('Views', default=0)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='author',
        blank=False,
        null=False,
        on_delete=models.CASCADE)
    article_order = models.IntegerField(
        'Sorting, the bigger the number, the higher the front', blank=False, null=False, default=0)
    show_toc = models.BooleanField(
        "Whether to display the toc directory", blank=False, null=False, default=False)
    category = models.ForeignKey(
        'Category',
        verbose_name='Classification',
        on_delete=models.CASCADE,
        blank=False,
        null=False)
    tags = models.ManyToManyField(
        'Tag', verbose_name='label collection', blank=True)

    def body_to_string(self):
        return self.body

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-article_order', '-pub_time']
        verbose_name = "article"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def get_absolute_url(self):
        return reverse('blog:detailbyid', kwargs={
            'article_id': self.id,
            'year': self.created_time.year,
            'month': self.created_time.month,
            'day': self.created_time.day
        })

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        tree = self.category.get_category_tree()
        names = list(map(lambda c: (c.name, c.get_absolute_url()), tree))

        return names

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    def comment_list(self):
        cache_key = 'article_comments_{id}'.format(id=self.id)
        value = cache.get(cache_key)
        if value:
            logger.info('get article comments:{id}'.format(id=self.id))
            return value
        else:
            comments = self.comment_set.filter(is_enable=True).order_by('-id')
            cache.set(cache_key, comments, 60 * 100)
            logger.info('set article comments:{id}'.format(id=self.id))
            return comments

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse('admin:%s_%s_change' % info, args=(self.pk,))

    @cache_decorator(expiration=60 * 100)
    def next_article(self):
        # Next
        return Article.objects.filter(
            id__gt=self.id, status='p').order_by('id').first()

    @cache_decorator(expiration=60 * 100)
    def prev_article(self):
        # Previous
        return Article.objects.filter(id__lt=self.id, status='p').first()


class Category(BaseModel):
    """articleClassification"""
    name = models.CharField('Classification name:', max_length=30, unique=True)
    parent_category = models.ForeignKey(
        'self',
        verbose_name="Further Classification",
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    slug = models.SlugField(default='no-slug', max_length=60, blank=True)
    index = models.IntegerField(
        default=0, verbose_name="Sorting by weight - the bigger the higher the front")

    class Meta:
        ordering = ['-index']
        verbose_name = "Classification"
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse(
            'blog:category_detail', kwargs={
                'category_name': self.slug})

    def __str__(self):
        return self.name

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        """
        Get the parent of Categories recursively
        :return:
        """
        categorys = []

        def parse(category):
            categorys.append(category)
            if category.parent_category:
                parse(category.parent_category)

        parse(self)
        return categorys

    @cache_decorator(60 * 60 * 10)
    def get_sub_categorys(self):
        """
        Get all subsets of the current Categories
        :return:
        """
        categorys = []
        all_categorys = Category.objects.all()

        def parse(category):
            if category not in categorys:
                categorys.append(category)
            childs = all_categorys.filter(parent_category=category)
            for child in childs:
                if category not in categorys:
                    categorys.append(child)
                parse(child)

        parse(self)
        return categorys


class Tag(BaseModel):
    """article tag"""
    name = models.CharField('tag name', max_length=30, unique=True)
    slug = models.SlugField(default='no-slug', max_length=60, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'tag_name': self.slug})

    @cache_decorator(60 * 60 * 10)
    def get_article_count(self):
        return Article.objects.filter(tags__name=self.name).distinct().count()

    class Meta:
        ordering = ['name']
        verbose_name = "Label"
        verbose_name_plural = verbose_name


class Links(models.Model):
    """Links"""

    name = models.CharField('link name', max_length=30, unique=True)
    link = models.URLField('link address')
    sequence = models.IntegerField('to sort', unique=True)
    is_enable = models.BooleanField(
        'whether to display', default=True, blank=False, null=False)
    show_type = models.CharField(
        'display type',
        max_length=1,
        choices=LinkShowType.choices,
        default=LinkShowType.I)
    created_time = models.DateTimeField('creation time', default=now)
    last_mod_time = models.DateTimeField('Change the time', default=now)

    class Meta:
        ordering = ['sequence']
        verbose_name = 'Links'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SideBar(models.Model):
    """Sidebar, you can display some html content"""
    name = models.CharField('title', max_length=100)
    content = models.TextField("content")
    sequence = models.IntegerField('to sort', unique=True)
    is_enable = models.BooleanField('Whether to enable', default=True)
    created_time = models.DateTimeField('creation time', default=now)
    last_mod_time = models.DateTimeField('Change the time', default=now)

    class Meta:
        ordering = ['sequence']
        verbose_name = 'Sidebar'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BlogSettings(models.Model):
    """blog configuration"""
    sitename = models.CharField(
        "website name",
        max_length=200,
        null=False,
        blank=False,
        default='')
    site_description = models.TextField(
        "website description",
        max_length=1000,
        null=False,
        blank=False,
        default='')
    site_seo_description = models.TextField(
        "Website SEO Description", max_length=1000, null=False, blank=False, default='')
    site_keywords = models.TextField(
        "website keywords",
        max_length=1000,
        null=False,
        blank=False,
        default='')
    article_sub_length = models.IntegerField(
        "article abstract length", default=300)
    sidebar_article_count = models.IntegerField(
        "Number of Sidebar articles", default=10)
    sidebar_comment_count = models.IntegerField(
        "Number of Sidebar Comments", default=5)
    article_comment_count = models.IntegerField(
        "number of article comments", default=5)
    show_google_adsense = models.BooleanField(
        'whether to display Google Ads', default=False)
    google_adsense_codes = models.TextField(
        'advertising content', max_length=2000, null=True, blank=True, default='')
    open_site_comment = models.BooleanField(
        'Whether to open website comment function', default=True)
    beiancode = models.CharField(
        'record number',
        max_length=2000,
        null=True,
        blank=True,
        default='')
    analyticscode = models.TextField(
        "website statistics code",
        max_length=1000,
        null=False,
        blank=False,
        default='')
    show_gongan_code = models.BooleanField(
        'whether to display public safety record number', default=False, null=False)
    gongan_beiancode = models.TextField(
        'Public security record number',
        max_length=2000,
        null=True,
        blank=True,
        default='')
    resource_path = models.CharField(
        "Static file save address",
        max_length=300,
        null=False,
        default='/var/www/resource/')

    class Meta:
        verbose_name = 'website configuration'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sitename

    def clean(self):
        if BlogSettings.objects.exclude(id=self.id).count():
            raise ValidationError(_('There can only be one configuration'))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from djangoblog.utils import cache
        cache.clear()
