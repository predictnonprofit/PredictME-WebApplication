# Generated by Django 3.2.6 on 2021-08-09 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210510_2027'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='member_type',
            field=models.CharField(choices=[('normal_member', 'Normal Member'), ('development_member', 'Development Member')], default='normal_member', max_length=50),
        ),
    ]