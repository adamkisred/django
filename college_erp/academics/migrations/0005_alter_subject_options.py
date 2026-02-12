from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0004_subject_regulation_constraints"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="subject",
            options={"ordering": ["academic_year", "branch", "semester", "regulation", "subject_id"]},
        ),
    ]
