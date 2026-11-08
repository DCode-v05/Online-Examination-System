from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0007_auto_20251026_2257'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='needs_review',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='result',
            name='student_answers',
            field=models.TextField(blank=True, null=True),
        ),
    ]
