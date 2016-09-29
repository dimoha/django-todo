# -*- coding: utf-8 -*-
import datetime
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from todo.models import Item


def mark_done(request, done_items):
    # Check for items in the mark_done POST array. If present, change status to complete.
    for item in done_items:
        i = Item.objects.get(id=item)
        i.completed = True
        i.completed_date = datetime.datetime.now()
        i.save()
        messages.success(request, u"Задача \"{i}\" помечена выполненной.".format(i=i.smart_title))


def undo_completed_task(request, undone_items):
    # Undo: Set completed items back to incomplete
    for item in undone_items:
        i = Item.objects.get(id=item)
        i.completed = False
        i.save()
        messages.success(request, u"Ранее выполненная задача \"{i}\" помечена невыполненной.".format(i=i.smart_title))


def del_tasks(request, deleted_items):
    # Delete selected items
    for item_id in deleted_items:
        i = Item.objects.get(id=item_id)
        messages.success(request, u"Задача \"{i}\" удалена.".format(i=i.smart_title))
        i.delete()


def send_notify_mail(request, new_task):
    # Send email
    email_subject = render_to_string("todo/email/assigned_subject.txt", {'task': new_task})
    email_body = render_to_string(
        "todo/email/assigned_body.txt",
        {'task': new_task, 'site': settings.SITE_DOMAIN, })
    try:
        send_mail(
            email_subject, email_body, new_task.created_by.email,
            [new_task.assigned_to.email], fail_silently=False)
    except:
        messages.error(request, u"Задача сохранена но письмо не отправлено. Свяжитесь с администратором.")


def translit(local_langstring):
    conversion = {
        u'\u0410': 'A',    u'\u0430': 'a',
        u'\u0411': 'B',    u'\u0431': 'b',
        u'\u0412': 'V',    u'\u0432': 'v',
        u'\u0413': 'G',    u'\u0433': 'g',
        u'\u0414': 'D',    u'\u0434': 'd',
        u'\u0415': 'E',    u'\u0435': 'e',
        u'\u0401': 'Yo',   u'\u0451': 'yo',
        u'\u0416': 'Zh',   u'\u0436': 'zh',
        u'\u0417': 'Z',    u'\u0437': 'z',
        u'\u0418': 'I',    u'\u0438': 'i',
        u'\u0419': 'Y',    u'\u0439': 'y',
        u'\u041a': 'K',    u'\u043a': 'k',
        u'\u041b': 'L',    u'\u043b': 'l',
        u'\u041c': 'M',    u'\u043c': 'm',
        u'\u041d': 'N',    u'\u043d': 'n',
        u'\u041e': 'O',    u'\u043e': 'o',
        u'\u041f': 'P',    u'\u043f': 'p',
        u'\u0420': 'R',    u'\u0440': 'r',
        u'\u0421': 'S',    u'\u0441': 's',
        u'\u0422': 'T',    u'\u0442': 't',
        u'\u0423': 'U',    u'\u0443': 'u',
        u'\u0424': 'F',    u'\u0444': 'f',
        u'\u0425': 'H',    u'\u0445': 'h',
        u'\u0426': 'Ts',   u'\u0446': 'ts',
        u'\u0427': 'Ch',   u'\u0447': 'ch',
        u'\u0428': 'Sh',   u'\u0448': 'sh',
        u'\u0429': 'Sch',  u'\u0449': 'sch',
        u'\u042a': '"',    u'\u044a': '"',
        u'\u042b': 'Y',    u'\u044b': 'y',
        u'\u042c': '\'',   u'\u044c': '\'',
        u'\u042d': 'E',    u'\u044d': 'e',
        u'\u042e': 'Yu',   u'\u044e': 'yu',
        u'\u042f': 'Ya',   u'\u044f': 'ya',
    }
    translit_string = []
    for c in local_langstring:
        translit_string.append(conversion.setdefault(c, c))
    return ''.join(translit_string)