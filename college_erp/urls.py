"""
URL configuration for college_erp project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


# ----------------------------------------
# Simple Health Check View (Root URL)
# ----------------------------------------
def home(request):
    return HttpResponse("🚀 College ERP Backend is Running Successfully!")


urlpatterns = [

    # Root URL (Health Check)
    path("", home, name="home"),

    # Django Admin
    path("admin/", admin.site.urls),

    # =====================================
    # ERP API ROUTES
    # =====================================

    # AUTH (login, otp, password)
    path("api/auth/", include("accounts.urls")),

    # STUDENTS
    path("api/students/", include("students.urls")),

    # FACULTY
    path("api/faculty/", include("faculty.urls")),

    # ACADEMICS
    path("api/academics/", include("academics.urls")),

    # ADMINISTRATION (Excel uploads)
    path("api/admin/", include("administration.urls")),
]


# =====================================
# MEDIA & STATIC (DEV ONLY)
# =====================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
