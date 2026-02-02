from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt import serializers as jwtSerializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "phone_number", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def to_internal_value(self, data):
        """Checks after conversion of email into lower case directly from JSON body before insertion"""
        data = data.copy()

        if "email" in data:
            data["email"] = data["email"].lower().strip()

        return super().to_internal_value(data)

    def create(self, validated_data):
        """Creates user using validated data, called when hit user.save() from `RegisterView`"""
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user"""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number")


class TokenObtainPairSerializer(jwtSerializers.TokenObtainPairSerializer):
    """Custom serializer for `TokenObtainPairSerializer` that checks after converting email to lower case"""

    def validate(self, attrs):
        email = attrs["email"]

        if isinstance(email, str):
            attrs["email"] = attrs["email"].lower()

        return super().validate(attrs)
