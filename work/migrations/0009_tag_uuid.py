# Generated by Django 3.1 on 2021-01-12 11:22

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0008_auto_20210112_1110'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
