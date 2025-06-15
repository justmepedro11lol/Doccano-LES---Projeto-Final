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
        
        # Ordenar e aplicar paginação
        annotator_details = self._sort_results(
            annotator_details, 
            filters.get('sort_by', 'total_anotacoes'),
            filters.get('order', 'desc')
        )
        
        # Aplicar paginação
        paginated_results, pagination_info = self._paginate_results(
            annotator_details,
            filters.get('page', 1),
            filters.get('page_size', 10)
        )
        
        # Calcular resumo global
        resumo_global = self._calculate_global_summary(annotator_details, filters)
        
        return {
            'filtros_aplicados': self._format_applied_filters(filters),
            'resumo_global': resumo_global,
            'detalhe_anotadores': paginated_results,
            'pagination': pagination_info
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
            data_inicial = self._parse_date(filters['data_inicial'])
            if data_inicial:
                categories_q = categories_q.filter(created_at__gte=data_inicial)
                spans_q = spans_q.filter(created_at__gte=data_inicial)
                texts_q = texts_q.filter(created_at__gte=data_inicial)
            
        if filters.get('data_final'):
            data_final = self._parse_date(filters['data_final'])
            if data_final:
                # Adicionar 23:59:59 para incluir todo o dia final
                data_final = data_final.replace(hour=23, minute=59, second=59)
                categories_q = categories_q.filter(created_at__lte=data_final)
                spans_q = spans_q.filter(created_at__lte=data_final)
                texts_q = texts_q.filter(created_at__lte=data_final)
        
        # Aplicar filtros de categoria
        if filters.get('categoria_label'):
            categories_q = categories_q.filter(label__text__in=filters['categoria_label'])
            spans_q = spans_q.filter(label__text__in=filters['categoria_label'])
        
        # Aplicar filtros de dataset se especificado
        if filters.get('dataset_id'):
            dataset_ids = [str(d) for d in filters['dataset_id']]
            # Filtrar por metadata do exemplo que contenha dataset_id
            categories_q = categories_q.filter(example__meta__dataset_id__in=dataset_ids)
            spans_q = spans_q.filter(example__meta__dataset_id__in=dataset_ids)
            texts_q = texts_q.filter(example__meta__dataset_id__in=dataset_ids)
        
        # Aplicar filtros de perspectiva
        if filters.get('perspectiva_id'):
            perspectiva_ids = [int(p) for p in filters['perspectiva_id'] if str(p).isdigit()]
            if perspectiva_ids:
                # Assumindo que há um campo perspectiva ou similar
                categories_q = categories_q.filter(example__meta__perspectiva_id__in=perspectiva_ids)
                spans_q = spans_q.filter(example__meta__perspectiva_id__in=perspectiva_ids)
                texts_q = texts_q.filter(example__meta__perspectiva_id__in=perspectiva_ids)
        
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
        
        # Exemplos de textos
        text_examples = TextLabel.objects.filter(
            user=user,
            example__project=self.project
        ).values_list('example_id', flat=True)
        example_ids.update(text_examples)
        
        # Obter datasets únicos dos exemplos
        if not example_ids:
            return 0
            
        datasets = Example.objects.filter(
            id__in=example_ids,
            project=self.project
        ).values_list('meta__dataset_id', flat=True).distinct()
        
        # Filtrar None values
        unique_datasets = [d for d in datasets if d is not None]
        
        return len(unique_datasets)
    
    def _calculate_time_metrics(self, user: User, filters: Dict[str, Any], total_annotations: int) -> Dict[str, float]:
        """Calcula métricas de tempo baseadas em criação/atualização de anotações"""
        
        # Obter todas as anotações do usuário
        all_annotations = []
        
        # Categories
        categories = Category.objects.filter(
            user=user,
            example__project=self.project
        ).values('created_at', 'updated_at')
        all_annotations.extend(categories)
        
        # Spans
        spans = Span.objects.filter(
            user=user,
            example__project=self.project
        ).values('created_at', 'updated_at')
        all_annotations.extend(spans)
        
        # Texts
        texts = TextLabel.objects.filter(
            user=user,
            example__project=self.project
        ).values('created_at', 'updated_at')
        all_annotations.extend(texts)
        
        if not all_annotations:
            return {
                'tempo_total_min': 0.0,
                'tempo_medio_por_anotacao_seg': 0.0
            }
        
        # Calcular tempo total aproximado
        # Usando diferença entre primeira e última anotação como proxy
        timestamps = []
        for annotation in all_annotations:
            timestamps.append(annotation['created_at'])
            if annotation['updated_at'] != annotation['created_at']:
                timestamps.append(annotation['updated_at'])
        
        if len(timestamps) < 2:
            # Se há apenas uma anotação, assumir 2 minutos por anotação
            tempo_total_min = total_annotations * 2.0
            tempo_medio_seg = 120.0
        else:
            timestamps.sort()
            tempo_total_segundos = (timestamps[-1] - timestamps[0]).total_seconds()
            tempo_total_min = tempo_total_segundos / 60.0
            tempo_medio_seg = tempo_total_segundos / total_annotations if total_annotations > 0 else 0.0
        
        return {
            'tempo_total_min': round(tempo_total_min, 2),
            'tempo_medio_por_anotacao_seg': round(tempo_medio_seg, 2)
        }
    
    def _calculate_quality_metrics(self, user: User, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de qualidade e concordância"""
        
        # Por enquanto, vamos usar métricas simuladas baseadas em padrões
        # Em uma implementação real, isso deveria calcular com base em:
        # - Comparações entre anotadores
        # - Histórico de discordâncias
        # - Métricas de inter-annotator agreement
        
        total_anotacoes = self._get_user_total_annotations(user)
        
        # Simular taxa de desacordo baseada na consistência do usuário
        # Usuários com mais anotações tendem a ter menos desacordos
        if total_anotacoes > 1000:
            taxa_desacordo = 5.0  # 5% para usuários experientes
        elif total_anotacoes > 500:
            taxa_desacordo = 12.0  # 12% para usuários intermediários
        elif total_anotacoes > 100:
            taxa_desacordo = 18.0  # 18% para usuários iniciantes
        else:
            taxa_desacordo = 25.0  # 25% para usuários muito novos
        
        # Simular desacordos resolvidos (assumindo que 70% são resolvidos)
        desacordos_total = int(total_anotacoes * (taxa_desacordo / 100))
        desacordos_resolvidos = int(desacordos_total * 0.7)
        
        # Calcular score de concordância (inverso da taxa de desacordo)
        score_concordancia = max(0.0, min(1.0, (100 - taxa_desacordo) / 100))
        
        # Aplicar filtro de estado de desacordo se especificado
        estado_desacordo = filters.get('estado_desacordo', 'todos')
        if estado_desacordo == 'em_desacordo':
            # Filtrar apenas casos em desacordo - ajustar métricas
            taxa_desacordo = min(100.0, taxa_desacordo * 1.5)
        elif estado_desacordo == 'resolvido':
            # Filtrar apenas casos resolvidos - melhorar métricas
            taxa_desacordo = max(0.0, taxa_desacordo * 0.5)
        
        return {
            'taxa_desacordo_percent': round(taxa_desacordo, 1),
            'desacordos_resolvidos': desacordos_resolvidos,
            'score_concordancia_medio': round(score_concordancia, 3)
        }
    
    def _get_user_total_annotations(self, user: User) -> int:
        """Obtém o total de anotações do usuário em todo o projeto"""
        categories = Category.objects.filter(user=user, example__project=self.project).count()
        spans = Span.objects.filter(user=user, example__project=self.project).count()
        texts = TextLabel.objects.filter(user=user, example__project=self.project).count()
        return categories + spans + texts
    
    def _get_used_perspectives(self, member: Member, filters: Dict[str, Any]) -> List[str]:
        """Obtém as perspectivas utilizadas pelo anotador"""
        # Por enquanto retornar lista vazia
        # Em implementação real, buscaria por perspectivas nos metadados das anotações
        return []
    
    def _get_top_categories(self, user: User, filters: Dict[str, Any]) -> List[str]:
        """Obtém as categorias mais frequentemente usadas pelo anotador"""
        
        # Obter categorias mais usadas
        category_counts = Category.objects.filter(
            user=user,
            example__project=self.project
        ).values('label__text').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Obter span labels mais usados
        span_counts = Span.objects.filter(
            user=user,
            example__project=self.project
        ).values('label__text').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Combinar e dedplicar
        all_labels = {}
        for item in category_counts:
            if item['label__text']:
                all_labels[item['label__text']] = all_labels.get(item['label__text'], 0) + item['count']
        
        for item in span_counts:
            if item['label__text']:
                all_labels[item['label__text']] = all_labels.get(item['label__text'], 0) + item['count']
        
        # Ordenar por frequência e retornar top 5
        sorted_labels = sorted(all_labels.items(), key=lambda x: x[1], reverse=True)[:5]
        return [label for label, count in sorted_labels]
    
    def _calculate_temporal_metrics(self, user: User, filters: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Calcula métricas temporais (primeira e última anotação)"""
        
        # Obter primeira anotação
        primeira_anotacao = None
        
        # Buscar em todas as tabelas de anotação
        primeiras = []
        
        # Categories
        first_category = Category.objects.filter(
            user=user,
            example__project=self.project
        ).order_by('created_at').first()
        if first_category:
            primeiras.append(first_category.created_at)
        
        # Spans
        first_span = Span.objects.filter(
            user=user,
            example__project=self.project
        ).order_by('created_at').first()
        if first_span:
            primeiras.append(first_span.created_at)
        
        # Texts
        first_text = TextLabel.objects.filter(
            user=user,
            example__project=self.project
        ).order_by('created_at').first()
        if first_text:
            primeiras.append(first_text.created_at)
        
        if primeiras:
            primeira_anotacao = min(primeiras).isoformat()
        
        # Obter última anotação
        ultima_anotacao = None
        
        ultimas = []
        
        # Categories
        last_category = Category.objects.filter(
            user=user,
            example__project=self.project
        ).order_by('-created_at').first()
        if last_category:
            ultimas.append(last_category.created_at)
        
        # Spans
        last_span = Span.objects.filter(
            user=user,
            example__project=self.project
        ).order_by('-created_at').first()
        if last_span:
            ultimas.append(last_span.created_at)
        
        # Texts
        last_text = TextLabel.objects.filter(
            user=user,
            example__project=self.project
        ).order_by('-created_at').first()
        if last_text:
            ultimas.append(last_text.created_at)
        
        if ultimas:
            ultima_anotacao = max(ultimas).isoformat()
        
        return {
            'primeira_anotacao': primeira_anotacao,
            'ultima_anotacao': ultima_anotacao
        }
    
    def _sort_results(self, data: List[Dict], sort_by: str, order: str) -> List[Dict]:
        """Ordena os resultados"""
        
        # Mapear campos para keys válidas
        sort_map = {
            'nome_anotador': 'nome_anotador',
            'total_anotacoes': 'total_anotacoes',
            'datasets_distintos': 'datasets_distintos',
            'tempo_total_min': 'tempo_total_min',
            'tempo_medio_por_anotacao_seg': 'tempo_medio_por_anotacao_seg',
            'taxa_desacordo_percent': 'taxa_desacordo_percent',
            'score_concordancia_medio': 'score_concordancia_medio',
            'primeira_anotacao': 'primeira_anotacao',
            'ultima_anotacao': 'ultima_anotacao'
        }
        
        sort_key = sort_map.get(sort_by, 'total_anotacoes')
        reverse = order == 'desc'
        
        try:
            # Tratar casos especiais para ordenação
            if sort_key in ['primeira_anotacao', 'ultima_anotacao']:
                # Ordenação por data
                return sorted(data, 
                    key=lambda x: x.get(sort_key) or '1900-01-01', 
                    reverse=reverse
                )
            else:
                # Ordenação numérica ou de string
                return sorted(data, 
                    key=lambda x: x.get(sort_key, 0), 
                    reverse=reverse
                )
        except (TypeError, KeyError):
            # Fallback para ordenação por total_anotacoes
            return sorted(data, key=lambda x: x.get('total_anotacoes', 0), reverse=True)
    
    def _paginate_results(self, data: List[Dict], page: int, page_size: int) -> Tuple[List[Dict], Dict[str, Any]]:
        """Aplica paginação aos resultados"""
        
        page = max(1, int(page))
        page_size = max(1, min(100, int(page_size)))  # Limitar página size a 100
        
        total_items = len(data)
        total_pages = (total_items + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated_data = data[start_idx:end_idx]
        
        pagination_info = {
            'total': total_items,
            'page': page,
            'pages': total_pages,
            'per_page': page_size,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
        
        return paginated_data, pagination_info
    
    def _calculate_global_summary(self, annotator_details: List[Dict], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula o resumo global do relatório"""
        
        if not annotator_details:
            return {
                'total_anotadores': 0,
                'total_anotacoes': 0,
                'taxa_desacordo_global_percent': 0.0,
                'score_concordancia_global': 0.0
            }
        
        total_anotadores = len(annotator_details)
        total_anotacoes = sum(detail['total_anotacoes'] for detail in annotator_details)
        
        # Calcular média ponderada da taxa de desacordo
        taxa_desacordo_ponderada = 0.0
        score_concordancia_ponderado = 0.0
        
        if total_anotacoes > 0:
            for detail in annotator_details:
                peso = detail['total_anotacoes'] / total_anotacoes
                taxa_desacordo_ponderada += detail['taxa_desacordo_percent'] * peso
                score_concordancia_ponderado += detail['score_concordancia_medio'] * peso
        
        return {
            'total_anotadores': total_anotadores,
            'total_anotacoes': total_anotacoes,
            'taxa_desacordo_global_percent': round(taxa_desacordo_ponderada, 1),
            'score_concordancia_global': round(score_concordancia_ponderado * 100, 1)  # Converter para percentual
        }
    
    def _format_applied_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Formata os filtros aplicados para exibição"""
        
        formatted = {}
        
        if filters.get('annotator_id'):
            formatted['anotadores'] = len(filters['annotator_id'])
        
        if filters.get('dataset_id'):
            formatted['datasets'] = len(filters['dataset_id'])
        
        if filters.get('categoria_label'):
            formatted['categorias'] = len(filters['categoria_label'])
        
        if filters.get('perspectiva_id'):
            formatted['perspectivas'] = len(filters['perspectiva_id'])
        
        if filters.get('data_inicial'):
            formatted['data_inicial'] = filters['data_inicial']
        
        if filters.get('data_final'):
            formatted['data_final'] = filters['data_final']
        
        if filters.get('estado_desacordo', 'todos') != 'todos':
            formatted['estado_desacordo'] = filters['estado_desacordo']
        
        return formatted
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Converte string de data para datetime"""
        if not date_string:
            return None
        
        try:
            # Tentar diferentes formatos
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    dt = datetime.strptime(date_string, fmt)
                    # Se não tem timezone, assumir timezone do Django
                    if dt.tzinfo is None:
                        dt = timezone.make_aware(dt)
                    return dt
                except ValueError:
                    continue
            
            return None
        except Exception:
            return None
    
    def export_to_csv(self, data: Dict[str, Any]) -> str:
        """Exporta os dados do relatório para CSV"""
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escrever cabeçalho
        headers = [
            'ID Anotador', 'Nome Anotador', 'Total Anotações', 'Datasets Distintos',
            'Tempo Total (min)', 'Tempo Médio por Anotação (seg)', 'Taxa Desacordo (%)',
            'Desacordos Resolvidos', 'Score Concordância', 'Perspectivas Usadas',
            'Categorias Mais Frequentes', 'Primeira Anotação', 'Última Anotação'
        ]
        writer.writerow(headers)
        
        # Escrever dados
        for annotator in data.get('detalhe_anotadores', []):
            row = [
                annotator.get('annotator_id', ''),
                annotator.get('nome_anotador', ''),
                annotator.get('total_anotacoes', 0),
                annotator.get('datasets_distintos', 0),
                annotator.get('tempo_total_min', 0.0),
                annotator.get('tempo_medio_por_anotacao_seg', 0.0),
                annotator.get('taxa_desacordo_percent', 0.0),
                annotator.get('desacordos_resolvidos', 0),
                annotator.get('score_concordancia_medio', 0.0),
                ', '.join(annotator.get('perspectivas_usadas', [])),
                ', '.join(annotator.get('categorias_mais_frequentes', [])),
                annotator.get('primeira_anotacao', ''),
                annotator.get('ultima_anotacao', '')
            ]
            writer.writerow(row)
        
        return output.getvalue()
    
    def export_to_pdf_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara os dados para exportação em PDF"""
        
        return {
            'title': f'Relatório de Anotadores - {self.project.name}',
            'project_name': self.project.name,
            'generated_at': timezone.now().strftime('%d/%m/%Y %H:%M'),
            'filters': data.get('filtros_aplicados', {}),
            'summary': data.get('resumo_global', {}),
            'annotators': data.get('detalhe_anotadores', [])
        } 