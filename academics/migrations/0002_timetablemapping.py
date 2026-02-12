from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("faculty", "0001_initial"),
        ("academics", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TimetableMapping",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("academic_year", models.CharField(max_length=20)),
                ("branch", models.CharField(max_length=30)),
                ("semester", models.CharField(max_length=20)),
                ("section", models.CharField(max_length=20)),
                ("week_day", models.CharField(max_length=20)),
                ("period_no", models.PositiveSmallIntegerField()),
                ("period_label", models.CharField(max_length=40)),
                ("period_time", models.CharField(blank=True, max_length=60)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "faculty",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="timetable_mappings", to="faculty.faculty"),
                ),
                (
                    "subject",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="timetable_mappings", to="academics.subject"),
                ),
            ],
            options={
                "db_table": "timetable_mappings",
                "ordering": [
                    "academic_year",
                    "branch",
                    "semester",
                    "section",
                    "week_day",
                    "period_no",
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("academic_year", "branch", "semester", "section", "week_day", "period_no"),
                        name="uniq_class_slot_mapping",
                    )
                ],
            },
        ),
    ]
