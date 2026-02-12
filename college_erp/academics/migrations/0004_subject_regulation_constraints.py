from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0003_subject_type_credits"),
    ]

    operations = [
        migrations.AddField(
            model_name="subject",
            name="regulation",
            field=models.CharField(default="R20", max_length=20),
        ),
        migrations.RemoveConstraint(
            model_name="subject",
            name="uniq_subject_per_context_by_id",
        ),
        migrations.RemoveConstraint(
            model_name="subject",
            name="uniq_subject_per_context_by_name",
        ),
        migrations.AddConstraint(
            model_name="subject",
            constraint=models.UniqueConstraint(
                fields=("academic_year", "branch", "semester", "regulation", "subject_id"),
                name="uniq_subject_per_context_regulation_by_id",
            ),
        ),
        migrations.AddConstraint(
            model_name="subject",
            constraint=models.UniqueConstraint(
                fields=("academic_year", "branch", "semester", "regulation", "subject_name"),
                name="uniq_subject_per_context_regulation_by_name",
            ),
        ),
    ]
