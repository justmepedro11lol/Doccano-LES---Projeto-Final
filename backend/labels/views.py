from functools import partial
from typing import Type

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import DiscrepancyMessage, AnnotationDiscrepancy, DiscrepancyType, DiscrepancyComment
from .serializers import DiscrepancyMessageSerializer, AnnotationDiscrepancySerializer, DiscrepancyTypeSerializer, DiscrepancyCommentSerializer
from projects.permissions import IsProjectMember
from projects.models import Project
from examples.models import Example

from .permissions import CanEditLabel
from .serializers import (
    BoundingBoxSerializer,
    CategorySerializer,
    RelationSerializer,
    SegmentationSerializer,
    SpanSerializer,
    TextLabelSerializer,
)
from labels.models import (
    BoundingBox,
    Category,
    Label,
    Relation,
    Segmentation,
    Span,
    TextLabel,
)

from django.utils import timezone
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg

from .services import DiscrepancyDetectionService, DiscrepancyResolutionService


class BaseListAPI(generics.ListCreateAPIView):
    label_class: Type[Label]
    pagination_class = None
    permission_classes = [IsAuthenticated & IsProjectMember]
    swagger_schema = None

    @property
    def project(self):
        return get_object_or_404(Project, pk=self.kwargs["project_id"])

    def get_queryset(self):
        queryset = self.label_class.objects.filter(example=self.kwargs["example_id"])
        if not self.project.collaborative_annotation:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data["example"] = self.kwargs["example_id"]
        try:
            response = super().create(request, args, kwargs)
        except ValidationError as err:
            response = Response({"detail": err.messages}, status=status.HTTP_400_BAD_REQUEST)
        return response

    def perform_create(self, serializer):
        serializer.save(example_id=self.kwargs["example_id"], user=self.request.user)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DiscrepancyMessageListAPI(generics.ListCreateAPIView):
    serializer_class = DiscrepancyMessageSerializer
    permission_classes = [permissions.IsAuthenticated & IsProjectMember]
    pagination_class = None

    @property
    def project(self):
        return get_object_or_404(Project, pk=self.kwargs["project_id"])

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        print(f"Recuperando mensagens do chat - Project ID: {project_id}")
        print(f"Request path: {self.request.path}")
        print(f"Request user: {self.request.user}")
        print(f"Request kwargs: {self.kwargs}")
        
        # Verifica se o projeto existe
        project = get_object_or_404(Project, pk=project_id)
        
        queryset = DiscrepancyMessage.objects.filter(project_id=project_id)
        print(f"Query SQL: {queryset.query}")
        print(f"Encontradas {queryset.count()} mensagens")
        for msg in queryset:
            print(f"Message {msg.id}: {msg.text} by {msg.user} at {msg.created_at}")
        return queryset

    def perform_create(self, serializer):
        project_id = self.kwargs["project_id"]
        print(f"Criando nova mensagem no chat - Project ID: {project_id}, User: {self.request.user}")
        
        # Verifica se o projeto existe antes de criar a mensagem
        project = get_object_or_404(Project, pk=project_id)
        
        serializer.save(
            project_id=project_id,
            user=self.request.user
        )
        print("Mensagem criada com sucesso")

class BaseDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = "annotation_id"
    swagger_schema = None

    @property
    def project(self):
        return get_object_or_404(Project, pk=self.kwargs["project_id"])

    def get_permissions(self):
        if self.project.collaborative_annotation:
            self.permission_classes = [IsAuthenticated & IsProjectMember]
        else:
            self.permission_classes = [IsAuthenticated & IsProjectMember & partial(CanEditLabel, self.queryset)]
        return super().get_permissions()


class CategoryListAPI(BaseListAPI):
    label_class = Category
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        if self.project.single_class_classification:
            self.get_queryset().delete()
        return super().create(request, args, kwargs)


class CategoryDetailAPI(BaseDetailAPI):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SpanListAPI(BaseListAPI):
    label_class = Span
    serializer_class = SpanSerializer


