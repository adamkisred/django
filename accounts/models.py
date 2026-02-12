from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils.timezone import now


# =========================================================
# USER MANAGER
# =========================================================
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, role="STUDENT", **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            role=role,
            **extra_fields
        )

        # Students → no password
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(
            email=email,
            password=password,
            role="ADMIN",
            **extra_fields
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# =========================================================
# CUSTOM USER MODEL
# =========================================================
class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("FACULTY", "Faculty"),
        ("STUDENT", "Student"),
        ("SPECIAL", "Special User"),
    )

    email = models.EmailField(unique=True)

    # 🔑 OPTIONAL — only for faculty/admin/special
    username = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=now, editable=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.email} ({self.role})"


# =========================================================
# EMAIL OTP (STUDENTS)
# =========================================================
class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=now)
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = "email_otp"
