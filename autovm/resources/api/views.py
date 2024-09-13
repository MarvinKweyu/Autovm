from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from autovm.billing.models import Subscription
from autovm.resources.models import Backup
from autovm.resources.models import Notification
from autovm.resources.models import OperatingSystemVersion
from autovm.resources.models import Region
from autovm.resources.models import VirtualMachine
from autovm.resources.models import VirtualMachineHistory
from autovm.users.models import User

from .serializers import AssignmentSerializer
from .serializers import BackupSerializer
from .serializers import NotificationSerializer
from .serializers import OperatingSystemVersionSerializer
from .serializers import RegionSerializer
from .serializers import VirtualMachineHistorySerializer
from .serializers import VirtualMachineSerializer


class OperatingSystemVersionViewSet(ModelViewSet):
    """
    Operating System Version viewset.
    """

    serializer_class = OperatingSystemVersionSerializer
    queryset = OperatingSystemVersion.objects.all()
    lookup_field = "pk"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["operating_system", "version"]
    search_fields = ["operating_system", "version"]


class RegionViewSet(ModelViewSet):
    """
    Region viewset.
    """

    serializer_class = RegionSerializer
    queryset = Region.objects.all()
    lookup_field = "pk"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["name"]
    search_fields = ["name"]


class VirtualMachineViewSet(ModelViewSet):
    """
    Virtual Machine viewset.
    """

    serializer_class = VirtualMachineSerializer
    queryset = VirtualMachine.objects.all()
    lookup_field = "pk"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["name", "is_active", "user__id"]
    search_fields = [
        "name",
        "user__name",
        "region__name",
        "operating_system_version__version",
        "operating_system_version__operating_system__name",
        "description",
    ]

    # if this is the admin user, return all virtual machines, else,
    # return only those that belong to the user making teh request
    def get_queryset(self):
        if self.request.user.role == "admin":
            return VirtualMachine.objects.all()
        return VirtualMachine.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Check the current active subscription of the user.
        """
        user = self.request.user
        if user.role == "admin":
            return super().create(request, *args, **kwargs)
        if user.role == "customer":
            # get the billing account
            account = user.billingaccount
            customer_profile = user.customer_profile
            active_subscription = Subscription.objects.filter(
                account=account,
                status="active",
            ).first()
            if not active_subscription:
                return Response(
                    {"message": "You do not have an active subscription."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if customer_profile.suspended:
                return Response(
                    {"message": "Your account has been suspended."},
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )

            # get the vm limit
            vm_limit = active_subscription.plan.vm_limit
            # get the number of virtual machines the user has
            vm_count = VirtualMachine.objects.filter(user=user).count()
            if vm_count >= vm_limit:
                return Response(
                    {
                        "message": """You have reached the virtual machine
                        limit for your subscription. Please upgrade your
                        plan to create more virtual machines.""",
                    },
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )

            return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["get"], name="Statistics")
    def statistics(self, request, pk=None):
        """
        Get statistics of virtual machines.
        """
        queryset = self.get_queryset()
        total = queryset.count()
        active = queryset.filter(is_active=True).count()
        inactive = queryset.filter(is_active=False).count()

        return Response(
            {
                "total": total,
                "active": active,
                "inactive": inactive,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], name="Backup")
    def backup(self, request, pk=None):
        """
        Backup virtual machine.
        """
        virtual_machine = self.get_object()
        account = virtual_machine.user.billingaccount

        active_subscription = Subscription.objects.filter(
            account=account,
            status="active",
        ).first()
        # customer profiile from account
        customer_profile = account.user.customer_profile

        if customer_profile.suspended:
            return Response(
                {"message": "This account has been suspended."},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        if not active_subscription:
            return Response(
                {"message": "You do not have an active subscription."},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        # get the backup limit of the subscription
        backup_limit = active_subscription.plan.backup_limit

        # get the number of backups for this virtual machine
        backup_count = Backup.objects.filter(vm=virtual_machine).count()

        if backup_count >= backup_limit:
            return Response(
                {
                    "message": """You have reached the backup limit for this
                    virtual machine. Please upgrade your plan to create more
                    backups.""",
                },
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        backup = Backup.objects.create(
            vm=virtual_machine,
            size=virtual_machine.disk_size,
        )

        return Response(
            {
                "message": "Backup created successfully.",
                "backup": backup.created,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        name="Asssign a virtual machine to a user",
        serializer_class=AssignmentSerializer,
    )
    def assign(self, request, pk=None):
        """
        Assign a virtual machine to a user.
        """
        virtual_machine = self.get_object()
        serializer = AssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            user = self.request.user
            # get the target user from the serializer
            assigned_user_id = serializer.validated_data["user_id"]
            assigned_user = User.objects.get(id=assigned_user_id)

            active_subscription = Subscription.objects.filter(
                account=assigned_user.billingaccount,
                status="active",
            ).first()

            if not active_subscription:
                return Response(
                    {"message": "No active subscription."},
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )

            vm_limit = active_subscription.plan.vm_limit
            vm_count = VirtualMachine.objects.filter(user=assigned_user).count()

            if vm_count >= vm_limit:
                return Response(
                    {
                        "message": """The limit has been reached for virtual
                          machines. Please upgrade this plan to create more
                          virtual machines.""",
                    },
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )

            previous_user = virtual_machine.user

            virtual_machine.user = assigned_user
            virtual_machine.save()
            # todo
            # create a history of the assignment
            # can be  a background task
            VirtualMachineHistory.objects.create(
                virtual_machine=virtual_machine,
                action="assign_vm",
                description=f"assigned this virtual machine to {assigned_user.name}",
                user=user,
            )

            # create a notification for the action
            # create as a background task

            with transaction.atomic():
                notifications = [
                    Notification(
                        user=previous_user,
                        message=f"""Virtual machine {virtual_machine.name} has
                        been unassigned from you.""",
                    ),
                    Notification(
                        user=assigned_user,
                        message=f"You haSve been assigned a virtual machine {virtual_machine.name}",
                    ),
                ]
                Notification.objects.bulk_create(notifications)

            return Response(
                {
                    "message": "Virtual machine assigned successfully.",
                    "user": assigned_user.name,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VirtualMachineHistoryViewSet(ModelViewSet):
    """
    Virtual Machine history viewset.
    """

    serializer_class = VirtualMachineHistorySerializer
    queryset = VirtualMachineHistory.objects.all()
    lookup_field = "pk"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["virtual_machine", "user"]
    search_fields = ["description", "user"]


class BackupViewSet(ModelViewSet):
    """
    Backup viewset.
    """

    serializer_class = BackupSerializer
    queryset = Backup.objects.all()
    lookup_field = "pk"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["vm"]
    search_fields = ["vm", "size", "created"]


class NotificationViewSet(ModelViewSet):
    """
    Notification viewset.
    """

    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    lookup_field = "pk"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["user"]
    search_fields = ["user", "message", "created"]
