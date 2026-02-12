from django.urls import path
from administration.views import (
    StudentExcelTemplateDownload,
    StudentExcelUpload,
    StudentExcelExport,
    FacultyExcelTemplateDownload,
    FacultyExcelUpload,
    FacultyExcelExport,
    AdminCreateFacultyView,
    FacultyListView,
    FacultySingleSaveView,
    FacultyTransferDepartmentView,
    FacultyRelievedListView,
    FacultyDetailView,
    FacultyRelieveView,
    FacultyRemoveView,
    AdminUserPasswordUpdateView,
)


urlpatterns = [
    path("students/template/", StudentExcelTemplateDownload.as_view()),
    path("students/upload/", StudentExcelUpload.as_view()),
    path("students/export/", StudentExcelExport.as_view()),
    path("faculty/template/", FacultyExcelTemplateDownload.as_view()),
    path("faculty/upload/", FacultyExcelUpload.as_view()),
    path("faculty/export/", FacultyExcelExport.as_view()),
    path("faculty/create/", AdminCreateFacultyView.as_view()),
    path("faculty/list/", FacultyListView.as_view()),
    path("faculty/save-single/", FacultySingleSaveView.as_view()),
    path("faculty/transfer-department/", FacultyTransferDepartmentView.as_view()),
    path("faculty/relieved-list/", FacultyRelievedListView.as_view()),
    path("faculty/detail/<str:id_no>/", FacultyDetailView.as_view()),
    path("faculty/relieve/<str:id_no>/", FacultyRelieveView.as_view()),
    path("faculty/remove/<str:id_no>/", FacultyRemoveView.as_view()),
    path("users/update-password/", AdminUserPasswordUpdateView.as_view()),

]
