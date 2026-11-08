from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_merge_20251026_1848'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='address',
        ),
    ]
