from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from predict_me import views as predict_views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^accounts/', include('allauth.urls')),
    path("", predict_views.LandPageView.as_view(), name="land-page"),
    path("dashboard/", include("dashboard.urls"), name='dashboard-url'),
    path("member/", include("users.urls"), name="users-url"),
    path("about/", predict_views.AboutView.as_view(), name="about"),
    path("contact/", predict_views.ContactView.as_view(), name="contact"),
    path("faq/", predict_views.FAQView.as_view(), name="faq"),
    path("pricing", predict_views.PricingView.as_view(), name="pricing"),
    path("model/", predict_views.ModelDescView.as_view(), name="model-desc"),
    path("policy/", predict_views.PrivacyPolicyView.as_view(), name="privacy-policy"),
    path("terms/", predict_views.TermsView.as_view(), name="terms"),
    path("profile/", include("members_app.urls"), name="profile-urls"),
    path("503", predict_views.error_503, name="503-urls"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
