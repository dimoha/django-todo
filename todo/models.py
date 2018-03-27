# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.db import models
from django.contrib.auth.models import User, Group
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone

#@python_2_unicode_compatible
class List(models.Model):
    name = models.CharField(max_length=60, verbose_name=u'Название')
    slug = models.SlugField(max_length=60, editable=False)
    group = models.ForeignKey(Group, verbose_name=u'Группа')

    def save(self, *args, **kwargs):
        if not self.id:
            from todo.utils import translit
            self.slug = slugify(translit(self.name))

        super(List, self).save(*args, **kwargs)

    # def __str__(self):
    #     return self.name

    def incomplete_tasks(self):
        # Count all incomplete tasks on the current list instance
        return Item.objects.filter(list=self, completed=0)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = u"Категории"
        verbose_name = u"Категория"

        # Prevents (at the database level) creation of two lists with the same name in the same group
        unique_together = ("group", "slug")


#@python_2_unicode_compatible
class Item(models.Model):
    title = models.CharField(max_length=140, verbose_name=u'Заголовок')
    list = models.ForeignKey(List, verbose_name=u'Категория')
    created_date = models.DateField(auto_now_add=True, verbose_name=u'Дата создания')
    due_date = models.DateField(blank=True, null=True, verbose_name=u'Дедлайн')
    completed = models.BooleanField(default=None, verbose_name=u'Выполнена')
    completed_date = models.DateField(blank=True, null=True, verbose_name=u'Дата выполнения')
    created_by = models.ForeignKey(User, related_name='todo_created_by', verbose_name=u'Автор')
    assigned_to = models.ForeignKey(User, blank=True, null=True, related_name='todo_assigned_to', verbose_name=u'Исполнитель')
    note = models.TextField(blank=True, null=True, verbose_name=u'Описание')
    priority = models.PositiveIntegerField(verbose_name=u'Приоритет')

    # Has due date for an instance of this object passed?
    def overdue_status(self):
        "Returns whether the item's due date has passed or not."
        if self.due_date and datetime.date.today() > self.due_date:
            return 1

    @property
    def smart_title(self):
        return self.title if self.title else "Task #{0}".format(self.pk)

    # def __str__(self):
    #     return self.smart_title


    def get_absolute_url(self):
        return reverse('todo-task_detail', kwargs={'task_id': self.id, })

    # Auto-set the item creation / completed date
    def save(self):
        # If Item is being marked complete, set the completed_date
        if self.completed:
            self.completed_date = datetime.datetime.now()
        super(Item, self).save()

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ["priority"]
        verbose_name_plural = u"Задачи"
        verbose_name = u"Задача"


#@python_2_unicode_compatible
class Comment(models.Model):
    """
    Not using Django's built-in comments because we want to be able to save
    a comment and change task details at the same time. Rolling our own since it's easy.
    """
    author = models.ForeignKey(User, verbose_name=u'Автор')
    task = models.ForeignKey(Item, verbose_name=u'Задача')
    date = models.DateTimeField(default=datetime.datetime.now, verbose_name=u'Дата')
    body = models.TextField(blank=True, verbose_name=u'Текст')

    def snippet(self):
        # Define here rather than in __str__ so we can use it in the admin list_display
        return "{author} - {snippet}...".format(author=self.author, snippet=self.body[:35])

    # def __str__(self):
    #     return self.snippet

    def __unicode__(self):
        return self.author.username

    class Meta:
        verbose_name_plural = u"Комментарии"
        verbose_name = u"Комментарий"

class ItemDocument(models.Model):
    item = models.ForeignKey(Item, verbose_name=u'Задача', related_name='docs_item')
    name = models.CharField(max_length=1024, verbose_name=u'Название')
    document = models.FileField(verbose_name=u'Файл', upload_to=u'docs/', blank=True, null=True)
    create_dt = models.DateTimeField(null=False, blank=False, default=timezone.now, verbose_name=u'Дата создания')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"Документ"
        verbose_name_plural = u"Документы"