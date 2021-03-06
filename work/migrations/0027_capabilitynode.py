# Generated by Django 3.1 on 2021-02-12 12:01

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0026_producttask'),
    ]

    operations = [
        migrations.CreateModel(
            name='CapabilityNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('product_id', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
