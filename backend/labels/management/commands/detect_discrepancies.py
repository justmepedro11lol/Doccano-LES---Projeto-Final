import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from projects.models import Project
from labels.services import DiscrepancyDetectionService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Detecta automaticamente discrepâncias em projetos de anotação'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='ID do projeto específico para analisar'
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            help='Analisa todos os projetos'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Número de exemplos a processar por vez (padrão: 100)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar as discrepâncias encontradas'
        )

    def handle(self, *args, **options):
        project_id = options.get('project_id')
        all_projects = options.get('all_projects')
        batch_size = options.get('batch_size')
        dry_run = options.get('dry_run')

        if not project_id and not all_projects:
            raise CommandError('Especifique --project-id ou --all-projects')

        if project_id and all_projects:
            raise CommandError('Use apenas --project-id OU --all-projects, não ambos')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('EXECUTANDO EM MODO DRY-RUN - Nenhuma discrepância será salva')
            )

        # Determina quais projetos processar
        if project_id:
            try:
                projects = [Project.objects.get(id=project_id)]
            except Project.DoesNotExist:
                raise CommandError(f'Projeto com ID {project_id} não encontrado')
        else:
            projects = Project.objects.all()

        total_discrepancies = 0

        for project in projects:
            self.stdout.write(f'\nProcessando projeto: {project.name} (ID: {project.id})')
            
            try:
                discrepancies_found = self.process_project(project, batch_size, dry_run)
                total_discrepancies += discrepancies_found
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Projeto {project.name}: {discrepancies_found} discrepâncias encontradas'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Erro no projeto {project.name}: {str(e)}')
                )
                logger.exception(f'Erro ao processar projeto {project.id}')

        # Resumo final
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 RESUMO: {total_discrepancies} discrepâncias encontradas em {len(projects)} projeto(s)'
            )
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('Nenhuma discrepância foi salva (modo dry-run)')
            )

    def process_project(self, project, batch_size, dry_run):
        """Processa um projeto específico para encontrar discrepâncias"""
        detection_service = DiscrepancyDetectionService(project)
        examples = project.examples.all()
        
        total_discrepancies = 0
        total_examples = examples.count()
        
        self.stdout.write(f'  Analisando {total_examples} exemplos...')
        
        # Processa em lotes
        for i in range(0, total_examples, batch_size):
            batch_examples = examples[i:i + batch_size]
            
            self.stdout.write(
                f'  Processando exemplos {i+1}-{min(i+batch_size, total_examples)} de {total_examples}...'
            )
            
            if not dry_run:
                with transaction.atomic():
                    batch_discrepancies = detection_service.detect_all_discrepancies(
                        list(batch_examples)
                    )
                    total_discrepancies += len(batch_discrepancies)
            else:
                # Em modo dry-run, ainda executa a detecção mas não salva
                batch_discrepancies = []
                for example in batch_examples:
                    # Simula a detecção sem salvar
                    mock_discrepancies = self.simulate_detection(detection_service, example)
                    batch_discrepancies.extend(mock_discrepancies)
                    
                total_discrepancies += len(batch_discrepancies)
                
                # Mostra alguns exemplos encontrados
                if batch_discrepancies:
                    self.stdout.write('    Discrepâncias encontradas (não salvas):')
                    for disc in batch_discrepancies[:3]:  # Mostra apenas as primeiras 3
                        self.stdout.write(f'      - {disc["type"]}: {disc["description"]}')
        
        return total_discrepancies

    def simulate_detection(self, detection_service, example):
        """Simula a detecção de discrepâncias sem salvar no banco"""
        mock_discrepancies = []
        
        try:
            # Detecção de anotações ausentes
            project_users = detection_service.project.members.all()
            annotating_users = set()
            
            from labels.models import Category, Span, TextLabel
            for model in [Category, Span, TextLabel]:
                users = model.objects.filter(example=example).values_list('user', flat=True).distinct()
                annotating_users.update(users)
            
            missing_users = set(project_users.values_list('id', flat=True)) - annotating_users
            
            if len(missing_users) > 0:
                mock_discrepancies.append({
                    'type': 'Anotação Ausente',
                    'description': f'{len(missing_users)} usuário(s) não anotaram este exemplo',
                    'example_id': example.id
                })
            
            # Detecção de rótulos conflitantes (simplificada)
            from collections import defaultdict
            spans_by_position = defaultdict(list)
            for span in Span.objects.filter(example=example):
                key = (span.start_offset, span.end_offset)
                spans_by_position[key].append(span)
            
            for position, spans in spans_by_position.items():
                if len(spans) > 1:
                    labels = [span.label for span in spans]
                    if len(set(labels)) > 1:
                        mock_discrepancies.append({
                            'type': 'Rótulos Conflitantes',
                            'description': f'Rótulos conflitantes na posição {position[0]}-{position[1]}',
                            'example_id': example.id
                        })
            
        except Exception as e:
            logger.warning(f'Erro na simulação para exemplo {example.id}: {str(e)}')
        
        return mock_discrepancies 