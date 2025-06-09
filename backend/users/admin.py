from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscription, User
from recipes.models import Recipe


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "recipes_count",
        "subscribers_count",
    )
    search_fields = ("email", "username")
    list_filter = ("email", "username", "first_name", "last_name")

    @admin.display(description="Подписчики")
    def subscriber_count(self, obj):
        return obj.subscribers.count()

    @admin.display(description="Рецепты")
    def recipe_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = (
        "user__username",
        "user__email",
        "author__username",
        "author__email",
    )
    list_filter = ("user", "author")
