from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import DefaultPagination
from api.serializers.users import (
    CustomUserCreateSerializer,
    UserResponseSerializer,
    SubscriptionSerializer,
)
from users.models import Subscription

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Регистрация, просмотр профилей, подписки и свой профиль."""
    queryset = User.objects.all()
    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.action in ("create", "list", "retrieve", "me"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return CustomUserCreateSerializer
        if self.action == "subscriptions":
            return SubscriptionSerializer
        return UserResponseSerializer

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Профиль авторизованного пользователя."""
        serializer = UserResponseSerializer(
            request.user, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="subscriptions",
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """
        Список авторов, на которых подписан текущий пользователь.
        Логика получения данных перенесена в SubscriptionSerializer.
        """
        subs = Subscription.objects.filter(
            user=request.user).select_related("author")
        page = self.paginate_queryset(subs)
        serializer = self.get_serializer(
            page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """
        Подписаться/отписаться на автора.
        Вся валидация и формирование ответа — в SubscriptionSerializer.
        """
        author = get_object_or_404(User, pk=pk)
        data = {"user": request.user.id, "author": author.id}

        if request.method == "POST":
            serializer = SubscriptionSerializer(
                data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response(
                serializer.to_representation(instance),
                status=status.HTTP_201_CREATED
            )

        # DELETE
        serializer = SubscriptionSerializer(
            data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.delete_instance()
        return Response(status=status.HTTP_204_NO_CONTENT)
