# Generated by Django 3.1 on 2021-04-13 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('talent', '0030_auto_20210402_1312'),
        ('work', '0072_auto_20210413_1407'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tasklisting',
            old_name='assign_to',
            new_name='assigned_to_data',
        ),
        migrations.AddField(
            model_name='tasklisting',
            name='assigned_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_to', to='talent.person'),
        ),
        migrations.AlterField(
            model_name='tasklisting',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator', to='talent.person'),
        ),
    ]
