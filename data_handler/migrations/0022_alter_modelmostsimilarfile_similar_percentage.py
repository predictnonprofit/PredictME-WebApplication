# Generated by Django 3.2.6 on 2021-08-09 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_handler', '0021_alter_modelmostsimilarfile_similar_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelmostsimilarfile',
            name='similar_percentage',
            field=models.DecimalField(decimal_places=5, max_digits=10),
        ),
    ]
