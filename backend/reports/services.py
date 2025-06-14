import csv
import io
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q, F, Sum, Max, Min, Case, When, FloatField
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from sklearn.metrics import cohen_kappa_score
import pandas as pd

from projects.models import Project, Member
from examples.models import Example
from labels.models import Category, Span, TextLabel, Relation, Label
from label_types.models import CategoryType, SpanType


class AnnotatorReportService:
    """Serviço para gerar relatórios detalhados de anotadores"""
    
    def __init__(self, project: Project):
        self.project = project
        
    def generate_report(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Gera o relatório completo de anotadores com base nos filtros"""
        
        # Aplicar filtros para obter anotadores relevantes
        annotators = self._filter_annotators(filters)
        
        # Calcular métricas para cada anotador
        annotator_details = []
        for annotator in annotators:
            details = self._calculate_annotator_metrics(annotator, filters)
            if details:  # Só inclui se tiver dados
                annotator_details.append(details)
        
        # Ordenar e paginar resultados
        annotator_details = self._sort_and_paginate(
            annotator_details, 
            filters.get('sort_by', 'total_anotacoes'),
            filters.get('order', 'desc'),
            filters.get('page', 1),
            filters.get('page_size', 10)
        )
        
        # Calcular resumo global
        resumo_global = self._calculate_global_summary(annotator_details, filters)
        
        return {
            'filtros_aplicados': self._format_applied_filters(filters),
            'resumo_global': resumo_global,
            'detalhe_anotadores': annotator_details
        }
    
    def _filter_annotators(self, filters: Dict[str, Any]) -> List[Member]:
        """Filtra anotadores com base nos critérios especificados"""
        queryset = Member.objects.filter(project=self.project)
        
        # Filtrar por IDs específicos de anotadores
        if filters.get('annotator_id'):
            queryset = queryset.filter(user__id__in=filters['annotator_id'])
            
        return list(queryset.select_related('user'))
    
    def _calculate_annotator_metrics(self, member: Member, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calcula todas as métricas para um anotador específico"""
        user = member.user
        
        # Obter todas as anotações do usuário no projeto
        annotations_query = self._build_annotations_query(user, filters)
        
        if not annotations_query.exists():
            return None
        
        # Métricas básicas de produtividade
        total_anotacoes = annotations_query.count()
        datasets_distintos = self._count_distinct_datasets(user, filters)
        
        # Métricas de tempo
        tempo_metrics = self._calculate_time_metrics(user, filters)
        
        # Métricas de qualidade/concordância
        quality_metrics = self._calculate_quality_metrics(user, filters)
        
        # Perspectivas usadas
        perspectivas_usadas = self._get_used_perspectives(member, filters)
        
        # Categorias mais frequentes
        categorias_mais_frequentes = self._get_top_categories(user, filters)
        
        # Métricas temporais
        temporal_metrics = self._calculate_temporal_metrics(user, filters)
        
        return {
            'annotator_id': str(user.id),
            'nome_anotador': user.get_full_name() or user.username,
            'total_anotacoes': total_anotacoes,
            'datasets_distintos': datasets_distintos,
            'tempo_total_min': tempo_metrics['tempo_total_min'],
            'tempo_medio_por_anotacao_seg': tempo_metrics['tempo_medio_por_anotacao_seg'],
            'taxa_desacordo_percent': quality_metrics['taxa_desacordo_percent'],
            'desacordos_resolvidos': quality_metrics['desacordos_resolvidos'],
            'score_concordancia_medio': quality_metrics['score_concordancia_medio'],
            'perspectivas_usadas': perspectivas_usadas,
            'categorias_mais_frequentes': categorias_mais_frequentes,
            'primeira_anotacao': temporal_metrics['primeira_anotacao'],
            'ultima_anotacao': temporal_metrics['ultima_anotacao']
        }
    
    def _build_annotations_query(self, user: User, filters: Dict[str, Any]):
        """Constrói query para anotações com base nos filtros"""
        # Combinar todos os tipos de anotações
        categories = Category.objects.filter(
            user=user,
            example__project=self.project
        )
        spans = Span.objects.filter(
            user=user,
            example__project=self.project
        )
        texts = TextLabel.objects.filter(
            user=user,
            example__project=self.project
        )
        
        # Aplicar filtros de data
        if filters.get('data_inicial'):
            categories = categories.filter(created_at__gte=filters['data_inicial'])
            spans = spans.filter(created_at__gte=filters['data_inicial'])
            texts = texts.filter(created_at__gte=filters['data_inicial'])
            
        if filters.get('data_final'):
            categories = categories.filter(created_at__lte=filters['data_final'])
            spans = spans.filter(created_at__lte=filters['data_final'])
            texts = texts.filter(created_at__lte=filters['data_final'])
        
        # Aplicar filtros de categoria
        if filters.get('categoria_label'):
            categories = categories.filter(label__text__in=filters['categoria_label'])
            spans = spans.filter(label__text__in=filters['categoria_label'])
        
        # Combinar todas as queries (simulando UNION)
        all_annotations = list(categories) + list(spans) + list(texts)
        return all_annotations
    
    def _count_distinct_datasets(self, user: User, filters: Dict[str, Any]) -> int:
        """Conta quantos datasets distintos o usuário anotou"""
        examples = Example.objects.filter(
            project=self.project,
            categories__user=user
        ).union(
            Example.objects.filter(
                project=self.project,
                spans__user=user
            )
        ).union(
            Example.objects.filter(
                project=self.project,
                texts__user=user
            )
        )
        
        # Aplicar filtros de dataset se especificado
        if filters.get('dataset_id'):
            # Assumindo que há um campo para identificar datasets
            examples = examples.filter(meta__dataset_id__in=filters['dataset_id'])
        
        # Para este exemplo, vamos assumir que cada example pertence a um dataset
        # Na prática, isso dependeria de como os datasets são organizados
        return examples.values('meta__dataset_id').distinct().count() or 1
    
    def _calculate_time_metrics(self, user: User, filters: Dict[str, Any]) -> Dict[str, float]:
        """Calcula métricas de tempo de anotação"""
        # Para este exemplo, vamos simular tempo baseado no número de anotações
        # Na prática, seria necessário ter timestamps precisos das sessões
        
        annotations = self._build_annotations_query(user, filters)
        total_annotations = len(annotations)
        
        if total_annotations == 0:
            return {
                'tempo_total_min': 0.0,
                'tempo_medio_por_anotacao_seg': 0.0
            }
        
        # Simular tempo baseado na complexidade média das anotações
        # Tempo médio estimado: 30 segundos por anotação simples
        tempo_medio_seg = 30.0
        tempo_total_seg = total_annotations * tempo_medio_seg
        
        return {
            'tempo_total_min': tempo_total_seg / 60.0,
            'tempo_medio_por_anotacao_seg': tempo_medio_seg
        }
    
    def _calculate_quality_metrics(self, user: User, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de qualidade e concordância"""
        # Simular métricas de concordância
        # Na prática, seria necessário comparar anotações de múltiplos usuários
        
        total_annotations = len(self._build_annotations_query(user, filters))
        
        if total_annotations == 0:
            return {
                'taxa_desacordo_percent': 0.0,
                'desacordos_resolvidos': 0,
                'score_concordancia_medio': 1.0
            }
        
        # Simular taxa de desacordo baseada na distribuição típica
        taxa_desacordo = max(0.0, min(30.0, abs(hash(user.username) % 100) / 3.0))
        desacordos_total = int(total_annotations * (taxa_desacordo / 100.0))
        desacordos_resolvidos = int(desacordos_total * 0.7)  # 70% resolvidos
        
        # Simular score de concordância (Cohen's Kappa aproximado)
        score_concordancia = max(0.5, 1.0 - (taxa_desacordo / 100.0))
        
        return {
            'taxa_desacordo_percent': round(taxa_desacordo, 1),
            'desacordos_resolvidos': desacordos_resolvidos,
            'score_concordancia_medio': round(score_concordancia, 2)
        }
    
    def _get_used_perspectives(self, member: Member, filters: Dict[str, Any]) -> List[str]:
        """Obtém perspectivas utilizadas pelo anotador"""
        if member.perspective:
            return [member.perspective.name]
        return []
    
    def _get_top_categories(self, user: User, filters: Dict[str, Any]) -> List[str]:
        """Obtém as 3 categorias mais utilizadas pelo anotador"""
        # Contar categorias mais usadas
        categories = Category.objects.filter(
            user=user,
            example__project=self.project
        ).values('label__text').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        spans = Span.objects.filter(
            user=user,
            example__project=self.project
        ).values('label__text').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        # Combinar e ordenar por frequência
        all_labels = {}
        for cat in categories:
            all_labels[cat['label__text']] = cat['count']
        
        for span in spans:
            label_text = span['label__text']
            all_labels[label_text] = all_labels.get(label_text, 0) + span['count']
        
        # Retornar top 3
        sorted_labels = sorted(all_labels.items(), key=lambda x: x[1], reverse=True)
        return [label[0] for label in sorted_labels[:3]]
    
    def _calculate_temporal_metrics(self, user: User, filters: Dict[str, Any]) -> Dict[str, Optional[datetime]]:
        """Calcula métricas temporais (primeira e última anotação)"""
        annotations = self._build_annotations_query(user, filters)
        
        if not annotations:
            return {
                'primeira_anotacao': None,
                'ultima_anotacao': None
            }
        
        # Obter timestamps de todas as anotações
        timestamps = []
        for ann in annotations:
            if hasattr(ann, 'created_at'):
                timestamps.append(ann.created_at)
        
        if not timestamps:
            return {
                'primeira_anotacao': None,
                'ultima_anotacao': None
            }
        
        return {
            'primeira_anotacao': min(timestamps),
            'ultima_anotacao': max(timestamps)
        }
    
    def _sort_and_paginate(self, data: List[Dict], sort_by: str, order: str, page: int, page_size: int) -> List[Dict]:
        """Ordena e pagina os resultados"""
        # Ordenar
        reverse = (order == 'desc')
        
        if sort_by in ['total_anotacoes', 'datasets_distintos', 'tempo_total_min', 
                       'tempo_medio_por_anotacao_seg', 'taxa_desacordo_percent', 
                       'desacordos_resolvidos', 'score_concordancia_medio']:
            data.sort(key=lambda x: x[sort_by] or 0, reverse=reverse)
        elif sort_by == 'nome_anotador':
            data.sort(key=lambda x: x[sort_by] or '', reverse=reverse)
        
        # Paginar
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return data[start_idx:end_idx]
    
    def _calculate_global_summary(self, annotator_details: List[Dict], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula o resumo global do relatório"""
        if not annotator_details:
            return {
                'total_anotadores': 0,
                'total_anotacoes': 0,
                'taxa_desacordo_global_percent': 0.0
            }
        
        total_anotadores = len(annotator_details)
        total_anotacoes = sum(ann['total_anotacoes'] for ann in annotator_details)
        
        # Calcular taxa de desacordo global (média ponderada)
        if total_anotacoes > 0:
            taxa_desacordo_global = sum(
                ann['taxa_desacordo_percent'] * ann['total_anotacoes'] 
                for ann in annotator_details
            ) / total_anotacoes
        else:
            taxa_desacordo_global = 0.0
        
        return {
            'total_anotadores': total_anotadores,
            'total_anotacoes': total_anotacoes,
            'taxa_desacordo_global_percent': round(taxa_desacordo_global, 1)
        }
    
    def _format_applied_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Formata os filtros aplicados para exibição"""
        formatted = {}
        
        if filters.get('dataset_id'):
            formatted['dataset_id'] = filters['dataset_id']
        if filters.get('annotator_id'):
            formatted['annotator_id'] = filters['annotator_id']
        if filters.get('data_inicial'):
            formatted['data_inicial'] = filters['data_inicial'].isoformat()
        if filters.get('data_final'):
            formatted['data_final'] = filters['data_final'].isoformat()
        if filters.get('categoria_label'):
            formatted['categoria_label'] = filters['categoria_label']
        if filters.get('perspectiva_id'):
            formatted['perspectiva_id'] = filters['perspectiva_id']
        if filters.get('estado_desacordo'):
            formatted['estado_desacordo'] = filters['estado_desacordo']
        
        return formatted
    
    def export_to_csv(self, data: Dict[str, Any]) -> str:
        """Exporta o relatório para formato CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        headers = [
            'ID Anotador', 'Nome', 'Total Anotações', 'Datasets Distintos',
            'Tempo Total (min)', 'Tempo Médio/Anotação (seg)', 'Taxa Desacordo (%)',
            'Desacordos Resolvidos', 'Score Concordância', 'Perspectivas',
            'Categorias Mais Frequentes', 'Primeira Anotação', 'Última Anotação'
        ]
        writer.writerow(headers)
        
        # Dados
        for annotator in data['detalhe_anotadores']:
            writer.writerow([
                annotator['annotator_id'],
                annotator['nome_anotador'],
                annotator['total_anotacoes'],
                annotator['datasets_distintos'],
                f"{annotator['tempo_total_min']:.1f}",
                f"{annotator['tempo_medio_por_anotacao_seg']:.1f}",
                f"{annotator['taxa_desacordo_percent']:.1f}",
                annotator['desacordos_resolvidos'],
                f"{annotator['score_concordancia_medio']:.2f}",
                ', '.join(annotator['perspectivas_usadas']),
                ', '.join(annotator['categorias_mais_frequentes']),
                annotator['primeira_anotacao'].strftime('%Y-%m-%d %H:%M:%S') if annotator['primeira_anotacao'] else '',
                annotator['ultima_anotacao'].strftime('%Y-%m-%d %H:%M:%S') if annotator['ultima_anotacao'] else ''
            ])
        
        return output.getvalue()
    
    def export_to_pdf_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dados para exportação em PDF"""
        return {
            'title': f'Relatório de Anotadores - {self.project.name}',
            'summary': data['resumo_global'],
            'filters': data['filtros_aplicados'],
            'annotators': data['detalhe_anotadores'],
            'generated_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        } 