# Generated by Django 3.2.7 on 2021-10-04 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice_app', '0003_auto_20211004_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='charges',
            name='is_paid',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
