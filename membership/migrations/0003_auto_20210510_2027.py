# Generated by Django 3.2.2 on 2021-05-10 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0002_auto_20210413_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
