from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class AnnotatorReportConfig(models.Model):
    """Configuração para relatórios de anotadores"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='annotator_reports')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Filtros aplicados
    dataset_ids = models.JSONField(default=list, blank=True)
    annotator_ids = models.JSONField(default=list, blank=True)
    data_inicial = models.DateTimeField(null=True, blank=True)
    data_final = models.DateTimeField(null=True, blank=True)
    categoria_labels = models.JSONField(default=list, blank=True)
    perspectiva_ids = models.JSONField(default=list, blank=True)
    estado_desacordo = models.CharField(
        max_length=20,
        choices=[
            ('todos', 'Todos'),
            ('em_desacordo', 'Em desacordo'),
            ('resolvido', 'Resolvido')
        ],
        default='todos'
    )
    
    class Meta:
        ordering = ['-created_at'] 