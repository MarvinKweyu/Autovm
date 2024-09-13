from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from autovm.billing.api.views import BillingAccountViewSet
from autovm.billing.api.views import RatePlanViewSet
from autovm.billing.api.views import SubscriptionViewSet
from autovm.billing.api.views import TransactionViewSet
from autovm.resources.api.views import BackupViewSet
from autovm.resources.api.views import NotificationViewSet
from autovm.resources.api.views import OperatingSystemVersionViewSet
from autovm.resources.api.views import RegionViewSet
from autovm.resources.api.views import VirtualMachineHistoryViewSet
from autovm.resources.api.views import VirtualMachineViewSet
from autovm.users.api.views import CustomerViewset
from autovm.users.api.views import GeneralAdminViewSet
from autovm.users.api.views import GoogleSocialLoginViewSet
from autovm.users.api.views import GuestViewset
from autovm.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# users
router.register("users", UserViewSet)
router.register("admins", GeneralAdminViewSet)
router.register("customers", CustomerViewset)
router.register("guests", GuestViewset)
router.register("google-auth", GoogleSocialLoginViewSet, basename="google-auth")

# resources
router.register("regions", RegionViewSet)
router.register("os-versions", OperatingSystemVersionViewSet)
router.register("virtual-machines", VirtualMachineViewSet)
router.register("vm-history", VirtualMachineHistoryViewSet)
router.register("backups", BackupViewSet)
router.register("notifications", NotificationViewSet)

# billing
router.register("rate-plans", RatePlanViewSet)
router.register("subscriptions", SubscriptionViewSet)
router.register("transactions", TransactionViewSet)
router.register("billing-accounts", BillingAccountViewSet)

app_name = "api"
urlpatterns = router.urls
