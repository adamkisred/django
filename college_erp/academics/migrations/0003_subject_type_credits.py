from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0002_timetablemapping"),
    ]

    operations = [
        migrations.AddField(
            model_name="subject",
            name="credits",
            field=models.DecimalField(decimal_places=1, default=0, max_digits=4),
        ),
        migrations.AddField(
            model_name="subject",
            name="subject_type",
            field=models.CharField(
                choices=[("THEORY", "Theory"), ("PRACTICAL", "Practical"), ("OTHER", "Other")],
                default="THEORY",
                max_length=20,
            ),
        ),
    ]
