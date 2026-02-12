from django.urls import path

from students.views import (
    AcademicYearOptionsView,
    StudentContextTransferView,
    StudentDetailView,
    StudentSearchListView,
    StudentSectionAssignView,
    StudentSectionMappingContextView,
    StudentSectionMappingListView,
    StudentSingleSaveView,
)

urlpatterns = [
    path("save-single/", StudentSingleSaveView.as_view()),
    path("transfer-context/", StudentContextTransferView.as_view()),
    path("academic-years/", AcademicYearOptionsView.as_view()),
    path("search/", StudentSearchListView.as_view()),
    path("detail/<str:roll_no>/", StudentDetailView.as_view()),
    path("section-mapping/context/", StudentSectionMappingContextView.as_view()),
    path("section-mapping/students/", StudentSectionMappingListView.as_view()),
    path("section-mapping/assign/", StudentSectionAssignView.as_view()),
]
