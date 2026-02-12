from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0002_student_upload_context_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="section",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
