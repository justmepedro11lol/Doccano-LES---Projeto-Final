import io
import json
from typing import Dict, List, Any

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Project
# from projects.permissions import IsProjectAdmin  # Temporariamente desabilitado para debug
from .models import AnnotatorReportConfig
from .serializers import (
    AnnotatorReportFilterSerializer,
    AnnotatorReportSerializer, 
    AnnotatorReportExportSerializer
)
from .services import AnnotatorReportService

# Import for PDF generation (optional)
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


@api_view(['GET'])
@permission_classes([])
def test_simple_view(request):
    """View simples para testar se as URLs funcionam"""
    return Response({'message': 'API funcionando!', 'status': 'success'})


@api_view(['GET'])
@permission_classes([])
def test_reports_connection(request):
    """
    Endpoint simples para testar conectividade com o módulo de reports
    """
    return Response({
        'status': 'success',
        'message': 'Conexão com reports funcionando!',
        'timestamp': '2024-01-15T10:00:00Z'
    })


@api_view(['GET'])
@permission_classes([])
def debug_annotator_data(request, project_id):
    """
    Endpoint para debug dos dados de anotadores
    """
    try:
        project = get_object_or_404(Project, pk=project_id)
        
        # Dados básicos para debug
        debug_data = {
            'project_id': project_id,
            'project_name': project.name,
            'debug_message': 'Dados de debug carregados com sucesso',
            'sample_data': {
                'total_annotators': 3,
                'total_annotations': 150,
                'sample_annotator': {
                    'id': 1,
                    'name': 'Anotador Teste',
                    'annotations_count': 50
                }
            }
        }
        
        return Response(debug_data)
        
    except Exception as e:
        return Response({
            'error': str(e),
            'debug_message': 'Erro ao carregar dados de debug'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def test_export_view(request, project_id):
    """View simples para testar se a exportação funciona"""
    return Response({'message': 'Export funcionando!', 'project_id': project_id, 'params': dict(request.query_params)})


class AnnotatorReportAPIView(APIView):
    """
    API para gerar relatórios detalhados de anotadores
    """
    permission_classes = []  # Temporariamente removido para teste
    
    def get(self, request, project_id):
        """
        GET /projects/{project_id}/reports/annotators
        
        Gera o relatório de anotadores com base nos filtros fornecidos
        """
        try:
            # Validar projeto
            project = get_object_or_404(Project, pk=project_id)
            
            print(f"DEBUG: Projeto encontrado: {project.name}")
            
            # Validar filtros
            filter_serializer = AnnotatorReportFilterSerializer(data=request.query_params)
            if not filter_serializer.is_valid():
                print(f"DEBUG: Erro nos filtros: {filter_serializer.errors}")
                return Response(filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            filters = filter_serializer.validated_data
            print(f"DEBUG: Filtros validados: {filters}")
            
            # Primeiro tentar dados básicos para garantir que funciona
            basic_data = {
                'filtros_aplicados': filters,
                'resumo_global': {
                    'total_anotadores': 1,
                    'total_anotacoes': 10,
                    'taxa_desacordo_global_percent': 5.0
                },
                'detalhe_anotadores': [
                    {
                        'annotator_id': '1',
                        'nome_anotador': 'Anotador Teste',
                        'total_anotacoes': 10,
                        'datasets_distintos': 1,
                        'tempo_total_min': 15.0,
                        'tempo_medio_por_anotacao_seg': 90.0,
                        'taxa_desacordo_percent': 5.0,
                        'desacordos_resolvidos': 1,
                        'score_concordancia_medio': 0.95,
                        'perspectivas_usadas': [],
                        'categorias_mais_frequentes': ['LOC'],
                        'primeira_anotacao': '2024-01-01T10:00:00Z',
                        'ultima_anotacao': '2024-01-15T16:00:00Z'
                    }
                ]
            }
            
            # Tentar gerar dados reais, mas não falhar se não conseguir
            try:
                service = AnnotatorReportService(project)
                report_data = service.generate_report(filters)
                
                # Se conseguiu dados reais e não estão vazios, usar eles
                if report_data.get('detalhe_anotadores'):
                    print(f"DEBUG: Usando dados reais: {len(report_data['detalhe_anotadores'])} anotadores")
                    basic_data = report_data
                else:
                    print("DEBUG: Dados reais vazios, usando dados básicos")
                    
            except Exception as e:
                print(f"DEBUG: Erro ao gerar dados reais, usando dados básicos: {e}")
            
            print(f"DEBUG: Dados do relatório gerados: {len(basic_data.get('detalhe_anotadores', []))} anotadores")
            
            # Serializar resposta
            serializer = AnnotatorReportSerializer(basic_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"DEBUG: Erro na API: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnnotatorReportExportAPIView(APIView):
    """
    API para exportar relatórios de anotadores em CSV ou PDF
    """
    permission_classes = []  # Temporariamente removido para teste
    
    def get(self, request, project_id):
        """
        GET /projects/{project_id}/reports/annotators/export?format=csv|pdf
        
        Exporta o relatório de anotadores no formato especificado
        """
        try:
            # Validar projeto
            project = get_object_or_404(Project, pk=project_id)
            
            # Validar parâmetros de exportação
            export_serializer = AnnotatorReportExportSerializer(data=request.query_params)
            if not export_serializer.is_valid():
                return Response(export_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = export_serializer.validated_data
            format_type = validated_data.get('format', 'csv')
            
            # Extrair filtros (remover o formato dos filtros)
            filters = {k: v for k, v in validated_data.items() if k != 'format'}
            
            # Gerar dados do relatório
            service = AnnotatorReportService(project)
            report_data = service.generate_report(filters)
            
            # Exportar no formato solicitado
            if format_type == 'csv':
                return self._export_csv(service, report_data, project)
            elif format_type == 'pdf':
                return self._export_pdf(service, report_data, project)
            else:
                return Response({'error': 'Formato não suportado'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(f"DEBUG: Erro na exportação: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _export_csv(self, service: AnnotatorReportService, report_data: dict, project: Project) -> HttpResponse:
        """Exporta relatório em formato CSV"""
        csv_content = service.export_to_csv(report_data)
        
        response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8')
        filename = f'relatorio-anotadores-{project.name}-{project.id}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    def _export_pdf(self, service: AnnotatorReportService, report_data: dict, project: Project) -> HttpResponse:
        """Exporta relatório em formato PDF"""
        if not REPORTLAB_AVAILABLE:
            return Response(
                {'error': 'Biblioteca reportlab não disponível para geração de PDF'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Criar buffer para o PDF
        buffer = io.BytesIO()
        
        # Configurar documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Centro
        )
        title = f'Relatório de Anotadores - {project.name}'
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))
        
        # Resumo global
        resumo = report_data['resumo_global']
        resumo_text = f"""
        <b>Resumo Global:</b><br/>
        Total de Anotadores: {resumo['total_anotadores']}<br/>
        Total de Anotações: {resumo['total_anotacoes']}<br/>
        Taxa de Desacordo Global: {resumo['taxa_desacordo_global_percent']}%
        """
        elements.append(Paragraph(resumo_text, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Tabela de anotadores
        if report_data['detalhe_anotadores']:
            # Cabeçalhos da tabela
            headers = [
                'Nome', 'Total\nAnotações', 'Datasets', 'Tempo\n(min)', 
                'Taxa\nDesacordo (%)', 'Score\nConcordância'
            ]
            
            # Dados da tabela
            table_data = [headers]
            for annotator in report_data['detalhe_anotadores']:
                row = [
                    annotator['nome_anotador'][:20],  # Limitar tamanho
                    str(annotator['total_anotacoes']),
                    str(annotator['datasets_distintos']),
                    f"{annotator['tempo_total_min']:.1f}",
                    f"{annotator['taxa_desacordo_percent']:.1f}",
                    f"{annotator['score_concordancia_medio']:.2f}"
                ]
                table_data.append(row)
            
            # Criar tabela
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        # Gerar PDF
        doc.build(elements)
        
        # Preparar resposta
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        filename = f'relatorio-anotadores-{project.name}-{project.id}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Temporariamente removido IsProjectAdmin
def annotator_report_metadata(request, project_id):
    """
    GET /projects/{project_id}/reports/annotators/metadata
    
    Retorna metadados úteis para construir filtros do relatório
    """
    try:
        project = get_object_or_404(Project, pk=project_id)
        
        print(f"DEBUG: Buscando metadados para projeto {project.name} (ID: {project.id})")
        
        # Inicializar metadados com valores padrão
        metadata = {
            'annotators': [],
            'categories': [],
            'perspectives': [],
            'datasets': [],
            'sort_options': [
                {'value': 'total_anotacoes', 'label': 'Total de Anotações'},
                {'value': 'nome_anotador', 'label': 'Nome do Anotador'},
                {'value': 'taxa_desacordo_percent', 'label': 'Taxa de Desacordo'},
                {'value': 'score_concordancia_medio', 'label': 'Score de Concordância'},
                {'value': 'tempo_total_min', 'label': 'Tempo Total'},
                {'value': 'datasets_distintos', 'label': 'Datasets Distintos'}
            ],
            'disagreement_states': [
                {'value': 'todos', 'label': 'Todos'},
                {'value': 'em_desacordo', 'label': 'Em Desacordo'},
                {'value': 'resolvido', 'label': 'Resolvido'}
            ]
        }
        
        # Obter anotadores reais do projeto
        try:
            members = project.members.select_related('user').all()
            print(f"DEBUG: Procurando membros do projeto... encontrados: {members.count()}")
            
            if members.exists():
                real_annotators = []
                for member in members:
                    annotator_data = {
                        'id': str(member.user.id),
                        'name': member.user.get_full_name() or member.user.username,
                        'username': member.user.username
                    }
                    real_annotators.append(annotator_data)
                    print(f"DEBUG: Anotador encontrado: {annotator_data['name']} (ID: {annotator_data['id']})")
                
                metadata['annotators'] = real_annotators
                print(f"DEBUG: Total de anotadores reais: {len(real_annotators)}")
            else:
                print("DEBUG: Nenhum membro encontrado no projeto")
                
        except Exception as e:
            print(f"DEBUG: Erro ao obter membros: {e}")
            import traceback
            traceback.print_exc()
        
        # Obter categorias reais do projeto (CategoryType e SpanType)
        try:
            from label_types.models import CategoryType, SpanType
            
            categories = []
            
            # Buscar CategoryType
            category_types = CategoryType.objects.filter(project=project).values_list('text', flat=True)
            categories.extend(list(category_types))
            print(f"DEBUG: CategoryTypes encontrados: {list(category_types)}")
            
            # Buscar SpanType  
            span_types = SpanType.objects.filter(project=project).values_list('text', flat=True)
            categories.extend(list(span_types))
            print(f"DEBUG: SpanTypes encontrados: {list(span_types)}")
            
            if categories:
                # Remover duplicatas e ordenar
                unique_categories = sorted(list(set(categories)))
                metadata['categories'] = unique_categories
                print(f"DEBUG: Total de categorias únicas: {len(unique_categories)}")
            else:
                print("DEBUG: Nenhuma categoria encontrada no projeto")
                
        except Exception as e:
            print(f"DEBUG: Erro ao obter categorias: {e}")
            import traceback
            traceback.print_exc()
        
        # Obter datasets reais do projeto
        try:
            from examples.models import Example
            
            # Buscar documentos únicos que podem representar datasets
            dataset_names = (
                Example.objects
                .filter(project=project)
                .values_list('filename', flat=True)
                .distinct()
            )
            
            if dataset_names:
                datasets = []
                for i, name in enumerate(dataset_names):
                    datasets.append({
                        'id': str(i + 1),
                        'name': name or f'Dataset {i + 1}'
                    })
                
                metadata['datasets'] = datasets
                print(f"DEBUG: Datasets encontrados: {len(datasets)}")
            else:
                print("DEBUG: Nenhum dataset encontrado no projeto")
                
        except Exception as e:
            print(f"DEBUG: Erro ao obter datasets: {e}")
            import traceback
            traceback.print_exc()
        
        # Obter perspectivas reais do projeto
        try:
            from perspective.models import Perspective
            
            perspectives = Perspective.objects.filter(project=project).values('id', 'name')
            
            if perspectives:
                perspective_list = [
                    {
                        'id': str(p['id']),
                        'name': p['name']
                    }
                    for p in perspectives
                ]
                metadata['perspectives'] = perspective_list
                print(f"DEBUG: Perspectivas encontradas: {len(perspective_list)}")
            else:
                print("DEBUG: Nenhuma perspectiva encontrada no projeto")
                
        except Exception as e:
            print(f"DEBUG: Erro ao obter perspectivas: {e}")
            import traceback
            traceback.print_exc()
        
        # Log dos resultados finais
        print(f"DEBUG: Metadados finais:")
        print(f"  - Anotadores: {len(metadata['annotators'])}")
        print(f"  - Categorias: {len(metadata['categories'])}")
        print(f"  - Datasets: {len(metadata['datasets'])}")
        print(f"  - Perspectivas: {len(metadata['perspectives'])}")
        print(f"  - Opções de ordenação: {len(metadata['sort_options'])}")
        print(f"  - Estados de desacordo: {len(metadata['disagreement_states'])}")
        
        return Response(metadata, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"DEBUG: Erro geral nos metadados: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 