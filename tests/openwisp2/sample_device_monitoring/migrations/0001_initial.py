# Generated by Django 3.0.3 on 2020-05-20 18:42

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('config', '0026_hardware_id_not_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceData',
            fields=[
                (
                    'device_ptr',
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to='config.Device',
                    ),
                ),
            ],
            options={
                'abstract': False,
                'swappable': 'DEVICE_MONITORING_DEVICEDATA_MODEL',
            },
            bases=('config.device',),
        ),
        migrations.CreateModel(
            name='DetailsModel',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('details', models.CharField(blank=True, max_length=64, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DeviceMonitoring',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='created',
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='modified',
                    ),
                ),
                (
                    'status',
                    model_utils.fields.StatusField(
                        choices=[
                            ('unknown', 'unknown'),
                            ('ok', 'ok'),
                            ('problem', 'problem'),
                            ('critical', 'critical'),
                        ],
                        db_index=True,
                        default='unknown',
                        help_text='"unknown" means the device has been recently added; \n"ok" means the device is operating normally; \n"problem" means the device is having issues but it\'s still reachable; \n"critical" means the device is not reachable or in critical conditions;',
                        max_length=100,
                        no_check_for_status=True,
                        verbose_name='health status',
                    ),
                ),
                (
                    'device',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='monitoring',
                        to='config.Device',
                    ),
                ),
            ],
            options={
                'abstract': False,
                'swappable': 'DEVICE_MONITORING_DEVICEMONITORING_MODEL',
            },
        ),
    ]
