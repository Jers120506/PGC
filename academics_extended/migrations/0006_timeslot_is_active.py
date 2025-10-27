# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics_extended', '0005_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Activo'),
        ),
    ]