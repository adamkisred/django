from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("faculty", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="faculty",
            name="gender",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="faculty",
            name="joining_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="faculty",
            name="relieving_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="faculty",
            name="salary",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="faculty",
            name="qualification",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="faculty",
            name="reference_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="faculty",
            name="husband_wife_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="faculty",
            name="d_no",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="faculty",
            name="street",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="faculty",
            name="village",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="faculty",
            name="district",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="faculty",
            name="pincode",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="faculty",
            name="area",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
