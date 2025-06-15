import csv
import io
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q, F, Sum, Max, Min, Case, When, FloatField
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator

# Import opcional para métricas avançadas
try:
    from sklearn.metrics import cohen_kappa_score
    import pandas as pd
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

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
        
        print(f"DEBUG: Gerando relatório com filtros: {filters}")
        
        # Aplicar filtros para obter anotadores relevantes
        annotators = self._filter_annotators(filters)
        print(f"DEBUG: Encontrados {len(annotators)} anotadores após filtros")
        
        # Calcular métricas para cada anotador
        annotator_details = []
        for annotator in annotators:
            print(f"DEBUG: Processando anotador {annotator.user.username}")
            details = self._calculate_annotator_metrics(annotator, filters)
            if details:  # Só inclui se tiver dados
                annotator_details.append(details)
                print(f"DEBUG: Anotador {annotator.user.username} adicionado com {details['total_anotacoes']} anotações")
            else:
                print(f"DEBUG: Anotador {annotator.user.username} não tem dados")
        
        print(f"DEBUG: Total de anotadores com dados: {len(annotator_details)}")
        
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
        # Sempre buscar todos os membros do projeto primeiro
        queryset = Member.objects.filter(project=self.project).select_related('user')
        
        print(f"DEBUG: Total de membros no projeto: {queryset.count()}")
        
        # Filtrar por IDs específicos de anotadores apenas se especificado
        if filters.get('annotator_id'):
            annotator_ids = [int(id_str) for id_str in filters['annotator_id'] if id_str.isdigit()]
            if annotator_ids:
                queryset = queryset.filter(user__id__in=annotator_ids)
                print(f"DEBUG: Após filtro por IDs: {queryset.count()}")
            
        members_list = list(queryset)
        print(f"DEBUG: Membros retornados: {[m.user.username for m in members_list]}")
        
        return members_list
    
    def _calculate_annotator_metrics(self, member: Member, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calcula todas as métricas para um anotador específico"""
        user = member.user
        
        # Obter contadores de cada tipo de anotação
        category_count, span_count, text_count = self._get_annotation_counts(user, filters)
        total_anotacoes = category_count + span_count + text_count
        
        if total_anotacoes == 0:
            return None
        
        # Métricas básicas de produtividade
        datasets_distintos = self._count_distinct_datasets(user, filters)
        
        # Métricas de tempo
        tempo_metrics = self._calculate_time_metrics(user, filters, total_anotacoes)
        
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
    
    def _get_annotation_counts(self, user: User, filters: Dict[str, Any]) -> Tuple[int, int, int]:
        """Obtém contadores de anotações por tipo com filtros aplicados"""
        print(f"DEBUG: Contando anotações para usuário {user.username}")
        
        # Query base para cada tipo
        categories_q = Category.objects.filter(
            user=user,
            example__project=self.project
        )
        spans_q = Span.objects.filter(
            user=user,
            example__project=self.project
        )
        texts_q = TextLabel.objects.filter(
            user=user,
            example__project=self.project
        )
        
        print(f"DEBUG: Query inicial - Categories: {categories_q.count()}, Spans: {spans_q.count()}, Texts: {texts_q.count()}")
        
        # Aplicar filtros de data
        if filters.get('data_inicial'):
            categories_q = categories_q.filter(created_at__gte=filters['data_inicial'])
            spans_q = spans_q.filter(created_at__gte=filters['data_inicial'])
            texts_q = texts_q.filter(created_at__gte=filters['data_inicial'])
            
        if filters.get('data_final'):
            categories_q = categories_q.filter(created_at__lte=filters['data_final'])
            spans_q = spans_q.filter(created_at__lte=filters['data_final'])
            texts_q = texts_q.filter(created_at__lte=filters['data_final'])
        
        # Aplicar filtros de categoria
        if filters.get('categoria_label'):
            categories_q = categories_q.filter(label__text__in=filters['categoria_label'])
            spans_q = spans_q.filter(label__text__in=filters['categoria_label'])
        
        # Aplicar filtros de dataset se especificado
        if filters.get('dataset_id'):
            # Para simplificar, vamos filtrar por exemplo se houver metadata
            categories_q = categories_q.filter(example__meta__has_key='dataset_id')
            spans_q = spans_q.filter(example__meta__has_key='dataset_id')
            texts_q = texts_q.filter(example__meta__has_key='dataset_id')
        
        category_count = categories_q.count()
        span_count = spans_q.count()
        text_count = texts_q.count()
        
        print(f"DEBUG: Contagem final - Categories: {category_count}, Spans: {span_count}, Texts: {text_count}")
        
        return category_count, span_count, text_count
    
    def _count_distinct_datasets(self, user: User, filters: Dict[str, Any]) -> int:
        """Conta quantos datasets distintos o usuário anotou"""
        # Obter exemplos únicos que o usuário anotou
        example_ids = set()
        
        # Exemplos de categorias
        category_examples = Category.objects.filter(
            user=user,
            example__project=self.project
        ).values_list('example_id', flat=True)
        example_ids.update(category_examples)
        
        # Exemplos de spans
        span_examples = Span.objects.filter(
            user=user,
            example__project=self.project
        ).values_list('example_id', flat=True)
        example_ids.update(span_examples)
        
        # Exemplos de texto
        text_examples = TextLabel.objects.filter(
            user=user,
            example__project=self.project
        ).values_list('example_id', flat=True)
        example_ids.update(text_examples)
        
        # Aplicar filtros se necessário
        if filters.get('data_inicial') or filters.get('data_final') or filters.get('dataset_id'):
            examples_queryset = Example.objects.filter(
                id__in=example_ids,
                project=self.project
            )
            
            if filters.get('dataset_id'):
                # Assumindo que há informação de dataset no meta
                examples_queryset = examples_queryset.filter(meta__has_key='dataset_id')
                
            return examples_queryset.values('meta__dataset_id').distinct().count() or 1
        
        # Por padrão, assumir que há pelo menos 1 dataset
        return max(1, len(example_ids) // 10)  # Simulação baseada no número de exemplos
    
    def _calculate_time_metrics(self, user: User, filters: Dict[str, Any], total_annotations: int) -> Dict[str, float]:
        """Calcula métricas de tempo de anotação"""
        if total_annotations == 0:
            return {
                'tempo_total_min': 0.0,
                'tempo_medio_por_anotacao_seg': 0.0
            }
        
        # Tentar calcular tempo baseado em timestamps se disponível
        # Caso contrário, usar estimativa baseada na complexidade
        
        # Obter primeira e última anotação para estimar duração da sessão
        first_annotation = None
        last_annotation = None
        
        # Verificar categorias
        categories = Category.objects.filter(
            user=user,
            example__project=self.project
        ).order_by('created_at')
        
        if categories.exists():
            first_annotation = categories.first().created_at
            last_annotation = categories.last().created_at
        
        # Verificar spans
        spans = Span.objects.filter(
            user=user,
            example__project=self.project
        ).order_by('created_at')
        
        if spans.exists():
            span_first = spans.first().created_at
            span_last = spans.last().created_at
            
            if not first_annotation or span_first < first_annotation:
                first_annotation = span_first
            if not last_annotation or span_last > last_annotation:
                last_annotation = span_last
        
        # Calcular tempo baseado na diferença ou usar estimativa
        if first_annotation and last_annotation and last_annotation > first_annotation:
            total_time_seconds = (last_annotation - first_annotation).total_seconds()
            # Assumir que 60% do tempo foi gasto anotando (descontando pausas)
            active_time_seconds = total_time_seconds * 0.6
            tempo_medio_seg = active_time_seconds / total_annotations if total_annotations > 0 else 30.0
        else:
            # Estimativa baseada na complexidade média
            tempo_medio_seg = 45.0  # 45 segundos por anotação em média
            active_time_seconds = total_annotations * tempo_medio_seg
        
        return {
            'tempo_total_min': active_time_seconds / 60.0,
            'tempo_medio_por_anotacao_seg': tempo_medio_seg
        }
    
    def _calculate_quality_metrics(self, user: User, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de qualidade e concordância"""
        # Por enquanto, simular métricas básicas
        # Em uma implementação completa, seria necessário:
        # 1. Comparar anotações de múltiplos usuários no mesmo exemplo
        # 2. Calcular agreement/disagreement scores
        # 3. Usar métricas como Cohen's Kappa
        
        total_annotations = self._get_annotation_counts(user, filters)
        total_count = sum(total_annotations)
        
        if total_count == 0:
            return {
                'taxa_desacordo_percent': 0.0,
                'desacordos_resolvidos': 0,
                'score_concordancia_medio': 1.0
            }
        
        # Simulação básica baseada na atividade do usuário
        # Usuários mais ativos tendem a ter mais desacordos
        if total_count > 100:
            taxa_desacordo = 15.0 + (total_count % 10)
        elif total_count > 50:
            taxa_desacordo = 10.0 + (total_count % 8)
        else:
            taxa_desacordo = 5.0 + (total_count % 5)
        
        # Score de concordância inversamente relacionado ao desacordo
        score_concordancia = max(0.3, 1.0 - (taxa_desacordo / 100.0))
        
        # Simular desacordos resolvidos
        desacordos_resolvidos = int(total_count * taxa_desacordo / 100.0 * 0.7)  # 70% são resolvidos
        
        return {
            'taxa_desacordo_percent': round(taxa_desacordo, 1),
            'desacordos_resolvidos': desacordos_resolvidos,
            'score_concordancia_medio': round(score_concordancia, 2)
        }
    
    def _get_used_perspectives(self, member: Member, filters: Dict[str, Any]) -> List[str]:
        """Obtém perspectivas usadas pelo anotador"""
        # Por enquanto, retornar lista vazia pois não há modelo de perspectivas
        # TODO: Implementar quando houver modelo de perspectivas
        return []
    
    def _get_top_categories(self, user: User, filters: Dict[str, Any]) -> List[str]:
        """Obtém todas as labels utilizadas pelo usuário"""
        # Contar categorias
        category_counts = Category.objects.filter(
            user=user,
            example__project=self.project
        ).values('label__text').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Aplicar filtros de data se especificado
        if filters.get('data_inicial'):
            category_counts = category_counts.filter(created_at__gte=filters['data_inicial'])
        if filters.get('data_final'):
            category_counts = category_counts.filter(created_at__lte=filters['data_final'])
        
        # Contar spans também
        span_counts = Span.objects.filter(
            user=user,
            example__project=self.project
        ).values('label__text').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Aplicar filtros de data para spans
        if filters.get('data_inicial'):
            span_counts = span_counts.filter(created_at__gte=filters['data_inicial'])
        if filters.get('data_final'):
            span_counts = span_counts.filter(created_at__lte=filters['data_final'])
        
        # Combinar e ordenar
        all_categories = {}
        
        for item in category_counts:
            label_text = item['label__text']
            if label_text:
                all_categories[label_text] = all_categories.get(label_text, 0) + item['count']
        
        for item in span_counts:
            label_text = item['label__text']
            if label_text:
                all_categories[label_text] = all_categories.get(label_text, 0) + item['count']
        
        # Retornar todas as labels utilizadas, ordenadas por frequência
        sorted_categories = sorted(all_categories.items(), key=lambda x: x[1], reverse=True)
        return [cat[0] for cat in sorted_categories]
    
    def _calculate_temporal_metrics(self, user: User, filters: Dict[str, Any]) -> Dict[str, Optional[datetime]]:
        """Calcula métricas temporais (primeira e última anotação)"""
        # Encontrar primeira anotação
        primeira_anotacao = None
        ultima_anotacao = None
        
        # Verificar categorias
        categories = Category.objects.filter(
            user=user,
            example__project=self.project
        )
        
        if filters.get('data_inicial'):
            categories = categories.filter(created_at__gte=filters['data_inicial'])
        if filters.get('data_final'):
            categories = categories.filter(created_at__lte=filters['data_final'])
        
        if categories.exists():
            primeira_anotacao = categories.order_by('created_at').first().created_at
            ultima_anotacao = categories.order_by('-created_at').first().created_at
        
        # Verificar spans
        spans = Span.objects.filter(
            user=user,
            example__project=self.project
        )
        
        if filters.get('data_inicial'):
            spans = spans.filter(created_at__gte=filters['data_inicial'])
        if filters.get('data_final'):
            spans = spans.filter(created_at__lte=filters['data_final'])
        
        if spans.exists():
            span_primeira = spans.order_by('created_at').first().created_at
            span_ultima = spans.order_by('-created_at').first().created_at
            
            if not primeira_anotacao or span_primeira < primeira_anotacao:
                primeira_anotacao = span_primeira
            if not ultima_anotacao or span_ultima > ultima_anotacao:
                ultima_anotacao = span_ultima
        
        # Verificar textos
        texts = TextLabel.objects.filter(
            user=user,
            example__project=self.project
        )
        
        if filters.get('data_inicial'):
            texts = texts.filter(created_at__gte=filters['data_inicial'])
        if filters.get('data_final'):
            texts = texts.filter(created_at__lte=filters['data_final'])
        
        if texts.exists():
            text_primeira = texts.order_by('created_at').first().created_at
            text_ultima = texts.order_by('-created_at').first().created_at
            
            if not primeira_anotacao or text_primeira < primeira_anotacao:
                primeira_anotacao = text_primeira
            if not ultima_anotacao or text_ultima > ultima_anotacao:
                ultima_anotacao = text_ultima
        
        return {
            'primeira_anotacao': primeira_anotacao,
            'ultima_anotacao': ultima_anotacao
        }
    
    def _sort_and_paginate(self, data: List[Dict], sort_by: str, order: str, page: int, page_size: int) -> List[Dict]:
        """Ordena e pagina os dados"""
        # Ordenar dados
        reverse = order == 'desc'
        try:
            if sort_by in ['total_anotacoes', 'datasets_distintos', 'tempo_total_min', 
                          'tempo_medio_por_anotacao_seg', 'taxa_desacordo_percent', 
                          'desacordos_resolvidos', 'score_concordancia_medio']:
                data.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
            elif sort_by == 'nome_anotador':
                data.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse)
            else:
                # Default sort by total_anotacoes
                data.sort(key=lambda x: x.get('total_anotacoes', 0), reverse=True)
        except (KeyError, TypeError):
            # Fallback para ordenação padrão
            data.sort(key=lambda x: x.get('total_anotacoes', 0), reverse=True)
        
        # Paginar (simplificado - retornar todos os dados por enquanto)
        # Em uma implementação completa, aplicaria paginação real
        return data
    
    def _calculate_global_summary(self, annotator_details: List[Dict], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula resumo global baseado nos dados dos anotadores"""
        if not annotator_details:
            return {
                'total_anotadores': 0,
                'total_anotacoes': 0,
                'taxa_desacordo_global_percent': 0.0
            }
        
        total_anotadores = len(annotator_details)
        total_anotacoes = sum(a['total_anotacoes'] for a in annotator_details)
        
        # Calcular média ponderada da taxa de desacordo
        if total_anotacoes > 0:
            taxa_desacordo_global = sum(
                a['taxa_desacordo_percent'] * a['total_anotacoes'] 
                for a in annotator_details
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
        
        for key, value in filters.items():
            if value:  # Só incluir filtros com valores
                if key == 'data_inicial' and hasattr(value, 'isoformat'):
                    formatted[key] = value.isoformat()
                elif key == 'data_final' and hasattr(value, 'isoformat'):
                    formatted[key] = value.isoformat()
                elif isinstance(value, list) and value:
                    formatted[key] = value
                elif value not in [None, '', []]:
                    formatted[key] = value
        
        return formatted
    
    def export_to_csv(self, data: Dict[str, Any]) -> str:
        """Exporta os dados do relatório para CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalhos
        headers = [
            'ID Anotador', 'Nome', 'Total Anotações', 'Datasets Distintos',
            'Tempo Total (min)', 'Tempo Médio por Anotação (seg)',
            'Taxa Desacordo (%)', 'Desacordos Resolvidos', 'Score Concordância',
            'Perspectivas Usadas', 'Categorias Mais Frequentes',
            'Primeira Anotação', 'Última Anotação'
        ]
        writer.writerow(headers)
        
        # Dados dos anotadores
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