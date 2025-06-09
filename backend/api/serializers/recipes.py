from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from api.serializers.users import UserResponseSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientCreateSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserResponseSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
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
        read_only_fields = fields

    def get_ingredients(self, obj):
        queryset = RecipeIngredient.objects.filter(recipe=obj)
        return [
            {
                "id": ri.ingredient.id,
                "name": ri.ingredient.name,
                "measurement_unit": ri.ingredient.measurement_unit,
                "amount": ri.amount,
            }
            for ri in queryset
        ]

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        return obj.in_favorites.filter(
            user=user).exists() if user.is_authenticated else False

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        return obj.in_carts.filter(
            user=user).exists() if user.is_authenticated else False


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ("ingredients", "tags", "image", "cooking_time")

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            author=self.context["request"].user,
            **validated_data
        )
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ing["id"],
                amount=ing["amount"],
            )
            for ing in ingredients
        ])
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance.tags.set(tags)
        instance.recipe_ingredients.clear()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=instance,
                ingredient=ing["id"],
                amount=ing["amount"],
            )
            for ing in ingredients
        ])
        return super().update(instance, validated_data)

    def validate(self, data):
        ing_ids = [ing["id"].id for ing in data.get("ingredients", [])]
        if len(ing_ids) != len(set(ing_ids)):
            raise serializers.ValidationError(
                "Ингредиенты должны быть уникальными.")
        return data
