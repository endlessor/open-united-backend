# Generated by Django 3.1 on 2021-02-18 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0036_auto_20210218_1534'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CapabilityNode',
            new_name='Capability',
        ),
        migrations.RenameModel(
            old_name='CapabilityNodeAttachment',
            new_name='CapabilityAttachment',
        ),
    ]
