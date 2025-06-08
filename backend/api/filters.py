from django_filters import (BaseInFilter, BooleanFilter, CharFilter, FilterSet,
                            ModelMultipleChoiceFilter, NumberFilter)
from recipes.models import Ingredient, Recipe, Tag


class CharInFilter(BaseInFilter, CharFilter):
    pass


class RecipeInlineFilter(FilterSet):
    author = NumberFilter(field_name="author__id")
    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    is_favorited = BooleanFilter(method="filter_favorited")
    is_in_shopping_cart = BooleanFilter(method="filter_in_cart")

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_favorited", "is_in_shopping_cart"]

    def filter_favorited(self, queryset, name, value):
        some = ["true", "1", "True", 1]
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if str(value).lower() in some else queryset
        if value in some:
            return queryset.filter(in_favorites__user=user)
        return queryset

    def filter_in_cart(self, queryset, name, value):
        some = ["true", "1", "True", 1]
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if str(value).lower() in some else queryset
        if value in some:
            return value
        return queryset


class IngredientFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ["name"]
