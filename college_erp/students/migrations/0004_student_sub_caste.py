from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0003_student_section"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="sub_caste",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
