# Generated by Django 3.1 on 2021-02-18 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0033_auto_20210217_1101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='capability',
        ),
        migrations.AddField(
            model_name='task',
            name='capability_node',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='work.capabilitynode'),
        ),
        migrations.DeleteModel(
            name='Capability',
        ),
    ]
