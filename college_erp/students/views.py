from datetime import datetime

import pandas as pd
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from students.models import Student


def _parse_date(value):
    if value is None or str(value).strip() == "":
        return None

    if isinstance(value, (datetime, pd.Timestamp)):
        return value.date()

    raw = str(value).strip()
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _clean(value):
    return str(value or "").strip()


DEFAULT_BRANCHES = ["CSE", "ECE", "EEE", "MECH", "CIVIL", "CSE (AI)", "IT"]
DEFAULT_SEMESTERS = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]
DEFAULT_SECTIONS = ["A", "B", "C", "D"]


def _split_address_blocks(address_value):
    do1 = village1 = mandal1 = district1 = pincode1 = ""
    do2 = village2 = mandal2 = district2 = pincode2 = ""
    raw = _clean(address_value)
    if not raw:
        return {
            "Do.No 1": do1,
            "Village 1": village1,
            "Mandal 1": mandal1,
            "District 1": district1,
            "Pincode 1": pincode1,
            "Do.No 2": do2,
            "Village 2": village2,
            "Mandal 2": mandal2,
            "District 2": district2,
            "Pincode 2": pincode2,
        }

    if "|" in raw:
        addr1, addr2 = raw.split("|", 1)
        v1 = (addr1.split("~") + ["", "", "", "", ""])[:5]
        v2 = (addr2.split("~") + ["", "", "", "", ""])[:5]
        do1, village1, mandal1, district1, pincode1 = [x.strip() for x in v1]
        do2, village2, mandal2, district2, pincode2 = [x.strip() for x in v2]
    else:
        do1 = raw

    return {
        "Do.No 1": do1,
        "Village 1": village1,
        "Mandal 1": mandal1,
        "District 1": district1,
        "Pincode 1": pincode1,
        "Do.No 2": do2,
        "Village 2": village2,
        "Mandal 2": mandal2,
        "District 2": district2,
        "Pincode 2": pincode2,
    }


