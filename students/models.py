from django.db import models
from django.utils.timezone import now
from accounts.models import User


class Student(models.Model):
    """
    Student Master Table
    - Created via Excel upload
    - Email auto-generated from HT No
    - User account linked later for OTP login
    """

    # ==================================================
    # AUTH LINK (AUTO-CREATED LATER)
    # ==================================================
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
        null=True,
        blank=True,
    )

    # ==================================================
    # CORE IDENTIFIERS
    # ==================================================
    hall_ticket_no = models.CharField(max_length=30, unique=True)
    admission_no = models.CharField(max_length=30, blank=True)

    # Context selected by admin during upload/template/export
    college_name = models.CharField(max_length=150, blank=True)
    branch = models.CharField(max_length=30, blank=True)
    academic_year = models.CharField(max_length=20, blank=True)
    semester = models.CharField(max_length=20, blank=True)
    section = models.CharField(max_length=20, blank=True)

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        help_text="Auto-generated student email",
    )

    # ==================================================
    # PERSONAL DETAILS
    # ==================================================
    name = models.CharField(max_length=150)
    gender = models.CharField(max_length=1, blank=True, help_text="M / F / O")
    dob = models.DateField(null=True, blank=True)
    father_name = models.CharField(max_length=150, blank=True)

    # ==================================================
    # ACADEMIC DETAILS
    # ==================================================
    rank = models.IntegerField(null=True, blank=True)
    admission_date = models.DateField(null=True, blank=True)
    convenor = models.CharField(max_length=50, blank=True)

    # ==================================================
    # CONTACT DETAILS
    # ==================================================
    student_mobile = models.CharField(max_length=10, blank=True)
    parent_mobile = models.CharField(max_length=10, blank=True)

    # ==================================================
    # OTHER DETAILS
    # ==================================================
    religion = models.CharField(max_length=50, blank=True)
    caste = models.CharField(max_length=50, blank=True)
    sub_caste = models.CharField(max_length=50, blank=True)
    aadhar = models.CharField(max_length=12, blank=True)
    address = models.TextField(blank=True)

    # ==================================================
    # AUDIT FIELDS
    # ==================================================
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student"
        ordering = ["hall_ticket_no"]

    def __str__(self):
        return f"{self.hall_ticket_no} - {self.name}"
