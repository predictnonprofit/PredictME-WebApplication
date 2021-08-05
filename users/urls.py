from django.urls import path
from .views import *
from membership.views import (CheckoutView, RegisterSuccessfully)
from django.contrib.auth import views as auth_views

# app_name = "users"

urlpatterns = [
    path("login", MembersLoginView.as_view(), name="login"),
    path("logout", logout_view, name="logout"),
    path("register", register_view, name="register"),
    path("reset", auth_views.PasswordResetView.as_view(template_name='users/auth/reset.html'), name='reset_password'),
    path("reset/sent", auth_views.PasswordResetDoneView.as_view(template_name='users/auth/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/auth/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path("reset/complete",
         auth_views.PasswordResetCompleteView.as_view(template_name='users/auth/password_reset_complete.html'),
         name='password_reset_complete'),
    path("checkout", CheckoutView.as_view(), name="checkout"),
    path("success", RegisterSuccessfully.as_view(), name="register_successfully"),
    path("complete", CompleteRegister.as_view(), name="register-complete"),
    path("pending", PendingUserView.as_view(), name="users_pending"),
    path("canceled", CancelUserView.as_view(), name="users_canceled"),
    path("verify", VerifyAccountView.as_view(), name="users_verify"),
    # re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #         activate_account, name='activate'),
    path(r'activate/<uidb64>/<token>/', activate_account, name='activate'),
    path("google", GoogleAuthenticationView.as_view(), name="auth-google"),

]
