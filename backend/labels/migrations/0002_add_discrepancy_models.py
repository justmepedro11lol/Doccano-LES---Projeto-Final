# Generated by Django 

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
        ('examples', '0001_initial'),
        ('labels', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscrepancyType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[
                    ('missing', 'Anotação Ausente'),
                    ('conflicting', 'Rótulos Conflitantes'),
                    ('overlapping', 'Spans Sobrepostos'),
                    ('relations', 'Relações Inconsistentes'),
                    ('low_agreement', 'Baixa Concordância')
                ], max_length=50, unique=True)),
                ('description', models.TextField()),
                ('severity', models.CharField(choices=[
                    ('low', 'Baixa'),
                    ('medium', 'Média'),
                    ('high', 'Alta'),
                    ('critical', 'Crítica')
                ], default='medium', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='AnnotationDiscrepancy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('agreement_score', models.FloatField(blank=True, help_text='Score de concordância entre 0 e 1', null=True)),
                ('conflicting_annotations', models.JSONField(default=dict, help_text='IDs e tipos das anotações em conflito')),
                ('status', models.CharField(choices=[
                    ('pending', 'Pendente'),
                    ('reviewing', 'Em Revisão'),
                    ('resolved', 'Resolvida'),
                    ('ignored', 'Ignorada')
                ], default='pending', max_length=20)),
                ('flagged_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('resolution_notes', models.TextField(blank=True)),
                ('priority', models.IntegerField(default=5, help_text='1=Muito Alta, 5=Muito Baixa')),
                ('discrepancy_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labels.discrepancytype')),
                ('example', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discrepancies', to='examples.example')),
                ('flagged_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='flagged_discrepancies', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discrepancies', to='projects.project')),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_discrepancies', to=settings.AUTH_USER_MODEL)),
                ('users_involved', models.ManyToManyField(related_name='discrepancies_involved', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['priority', '-flagged_at'],
            },
        ),
        migrations.CreateModel(
            name='DiscrepancyComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('discrepancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='labels.annotationdiscrepancy')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='annotationdiscrepancy',
            index=models.Index(fields=['project', 'status'], name='labels_anno_project_b8e4aa_idx'),
        ),
        migrations.AddIndex(
            model_name='annotationdiscrepancy',
            index=models.Index(fields=['example', 'discrepancy_type'], name='labels_anno_example_12345a_idx'),
        ),
        migrations.AddIndex(
            model_name='annotationdiscrepancy',
            index=models.Index(fields=['priority', 'flagged_at'], name='labels_anno_priorit_67890b_idx'),
        ),
    ]


def create_default_discrepancy_types(apps, schema_editor):
    """Cria os tipos de discrepância padrão"""
    DiscrepancyType = apps.get_model('labels', 'DiscrepancyType')
    
    default_types = [
        {
            'name': 'missing',
            'description': 'Anotação Ausente - Usuário não anotou o exemplo',
            'severity': 'medium'
        },
        {
            'name': 'conflicting',
            'description': 'Rótulos Conflitantes - Diferentes rótulos para mesma entidade',
            'severity': 'high'
        },
        {
            'name': 'overlapping',
            'description': 'Spans Sobrepostos - Sobreposição não permitida',
            'severity': 'medium'
        },
        {
            'name': 'relations',
            'description': 'Relações Inconsistentes - Relações conflitantes entre entidades',
            'severity': 'high'
        },
        {
            'name': 'low_agreement',
            'description': 'Baixa Concordância - Score de concordância abaixo do threshold',
            'severity': 'critical'
        }
    ]
    
    for type_data in default_types:
        DiscrepancyType.objects.get_or_create(**type_data)


def remove_default_discrepancy_types(apps, schema_editor):
    """Remove os tipos de discrepância padrão"""
    DiscrepancyType = apps.get_model('labels', 'DiscrepancyType')
    DiscrepancyType.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
        ('examples', '0001_initial'),
        ('labels', '0001_initial'),
    ]

    operations = [
        # ... operações anteriores ...
        migrations.RunPython(create_default_discrepancy_types, remove_default_discrepancy_types),
    ] 