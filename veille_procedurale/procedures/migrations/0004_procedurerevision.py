# Generated by Django 5.2 on 2025-04-25 00:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procedures', '0003_procedure_concerned_users'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcedureRevision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('bpmn_diagram', models.TextField()),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
                ('change_description', models.TextField(help_text='Description des modifications apportées')),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('procedure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revisions', to='procedures.procedure')),
            ],
            options={
                'ordering': ['-version'],
            },
        ),
    ]
