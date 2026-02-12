from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static


def health_check(request):
    return HttpResponse("ERP Backend Running ✅")


urlpatterns = [

    # Django Admin FIRST
    path("admin/", admin.site.urls),

    # Root health check
    path("", health_check),

    # APIs
    path("api/auth/", include("accounts.urls")),
    path("api/students/", include("students.urls")),
    path("api/faculty/", include("faculty.urls")),
    path("api/academics/", include("academics.urls")),
    path("api/admin/", include("administration.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
