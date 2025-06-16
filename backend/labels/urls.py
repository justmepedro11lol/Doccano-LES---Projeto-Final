# backend/labels/urls.py

from django.urls import path
from .views import (
    DiscrepancyMessageListAPI,
    ExampleDiscrepancyMessageListAPI,
    RelationList, RelationDetail,
    CategoryListAPI, CategoryDetailAPI,
    SpanListAPI, SpanDetailAPI,
    TextLabelListAPI, TextLabelDetailAPI,
    BoundingBoxListAPI, BoundingBoxDetailAPI,
    SegmentationListAPI, SegmentationDetailAPI,
    DiscrepancyViewSet,
)

urlpatterns = [
    path(
        "examples/<int:example_id>/relations",
        RelationList.as_view(),
        name="relation_list",
    ),
    path(
        "examples/<int:example_id>/relations/<int:annotation_id>",
        RelationDetail.as_view(),
        name="relation_detail",
    ),

    # Rota para chat de discrepância do projeto
    path(
        "discrepancies/messages",
        DiscrepancyMessageListAPI.as_view(),
        name="discrepancy_messages",
    ),

    # Rota para chat de discrepância específica de um exemplo
    path(
        "examples/<int:example_id>/discrepancies/messages",
        ExampleDiscrepancyMessageListAPI.as_view(),
        name="example_discrepancy_messages",
    ),

    path(
        "examples/<int:example_id>/categories",
        CategoryListAPI.as_view(),
        name="category_list",
    ),
    path(
        "examples/<int:example_id>/categories/<int:annotation_id>",
        CategoryDetailAPI.as_view(),
        name="category_detail",
    ),

    path(
        "examples/<int:example_id>/spans",
        SpanListAPI.as_view(),
        name="span_list",
    ),
    path(
        "examples/<int:example_id>/spans/<int:annotation_id>",
        SpanDetailAPI.as_view(),
        name="span_detail",
    ),

    path(
        "examples/<int:example_id>/texts",
        TextLabelListAPI.as_view(),
        name="text_list",
    ),
    path(
        "examples/<int:example_id>/texts/<int:annotation_id>",
        TextLabelDetailAPI.as_view(),
        name="text_detail",
    ),

    path(
        "examples/<int:example_id>/bboxes",
        BoundingBoxListAPI.as_view(),
        name="bbox_list",
    ),
    path(
        "examples/<int:example_id>/bboxes/<int:annotation_id>",
        BoundingBoxDetailAPI.as_view(),
        name="bbox_detail",
    ),

    path(
        "examples/<int:example_id>/segments",
        SegmentationListAPI.as_view(),
        name="segmentation_list",
    ),
    path(
        "examples/<int:example_id>/segments/<int:annotation_id>",
        SegmentationDetailAPI.as_view(),
        name="segmentation_detail",
    ),

    path(
        "projects/<int:project_id>/discrepancies/",
        DiscrepancyViewSet.as_view({"get": "list", "post": "create"}),
        name="discrepancy_list",
    ),
    path(
        "projects/<int:project_id>/discrepancies/<int:pk>/",
        DiscrepancyViewSet.as_view({
            "get": "retrieve", 
            "put": "update", 
            "patch": "partial_update", 
            "delete": "destroy"
        }),
        name="discrepancy_detail",
    ),
    path(
        "projects/<int:project_id>/discrepancies/detect/",
        DiscrepancyViewSet.as_view({"post": "detect_discrepancies"}),
        name="detect_discrepancies",
    ),
    path(
        "projects/<int:project_id>/discrepancies/statistics/",
        DiscrepancyViewSet.as_view({"get": "statistics"}),
        name="discrepancy_statistics",
    ),
    path(
        "projects/<int:project_id>/discrepancies/<int:pk>/resolve/",
        DiscrepancyViewSet.as_view({"post": "resolve"}),
        name="resolve_discrepancy",
    ),
    path(
        "projects/<int:project_id>/discrepancies/<int:pk>/suggest-resolution/",
        DiscrepancyViewSet.as_view({"get": "suggest_resolution"}),
        name="suggest_resolution",
    ),
    path(
        "projects/<int:project_id>/discrepancies/<int:pk>/comments/",
        DiscrepancyViewSet.as_view({"post": "add_comment"}),
        name="add_discrepancy_comment",
    ),
]
