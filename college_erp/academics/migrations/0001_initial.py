from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Subject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("academic_year", models.CharField(max_length=20)),
                ("branch", models.CharField(max_length=30)),
                ("semester", models.CharField(max_length=20)),
                ("subject_id", models.CharField(max_length=30)),
                ("subject_name", models.CharField(max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "subjects",
                "ordering": ["academic_year", "branch", "semester", "subject_id"],
            },
        ),
        migrations.AddConstraint(
            model_name="subject",
            constraint=models.UniqueConstraint(
                fields=("academic_year", "branch", "semester", "subject_id"),
                name="uniq_subject_per_context_by_id",
            ),
        ),
        migrations.AddConstraint(
            model_name="subject",
            constraint=models.UniqueConstraint(
                fields=("academic_year", "branch", "semester", "subject_name"),
                name="uniq_subject_per_context_by_name",
            ),
        ),
    ]
