# Generated by Django 3.1 on 2021-03-09 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0053_remove_task_depend_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskDepend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('depends_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='work.task')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Task', to='work.task')),
            ],
        ),
    ]
