from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from . import resources


class Likeable(models.Model):
    """
    Хранит рейтинг и методы его увеличения и уменьшения.
    Отрицательный рейтинг допусти.
    """

    class Meta:
        abstract = True

    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


class Author(models.Model):
    """
    Авторы.
    Поля:
        связь «один к одному» с встроенной моделью пользователей User;
        рейтинг пользователя. Ниже будет дано описание того, как этот рейтинг можно посчитать.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        """
        Обновляет рейтинг пользователя, переданный в аргумент этого метода:
            суммарный рейтинг каждой статьи автора умножается на 3;
            суммарный рейтинг всех комментариев автора;
            суммарный рейтинг всех комментариев к статьям автора.
        """
        posts = Post.objects.filter(author=self)
        posts_rating = 0
        all_comments_rating = 0
        for post in posts:
            posts_rating += post.rating * 3
            all_post_comment = Comment.objects.filter(post=post)
            for comment in all_post_comment:
                all_comments_rating += comment.rating

        comments_rating = Comment.objects.filter(user=self.user).aggregate(Sum('rating'))

        self.rating = posts_rating + all_comments_rating + comments_rating
        self.save()


class Category(models.Model):
    """
    Категории новостей/статей — темы, которые они отражают (спорт, политика, образование и т. д.).
    Имеет единственное поле: название категории. Поле уникальное.
    """
    name = models.CharField(max_length=100, default="", unique=True)
    subscribers = models.ManyToManyField(User, through='SubscribersOfNews')

    def __str__(self):
        return self.name


class Post(Likeable):
    """
    Эта модель должна содержать в себе статьи и новости, которые создают пользователи.
    Каждый объект может иметь одну или несколько категорий.
    Соответственно, модель должна включать следующие поля:
        связь «один ко многим» с моделью Author;
        поле с выбором — «статья» или «новость»;
        автоматически добавляемая дата и время создания;
        связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory);
        заголовок статьи/новости;
        текст статьи/новости;
        рейтинг статьи/новости.
    """
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=resources.POST_TYPE, default=resources.post_type_news)
    created = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=300)
    content = models.TextField(default="")

    def __str__(self):
        return f'{self.title}: {self.author} (price:{self.preview()})'

    def preview(self):
        """
        Возвращает первые 124 символа статьи дополняя многоточием
        """
        max_len = 124
        suffix = '...' if len(self.content) > max_len else ''
        return f'{self.content[:max_len]}{suffix}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # ToDo сделать контроль не более 3 записей от автора в день, вместо pre_save
        super().save(force_insert, force_update, using, update_fields)


class PostCategory(models.Model):
    """
    Промежуточная модель для связи «многие ко многим»:
        связь «один ко многим» с моделью Post;
        связь «один ко многим» с моделью Category.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(Likeable):
    """
    Под каждой новостью/статьёй можно оставлять комментарии, поэтому необходимо организовать их способ хранения тоже.
    Модель будет иметь следующие поля:
        связь «один ко многим» с моделью Post;
        связь «один ко многим» со встроенной моделью User (комментарии может оставить любой пользователь,
            необязательно автор);
        текст комментария;
        дата и время создания комментария;
        рейтинг комментария.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(default="")
    created = models.DateTimeField(auto_now_add=True)


class SubscribersOfNews(models.Model):
    """
    Подписчики на новости данной категории
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
