# Generated by Django 4.2.15 on 2025-06-15 17:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("examples", "0008_assignment"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("projects", "0017_alter_answer_unique_together"),
        ("labels", "0019_merge_20250615_1548"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnnotationDiscrepancy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.TextField()),
                (
                    "agreement_score",
                    models.FloatField(blank=True, help_text="Score de concordância entre 0 e 1", null=True),
                ),
                (
                    "conflicting_annotations",
                    models.JSONField(default=dict, help_text="IDs e tipos das anotações em conflito"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendente"),
                            ("reviewing", "Em Revisão"),
                            ("resolved", "Resolvida"),
                            ("ignored", "Ignorada"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("flagged_at", models.DateTimeField(auto_now_add=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("resolution_notes", models.TextField(blank=True)),
                ("priority", models.IntegerField(default=5, help_text="1=Muito Alta, 5=Muito Baixa")),
            ],
            options={
                "ordering": ["priority", "-flagged_at"],
            },
        ),
        migrations.CreateModel(
            name="DiscrepancyType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("missing", "Anotação Ausente"),
                            ("conflicting", "Rótulos Conflitantes"),
                            ("overlapping", "Spans Sobrepostos"),
                            ("relations", "Relações Inconsistentes"),
                            ("low_agreement", "Baixa Concordância"),
                        ],
                        max_length=50,
                        unique=True,
                    ),
                ),
                ("description", models.TextField()),
                (
                    "severity",
                    models.CharField(
                        choices=[("low", "Baixa"), ("medium", "Média"), ("high", "Alta"), ("critical", "Crítica")],
                        default="medium",
                        max_length=20,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DiscrepancyComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("comment", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "discrepancy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="labels.annotationdiscrepancy",
                    ),
                ),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
        migrations.AddField(
            model_name="annotationdiscrepancy",
            name="discrepancy_type",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="labels.discrepancytype"),
        ),
        migrations.AddField(
            model_name="annotationdiscrepancy",
            name="example",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="discrepancies", to="examples.example"
            ),
        ),
        migrations.AddField(
            model_name="annotationdiscrepancy",
            name="flagged_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="flagged_discrepancies",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="annotationdiscrepancy",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="discrepancies", to="projects.project"
            ),
        ),
        migrations.AddField(
            model_name="annotationdiscrepancy",
            name="resolved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="resolved_discrepancies",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="annotationdiscrepancy",
            name="users_involved",
            field=models.ManyToManyField(related_name="discrepancies_involved", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name="annotationdiscrepancy",
            index=models.Index(fields=["project", "status"], name="labels_anno_project_9018cb_idx"),
        ),
        migrations.AddIndex(
            model_name="annotationdiscrepancy",
            index=models.Index(fields=["example", "discrepancy_type"], name="labels_anno_example_11e475_idx"),
        ),
        migrations.AddIndex(
            model_name="annotationdiscrepancy",
            index=models.Index(fields=["priority", "flagged_at"], name="labels_anno_priorit_71ce50_idx"),
        ),
    ]
