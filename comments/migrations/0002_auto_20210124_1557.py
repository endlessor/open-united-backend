# Generated by Django 3.1 on 2021-01-24 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='level',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='comment',
            name='nested_count',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='comment',
            name='order',
            field=models.IntegerField(db_index=True, default=1),
        ),
        migrations.AddField(
            model_name='comment',
            name='parent_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='comment',
            name='thread_id',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
