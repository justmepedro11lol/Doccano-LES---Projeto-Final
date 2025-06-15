from rest_framework import serializers

from .models import BoundingBox, Category, Relation, Segmentation, Span, TextLabel
from examples.models import Example
from label_types.models import CategoryType, RelationType, SpanType
from .models import DiscrepancyMessage
from .models import (
    AnnotationDiscrepancy,
    DiscrepancyType,
    DiscrepancyComment,
)


class CategorySerializer(serializers.ModelSerializer):
    label = serializers.PrimaryKeyRelatedField(queryset=CategoryType.objects.all())
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())

    class Meta:
        model = Category
        fields = (
            "id",
            "prob",
            "user",
            "example",
            "created_at",
            "updated_at",
            "label",
        )
        read_only_fields = ("user",)


class SpanSerializer(serializers.ModelSerializer):
    label = serializers.PrimaryKeyRelatedField(queryset=SpanType.objects.all())
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())

    class Meta:
        model = Span
        fields = (
            "id",
            "prob",
            "user",
            "example",
            "created_at",
            "updated_at",
            "label",
            "start_offset",
            "end_offset",
        )
        read_only_fields = ("user",)

class DiscrepancyMessageSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DiscrepancyMessage
        fields = ["id", "user", "text", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class TextLabelSerializer(serializers.ModelSerializer):
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())

    class Meta:
        model = TextLabel
        fields = (
            "id",
            "prob",
            "user",
            "example",
            "created_at",
            "updated_at",
            "text",
        )
        read_only_fields = ("user",)


class RelationSerializer(serializers.ModelSerializer):
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=RelationType.objects.all())

    class Meta:
        model = Relation
        fields = ("id", "prob", "user", "example", "created_at", "updated_at", "from_id", "to_id", "type")
        read_only_fields = ("user",)


class BoundingBoxSerializer(serializers.ModelSerializer):
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())
    label = serializers.PrimaryKeyRelatedField(queryset=CategoryType.objects.all())

    class Meta:
        model = BoundingBox
        fields = (
            "id",
            "uuid",
            "prob",
            "user",
            "example",
            "created_at",
            "updated_at",
            "label",
            "x",
            "y",
            "width",
            "height",
        )
        read_only_fields = ("user",)


class SegmentationSerializer(serializers.ModelSerializer):
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())
    label = serializers.PrimaryKeyRelatedField(queryset=CategoryType.objects.all())

    class Meta:
        model = Segmentation
        fields = (
            "id",
            "uuid",
            "prob",
            "user",
            "example",
            "created_at",
            "updated_at",
            "label",
            "points",
        )
        read_only_fields = ("user",)


class DiscrepancyTypeSerializer(serializers.ModelSerializer):
    """Serializer para tipos de discrepância"""
    
    class Meta:
        model = DiscrepancyType
        fields = ['id', 'name', 'description', 'severity']


class DiscrepancyCommentSerializer(serializers.ModelSerializer):
    """Serializer para comentários de discrepância"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = DiscrepancyComment
        fields = ['id', 'user', 'user_name', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']


class AnnotationDiscrepancySerializer(serializers.ModelSerializer):
    """Serializer para discrepâncias de anotação"""
    
    discrepancy_type = DiscrepancyTypeSerializer(read_only=True)
    discrepancy_type_id = serializers.IntegerField(write_only=True, required=False)
    
    users_involved_names = serializers.SerializerMethodField()
    flagged_by_name = serializers.CharField(source='flagged_by.username', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)
    
    comments = DiscrepancyCommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    example_text = serializers.CharField(source='example.text', read_only=True)
    example_id = serializers.IntegerField(source='example.id', read_only=True)
    
    class Meta:
        model = AnnotationDiscrepancy
        fields = [
            'id', 'project', 'example', 'example_id', 'example_text',
            'discrepancy_type', 'discrepancy_type_id',
            'users_involved', 'users_involved_names', 
            'description', 'agreement_score', 'conflicting_annotations',
            'status', 'flagged_by', 'flagged_by_name', 'flagged_at',
            'resolved_by', 'resolved_by_name', 'resolved_at', 'resolution_notes',
            'priority', 'comments', 'comments_count'
        ]
        read_only_fields = [
            'flagged_by', 'flagged_at', 'resolved_by', 'resolved_at', 'priority'
        ]
    
    def get_users_involved_names(self, obj):
        """Retorna os nomes dos usuários envolvidos"""
        return [user.username for user in obj.users_involved.all()]
    
    def get_comments_count(self, obj):
        """Retorna a quantidade de comentários"""
        return obj.comments.count()
    
    def create(self, validated_data):
        """Cria uma nova discrepância"""
        # Remove users_involved do validated_data se presente
        users_involved = validated_data.pop('users_involved', [])
        
        # Define flagged_by como o usuário atual
        validated_data['flagged_by'] = self.context['request'].user
        
        # Calcula prioridade automaticamente
        discrepancy = AnnotationDiscrepancy(**validated_data)
        discrepancy.priority = discrepancy.calculate_priority()
        discrepancy.save()
        
        # Adiciona usuários envolvidos
        if users_involved:
            discrepancy.users_involved.set(users_involved)
        
        return discrepancy
