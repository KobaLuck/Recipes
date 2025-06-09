from django.contrib import admin

from recipes.models import RecipeIngredient

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    validate_min = True
    verbose_name = "Ингредиент"
    verbose_name_plural = "Ингредиенты"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "id")
    search_fields = ("name", "slug")
    list_filter = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]
    list_display = ("name", "author", "favorites_count", "created", "id")
    search_fields = ("name", "author__username", "author__email")
    list_filter = ("author", "tags")
    readonly_fields = ("favorites_count",)

    @admin.display(description="В избранном")
    def favorites_count(self, obj):
        return obj.in_favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user",)
