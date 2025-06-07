from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    avatar = models.ImageField(
        upload_to='users/',
        blank=True, null=True,
        verbose_name='Аватар',
    )
    email = models.EmailField('Почта', unique=True)
    id = models.AutoField(primary_key=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def get_shopping_list(self):
        from recipes.models import RecipeIngredient

        ingredient_qs = RecipeIngredient.objects.filter(
            recipe__in_carts__user=self
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=models.Sum('amount')
        )
        result = []
        for item in ingredient_qs:
            result.append({
                'name': item['ingredient__name'],
                'measurement_unit': item['ingredient__measurement_unit'],
                'total': item['total_amount']
            })
        return result


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
