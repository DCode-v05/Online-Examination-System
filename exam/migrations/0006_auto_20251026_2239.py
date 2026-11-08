from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0005_auto_20201209_2125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='question_number',
        ),
        migrations.RemoveField(
            model_name='course',
            name='total_marks',
        ),
    ]
