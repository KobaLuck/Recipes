from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import DefaultPagination
from api.serializers.users import UserCreateSerializer, UserResponseSerializer
from users.models import Subscription

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.action in ("create", "list", "retrieve", "me"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserResponseSerializer

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = UserResponseSerializer(
            request.user, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="subscriptions",
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        subs = Subscription.objects.filter(
            user=request.user).select_related("author")
        authors = [sub.author for sub in subs]
        page = self.paginate_queryset(authors)
        serializer = UserResponseSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if user == author:
            return Response(
                {"errors": "Нельзя подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "POST":
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {"errors": "Вы уже подписаны на этого автора."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Subscription.objects.create(user=user, author=author)
            serializer = UserResponseSerializer(
                author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE
        sub = Subscription.objects.filter(user=user, author=author).first()
        if sub:
            sub.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Вы не были подписаны на этого пользователя."},
            status=status.HTTP_400_BAD_REQUEST,
        )
