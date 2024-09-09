import random
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

from autovm.users.models import User, Customer, Guest
from django.db.utils import IntegrityError

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer[User]):
    """
    user serializer
    """

    class Meta:
        """
        Fields to render in the serializer.
        """

        model = User
        fields = ["name", "username", "role", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class GeneralAdminSerializer(serializers.ModelSerializer[User]):
    """
    A serializer for general admin users.
    """

    class Meta:
        """
        Allowed fields for the serializer.
        """

        model = User
        fields = ["id", "username", "name", "email"]


class CustomerUserSerializer(serializers.ModelSerializer[User]):
    """
    A serializer for customer users.
    """

    class Meta:
        """
        Allowed fields for the serializer.
        """

        model = User
        fields = ["id", "username", "name", "email"]


class GuestUserSerializer(serializers.ModelSerializer):
    """
    A serializer for guest users.
    """

    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        """
        Allowed fields for the serializer.
        """

        model = Guest
        fields = ["id", "name", "email", "status", "created"]

    def get_name(self, obj):
        """
        Name of the guest user.
        """
        return obj.user.name

    def get_email(self, obj):
        """
        Email of the guest user.
        """
        return obj.user.email


class GuestRegistrationSerializer(serializers.Serializer):
    """
    Serializer for registering a guest user.
    """

    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()

    def create(self, validated_data):
        current_user = self.context["request"].user.id

        # get the customer making the request
        customer = Customer.objects.get(user_id=current_user)

        # Create the user with the validated data
        # generate a random number between 1 and 999999
        otp = random.randint(100000, 999999)
        password = User.objects.make_random_password()
        username = validated_data["name"] + str(otp)

        # get the user making the request
        new_user = None
        new_user = User(
            # username=username,
            name=validated_data["name"],
            email=validated_data["email"],
            role="guest",
        )
        new_user.set_password(password)
        new_user.save()

        new_user.guest_profile.customer = customer
        new_user.guest_profile.save()

        # send the password and confirmation email to the user
        message = f"Dear {new_user.name}, \n Your VMControlHub guest account has been created. Your details are as below: \n Login email {new_user.email} \n\n is: {password}"
        # send a confirmation email to the user
        new_user.email_user(
            "VMControlHub Account Creation",
            message,
            "VMControlHub <no-reply@example.com>",
        )

        return new_user

    def validate(self, attrs):

        if User.objects.filter(email=attrs["email"]).exists():
            serializers.ValidationError("This email is already registered")

        if User.objects.filter(name=attrs["name"]).exists():
            raise serializers.ValidationError("A user with this name already exists.")

        return attrs
