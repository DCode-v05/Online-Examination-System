from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0004_auto_20201209_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
