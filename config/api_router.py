from django.conf import settings
from rest_framework.routers import SimpleRouter, DefaultRouter

from autovm.users.api.views import (
    UserViewSet,
    GeneralAdminViewSet,
    CustomerViewset,
    GuestViewset,
    GoogleSocialLoginViewSet,
)

from autovm.resources.api.views import (
    RegionViewSet,
    OperatingSystemVersionViewSet,
    VirtualMachineViewSet,
    VirtualMachineHistoryViewSet,
    BackupViewSet,
    NotificationViewSet,
)

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# users
router.register("users", UserViewSet)
router.register("admins", GeneralAdminViewSet)
router.register("customers", CustomerViewset)
router.register("guests", GuestViewset)
router.register("google-sign-in", GoogleSocialLoginViewSet, basename="google-sign-in")

# virtual machines
router.register("regions", RegionViewSet)
router.register("os-versions", OperatingSystemVersionViewSet)
router.register("virtual-machines", VirtualMachineViewSet)
router.register("vm-history", VirtualMachineHistoryViewSet)
router.register("backups", BackupViewSet)
router.register("notifications", NotificationViewSet)

app_name = "api"
urlpatterns = router.urls
