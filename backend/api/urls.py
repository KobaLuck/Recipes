from api.views.recipes import (IngredientViewSet, RecipeViewSet, ShortLinkView,
                               TagViewSet)
from api.views.users import UserViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('r/<int:recipe_id>/', ShortLinkView.as_view(), name='short_link'),

    path('', include(router.urls)),
]
