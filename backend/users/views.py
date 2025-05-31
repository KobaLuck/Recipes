from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import (
    CustomUserCreateSerializer, CustomUserResponseSerializer,
    SetAvatarSerializer, PasswordChangeSerializer
)
from .models import Subscription
from recipes.serializers import RecipeMinifiedSerializer
from core.pagination import DefaultPagination

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserResponseSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'],
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        serializer = SetAvatarSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            if author == request.user:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            sub, created = Subscription.objects.get_or_create(
                user=request.user, author=author
            )
            if not created:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            data = CustomUserResponseSerializer(
                author, context={'request': request}).data
            data['recipes'] = RecipeMinifiedSerializer(
                author.recipes.all()[:1], many=True).data
            return Response(data, status=status.HTTP_201_CREATED)
        # DELETE
        sub = Subscription.objects.filter(user=request.user, author=author)
        if not sub.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        sub.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
