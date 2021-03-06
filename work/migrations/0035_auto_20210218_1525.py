# Generated by Django 3.1 on 2021-02-18 15:25

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0034_auto_20210218_1457'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='capability_node',
        ),
        migrations.CreateModel(
            name='Capability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.TextField()),
                ('attachment', models.ManyToManyField(blank=True, related_name='capability_attachements', to='work.Attachment')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='work.capability')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='work.product')),
            ],
            options={
                'verbose_name_plural': 'Capabilities',
            },
        ),
        migrations.AddField(
            model_name='task',
            name='capability',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='work.capability'),
        ),
    ]
