from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from autovm.resources.models import (
    Backup,
    Notification,
    OperatingSystemVersion,
    Region,
    VirtualMachine,
    VirtualMachineHistory,
)

from autovm.users.models import User

from .serializers import (
    BackupSerializer,
    NotificationSerializer,
    OperatingSystemVersionSerializer,
    RegionSerializer,
    VirtualMachineHistorySerializer,
    VirtualMachineSerializer,
    AssignmentSerializer,
)


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

    # if this is the admin user, return all virtual machines, else, return only those that belong to the user making teh request
    def get_queryset(self):
        if self.request.user.role == "admin":
            return VirtualMachine.objects.all()
        return VirtualMachine.objects.filter(user=self.request.user)

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

            previous_user = virtual_machine.user

            virtual_machine.user = assigned_user
            virtual_machine.save()
            # todo
            # create a history of the assignment
            # can be  a background task
            VirtualMachineHistory.objects.create(
                virtual_machine=virtual_machine,
                action="assign_vm",
                description="Assigned this virtual machine ",
                user=user,
            )

            # create a notification for the action
            # create as a background task

            with transaction.atomic():
                notifications = [
                    Notification(
                        user=previous_user,
                        message=f"Virtual machine {virtual_machine.name} has been unassigned from you.",
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
