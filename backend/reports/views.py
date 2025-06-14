import io
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from projects.models import Project
from projects.permissions import IsProjectAdmin
from .serializers import (
    AnnotatorReportFilterSerializer,
    AnnotatorReportSerializer,
    AnnotatorReportExportSerializer
)
from .services import AnnotatorReportService


class AnnotatorReportAPIView(APIView):
    """
    API para gerar relatórios detalhados de anotadores
    """
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    
    def get(self, request, project_id):
        """
        GET /projects/{project_id}/reports/annotators
        
        Gera o relatório de anotadores com base nos filtros fornecidos
        """
        # Validar projeto
        project = get_object_or_404(Project, pk=project_id)
        
        # Validar e processar filtros
        filter_serializer = AnnotatorReportFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data
        
        try:
            # Gerar relatório
            service = AnnotatorReportService(project)
            report_data = service.generate_report(filters)
            
            # Serializar resposta
            serializer = AnnotatorReportSerializer(data=report_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erro ao gerar relatório: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnnotatorReportExportAPIView(APIView):
    """
    API para exportar relatórios de anotadores em CSV ou PDF
    """
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    
    def get(self, request, project_id):
        """
        GET /projects/{project_id}/reports/annotators/export?format=csv|pdf
        
        Exporta o relatório de anotadores no formato especificado
        """
        # Validar projeto
        project = get_object_or_404(Project, pk=project_id)
        
        # Validar parâmetros de exportação
        export_serializer = AnnotatorReportExportSerializer(data=request.query_params)
        export_serializer.is_valid(raise_exception=True)
        export_data = export_serializer.validated_data
        
        format_type = export_data.pop('format', 'csv')
        
        try:
            # Gerar dados do relatório
            service = AnnotatorReportService(project)
            report_data = service.generate_report(export_data)
            
            if format_type == 'csv':
                return self._export_csv(service, report_data, project)
            elif format_type == 'pdf':
                return self._export_pdf(service, report_data, project)
            else:
                return Response(
                    {'error': 'Formato não suportado. Use csv ou pdf'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Erro ao exportar relatório: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
@permission_classes([IsAuthenticated & IsProjectAdmin])
def annotator_report_metadata(request, project_id):
    """
    GET /projects/{project_id}/reports/annotators/metadata
    
    Retorna metadados úteis para construir filtros do relatório
    """
    project = get_object_or_404(Project, pk=project_id)
    
    try:
        # Obter listas de valores únicos para os filtros
        from django.db.models import Q
        from projects.models import Member
        from label_types.models import CategoryType, SpanType
        from labels.models import Category, Span
        
        # Anotadores do projeto
        annotators = Member.objects.filter(project=project).select_related('user')
        annotator_list = [
            {
                'id': str(member.user.id),
                'name': member.user.get_full_name() or member.user.username,
                'username': member.user.username
            }
            for member in annotators
        ]
        
        # Categorias disponíveis
        categories = CategoryType.objects.filter(project=project).values_list('text', flat=True).distinct()
        span_types = SpanType.objects.filter(project=project).values_list('text', flat=True).distinct()
        all_categories = list(set(list(categories) + list(span_types)))
        
        # Perspectivas disponíveis
        perspectives = []
        if hasattr(project, 'perspective'):
            perspectives = [{
                'id': str(project.perspective.id),
                'name': project.perspective.name
            }]
        
        # Datasets disponíveis (simulado)
        datasets = [
            {'id': 'dataset_1', 'name': 'Dataset Principal'},
            {'id': 'dataset_2', 'name': 'Dataset Teste'}
        ]
        
        metadata = {
            'annotators': annotator_list,
            'categories': all_categories,
            'perspectives': perspectives,
            'datasets': datasets,
            'sort_options': [
                {'value': 'total_anotacoes', 'label': 'Total de Anotações'},
                {'value': 'nome_anotador', 'label': 'Nome do Anotador'},
                {'value': 'taxa_desacordo_percent', 'label': 'Taxa de Desacordo'},
                {'value': 'score_concordancia_medio', 'label': 'Score de Concordância'},
                {'value': 'tempo_total_min', 'label': 'Tempo Total'}
            ],
            'disagreement_states': [
                {'value': 'todos', 'label': 'Todos'},
                {'value': 'em_desacordo', 'label': 'Em Desacordo'},
                {'value': 'resolvido', 'label': 'Resolvido'}
            ]
        }
        
        return Response(metadata, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Erro ao obter metadados: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 