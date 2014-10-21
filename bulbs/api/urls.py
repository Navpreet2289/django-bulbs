from bulbs.cms_notifications.api import notifications_view
from django.conf import settings
from django.conf.urls import url, include

from .views import api_v1_router, MeViewSet

urlpatterns = (
    url(r"^me/logout/?$", "django.contrib.auth.views.logout", name="logout"),
    url(r"^me/?$", MeViewSet.as_view({"get": "retrieve"}), name="me"),
    url(r"^", include(api_v1_router.urls))       # noqa
)

if "bulbs.cms_notifications" in settings.INSTALLED_APPS:
    urlpatterns += (
        url(r"^notifications/(?P<pk>\d+)?", notifications_view, name="notifications"),
    )

if "bulbs.contributions" in settings.INSTALLED_APPS:
    urlpatterns += (
        url(r"^contributions/", include('bulbs.contributions.urls')),
    )
