# Generated by Django 3.2.7 on 2021-10-04 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice_app', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='charges',
            name='invoice_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='charges',
            name='payment_intent_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
