from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from autovm.billing.models import BillingAccount
from autovm.users.models import Customer
from autovm.users.models import GeneralAdmin
from autovm.users.models import Guest
from autovm.users.models import User

from .serializers import CustomerSusensionSerializer
from .serializers import CustomerUserSerializer
from .serializers import CustomUserSerializer
from .serializers import GeneralAdminSerializer
from .serializers import GuestRegistrationSerializer
from .serializers import GuestUserSerializer
from .serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    """
    User vuiew
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        """
        Retrieve the current user profile
        """
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class GeneralAdminViewSet(viewsets.ModelViewSet):
    """
    Platform administrators and superusers.
    """

    serializer_class = GeneralAdminSerializer
    queryset = GeneralAdmin.objects.all()
    lookup_field = "pk"
    filter_backends = [SearchFilter]
    search_fields = ["user__name", "user__email"]


class CustomerViewset(viewsets.ModelViewSet):
    """
    An API viewset for customer users.
    """

    serializer_class = CustomerUserSerializer
    queryset = Customer.objects.all()
    lookup_field = "pk"
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["user__name", "user__email"]
    filterset_fields = ["suspended"]

    @action(detail=False, methods=["get"], name="Statistics")
    def statistics(self, request, pk=None):
        """
        Get statistics of customers
        """
        queryset = self.get_queryset()
        total = queryset.count()
        active = queryset.filter(suspended=False).count()
        inactive = queryset.filter(suspended=True).count()

        total_guests = Guest.objects.count()

        return Response(
            {
                "total": total,
                "active": active,
                "inactive": inactive,
                "guests": total_guests,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        name="Suspend",
        serializer_class=CustomerSusensionSerializer,
    )
    def suspend(self, request, pk=None):
        """
        Suspend a customer account
        """
        customer = self.get_object()
        serializer = CustomerSusensionSerializer(data=request.data)
        if serializer.is_valid():
            customer.suspended = serializer.data["suspend"]
            customer.save()
            return Response(
                {"success": "Customer account suspended successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuestViewset(viewsets.ModelViewSet):
    """
    An API viewset for guest users.
    """

    serializer_class = GuestUserSerializer
    queryset = Guest.objects.all()
    lookup_field = "pk"
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["user__name", "user__email"]
    filterset_fields = ["status", "customer__user__email", "customer__user__id"]

    def get_queryset(self):
        """
        A customer should be able to list only the guest users they have created.
        """
        user = self.request.user
        if user.role == "admin":
            return self.queryset
        customer = Customer.objects.get(user=self.request.user)
        return self.queryset.filter(customer=customer)

    @action(detail=False, methods=["get"], name="Statistics")
    def statistics(self, request, pk=None):
        """
        Get statistics of guest users
        """
        queryset = self.get_queryset()
        total = queryset.count()
        active = queryset.filter(status="active").count()
        inactive = queryset.filter(status="inactive").count()

        return Response(
            {
                "total": total,
                "active": active,
                "inactive": inactive,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(
    name="post",
    decorator=extend_schema(
        request=GuestRegistrationSerializer,
    ),
)
class GuestRegistrationView(APIView):
    """
    Register guest under a customer
    """

    serializer_class = GuestRegistrationSerializer

    def post(self, request):
        """
        Create a guest associated with the current user.
        """
        serializer = GuestRegistrationSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": "Guest created successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def check_required_fields(data, required_fields):
    """
    Check if the required fields are present in the given data.
    """
    for field in required_fields:
        if field not in data:
            return Response(
                {"message": f"{field.capitalize()} is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    return None


class GoogleSocialLoginViewSet(ModelViewSet):
    """
    Create a new user using google aith
    """

    permission_classes = [AllowAny]
    http_method_names = ["post"]
    # serializer_class = GoogleSocialSerializer

    def create(self, request, *args, **kwargs):
        required_fields = ["name", "email"]

        fields = check_required_fields(request.data, required_fields)
        if fields:
            return fields

        email = request.data.get("email")
        name = request.data.get("name")

        try:
            user, created = User.objects.get_or_create(email=email)
            BillingAccount.objects.get_or_create(
                user=user,
            )  # move this to under created
            if created:
                user.name = name
                user.is_active = True
                user.set_unusable_password()
                user.save()
                # only customers have billing accounts.
                # guest accounts are already created with their email accounts

            serializer = CustomUserSerializer(user, context={"request": request})

            token = RefreshToken.for_user(user)
            return Response(
                {
                    "user": serializer.data,
                    "access": str(token.access_token),
                    "refresh": str(token),
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"message": "Unable to authenticate user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
