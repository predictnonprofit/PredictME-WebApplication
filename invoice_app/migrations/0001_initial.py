# Generated by Django 3.2.7 on 2021-09-26 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Charges',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('charge_token', models.CharField(max_length=100, unique=True)),
                ('amount', models.BigIntegerField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=20, null=True)),
                ('charge_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'charges',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_stripe_id', models.CharField(max_length=100, unique=True)),
                ('invoice_pdf_url', models.URLField(max_length=255, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'invoices',
            },
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trans_stripe_id', models.CharField(max_length=100, unique=True)),
                ('invoice_stripe_id', models.CharField(max_length=100, null=True, unique=True)),
                ('receipt_pdf_url', models.URLField(max_length=255, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'transactions',
            },
        ),
    ]
