from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0005_alter_subject_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subject",
            name="subject_type",
            field=models.CharField(
                choices=[
                    ("THEORY", "Theory"),
                    ("PRACTICAL", "Practical"),
                    ("CRT", "CRT"),
                    ("MENTORING", "Mentoring"),
                    ("OTHER", "Other"),
                ],
                default="THEORY",
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="TimeSlot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("day", models.CharField(max_length=20)),
                ("period_number", models.PositiveSmallIntegerField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
            ],
            options={
                "db_table": "time_slots",
                "ordering": ["period_number"],
                "constraints": [
                    models.UniqueConstraint(fields=("day", "period_number"), name="uniq_day_period_time_slot")
                ],
            },
        ),
        migrations.CreateModel(
            name="Timetable",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("academic_year", models.CharField(max_length=20)),
                ("branch", models.CharField(max_length=30)),
                ("semester", models.CharField(max_length=20)),
                ("section", models.CharField(max_length=20)),
                ("regulation", models.CharField(default="R20", max_length=20)),
                ("day", models.CharField(max_length=20)),
                ("period_no", models.PositiveSmallIntegerField()),
                ("generated_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="auto_timetables",
                        to="academics.subject",
                    ),
                ),
                (
                    "timeslot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="timetables",
                        to="academics.timeslot",
                    ),
                ),
            ],
            options={
                "db_table": "timetables",
                "ordering": ["academic_year", "branch", "semester", "section", "day", "period_no"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("academic_year", "branch", "semester", "section", "regulation", "day", "period_no"),
                        name="uniq_timetable_class_slot",
                    )
                ],
            },
        ),
    ]
