# Generated by Django 3.1 on 2021-01-22 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0021_auto_20210121_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='video_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
