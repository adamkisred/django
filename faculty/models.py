from django.db import models
from django.utils.timezone import now
from accounts.models import User


class Faculty(models.Model):
    """
    Faculty Master Table
    - Created via Excel upload or single entry
    - User account is auto-linked later
    """

    # --------------------------------------------------
    # AUTH LINK (AUTO-CREATED LATER)
    # --------------------------------------------------
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="faculty_profile"
    )

    # --------------------------------------------------
    # UNIQUE IDENTIFIERS
    # --------------------------------------------------
    id_no = models.CharField(
        max_length=50,
        unique=True,
        help_text="Official Faculty ID Number"
    )

    faculty_id = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        help_text="System-generated Faculty Login ID"
    )

    # --------------------------------------------------
    # PERSONAL DETAILS
    # --------------------------------------------------
    full_name = models.CharField(max_length=200, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    dob = models.DateField(null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    relieving_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    reference_name = models.CharField(max_length=200, blank=True)
    husband_wife_name = models.CharField(max_length=200, blank=True)

    mother_name = models.CharField(max_length=200, blank=True)
    father_name = models.CharField(max_length=200, blank=True)

    nationality = models.CharField(max_length=100, blank=True)
    religion = models.CharField(max_length=100, blank=True)

    wedding_date = models.DateField(null=True, blank=True)

    caste = models.CharField(max_length=100, blank=True)
    reservation_category = models.CharField(max_length=100, blank=True)
    minority_indicator = models.CharField(max_length=50, blank=True)

    # --------------------------------------------------
    # CONTACT DETAILS
    # --------------------------------------------------
    mobile_no = models.CharField(max_length=15, blank=True)
    other_mobile_no = models.CharField(max_length=15, blank=True)

    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Official faculty email"
    )

    # --------------------------------------------------
    # MEDICAL & ID DETAILS
    # --------------------------------------------------
    is_physically_challenged = models.CharField(max_length=10, blank=True)
    blood_group = models.CharField(max_length=10, blank=True)

    aadhar_no = models.CharField(max_length=20, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)
    aicte_id = models.CharField(max_length=30, blank=True)
    licence_number = models.CharField(max_length=30, blank=True)

    # --------------------------------------------------
    # PROFESSIONAL DETAILS
    # --------------------------------------------------
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    d_no = models.CharField(max_length=120, blank=True)
    street = models.CharField(max_length=200, blank=True)
    village = models.CharField(max_length=200, blank=True)
    district = models.CharField(max_length=200, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    area = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)

    # --------------------------------------------------
    # AUDIT FIELDS (SAFE FOR EXISTING DATA)
    # --------------------------------------------------
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    # --------------------------------------------------
    # META
    # --------------------------------------------------
    class Meta:
        db_table = "faculty"
        ordering = ["id_no"]

    def __str__(self):
        return f"{self.id_no} - {self.full_name}"
