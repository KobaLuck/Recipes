from base64 import b64decode

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:"):
            header, base64_str = data.split(";base64,")
            decoded_file = b64decode(base64_str)
            ext = header.split("/")[-1]
            file_name = f"avatar_{self.context['request'].user.id}.{ext}"
            data = ContentFile(decoded_file, name=file_name)
        return super().to_internal_value(data)


class UserCreateSerializer(DjoserUserSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        read_only_fields = ("id",)


class UserResponseSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and not request.user.is_anonymous
            and obj.subscribers.filter(user=request.user).exists()
        )


class SetAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