class SpanDetailAPI(BaseDetailAPI):
    queryset = Span.objects.all()
    serializer_class = SpanSerializer


class TextLabelListAPI(BaseListAPI):
    label_class = TextLabel
    serializer_class = TextLabelSerializer


class TextLabelDetailAPI(BaseDetailAPI):
    queryset = TextLabel.objects.all()
    serializer_class = TextLabelSerializer


class RelationList(BaseListAPI):
    label_class = Relation
    serializer_class = RelationSerializer


class RelationDetail(BaseDetailAPI):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer


class BoundingBoxListAPI(BaseListAPI):
    label_class = BoundingBox
    serializer_class = BoundingBoxSerializer


class BoundingBoxDetailAPI(BaseDetailAPI):
    queryset = BoundingBox.objects.all()
    serializer_class = BoundingBoxSerializer


class SegmentationListAPI(BaseListAPI):
    label_class = Segmentation
    serializer_class = SegmentationSerializer


class SegmentationDetailAPI(BaseDetailAPI):
    queryset = Segmentation.objects.all()
    serializer_class = SegmentationSerializer


class DiscrepancyViewSet(ModelViewSet):
    """ViewSet para gerenciar discrepâncias de anotação"""
    
    queryset = AnnotationDiscrepancy.objects.all()
    serializer_class = AnnotationDiscrepancySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'discrepancy_type', 'priority', 'example']
    search_fields = ['description', 'users_involved__username']
    ordering_fields = ['priority', 'flagged_at', 'agreement_score']
    ordering = ['priority', '-flagged_at']
    
    def get_queryset(self):
        """Filtra discrepâncias por projeto"""
        project_id = self.kwargs.get('project_id')
        if project_id:
            return self.queryset.filter(project_id=project_id)
        return self.queryset.none()
    
    @action(detail=False, methods=['post'])
    def detect_discrepancies(self, request, project_id=None):
        """Detecta automaticamente discrepâncias em um projeto"""
        try:
            project = Project.objects.get(id=project_id)
            
            detection_service = DiscrepancyDetectionService(project)
            discrepancies = detection_service.detect_all_discrepancies()
            
            return Response({
                'message': f'{len(discrepancies)} discrepâncias detectadas',
                'discrepancies': self.get_serializer(discrepancies, many=True).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None, project_id=None):
        """Marca uma discrepância como resolvida"""
        discrepancy = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        discrepancy.status = 'resolved'
        discrepancy.resolved_by = request.user
        discrepancy.resolved_at = timezone.now()
        discrepancy.resolution_notes = resolution_notes
        discrepancy.save()
        
        return Response({'message': 'Discrepância resolvida com sucesso'})
    
    @action(detail=True, methods=['get'])
    def suggest_resolution(self, request, pk=None, project_id=None):
        """Obtém sugestões para resolver uma discrepância"""
        discrepancy = self.get_object()
        resolution_service = DiscrepancyResolutionService()
        suggestion = resolution_service.suggest_resolution(discrepancy)
        
        return Response(suggestion)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None, project_id=None):
        """Adiciona comentário a uma discrepância"""
        discrepancy = self.get_object()
        comment_text = request.data.get('comment', '')
        
        if not comment_text:
            return Response(
                {'error': 'Comentário não pode estar vazio'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comment = DiscrepancyComment.objects.create(
            discrepancy=discrepancy,
            user=request.user,
            comment=comment_text
        )
        
        serializer = DiscrepancyCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request, project_id=None):
        """Retorna estatísticas das discrepâncias do projeto"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'by_status': dict(queryset.values_list('status').annotate(count=Count('id'))),
            'by_type': dict(queryset.values_list('discrepancy_type__name').annotate(count=Count('id'))),
            'by_priority': dict(queryset.values_list('priority').annotate(count=Count('id'))),
            'avg_agreement_score': queryset.aggregate(avg=Avg('agreement_score'))['avg'],
            'pending_high_priority': queryset.filter(status='pending', priority__lte=2).count()
        }
        
        return Response(stats)
