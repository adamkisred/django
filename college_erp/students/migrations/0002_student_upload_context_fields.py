from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="academic_year",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="student",
            name="branch",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="student",
            name="college_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="student",
            name="semester",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
