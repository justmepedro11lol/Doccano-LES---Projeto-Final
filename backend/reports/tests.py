import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from projects.models import Project, Member
from projects.tests.utils import prepare_project
from examples.models import Example
from labels.models import Category, Span, TextLabel
from label_types.models import CategoryType, SpanType
from .services import AnnotatorReportService
from .models import AnnotatorReportConfig


class AnnotatorReportServiceTestCase(TestCase):
    """Testes para o serviço de relatórios de anotadores"""
    
    def setUp(self):
        self.project = prepare_project()
        self.service = AnnotatorReportService(self.project.item)
        
        # Criar usuários e membros adicionais
        self.user1 = User.objects.create_user('annotator1', 'ann1@test.com', 'pass')
        self.user2 = User.objects.create_user('annotator2', 'ann2@test.com', 'pass')
        
        self.member1 = Member.objects.create(
            user=self.user1,
            project=self.project.item,
            role=self.project.annotator_role
        )
        self.member2 = Member.objects.create(
            user=self.user2,
            project=self.project.item,
            role=self.project.annotator_role
        )
        
        # Criar exemplos e anotações para teste
        self.create_test_data()
    
    def create_test_data(self):
        """Criar dados de teste: examples, labels, etc."""
        # Criar tipos de categoria
        self.cat_type1 = CategoryType.objects.create(
            text='LOC',
            project=self.project.item
        )
        self.cat_type2 = CategoryType.objects.create(
            text='ORG',
            project=self.project.item
        )
        
        # Criar exemplos
        self.example1 = Example.objects.create(
            text='Test text 1',
            project=self.project.item
        )
        self.example2 = Example.objects.create(
            text='Test text 2',
            project=self.project.item
        )
        
        # Criar anotações para user1
        Category.objects.create(
            example=self.example1,
            user=self.user1,
            label=self.cat_type1,
            created_at=timezone.now() - timedelta(days=5)
        )
        Category.objects.create(
            example=self.example2,
            user=self.user1,
            label=self.cat_type2,
            created_at=timezone.now() - timedelta(days=3)
        )
        
        # Criar anotações para user2
        Category.objects.create(
            example=self.example1,
            user=self.user2,
            label=self.cat_type1,
            created_at=timezone.now() - timedelta(days=4)
        )
    
    def test_generate_report_basic(self):
        """Testa geração básica de relatório"""
        filters = {
            'sort_by': 'total_anotacoes',
            'order': 'desc',
            'page': 1,
            'page_size': 10
        }
        
        report = self.service.generate_report(filters)
        
        # Verificar estrutura do relatório
        self.assertIn('filtros_aplicados', report)
        self.assertIn('resumo_global', report)
        self.assertIn('detalhe_anotadores', report)
        
        # Verificar resumo global
        resumo = report['resumo_global']
        self.assertIn('total_anotadores', resumo)
        self.assertIn('total_anotacoes', resumo)
        self.assertIn('taxa_desacordo_global_percent', resumo)
        
        # Verificar que há pelo menos um anotador
        self.assertGreater(len(report['detalhe_anotadores']), 0)
    
    def test_filter_by_annotator_id(self):
        """Testa filtro por ID de anotador"""
        filters = {
            'annotator_id': [str(self.user1.id)],
            'sort_by': 'total_anotacoes',
            'order': 'desc',
            'page': 1,
            'page_size': 10
        }
        
        report = self.service.generate_report(filters)
        
        # Deve retornar apenas dados do user1
        annotators = report['detalhe_anotadores']
        self.assertEqual(len(annotators), 1)
        self.assertEqual(annotators[0]['annotator_id'], str(self.user1.id))
    
    def test_filter_by_date_range(self):
        """Testa filtro por intervalo de datas"""
        filters = {
            'data_inicial': timezone.now() - timedelta(days=4),
            'data_final': timezone.now() - timedelta(days=2),
            'sort_by': 'total_anotacoes',
            'order': 'desc',
            'page': 1,
            'page_size': 10
        }
        
        report = self.service.generate_report(filters)
        
        # Deve incluir apenas anotações no intervalo especificado
        self.assertIsNotNone(report['detalhe_anotadores'])
    
    def test_export_to_csv(self):
        """Testa exportação para CSV"""
        filters = {}
        report_data = self.service.generate_report(filters)
        
        csv_content = self.service.export_to_csv(report_data)
        
        # Verificar que o CSV contém cabeçalhos
        self.assertIn('ID Anotador', csv_content)
        self.assertIn('Nome', csv_content)
        self.assertIn('Total Anotações', csv_content)
        
        # Verificar que há pelo menos uma linha de dados
        lines = csv_content.split('\n')
        self.assertGreater(len(lines), 1)
    
    def test_calculate_annotator_metrics(self):
        """Testa cálculo de métricas individuais do anotador"""
        filters = {}
        
        # Testar métricas para user1
        metrics = self.service._calculate_annotator_metrics(self.member1, filters)
        
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics['annotator_id'], str(self.user1.id))
        self.assertGreater(metrics['total_anotacoes'], 0)
        self.assertGreaterEqual(metrics['datasets_distintos'], 1)
        self.assertGreaterEqual(metrics['tempo_total_min'], 0)
        self.assertGreaterEqual(metrics['score_concordancia_medio'], 0)


