from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("faculty", "0003_faculty_aicte_id"),
        ("academics", "0007_midmark"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubjectFacultyMapping",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("academic_year", models.CharField(max_length=20)),
                ("branch", models.CharField(max_length=30)),
                ("semester", models.CharField(max_length=20)),
                ("section", models.CharField(max_length=20)),
                ("regulation", models.CharField(default="R20", max_length=20)),
                ("slot_key", models.CharField(max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subject_faculty_mappings",
                        to="faculty.faculty",
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subject_faculty_mappings",
                        to="academics.subject",
                    ),
                ),
            ],
            options={
                "db_table": "subject_faculty_mappings",
                "ordering": ["academic_year", "branch", "semester", "section", "slot_key"],
            },
        ),
        migrations.AddConstraint(
            model_name="subjectfacultymapping",
            constraint=models.UniqueConstraint(
                fields=("academic_year", "branch", "semester", "section", "regulation", "slot_key"),
                name="uniq_subject_faculty_slot_per_context",
            ),
        ),
    ]
