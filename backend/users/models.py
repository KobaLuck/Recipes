from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(
        max_length=20,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=20,
        verbose_name='Фамилия',
    )
    username = models.CharField(
        max_length=20,
        verbose_name='Имя пользователя',
        unique=True,
    )
    email = models.EmailField(
        max_length=75,
        unique=True,
        verbose_name='Почта',
    )
    avatar = models.ImageField(
        upload_to='users/',
        blank=True, null=True,
        verbose_name='Аватар',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
