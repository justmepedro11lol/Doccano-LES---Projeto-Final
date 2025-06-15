from collections import defaultdict
from typing import Dict, List, Tuple
from django.db.models import Count, Q
from django.contrib.auth.models import User
from sklearn.metrics import cohen_kappa_score
import numpy as np

from .models import (
    AnnotationDiscrepancy, 
    DiscrepancyType, 
    Category, 
    Span, 
    TextLabel, 
    Relation
)
from examples.models import Example
from projects.models import Project


class DiscrepancyDetectionService:
    """Serviço para detectar automaticamente discrepâncias entre anotações"""
    
    def __init__(self, project: Project):
        self.project = project
    
    def detect_all_discrepancies(self, examples: List[Example] = None) -> List[AnnotationDiscrepancy]:
        """Detecta todas as discrepâncias em um projeto ou lista de exemplos"""
        if examples is None:
            examples = self.project.examples.all()
        
        all_discrepancies = []
        
        for example in examples:
            # Detecta diferentes tipos de discrepâncias
            all_discrepancies.extend(self.detect_missing_annotations(example))
            all_discrepancies.extend(self.detect_conflicting_labels(example))
            all_discrepancies.extend(self.detect_overlapping_spans(example))
            all_discrepancies.extend(self.detect_low_agreement(example))
            
        return all_discrepancies
    
    def detect_missing_annotations(self, example: Example) -> List[AnnotationDiscrepancy]:
        """Detecta quando alguns usuários não anotaram um exemplo"""
        discrepancies = []
        
        # Pega todos os usuários do projeto
        project_users = self.project.members.all()
        
        # Pega usuários que anotaram este exemplo
        annotating_users = set()
        for model in [Category, Span, TextLabel]:
            users = model.objects.filter(example=example).values_list('user', flat=True).distinct()
            annotating_users.update(users)
        
        # Usuários que não anotaram
        missing_users = set(project_users.values_list('id', flat=True)) - annotating_users
        
        if len(missing_users) > 0:
            discrepancy_type = DiscrepancyType.objects.get(name=DiscrepancyType.MISSING_ANNOTATION)
            
            discrepancy = AnnotationDiscrepancy.objects.create(
                project=self.project,
                example=example,
                discrepancy_type=discrepancy_type,
                description=f"{len(missing_users)} usuário(s) não anotaram este exemplo",
                flagged_by=None  # Sistema automático
            )
            
            # Adiciona usuários envolvidos
            discrepancy.users_involved.set(User.objects.filter(id__in=missing_users))
            discrepancy.priority = discrepancy.calculate_priority()
            discrepancy.save()
            
            discrepancies.append(discrepancy)
        
        return discrepancies
    
    def detect_conflicting_labels(self, example: Example) -> List[AnnotationDiscrepancy]:
        """Detecta rótulos conflitantes para o mesmo span/categoria"""
        discrepancies = []
        
        # Para spans
        spans_by_position = defaultdict(list)
        for span in Span.objects.filter(example=example):
            key = (span.start_offset, span.end_offset)
            spans_by_position[key].append(span)
        
        for position, spans in spans_by_position.items():
            if len(spans) > 1:
                labels = [span.label for span in spans]
                if len(set(labels)) > 1:  # Rótulos diferentes
                    discrepancy_type = DiscrepancyType.objects.get(name=DiscrepancyType.CONFLICTING_LABELS)
                    
                    discrepancy = AnnotationDiscrepancy.objects.create(
                        project=self.project,
                        example=example,
                        discrepancy_type=discrepancy_type,
                        description=f"Rótulos conflitantes na posição {position[0]}-{position[1]}",
                        conflicting_annotations={
                            'spans': [{'id': s.id, 'label': s.label.text, 'user': s.user.username} for s in spans]
                        }
                    )
                    
                    discrepancy.users_involved.set([span.user for span in spans])
                    discrepancy.priority = discrepancy.calculate_priority()
                    discrepancy.save()
                    
                    discrepancies.append(discrepancy)
        
        return discrepancies
    
    def detect_overlapping_spans(self, example: Example) -> List[AnnotationDiscrepancy]:
        """Detecta spans sobrepostos do mesmo usuário quando não é permitido"""
        discrepancies = []
        
        if getattr(example.project, 'allow_overlapping', True):
            return discrepancies  # Sobreposição é permitida
        
        spans_by_user = defaultdict(list)
        for span in Span.objects.filter(example=example):
            spans_by_user[span.user].append(span)
        
        for user, spans in spans_by_user.items():
            for i, span1 in enumerate(spans):
                for span2 in spans[i+1:]:
                    if span1.is_overlapping(span2):
                        discrepancy_type = DiscrepancyType.objects.get(name=DiscrepancyType.OVERLAPPING_SPANS)
                        
                        discrepancy = AnnotationDiscrepancy.objects.create(
                            project=self.project,
                            example=example,
                            discrepancy_type=discrepancy_type,
                            description=f"Spans sobrepostos do usuário {user.username}",
                            conflicting_annotations={
                                'overlapping_spans': [
                                    {'id': span1.id, 'range': f"{span1.start_offset}-{span1.end_offset}"},
                                    {'id': span2.id, 'range': f"{span2.start_offset}-{span2.end_offset}"}
                                ]
                            }
                        )
                        
                        discrepancy.users_involved.add(user)
                        discrepancy.priority = discrepancy.calculate_priority()
                        discrepancy.save()
                        
                        discrepancies.append(discrepancy)
        
        return discrepancies
    
    def detect_low_agreement(self, example: Example) -> List[AnnotationDiscrepancy]:
        """Detecta baixa concordância entre anotadores usando Cohen's Kappa"""
        discrepancies = []
        
        # Calcula concordância para categorias
        categories = Category.objects.filter(example=example)
        if categories.count() >= 2:
            agreement_score = self.calculate_category_agreement(categories)
            
            if agreement_score < 0.4:  # Threshold baixo
                discrepancy_type = DiscrepancyType.objects.get(name=DiscrepancyType.LOW_AGREEMENT)
                
                discrepancy = AnnotationDiscrepancy.objects.create(
                    project=self.project,
                    example=example,
                    discrepancy_type=discrepancy_type,
                    description=f"Baixa concordância entre anotadores (κ = {agreement_score:.3f})",
                    agreement_score=agreement_score
                )
                
                users = categories.values_list('user', flat=True).distinct()
                discrepancy.users_involved.set(User.objects.filter(id__in=users))
                discrepancy.priority = discrepancy.calculate_priority()
                discrepancy.save()
                
                discrepancies.append(discrepancy)
        
        return discrepancies
    
    def calculate_category_agreement(self, categories) -> float:
        """Calcula Cohen's Kappa para concordância entre categorias"""
        users = list(categories.values_list('user', flat=True).distinct())
        
        if len(users) < 2:
            return 1.0  # Concordância perfeita se há apenas um usuário
        
        # Cria matriz de anotações (usuário x categoria)
        user_annotations = defaultdict(list)
        all_labels = set()
        
        for category in categories:
            user_annotations[category.user].append(category.label.text)
            all_labels.add(category.label.text)
        
        # Converte para formato numérico para o cálculo
        label_to_num = {label: i for i, label in enumerate(sorted(all_labels))}
        
        # Compara pares de usuários e calcula kappa médio
        kappa_scores = []
        for i, user1 in enumerate(users):
            for user2 in users[i+1:]:
                annotations1 = [label_to_num[label] for label in user_annotations[user1]]
                annotations2 = [label_to_num[label] for label in user_annotations[user2]]
                
                if len(annotations1) == len(annotations2):
                    try:
                        kappa = cohen_kappa_score(annotations1, annotations2)
                        kappa_scores.append(kappa)
                    except:
                        pass
        
        return np.mean(kappa_scores) if kappa_scores else 0.0


