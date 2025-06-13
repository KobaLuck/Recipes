from django_filters import (NumberFilter, CharFilter, FilterSet,
                            ModelMultipleChoiceFilter, NumberFilter)
from recipes.models import Ingredient, Recipe, Tag


class RecipeInlineFilter(FilterSet):
    author = NumberFilter(field_name="author__id")
    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    is_favorited = NumberFilter(method="filter_favorited")
    is_in_shopping_cart = NumberFilter(method="filter_in_cart")

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_favorited", "is_in_shopping_cart"]

    def filter_favorited(self, queryset, name, value):
        if value == 1 and self.request.user.is_authenticated:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def filter_in_cart(self, queryset, name, value):
        if value == 1 and self.request.user.is_authenticated:
            return queryset.filter(in_carts__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)
