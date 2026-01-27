from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt import serializers as jwtSerializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone_number", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        """Checks for existence of user with same email on changing case"""

        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user"""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number"]


class TokenObtainPairSerializer(jwtSerializers.TokenObtainPairSerializer):
    """Custom serializer for `TokenObtainPairSerializer` that checks after converting email to lower case"""

    def validate(self, attrs):
        email = attrs["email"]

        if isinstance(email, str):
            attrs["email"] = attrs["email"].lower()

        return super().validate(attrs)
