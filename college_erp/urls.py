from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static


def health_check(request):
    return HttpResponse("ERP Backend Running ✅")


urlpatterns = [
    # Root health check
    path("", health_check),

    # Django Admin
    path("admin/", admin.site.urls),

    # AUTH
    path("api/auth/", include("accounts.urls")),

    # STUDENTS
    path("api/students/", include("students.urls")),

    # FACULTY
    path("api/faculty/", include("faculty.urls")),

    # ACADEMICS
    path("api/academics/", include("academics.urls")),

    # ADMINISTRATION
    path("api/admin/", include("administration.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
