# Generated by Django 3.1 on 2021-03-16 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0060_auto_20210316_1632'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='uuid',
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.CreateModel(
            name='ProductTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='work.product')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='work.tag')),
            ],
        ),
    ]
