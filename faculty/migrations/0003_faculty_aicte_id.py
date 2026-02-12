from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("faculty", "0002_faculty_extended_profile_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="faculty",
            name="aicte_id",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
