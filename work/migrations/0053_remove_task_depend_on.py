# Generated by Django 3.1 on 2021-03-09 15:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0052_auto_20210308_1657'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='depend_on',
        ),
    ]
