from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q, F, Sum
from django.utils import timezone
from datetime import timedelta
from labels.models import Category, Span, TextLabel, Relation
from examples.models import Example
from projects.models import Member, Project
from label_types.models import CategoryType, SpanType
from .models import AnnotatorReportConfig


class AnnotatorReportFilterSerializer(serializers.Serializer):
    """Serializer para filtros do relatório de anotadores"""
    dataset_id = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    annotator_id = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    data_inicial = serializers.DateTimeField(required=False)
    data_final = serializers.DateTimeField(required=False)
    categoria_label = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    perspectiva_id = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    estado_desacordo = serializers.ChoiceField(
        choices=['todos', 'em_desacordo', 'resolvido'],
        default='todos'
    )
    
    # Parâmetros de paginação e ordenação
    sort_by = serializers.CharField(default='total_anotacoes')
    order = serializers.ChoiceField(choices=['asc', 'desc'], default='desc')
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=10, min_value=1, max_value=100)


class AnnotatorDetailSerializer(serializers.Serializer):
    """Serializer para detalhes de um anotador no relatório"""
    annotator_id = serializers.CharField()
    nome_anotador = serializers.CharField()
    total_anotacoes = serializers.IntegerField()
    datasets_distintos = serializers.IntegerField()
    tempo_total_min = serializers.FloatField()
    tempo_medio_por_anotacao_seg = serializers.FloatField()
    taxa_desacordo_percent = serializers.FloatField()
    desacordos_resolvidos = serializers.IntegerField()
    score_concordancia_medio = serializers.FloatField()
    perspectivas_usadas = serializers.ListField(child=serializers.CharField())
    categorias_mais_frequentes = serializers.ListField(child=serializers.CharField())
    primeira_anotacao = serializers.DateTimeField()
    ultima_anotacao = serializers.DateTimeField()


class AnnotatorReportSerializer(serializers.Serializer):
    """Serializer principal para o relatório de anotadores"""
    filtros_aplicados = serializers.DictField()
    resumo_global = serializers.DictField()
    detalhe_anotadores = AnnotatorDetailSerializer(many=True)
    
    
class AnnotatorReportExportSerializer(serializers.Serializer):
    """Serializer para exportação do relatório"""
    format = serializers.ChoiceField(choices=['csv', 'pdf'], default='csv')
    
    # Reusa os filtros do relatório principal
    dataset_id = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    annotator_id = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    data_inicial = serializers.DateTimeField(required=False)
    data_final = serializers.DateTimeField(required=False)
    categoria_label = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    perspectiva_id = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    estado_desacordo = serializers.ChoiceField(
        choices=['todos', 'em_desacordo', 'resolvido'],
        default='todos'
    ) 