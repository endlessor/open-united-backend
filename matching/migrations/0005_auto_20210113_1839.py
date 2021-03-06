# Generated by Django 3.1 on 2021-01-13 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('talent', '0006_auto_20210109_2057'),
        ('work', '0010_auto_20210113_1836'),
        ('matching', '0004_auto_20210112_1110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskclaimrequest',
            name='task_claim',
        ),
        migrations.AddField(
            model_name='taskclaimrequest',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='talent.person'),
        ),
        migrations.AddField(
            model_name='taskclaimrequest',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='work.task'),
        ),
        migrations.AlterField(
            model_name='taskclaim',
            name='kind',
            field=models.IntegerField(choices=[(0, 'AVAILABLE'), (1, 'DONE'), (2, 'CLAIMED'), (3, 'FAILED'), (4, 'DRAFTED'), (5, 'PUBLISHED'), (5, 'IN REVIEW')], default=0),
        ),
    ]
