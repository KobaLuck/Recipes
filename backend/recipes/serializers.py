from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.serializers import Base64ImageField, CustomUserResponseSerializer

from .models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserResponseSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source="recipe_ingredients", many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.in_favorites.filter(user=user).exists()
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.in_carts.filter(user=user).exists()
        else:
            return False


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(), required=True, allow_empty=False
    )
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
    )
    image = Base64ImageField(required=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=256)
    text = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = Recipe
        fields = (
            "ingredients", "tags", "image", "name", "text", "cooking_time")

    def validate_ingredients(self, data):

        ids = [item.get("id") for item in data]
        if any(id_ is None for id_ in ids):
            raise serializers.ValidationError(
                'Каждый ингредиент должен иметь ключ "id".'
            )
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Ингредиенты должны быть уникальными.")
        if not Ingredient.objects.filter(id__in=ids).count() == len(ids):
            raise serializers.ValidationError(
                "Указан несуществующий ингредиент.")
        for item in data:
            if "amount" not in item:
                raise serializers.ValidationError(
                    "Укажите количество ингредиента.")
            if not isinstance(item["amount"], int) or item["amount"] < 1:
                raise serializers.ValidationError(
                    'Поле "amount" должно быть целым ≥ 1.'
                )

        return data

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            **validated_data, author=self.context["request"].user
        )
        recipe.tags.set(tags)
        for item in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient_id=item["id"], amount=item["amount"]
            )
        return recipe

    def update(self, instance, validated_data):
        instance.tags.set(validated_data.pop("tags"))
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for item in validated_data.pop("ingredients"):
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=item["id"],
                amount=item["amount"]
            )
        return super().update(instance, validated_data)

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Теги должны быть уникальными.")
        if Tag.objects.filter(id__in=value).count() != len(value):
            raise serializers.ValidationError("Указан несуществующий тег.")
        return value
