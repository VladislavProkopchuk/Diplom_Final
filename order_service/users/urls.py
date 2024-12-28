import authemail.views
from django.urls import path

from . import views

urlpatterns = [
    path("user/contacts", views.ContactList.as_view()),
    path("user/contacts/<int:pk>", views.ContactDetail.as_view()),
    path("user/register", authemail.views.Signup.as_view(), name="authemail-signup"),
    path(
        "user/register/confirm",
        authemail.views.SignupVerify.as_view(),
        name="authemail-signup-verify",
    ),
    path("user/login", authemail.views.Login.as_view(), name="authemail-login"),
    path("user/logout", authemail.views.Logout.as_view(), name="authemail-logout"),
    path(
        "user/password/reset",
        authemail.views.PasswordReset.as_view(),
        name="authemail-password-reset",
    ),
    path(
        "user/password/reset/confirm",
        authemail.views.PasswordResetVerify.as_view(),
        name="authemail-password-reset-verify",
    ),
    path(
        "user/password/reset/verified",
        authemail.views.PasswordResetVerified.as_view(),
        name="authemail-password-reset-verified",
    ),
    path(
        "user/email/change",
        authemail.views.EmailChange.as_view(),
        name="authemail-email-change",
    ),
    path(
        "user/email/change/verify",
        authemail.views.EmailChangeVerify.as_view(),
        name="authemail-email-change-verify",
    ),
    path(
        "user/password/change",
        authemail.views.PasswordChange.as_view(),
        name="authemail-password-change",
    ),
    path("user/details", views.UserDetail.as_view()),    
]
