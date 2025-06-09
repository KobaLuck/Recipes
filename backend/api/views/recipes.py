from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeInlineFilter
from api.pagination import DefaultPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers.recipes import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeListSerializer,
    RecipeMinifiedSerializer,
    TagSerializer,
)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class ShortLinkView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        absolute_url = request.build_absolute_uri(recipe.get_short_link())
        return Response(
            {"short-link": absolute_url}, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeInlineFilter

    def get_permissions(self):
        if self.action in ("list", "retrieve", "get_link"):
            return [AllowAny()]
        if self.action in ("favorite", "shopping_cart", "create"):
            return [IsAuthenticated()]
        return [IsAuthorOrReadOnly()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        absolute_url = request.build_absolute_uri(recipe.get_short_link())
        return Response({"short-link": absolute_url})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializers.Serializer(
            data={"user": request.user.id, "recipe": recipe.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            RecipeMinifiedSerializer(
                recipe, context={"request": request}
            ).data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        deleted, _ = Favorite.objects.filter(
            user=request.user, recipe_id=pk).delete()
        if not deleted:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=["post"],
        url_path="shopping_cart",
        permission_classes=[IsAuthenticated])
    def add_to_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializers.Serializer(
            data={"user": request.user.id, "recipe": recipe.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            RecipeMinifiedSerializer(
                recipe, context={"request": request}
            ).data, status=status.HTTP_201_CREATED)

    @add_to_cart.mapping.delete
    def delete_from_cart(self, request, pk=None):
        deleted, _ = ShoppingCart.objects.filter(
            user=request.user, recipe_id=pk).delete()
        if not deleted:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="download_shopping_cart"
    )
    def download_shopping_cart(self, request):
        lines = (
            f"{it['name']} ({it['measurement_unit']}) — {it['total']}"
            for it in request.user.get_shopping_list()
        )
        return Response("\n".join(lines), content_type="text/plain")
