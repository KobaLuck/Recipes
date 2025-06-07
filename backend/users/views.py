from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from core.pagination import DefaultPagination
from .models import Subscription
from .serializers import (
    CustomUserCreateSerializer,
    CustomUserResponseSerializer,
    PasswordChangeSerializer,
    SetAvatarSerializer
)
from recipes.serializers import RecipeMinifiedSerializer


User = get_user_model()


class UserViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet
):
    queryset = User.objects.all()
    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.action in ('create', 'list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(
        detail=False, methods=['get'],
        url_path='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                return Response({'detail': 'recipes_limit должен быть целым числом.'},
                                status=status.HTTP_400_BAD_REQUEST)
        queryset = Subscription.objects.filter(user=user).select_related(
            'author')
        page = self.paginate_queryset([sub.author for sub in queryset])
        data = []
        for author in page:
            recipes = author.recipes.all().order_by('-created')
            if recipes_limit is not None:
                recipes = recipes[:recipes_limit]
            recipes_data = RecipeMinifiedSerializer(
                recipes, many=True, context={'request': request}).data
            author_data = CustomUserResponseSerializer(
                author, context={'request': request}).data
            author_data['recipes'] = recipes_data
            author_data['recipes_count'] = author.recipes.count()
            data.append(author_data)
        return self.get_paginated_response(data)

    def get_object(self):
        if self.action == 'me':
            return self.request.user
        return super().get_object()

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserResponseSerializer

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = CustomUserResponseSerializer(
            request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = SetAvatarSerializer(
                instance=user,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"avatar": request.build_absolute_uri(user.avatar.url)},
                status=status.HTTP_200_OK
            )

        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)

        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                return Response({'detail': 'recipes_limit должен быть целым числом.'},
                                status=status.HTTP_400_BAD_REQUEST)
        author_recipes = author.recipes.order_by('-created')
        if recipes_limit is not None:
            truncated = author_recipes[:recipes_limit]
        else:
            truncated = author_recipes
        recipes_data = RecipeMinifiedSerializer(truncated, many=True, context={'request': request}).data

        data = CustomUserResponseSerializer(author,
                                            context={'request': request}).data
        data['recipes'] = recipes_data
        data['recipes_count'] = author.recipes.count()

        if request.method == 'POST':
            if author == request.user:
                return Response({'detail': 'Нельзя подписаться на себя.'},
                                status=status.HTTP_400_BAD_REQUEST)
            sub, created = Subscription.objects.get_or_create(
                user=request.user, author=author
            )
            if not created:
                return Response({'detail': 'Вы уже подписаны.'},
                                status=status.HTTP_400_BAD_REQUEST)
            data = CustomUserResponseSerializer(
                author, context={'request': request}
            ).data
            data['recipes'] = RecipeMinifiedSerializer(
                author.recipes.all()[:1], many=True
            ).data
            data['recipes_count'] = author.recipes.count()
            return Response(data, status=status.HTTP_201_CREATED)

        deleted, _ = Subscription.objects.filter(
            user=request.user, author=author
        ).delete()
        if not deleted:
            return Response({'detail': 'Вы не были подписаны.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'],
            url_path='set_password', permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current = serializer.validated_data['current_password']
        new = serializer.validated_data['new_password']
        user = request.user
        if not user.check_password(current):
            return Response({'current_password': 'Неправильный пароль.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