def _upsert_student_from_payload(payload):
    college_name = _clean(payload.get("college_name") or "SVREC")
    branch = _clean(payload.get("branch"))
    academic_year = _clean(payload.get("academic_year"))
    semester = _clean(payload.get("semester"))
    if not branch or not academic_year or not semester:
        return None, None, Response(
            {
                "success": False,
                "message": "Please select Branch, Academic Year and Semester",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    hall_ticket_no = _clean(payload.get("hall_ticket_no")).upper()
    name = _clean(payload.get("name"))
    if not hall_ticket_no:
        return None, None, Response(
            {"success": False, "message": "Roll No is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not name:
        return None, None, Response(
            {"success": False, "message": "Student name is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = f"{hall_ticket_no.lower()}@svrec.ac.in"
    with transaction.atomic():
        user, created_user = User.objects.get_or_create(
            email=email,
            defaults={
                "username": None,
                "role": "STUDENT",
                "is_active": True,
            },
        )
        if created_user:
            user.set_unusable_password()
            user.save(update_fields=["password"])

        student, created_student = Student.objects.update_or_create(
            hall_ticket_no=hall_ticket_no,
            defaults={
                "user": user,
                "email": email,
                "college_name": college_name,
                "branch": branch,
                "academic_year": academic_year,
                "semester": semester,
                "section": _clean(payload.get("section")).upper(),
                "admission_no": _clean(payload.get("admission_no")),
                "name": name,
                "gender": _clean(payload.get("gender"))[:1].upper(),
                "rank": int(_clean(payload.get("rank")))
                if _clean(payload.get("rank")).isdigit()
                else None,
                "father_name": _clean(payload.get("father_name")),
                "dob": _parse_date(payload.get("dob")),
                "admission_date": _parse_date(payload.get("admission_date")),
                "student_mobile": _clean(payload.get("student_mobile")),
                "parent_mobile": _clean(payload.get("parent_mobile")),
                "religion": _clean(payload.get("religion")),
                "caste": _clean(payload.get("caste")),
                "sub_caste": _clean(payload.get("sub_caste")),
                "aadhar": _clean(payload.get("aadhar")),
                "address": _clean(payload.get("address")),
                "convenor": _clean(payload.get("convenor")),
            },
        )

    return student, created_student, None


class StudentSingleSaveView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        student, created_student, error_response = _upsert_student_from_payload(
            request.data
        )
        if error_response is not None:
            return error_response

        return Response(
            {
                "success": True,
                "message": (
                    "Student record created successfully"
                    if created_student
                    else "Student record updated successfully"
                ),
                "email": student.email,
                "hall_ticket_no": student.hall_ticket_no,
                "context": {
                    "college_name": student.college_name,
                    "branch": student.branch,
                    "academic_year": student.academic_year,
                    "semester": student.semester,
                    "section": student.section,
                },
            },
            status=status.HTTP_201_CREATED if created_student else status.HTTP_200_OK,
        )


class StudentContextTransferView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        branch = _clean(request.data.get("branch"))
        present_year = _clean(
            request.data.get("present_academic_year")
            or request.data.get("academic_year")
        )
        present_semester = _clean(
            request.data.get("present_semester")
            or request.data.get("semester")
        )
        target_year = _clean(request.data.get("target_academic_year"))
        target_semester = _clean(request.data.get("target_semester"))

        if not branch or not present_year or not present_semester:
            return Response(
                {
                    "success": False,
                    "message": "Branch, present academic year and present semester are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not target_year or not target_semester:
            return Response(
                {
                    "success": False,
                    "message": "Target academic year and target semester are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if present_year == target_year and present_semester == target_semester:
            return Response(
                {
                    "success": False,
                    "message": "Target year/semester must differ from present values",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = Student.objects.filter(
            branch=branch,
            academic_year=present_year,
            semester=present_semester,
        )
        matched_count = queryset.count()

        if matched_count == 0:
            return Response(
                {
                    "success": True,
                    "message": "No students found for selected present context",
                    "summary": {"matched": 0, "updated": 0},
                },
                status=status.HTTP_200_OK,
            )

        updated_count = queryset.update(
            academic_year=target_year,
            semester=target_semester,
        )

        return Response(
            {
                "success": True,
                "message": "Student context transfer completed successfully",
                "summary": {
                    "matched": matched_count,
                    "updated": updated_count,
                },
                "from": {
                    "branch": branch,
                    "academic_year": present_year,
                    "semester": present_semester,
                },
                "to": {
                    "branch": branch,
                    "academic_year": target_year,
                    "semester": target_semester,
                },
            },
            status=status.HTTP_200_OK,
        )


class AcademicYearOptionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        now_year = datetime.now().year

        auto_years = []
        for y in range(now_year - 2, now_year + 5):
            auto_years.append(f"{y}-{y + 1}")

        db_years = list(
            Student.objects.exclude(academic_year="")
            .values_list("academic_year", flat=True)
            .distinct()
        )

        all_years = sorted(set(auto_years + db_years))
        return Response(
            {"success": True, "academic_years": all_years},
            status=status.HTTP_200_OK,
        )


class StudentSearchListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = _clean(request.query_params.get("q")).lower()
        academic_year = _clean(request.query_params.get("academic_year"))
        semester = _clean(request.query_params.get("semester"))
        branch = _clean(request.query_params.get("branch"))

        queryset = Student.objects.all().order_by("hall_ticket_no")

        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        if semester:
            queryset = queryset.filter(semester=semester)
        if branch:
            queryset = queryset.filter(branch=branch)

        if q:
            queryset = queryset.filter(
                Q(hall_ticket_no__icontains=q) | Q(name__icontains=q)
            )

        data = []
        for s in queryset[:500]:
            data.append(
                {
                    "roll_no": s.hall_ticket_no,
                    "name": s.name,
                    "admission_no": s.admission_no,
                    "academic_year": s.academic_year,
                    "semester": s.semester,
                    "branch": s.branch,
                    "section": s.section,
                    "student_mobile": s.student_mobile,
                }
            )

        return Response(
            {"success": True, "count": len(data), "results": data},
            status=status.HTTP_200_OK,
        )


class StudentDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, roll_no):
        roll = _clean(roll_no).upper()
        student = Student.objects.filter(hall_ticket_no=roll).first()
        if not student:
            return Response(
                {"success": False, "message": "Student not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        addr = _split_address_blocks(student.address)
        payload = {
            "Roll No": student.hall_ticket_no,
            "Admission No": student.admission_no,
            "Student Name": student.name,
            "Gender": student.gender,
            "Date of Birth": student.dob.strftime("%Y-%m-%d") if student.dob else "",
            "Admission Date": student.admission_date.strftime("%Y-%m-%d") if student.admission_date else "",
            "Admission Type": student.convenor,
            "Batch": student.academic_year,
            "Section": student.section,
            "CET Rank": student.rank or "",
            "Branch": student.branch,
            "Father Name": student.father_name,
            "Student Aadhaar No": student.aadhar,
            "Student Mobile No": student.student_mobile,
            "Father Mobile No": student.parent_mobile,
            "Religion": student.religion,
            "Caste": student.caste,
            "Sub-Caste": student.sub_caste,
            "Scholarship": "",
            **addr,
        }
        return Response(
            {
                "success": True,
                "data": payload,
                "context": {
                    "academic_year": student.academic_year,
                    "semester": student.semester,
                    "branch": student.branch,
                    "section": student.section,
                    "college_name": student.college_name,
                },
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, roll_no):
        roll = _clean(roll_no).upper()
        existing = Student.objects.filter(hall_ticket_no=roll).first()
        if not existing:
            return Response(
                {"success": False, "message": "Student not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = dict(request.data)
        payload["hall_ticket_no"] = roll
        student, created_student, error_response = _upsert_student_from_payload(payload)
        if error_response is not None:
            return error_response

        return Response(
            {
                "success": True,
                "message": "Student updated successfully",
                "roll_no": student.hall_ticket_no,
                "created": created_student,
            },
            status=status.HTTP_200_OK,
        )


class StudentSectionMappingContextView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        db_years = list(
            Student.objects.exclude(academic_year="")
            .values_list("academic_year", flat=True)
            .distinct()
        )
        now_year = datetime.now().year
        auto_years = [f"{y}-{y + 1}" for y in range(now_year - 2, now_year + 5)]
        years = sorted(set(auto_years + db_years))

        branches = sorted(
            set(
                list(
                    Student.objects.exclude(branch="")
                    .values_list("branch", flat=True)
                    .distinct()
                )
                + DEFAULT_BRANCHES
            )
        )
        sections = sorted(
            set(
                list(
                    Student.objects.exclude(section="")
                    .values_list("section", flat=True)
                    .distinct()
                )
                + DEFAULT_SECTIONS
            )
        )

        return Response(
            {
                "success": True,
                "academic_years": years,
                "batches": years,
                "branches": branches,
                "semesters": DEFAULT_SEMESTERS,
                "sections": sections,
            },
            status=status.HTTP_200_OK,
        )


class StudentSectionMappingListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        academic_year = _clean(request.query_params.get("academic_year"))
        batch = _clean(request.query_params.get("batch"))
        branch = _clean(request.query_params.get("branch"))
        semester = _clean(request.query_params.get("semester"))

        year = academic_year or batch
        if not year or not branch or not semester:
            return Response(
                {"success": False, "message": "academic_year/batch, branch and semester are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = Student.objects.filter(
            academic_year=year,
            branch=branch,
            semester=semester,
        ).order_by("hall_ticket_no")

        rows = [
            {"roll_no": s.hall_ticket_no, "name": s.name, "section": s.section or ""}
            for s in qs[:1000]
        ]
        return Response({"success": True, "count": len(rows), "results": rows}, status=status.HTTP_200_OK)


class StudentSectionAssignView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        academic_year = _clean(request.data.get("academic_year"))
        batch = _clean(request.data.get("batch"))
        branch = _clean(request.data.get("branch"))
        semester = _clean(request.data.get("semester"))
        section = _clean(request.data.get("section")).upper()
        roll_nos = request.data.get("roll_nos") or []

        year = academic_year or batch
        if not year or not branch or not semester:
            return Response(
                {"success": False, "message": "academic_year/batch, branch and semester are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not section:
            return Response({"success": False, "message": "section is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(roll_nos, list) or not roll_nos:
            return Response({"success": False, "message": "Select at least one student"}, status=status.HTTP_400_BAD_REQUEST)

        normalized_rolls = [str(r).strip().upper() for r in roll_nos if str(r).strip()]
        qs = Student.objects.filter(
            hall_ticket_no__in=normalized_rolls,
            academic_year=year,
            branch=branch,
            semester=semester,
        )
        matched = qs.count()
        if matched == 0:
            return Response({"success": False, "message": "No matching students found in selected context"}, status=404)

        updated = qs.update(section=section)
        return Response(
            {
                "success": True,
                "message": "Students mapped to section successfully",
                "summary": {"selected": len(normalized_rolls), "matched": matched, "updated": updated},
                "section": section,
            },
            status=status.HTTP_200_OK,
        )
