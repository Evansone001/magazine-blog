from django.db import models


# Create your models here.
class commands(models.Model):
    title = models.CharField('command title', max_length=300)
    command = models.CharField('Order', max_length=2000)
    describe = models.CharField('command description', max_length=300)
    created_time = models.DateTimeField('creation time', auto_now_add=True)
    last_mod_time = models.DateTimeField('Change the time', auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = verbose_name


class EmailSendLog(models.Model):
    emailto = models.CharField('recipient', max_length=300)
    title = models.CharField('email title', max_length=2000)
    content = models.TextField('email content')
    send_result = models.BooleanField('result', default=False)
    created_time = models.DateTimeField('creation time', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'mail sending log'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
