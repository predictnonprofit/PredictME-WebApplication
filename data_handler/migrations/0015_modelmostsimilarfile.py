# Generated by Django 3.2.6 on 2021-08-07 19:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_handler', '0014_datahandlersession_numeric_columns'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelMostSimilarFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similar_file_path', models.CharField(max_length=255, unique=True)),
                ('similar_value', models.DecimalField(decimal_places=3, max_digits=5)),
                ('counter', models.PositiveBigIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data_session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='data_session_model_similar_files', to='data_handler.datahandlersession')),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='member_model_similar_files', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]