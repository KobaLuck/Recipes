from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from api.constants import (IMAGE_UPLOAD_RECIPE, MAX_ING_NAME,
                           MAX_MEASUREMENT_UNIT, MAX_RECIPE_NAME,
                           MAX_SLUG_LENGTH, MAX_TAG_NAME, MIN_AMOUNT,
                           MIN_COOK_TIME)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        "Название тега",
        max_length=MAX_TAG_NAME,
        unique=True,
    )
    slug = models.SlugField(
        "Слаг тега",
        max_length=MAX_SLUG_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        "Название ингредиента",
        max_length=MAX_ING_NAME,
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=MAX_MEASUREMENT_UNIT,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient_name_unit"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    name = models.CharField(
        "Название рецепта",
        max_length=MAX_RECIPE_NAME,
    )
    image = models.ImageField(
        "Изображение",
        upload_to=IMAGE_UPLOAD_RECIPE,
    )
    text = models.TextField(
        "Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления (мин.)",
        validators=[
            MinValueValidator(
                MIN_COOK_TIME,
                message=f"Время должно быть не менее {MIN_COOK_TIME} минуты."
            )
        ],
    )
    created = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        "Дата обновления",
        auto_now=True,
    )

    class Meta:
        default_related_name = "recipes"
        ordering = ("-created",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name

    def get_short_link(self, request=None):
        relative = reverse("short_link", kwargs={"recipe_id": self.id})
        return request.build_absolute_uri(relative) if request else relative


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        related_name="recipe_ingredients"
    )
    amount = models.PositiveIntegerField(
        "Количество",
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                message=f"Количество должно быть не менее {MIN_AMOUNT}."
            )
        ],
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient"
            ),
        ]

    def __str__(self):
        return f"{self.ingredient.name} в «{self.recipe.name}»: {self.amount}"


class UserRecipeRelation(models.Model):
    """
    Абстрактная базовая модель для отношений User–Recipe:
    избранное, корзина, подписки и т.п.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        abstract = True


class Favorite(UserRecipeRelation):
    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite"
            )
        ]

    def __str__(self):
        return f"{self.user} добавил(а) «{self.recipe}» в избранное"


class ShoppingCart(UserRecipeRelation):
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_shopping_cart"
            )
        ]

    def __str__(self):
        return f"{self.user} добавил(а) «{self.recipe}» в корзину"
