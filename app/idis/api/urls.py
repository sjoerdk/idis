from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from grandchallenge.subdomains.utils import reverse_lazy

app_name = "api"

router = routers.DefaultRouter()
"""
# Algorithms
router.register(
    r"algorithms/images", AlgorithmImageViewSet, basename="algorithms-image"
)
"""
schema_view = get_schema_view(
    openapi.Info(
        title=f"{settings.SESSION_COOKIE_DOMAIN.lstrip('.')} API",
        default_version="v1",
        description=f"The API for {settings.SESSION_COOKIE_DOMAIN.lstrip('.')}.",
        license=openapi.License(name="Apache License 2.0"),
        terms_of_service=reverse_lazy(
            "policies:detail", kwargs={"slug": "terms-of-service"}
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[path("api/v1/", include(router.urls))],
)

urlpatterns = [
    url(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(),
        name="schema-json",
    ),
    # Do not namespace the router.urls without updating the view names in
    # the serializers
    path("v1/", include(router.urls)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("", schema_view.with_ui("swagger"), name="schema-docs"),
]
