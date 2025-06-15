from django.urls import path
from .views import (
    AnnotatorReportAPIView,
    AnnotatorReportExportAPIView,
    annotator_report_metadata,
    test_reports_connection,
    debug_annotator_data,
    test_simple_view,
    test_export_view
)

urlpatterns = [
    # Teste simples
    path(
        'test-simple/',
        test_simple_view,
        name='test_simple'
    ),
    
    # Teste de conexão
    path(
        'test-reports/',
        test_reports_connection,
        name='test_reports'
    ),
    
    # Debug de dados de anotadores
    path(
        'annotators/debug',
        debug_annotator_data,
        name='debug_annotator_data'
    ),
    
    # Relatório de anotadores
    path(
        'annotators',
        AnnotatorReportAPIView.as_view(),
        name='annotator_report'
    ),
    
    # Teste de exportação
    path(
        'annotators/export-test',
        test_export_view,
        name='test_export'
    ),
    
    # Exportação do relatório
    path(
        'annotators/export',
        AnnotatorReportExportAPIView.as_view(),
        name='annotator_report_export'
    ),
    
    # Metadados para filtros
    path(
        'annotators/metadata',
        annotator_report_metadata,
        name='annotator_report_metadata'
    ),
] 