class DiscrepancyResolutionService:
    """Serviço para resolver discrepâncias"""
    
    def __init__(self):
        pass
    
    def suggest_resolution(self, discrepancy: AnnotationDiscrepancy) -> Dict:
        """Sugere uma resolução para a discrepância"""
        suggestions = {
            DiscrepancyType.MISSING_ANNOTATION: self._suggest_missing_annotation,
            DiscrepancyType.CONFLICTING_LABELS: self._suggest_conflicting_labels,
            DiscrepancyType.OVERLAPPING_SPANS: self._suggest_overlapping_spans,
            DiscrepancyType.LOW_AGREEMENT: self._suggest_low_agreement,
        }
        
        suggestion_func = suggestions.get(discrepancy.discrepancy_type.name)
        if suggestion_func:
            return suggestion_func(discrepancy)
        
        return {"suggestion": "Revisar manualmente"}
    
    def _suggest_missing_annotation(self, discrepancy: AnnotationDiscrepancy) -> Dict:
        return {
            "suggestion": "Notificar usuários para completar anotação",
            "actions": [
                "Enviar notificação para usuários pendentes",
                "Definir prazo para completar anotação",
                "Redistribuir para outros anotadores se necessário"
            ]
        }
    
    def _suggest_conflicting_labels(self, discrepancy: AnnotationDiscrepancy) -> Dict:
        return {
            "suggestion": "Revisar com expert ou por consenso",
            "actions": [
                "Criar sessão de discussão entre anotadores",
                "Escalar para supervisor/expert",
                "Aplicar regra de maioria se aplicável"
            ]
        }
    
    def _suggest_overlapping_spans(self, discrepancy: AnnotationDiscrepancy) -> Dict:
        return {
            "suggestion": "Corrigir sobreposições",
            "actions": [
                "Revisar e ajustar boundaries dos spans",
                "Verificar se sobreposição é intencional",
                "Aplicar regras de precedência"
            ]
        }
    
    def _suggest_low_agreement(self, discrepancy: AnnotationDiscrepancy) -> Dict:
        return {
            "suggestion": "Melhorar guidelines de anotação",
            "actions": [
                "Revisar guidelines de anotação",
                "Providenciar treinamento adicional",
                "Discutir casos ambíguos em equipe"
            ]
        } 