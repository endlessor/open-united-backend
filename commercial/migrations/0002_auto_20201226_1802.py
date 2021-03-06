# Generated by Django 3.1 on 2020-12-26 18:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('talent', '0001_initial'),
        ('commercial', '0001_initial'),
        ('work', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='work.product'),
        ),
        migrations.AddField(
            model_name='organisationperson',
            name='organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='commercial.organisation'),
        ),
        migrations.AddField(
            model_name='organisationperson',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='talent.person'),
        ),
    ]
