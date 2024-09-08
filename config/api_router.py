from django.conf import settings
from rest_framework.routers import SimpleRouter, DefaultRouter

from autovm.users.api.views import (
    UserViewSet,
    GeneralAdminViewSet,
    CustomerViewset,
    GuestViewset,
    GoogleSocialLoginViewSet,
)

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# users
router.register("users", UserViewSet)
router.register("admins", GeneralAdminViewSet)
router.register("customers", CustomerViewset)
router.register("guests", GuestViewset)
router.register("google-sign-in", GoogleSocialLoginViewSet, basename="google-sign-in")


app_name = "api"
urlpatterns = router.urls
