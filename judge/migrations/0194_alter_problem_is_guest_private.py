# Generated by Django 3.2.21 on 2023-10-08 03:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0193_auto_20231008_0255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='is_guest_private',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Public to guest'),
        ),
    ]