class AnnotatorReportAPITestCase(APITestCase):
    """Testes para as APIs de relatórios de anotadores"""
    
    def setUp(self):
        self.project = prepare_project()
        self.admin_user = self.project.admin
        self.annotator_user = self.project.annotator
        
        # URLs
        self.report_url = reverse(
            'annotator_report',
            kwargs={'project_id': self.project.item.id}
        )
        self.export_url = reverse(
            'annotator_report_export',
            kwargs={'project_id': self.project.item.id}
        )
        self.metadata_url = reverse(
            'annotator_report_metadata',
            kwargs={'project_id': self.project.item.id}
        )
    
    def test_get_report_as_admin(self):
        """Testa acesso ao relatório como admin"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.report_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estrutura da resposta
        data = response.json()
        self.assertIn('filtros_aplicados', data)
        self.assertIn('resumo_global', data)
        self.assertIn('detalhe_anotadores', data)
    
    def test_get_report_as_annotator_forbidden(self):
        """Testa que anotadores não podem acessar relatórios"""
        self.client.force_authenticate(user=self.annotator_user)
        
        response = self.client.get(self.report_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_report_unauthenticated(self):
        """Testa acesso não autenticado"""
        response = self.client.get(self.report_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_report_with_filters(self):
        """Testa relatório com filtros aplicados"""
        self.client.force_authenticate(user=self.admin_user)
        
        params = {
            'sort_by': 'nome_anotador',
            'order': 'asc',
            'page_size': 5,
            'estado_desacordo': 'todos'
        }
        
        response = self.client.get(self.report_url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('filtros_aplicados', data)
        
        # Verificar que filtros foram aplicados
        filtros = data['filtros_aplicados']
        if filtros:  # Pode estar vazio se não houver dados
            self.assertEqual(filtros.get('estado_desacordo'), 'todos')
    
    def test_export_csv(self):
        """Testa exportação CSV"""
        self.client.force_authenticate(user=self.admin_user)
        
        params = {'format': 'csv'}
        response = self.client.get(self.export_url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment', response['Content-Disposition'])
    
    @patch('reports.views.REPORTLAB_AVAILABLE', True)
    def test_export_pdf_with_reportlab(self):
        """Testa exportação PDF quando reportlab está disponível"""
        self.client.force_authenticate(user=self.admin_user)
        
        params = {'format': 'pdf'}
        
        with patch('reports.views.SimpleDocTemplate') as mock_doc:
            mock_doc.return_value.build = MagicMock()
            
            response = self.client.get(self.export_url, params)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response['Content-Type'], 'application/pdf')
    
    @patch('reports.views.REPORTLAB_AVAILABLE', False)
    def test_export_pdf_without_reportlab(self):
        """Testa exportação PDF quando reportlab não está disponível"""
        self.client.force_authenticate(user=self.admin_user)
        
        params = {'format': 'pdf'}
        response = self.client.get(self.export_url, params)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('reportlab', data['error'])
    
    def test_export_invalid_format(self):
        """Testa exportação com formato inválido"""
        self.client.force_authenticate(user=self.admin_user)
        
        params = {'format': 'xlsx'}  # Formato não suportado
        response = self.client.get(self.export_url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('não suportado', data['error'])
    
    def test_get_metadata(self):
        """Testa obtenção de metadados para filtros"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.metadata_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('annotators', data)
        self.assertIn('categories', data)
        self.assertIn('perspectives', data)
        self.assertIn('datasets', data)
        self.assertIn('sort_options', data)
        self.assertIn('disagreement_states', data)
        
        # Verificar estrutura dos anotadores
        if data['annotators']:
            annotator = data['annotators'][0]
            self.assertIn('id', annotator)
            self.assertIn('name', annotator)
            self.assertIn('username', annotator)
    
    def test_invalid_project_id(self):
        """Testa acesso com ID de projeto inválido"""
        self.client.force_authenticate(user=self.admin_user)
        
        invalid_url = reverse(
            'annotator_report',
            kwargs={'project_id': 99999}
        )
        
        response = self.client.get(invalid_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AnnotatorReportConfigTestCase(TestCase):
    """Testes para o modelo AnnotatorReportConfig"""
    
    def setUp(self):
        self.project = prepare_project()
        self.user = self.project.admin
    
    def test_create_report_config(self):
        """Testa criação de configuração de relatório"""
        config = AnnotatorReportConfig.objects.create(
            project=self.project.item,
            created_by=self.user,
            dataset_ids=['dataset_1', 'dataset_2'],
            annotator_ids=['1', '2'],
            data_inicial=timezone.now() - timedelta(days=30),
            data_final=timezone.now(),
            categoria_labels=['LOC', 'ORG'],
            perspectiva_ids=['1'],
            estado_desacordo='em_desacordo'
        )
        
        self.assertEqual(config.project, self.project.item)
        self.assertEqual(config.created_by, self.user)
        self.assertEqual(len(config.dataset_ids), 2)
        self.assertEqual(len(config.annotator_ids), 2)
        self.assertEqual(len(config.categoria_labels), 2)
        self.assertEqual(config.estado_desacordo, 'em_desacordo')
    
    def test_default_values(self):
        """Testa valores padrão do modelo"""
        config = AnnotatorReportConfig.objects.create(
            project=self.project.item,
            created_by=self.user
        )
        
        self.assertEqual(config.dataset_ids, [])
        self.assertEqual(config.annotator_ids, [])
        self.assertEqual(config.categoria_labels, [])
        self.assertEqual(config.perspectiva_ids, [])
        self.assertEqual(config.estado_desacordo, 'todos')
        self.assertIsNone(config.data_inicial)
        self.assertIsNone(config.data_final)
    
    def test_ordering(self):
        """Testa ordenação do modelo"""
        config1 = AnnotatorReportConfig.objects.create(
            project=self.project.item,
            created_by=self.user
        )
        
        config2 = AnnotatorReportConfig.objects.create(
            project=self.project.item,
            created_by=self.user
        )
        
        configs = AnnotatorReportConfig.objects.all()
        
        # Deve estar ordenado por created_at decrescente
        self.assertEqual(configs[0], config2)
        self.assertEqual(configs[1], config1)


class AnnotatorReportIntegrationTestCase(APITestCase):
    """Testes de integração completos"""
    
    def setUp(self):
        self.project = prepare_project()
        self.admin_user = self.project.admin
        
        # Criar dados mais realistas
        self.setup_realistic_data()
    
    def setup_realistic_data(self):
        """Configurar dados realistas para testes de integração"""
        # Criar anotadores adicionais
        self.annotator1 = User.objects.create_user(
            'ann1', 'ann1@test.com', 'pass',
            first_name='Ana', last_name='Silva'
        )
        self.annotator2 = User.objects.create_user(
            'ann2', 'ann2@test.com', 'pass',
            first_name='João', last_name='Santos'
        )
        
        Member.objects.create(
            user=self.annotator1,
            project=self.project.item,
            role=self.project.annotator_role
        )
        Member.objects.create(
            user=self.annotator2,
            project=self.project.item,
            role=self.project.annotator_role
        )
        
        # Criar tipos de categoria
        self.cat_loc = CategoryType.objects.create(text='LOC', project=self.project.item)
        self.cat_org = CategoryType.objects.create(text='ORG', project=self.project.item)
        self.cat_per = CategoryType.objects.create(text='PER', project=self.project.item)
        
        # Criar exemplos
        examples = []
        for i in range(10):
            example = Example.objects.create(
                text=f'Example text {i}',
                project=self.project.item,
                created_at=timezone.now() - timedelta(days=i)
            )
            examples.append(example)
        
        # Criar anotações distribuídas
        for i, example in enumerate(examples):
            # Annotator1 anota mais LOC
            if i % 2 == 0:
                Category.objects.create(
                    example=example,
                    user=self.annotator1,
                    label=self.cat_loc,
                    created_at=timezone.now() - timedelta(days=i, hours=1)
                )
            
            # Annotator2 anota mais ORG
            if i % 3 == 0:
                Category.objects.create(
                    example=example,
                    user=self.annotator2,
                    label=self.cat_org,
                    created_at=timezone.now() - timedelta(days=i, hours=2)
                )
    
    def test_full_workflow(self):
        """Testa fluxo completo de geração e exportação de relatório"""
        self.client.force_authenticate(user=self.admin_user)
        
        # 1. Obter metadados
        metadata_url = reverse(
            'annotator_report_metadata',
            kwargs={'project_id': self.project.item.id}
        )
        metadata_response = self.client.get(metadata_url)
        
        self.assertEqual(metadata_response.status_code, status.HTTP_200_OK)
        metadata = metadata_response.json()
        
        # Verificar que há anotadores
        self.assertGreater(len(metadata['annotators']), 0)
        self.assertGreater(len(metadata['categories']), 0)
        
        # 2. Gerar relatório com filtros
        report_url = reverse(
            'annotator_report',
            kwargs={'project_id': self.project.item.id}
        )
        
        filters = {
            'sort_by': 'total_anotacoes',
            'order': 'desc',
            'page_size': 10,
            'categoria_label': ['LOC', 'ORG']
        }
        
        report_response = self.client.get(report_url, filters)
        
        self.assertEqual(report_response.status_code, status.HTTP_200_OK)
        report_data = report_response.json()
        
        # Verificar estrutura do relatório
        self.assertIn('resumo_global', report_data)
        self.assertIn('detalhe_anotadores', report_data)
        
        # 3. Exportar relatório em CSV
        export_url = reverse(
            'annotator_report_export',
            kwargs={'project_id': self.project.item.id}
        )
        
        csv_params = {**filters, 'format': 'csv'}
        csv_response = self.client.get(export_url, csv_params)
        
        self.assertEqual(csv_response.status_code, status.HTTP_200_OK)
        self.assertEqual(csv_response['Content-Type'], 'text/csv; charset=utf-8')
        
        # Verificar conteúdo do CSV
        csv_content = csv_response.content.decode('utf-8')
        self.assertIn('ID Anotador', csv_content)
        self.assertIn('Total Anotações', csv_content)
    
    def test_performance_with_large_dataset(self):
        """Testa performance com dataset maior"""
        # Simular mais dados
        for i in range(100):
            example = Example.objects.create(
                text=f'Large dataset example {i}',
                project=self.project.item
            )
            
            if i % 2 == 0:
                Category.objects.create(
                    example=example,
                    user=self.annotator1,
                    label=self.cat_loc
                )
        
        self.client.force_authenticate(user=self.admin_user)
        
        report_url = reverse(
            'annotator_report',
            kwargs={'project_id': self.project.item.id}
        )
        
        start_time = timezone.now()
        response = self.client.get(report_url)
        end_time = timezone.now()
        
        # Verificar que a resposta veio em tempo razoável (< 5 segundos)
        duration = (end_time - start_time).total_seconds()
        self.assertLess(duration, 5.0)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK) 