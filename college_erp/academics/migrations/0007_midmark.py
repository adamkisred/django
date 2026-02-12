from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0006_subject_type_timeslot_timetable"),
    ]

    operations = [
        migrations.CreateModel(
            name="MidMark",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("academic_year", models.CharField(max_length=20)),
                ("branch", models.CharField(max_length=30)),
                ("semester", models.CharField(max_length=20)),
                ("section", models.CharField(max_length=20)),
                ("exam_type", models.CharField(max_length=20)),
                ("student_roll_no", models.CharField(max_length=30)),
                ("marks", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mid_marks",
                        to="academics.subject",
                    ),
                ),
            ],
            options={
                "db_table": "mid_marks",
                "ordering": [
                    "academic_year",
                    "branch",
                    "semester",
                    "section",
                    "exam_type",
                    "student_roll_no",
                    "subject__subject_id",
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=(
                            "academic_year",
                            "branch",
                            "semester",
                            "section",
                            "exam_type",
                            "student_roll_no",
                            "subject",
                        ),
                        name="uniq_midmark_context_student_subject",
                    )
                ],
            },
        ),
    ]
