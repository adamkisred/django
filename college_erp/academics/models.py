from django.db import models
from django.utils.timezone import now

from faculty.models import Faculty


class Subject(models.Model):
    SUBJECT_TYPE_CHOICES = (
        ("THEORY", "Theory"),
        ("PRACTICAL", "Practical"),
        ("CRT", "CRT"),
        ("MENTORING", "Mentoring"),
        ("OTHER", "Other"),
    )

    academic_year = models.CharField(max_length=20)
    branch = models.CharField(max_length=30)
    semester = models.CharField(max_length=20)
    regulation = models.CharField(max_length=20, default="R20")
    subject_id = models.CharField(max_length=30)
    subject_name = models.CharField(max_length=150)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPE_CHOICES, default="THEORY")
    credits = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subjects"
        ordering = ["academic_year", "branch", "semester", "regulation", "subject_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "branch", "semester", "regulation", "subject_id"],
                name="uniq_subject_per_context_regulation_by_id",
            ),
            models.UniqueConstraint(
                fields=["academic_year", "branch", "semester", "regulation", "subject_name"],
                name="uniq_subject_per_context_regulation_by_name",
            ),
        ]

    def __str__(self):
        return f"{self.subject_id} - {self.subject_name}"


class TimetableMapping(models.Model):
    academic_year = models.CharField(max_length=20)
    branch = models.CharField(max_length=30)
    semester = models.CharField(max_length=20)
    section = models.CharField(max_length=20)
    week_day = models.CharField(max_length=20)
    period_no = models.PositiveSmallIntegerField()
    period_label = models.CharField(max_length=40)
    period_time = models.CharField(max_length=60, blank=True)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="timetable_mappings")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="timetable_mappings")

    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "timetable_mappings"
        ordering = [
            "academic_year",
            "branch",
            "semester",
            "section",
            "week_day",
            "period_no",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "academic_year",
                    "branch",
                    "semester",
                    "section",
                    "week_day",
                    "period_no",
                ],
                name="uniq_class_slot_mapping",
            ),
        ]

    def __str__(self):
        return (
            f"{self.academic_year} {self.branch} {self.semester} {self.section} "
            f"{self.week_day} P{self.period_no}"
        )


class TimeSlot(models.Model):
    day = models.CharField(max_length=20)
    period_number = models.PositiveSmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = "time_slots"
        ordering = ["period_number"]
        constraints = [
            models.UniqueConstraint(fields=["day", "period_number"], name="uniq_day_period_time_slot"),
        ]

    def __str__(self):
        return f"{self.day} P{self.period_number} ({self.start_time}-{self.end_time})"


class Timetable(models.Model):
    academic_year = models.CharField(max_length=20)
    branch = models.CharField(max_length=30)
    semester = models.CharField(max_length=20)
    section = models.CharField(max_length=20)
    regulation = models.CharField(max_length=20, default="R20")
    day = models.CharField(max_length=20)
    period_no = models.PositiveSmallIntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="auto_timetables")
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, related_name="timetables")
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "timetables"
        ordering = ["academic_year", "branch", "semester", "section", "day", "period_no"]
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "branch", "semester", "section", "regulation", "day", "period_no"],
                name="uniq_timetable_class_slot",
            ),
        ]

    def __str__(self):
        return f"{self.academic_year} {self.branch} {self.semester}-{self.section} {self.day} P{self.period_no}"


class SubjectFacultyMapping(models.Model):
    academic_year = models.CharField(max_length=20)
    branch = models.CharField(max_length=30)
    semester = models.CharField(max_length=20)
    section = models.CharField(max_length=20)
    regulation = models.CharField(max_length=20, default="R20")
    slot_key = models.CharField(max_length=30)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="subject_faculty_mappings")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="subject_faculty_mappings")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subject_faculty_mappings"
        ordering = ["academic_year", "branch", "semester", "section", "slot_key"]
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "branch", "semester", "section", "regulation", "slot_key"],
                name="uniq_subject_faculty_slot_per_context",
            ),
        ]

    def __str__(self):
        return (
            f"{self.academic_year} {self.branch} {self.semester}-{self.section} "
            f"{self.regulation} {self.slot_key}"
        )


class MidMark(models.Model):
    academic_year = models.CharField(max_length=20)
    branch = models.CharField(max_length=30)
    semester = models.CharField(max_length=20)
    section = models.CharField(max_length=20)
    exam_type = models.CharField(max_length=20)

    student_roll_no = models.CharField(max_length=30)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="mid_marks")
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mid_marks"
        ordering = ["academic_year", "branch", "semester", "section", "exam_type", "student_roll_no", "subject__subject_id"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "academic_year",
                    "branch",
                    "semester",
                    "section",
                    "exam_type",
                    "student_roll_no",
                    "subject",
                ],
                name="uniq_midmark_context_student_subject",
            )
        ]

    def __str__(self):
        return (
            f"{self.academic_year} {self.branch} {self.semester}-{self.section} "
            f"{self.exam_type} {self.student_roll_no} {self.subject.subject_id}"
        )
