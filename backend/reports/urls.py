from django.urls import path
from .views import (
    AnnotatorReportAPIView,
    AnnotatorReportExportAPIView,
    annotator_report_metadata,
    test_reports_connection,
    debug_annotator_data
)

urlpatterns = [
    # Teste de conexão
    path(
        'test-reports/',
        test_reports_connection,
        name='test_reports'
    ),
    
    # Debug de dados de anotadores
    path(
        'projects/<int:project_id>/reports/annotators/debug',
        debug_annotator_data,
        name='debug_annotator_data'
    ),
    
    # Relatório de anotadores
    path(
        'projects/<int:project_id>/reports/annotators',
        AnnotatorReportAPIView.as_view(),
        name='annotator_report'
    ),
    
    # Exportação do relatório
    path(
        'projects/<int:project_id>/reports/annotators/export',
        AnnotatorReportExportAPIView.as_view(),
        name='annotator_report_export'
    ),
    
    # Metadados para filtros
    path(
        'projects/<int:project_id>/reports/annotators/metadata',
        annotator_report_metadata,
        name='annotator_report_metadata'
    ),
] 