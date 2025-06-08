from api.filters import IngredientFilter, RecipeInlineFilter
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from serializers.recipes import (IngredientSerializer,
                                 RecipeCreateUpdateSerializer,
                                 RecipeListSerializer,
                                 RecipeMinifiedSerializer, TagSerializer)

from backend.api.pagination import DefaultPagination
from backend.api.permissions import IsAuthorOrReadOnly


class ShortLinkView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        relative = recipe.get_short_link()
        absolute = request.build_absolute_uri(relative)
        return Response({"short-link": absolute}, status=status.HTTP_200_OK)


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
        if self.action in ["list", "retrieve", "get_link"]:
            return [AllowAny()]
        if self.action in ["favorite", "shopping_cart", "create"]:
            return [IsAuthenticated()]
        return [IsAuthorOrReadOnly()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        out = RecipeListSerializer(recipe, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        out = RecipeListSerializer(recipe, context={"request": request})
        return Response(out.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        if "tags" not in request.data:
            return Response(
                {"tags": ["Это поле обязательно при обновлении."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "ingredients" not in request.data:
            return Response(
                {"ingredients": ["Это поле обязательно при обновлении."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        absolute_url = request.build_absolute_uri(recipe.get_short_link())
        return Response({"short-link": absolute_url})

    @action(
        detail=True,
        methods=["post", "delete"],
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            fav, created = Favorite.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if not created:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        fav = Favorite.objects.filter(user=request.user, recipe=recipe)
        if not fav.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        fav.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"], url_path="shopping_cart")
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            cart, created = ShoppingCart.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if not created:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        cart = ShoppingCart.objects.filter(user=request.user, recipe=recipe)
        if not cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        data = request.user.get_shopping_list()
        txt = "\n".join(
            [
                f"{it['name']} ({it['measurement_unit']}) — {it['total']}"
                for it in data
            ]
        )
        return Response(txt, content_type="text/plain")
