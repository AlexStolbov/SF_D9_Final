from datetime import datetime
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver  # импортируем нужный декоратор
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Post


@receiver(post_save, sender=Post)
def notify_of_post(sender, instance, created, **kwargs):
    post_description = f' {instance.title} {instance.created.strftime("%d %m %Y")}'
    if created:
        subject = post_description
    else:
        subject = f'Post changed for {post_description}'

    send_mail_to_subscriber(instance, subject)


def send_mail_to_subscriber(post: Post, subject: str):
    """
    При создании новости подписчикам этой категории автоматически отправляется сообщение о пополнении в разделе.
    """
    domain = settings.CURRENT_HOST
    for category in post.category.all():
        for current_user in category.subscribers.all():
            html_content = render_to_string(
                'news_create_email.html',
                {
                    'post': post,
                    'domain': domain,
                }
            ) + f'\nЗдравствуй, {current_user.username}. Новая статья в твоём любимом разделе!';

            msg = EmailMultiAlternatives(
                subject=subject,
                body='',
                from_email='',
                to=[current_user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()


@receiver(pre_save, sender=Post)
def control_of_post(sender, instance, **kwargs):
    """
    Один пользователь не может публиковать более трёх новостей в сутки
    """
    today = datetime.now()
    start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    finish = datetime(today.year, today.month, today.day, 23, 59, 59, 999999, tzinfo=timezone.utc)

    posted_today = Post.objects.filter(author=instance.author).filter(created__range=[start, finish])

    if len(posted_today) >= 3:
        # ToDo попытаться не выбрасывать исключение, а отменить запись
        raise ValueError('Не более 3 новостей в день')


@receiver(post_save, sender=User)
def new_user_greetings(sender, instance: User, created, **kwargs):
    if created:
        send_mail(
            subject=f'Приветствуем на портале новостей  {instance.username}',
            message='',
            from_email='',
            recipient_list=[instance.email]
        )
