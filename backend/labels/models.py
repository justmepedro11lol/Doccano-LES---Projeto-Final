import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from examples.models import Example
from projects.models import Project

from .managers import (
    BoundingBoxManager,
    CategoryManager,
    LabelManager,
    RelationManager,
    SegmentationManager,
    SpanManager,
    TextLabelManager,
)
from examples.models import Example
from label_types.models import CategoryType, RelationType, SpanType


class Label(models.Model):
    objects = LabelManager()

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    prob = models.FloatField(default=0.0)
    manual = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(Label):
    objects = CategoryManager()
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="categories")
    label = models.ForeignKey(to=CategoryType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("example", "user", "label")


class DiscrepancyMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="discrepancy_messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.user.username}: {self.text[:20]}"


class DiscrepancyType(models.Model):
    MISSING_ANNOTATION = 'missing'
    CONFLICTING_LABELS = 'conflicting'
    OVERLAPPING_SPANS = 'overlapping'
    INCONSISTENT_RELATIONS = 'relations'
    LOW_AGREEMENT = 'low_agreement'
    
    TYPE_CHOICES = [
        (MISSING_ANNOTATION, 'Anotação Ausente'),
        (CONFLICTING_LABELS, 'Rótulos Conflitantes'),
        (OVERLAPPING_SPANS, 'Spans Sobrepostos'),
        (INCONSISTENT_RELATIONS, 'Relações Inconsistentes'),
        (LOW_AGREEMENT, 'Baixa Concordância'),
    ]
    
    name = models.CharField(max_length=50, choices=TYPE_CHOICES, unique=True)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica')
    ], default='medium')
    
    def __str__(self):
        return self.get_name_display()


class AnnotationDiscrepancy(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('reviewing', 'Em Revisão'),
        ('resolved', 'Resolvida'),
        ('ignored', 'Ignorada'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="discrepancies")
    example = models.ForeignKey(Example, on_delete=models.CASCADE, related_name="discrepancies")
    discrepancy_type = models.ForeignKey(DiscrepancyType, on_delete=models.CASCADE)
    
    # Usuários envolvidos na discrepância
    users_involved = models.ManyToManyField(User, related_name="discrepancies_involved")
    
    # Detalhes da discrepância
    description = models.TextField()
    agreement_score = models.FloatField(null=True, blank=True, help_text="Score de concordância entre 0 e 1")
    
    # IDs das anotações conflitantes (JSON para flexibilidade)
    conflicting_annotations = models.JSONField(default=dict, help_text="IDs e tipos das anotações em conflito")
    
    # Status e resolução
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    flagged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="flagged_discrepancies")
    flagged_at = models.DateTimeField(auto_now_add=True)
    
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_discrepancies")
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Prioridade automática baseada na severidade e score
    priority = models.IntegerField(default=5, help_text="1=Muito Alta, 5=Muito Baixa")
    
    class Meta:
        ordering = ['priority', '-flagged_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['example', 'discrepancy_type']),
            models.Index(fields=['priority', 'flagged_at']),
        ]
    
    def __str__(self):
        return f"Discrepância {self.discrepancy_type} - Exemplo {self.example.id}"
    
    def calculate_priority(self):
        """Calcula prioridade baseada na severidade e score de concordância"""
        severity_weights = {'low': 4, 'medium': 3, 'high': 2, 'critical': 1}
        base_priority = severity_weights.get(self.discrepancy_type.severity, 3)
        
        if self.agreement_score is not None and self.agreement_score < 0.3:
            base_priority = max(1, base_priority - 1)  # Aumenta prioridade para baixa concordância
            
        return base_priority


class DiscrepancyComment(models.Model):
    discrepancy = models.ForeignKey(AnnotationDiscrepancy, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']


class Span(Label):
    objects = SpanManager()
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="spans")
    label = models.ForeignKey(to=SpanType, on_delete=models.CASCADE)
    start_offset = models.IntegerField()
    end_offset = models.IntegerField()

    def __str__(self):
        text = self.example.text[self.start_offset : self.end_offset]
        return f"({text}, {self.start_offset}, {self.end_offset}, {self.label.text})"

    def validate_unique(self, exclude=None):
        allow_overlapping = getattr(self.example.project, "allow_overlapping", False)
        is_collaborative = self.example.project.collaborative_annotation
        if allow_overlapping:
            super().validate_unique(exclude=exclude)
            return

        overlapping_span = (
            Span.objects.exclude(id=self.id)
            .filter(example=self.example)
            .filter(
                models.Q(start_offset__gte=self.start_offset, start_offset__lt=self.end_offset)
                | models.Q(end_offset__gt=self.start_offset, end_offset__lte=self.end_offset)
                | models.Q(start_offset__lte=self.start_offset, end_offset__gte=self.end_offset)
            )
        )
        if is_collaborative:
            if overlapping_span.exists():
                raise ValidationError("This overlapping is not allowed in this project.")
        else:
            if overlapping_span.filter(user=self.user).exists():
                raise ValidationError("This overlapping is not allowed in this project.")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def is_overlapping(self, other: "Span"):
        return (
            (other.start_offset <= self.start_offset < other.end_offset)
            or (other.start_offset < self.end_offset <= other.end_offset)
            or (self.start_offset < other.start_offset and other.end_offset < self.end_offset)
        )

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(start_offset__gte=0), name="startOffset >= 0"),
            models.CheckConstraint(check=models.Q(end_offset__gte=0), name="endOffset >= 0"),
            models.CheckConstraint(check=models.Q(start_offset__lt=models.F("end_offset")), name="start < end"),
        ]


class TextLabel(Label):
    objects = TextLabelManager()
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="texts")
    text = models.TextField()

    def is_same_text(self, other: "TextLabel"):
        return self.text == other.text

    class Meta:
        unique_together = ("example", "user", "text")


class Relation(Label):
    objects = RelationManager()
    from_id = models.ForeignKey(Span, on_delete=models.CASCADE, related_name="from_relations")
    to_id = models.ForeignKey(Span, on_delete=models.CASCADE, related_name="to_relations")
    type = models.ForeignKey(RelationType, on_delete=models.CASCADE)
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="relations")

    def __str__(self):
        text = self.example.text
        from_span = text[self.from_id.start_offset : self.from_id.end_offset]
        to_span = text[self.to_id.start_offset : self.to_id.end_offset]
        type_text = self.type.text
        return f"{from_span} - ({type_text}) -> {to_span}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def clean(self):
        same_example = self.from_id.example == self.to_id.example == self.example
        if not same_example:
            raise ValidationError("You need to label the same example.")
        return super().clean()


class BoundingBox(Label):
    objects = BoundingBoxManager()
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    label = models.ForeignKey(to=CategoryType, on_delete=models.CASCADE)
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="bboxes")

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(x__gte=0), name="x >= 0"),
            models.CheckConstraint(check=models.Q(y__gte=0), name="y >= 0"),
            models.CheckConstraint(check=models.Q(width__gte=0), name="width >= 0"),
            models.CheckConstraint(check=models.Q(height__gte=0), name="height >= 0"),
        ]


class Segmentation(Label):
    objects = SegmentationManager()
    points = models.JSONField(default=list)
    label = models.ForeignKey(to=CategoryType, on_delete=models.CASCADE)
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="segmentations")
