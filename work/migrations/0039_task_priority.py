# Generated by Django 3.1 on 2021-02-22 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0038_auto_20210219_0914'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.IntegerField(choices=[(0, 'High'), (1, 'Medium'), (2, 'Low')], default=1),
        ),
    ]
