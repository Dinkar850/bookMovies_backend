from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt import serializers as jwtSerializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user model

    JSON Structure:
    {
        "id": int,
        "first_name": string,
        "last_name": string,
        "email": string,
        "phone_number": string,
        "password": string
    }

    Notes:
        - Password write only
        - Email normalized to lowercase
    """

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
    """
    Serializer for updating user fields

    JSON Structure:
    {
        "first_name": string,
        "last_name": string,
        "phone_number": string
    }
    """

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number")


class TokenObtainPairSerializer(jwtSerializers.TokenObtainPairSerializer):
    """
    Serializer for authentication tokens

    JSON Structure:
    {
        "email": string,
        "password": string,
        "access": string,
        "refresh": string
    }

    Notes:
        - View may modify or hide refresh
    """

    def validate(self, attrs):
        """Custom validation for email that converts entered email into lower case prior to validation"""

        email = attrs["email"]

        if isinstance(email, str):
            attrs["email"] = attrs["email"].lower()

        return super().validate(attrs)
