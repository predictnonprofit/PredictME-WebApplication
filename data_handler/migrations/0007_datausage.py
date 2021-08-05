# Generated by Django 3.2.3 on 2021-05-22 14:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_handler', '0006_alter_datahandlersession_data_handler_session_label'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_created=True, default=django.utils.timezone.now)),
                ('records_used', models.BigIntegerField(blank=True, default=0, null=True)),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='data_usage', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'data_usage',
            },
        ),
    ]
