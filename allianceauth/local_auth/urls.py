from allianceauth import urls
from django.conf import settings
from django.urls import include, path

urlpatterns = []
if "allianceauth_oidc" in settings.INSTALLED_APPS:
    urlpatterns.append(path("o/", include("allianceauth_oidc.urls", namespace="oauth2_provider")))
urlpatterns.append(path("", include(urls)))

handler500 = "allianceauth.views.Generic500Redirect"
handler404 = "allianceauth.views.Generic404Redirect"
handler403 = "allianceauth.views.Generic403Redirect"
handler400 = "allianceauth.views.Generic400Redirect"
