# Generated by Django 3.2.6 on 2021-08-07 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_handler', '0019_modelmostsimilarfile_categorical_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelmostsimilarfile',
            name='common_features',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
