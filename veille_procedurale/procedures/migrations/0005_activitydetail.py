# Generated by Django 5.2 on 2025-04-25 01:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procedures', '0004_procedurerevision'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_id', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('duration', models.FloatField()),
                ('procedure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='procedures.procedure')),
                ('responsible', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('procedure', 'activity_id')},
            },
        ),
    ]
