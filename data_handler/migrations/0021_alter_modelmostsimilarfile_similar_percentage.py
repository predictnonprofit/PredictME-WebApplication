# Generated by Django 3.2.6 on 2021-08-09 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_handler', '0020_modelmostsimilarfile_common_features'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelmostsimilarfile',
            name='similar_percentage',
            field=models.DecimalField(decimal_places=3, max_digits=10),
        ),
    ]
