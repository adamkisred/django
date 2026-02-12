from django.urls import path
from accounts.views import (
    LoginRouterView,
    VerifyLoginView,
)

urlpatterns = [
    path("check-user/", LoginRouterView.as_view()),
    path("verify-login/", VerifyLoginView.as_view()),
]
