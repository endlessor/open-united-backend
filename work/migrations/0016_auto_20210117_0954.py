# Generated by Django 3.1 on 2021-01-17 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0015_auto_20210117_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initiative',
            name='status',
            field=models.IntegerField(choices=[(1, 'Active'), (2, 'Completed')], default=1),
        ),
    ]
