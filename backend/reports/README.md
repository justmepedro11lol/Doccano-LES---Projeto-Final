# Sistema de Relatórios de Anotadores - Doccano

Este módulo implementa um sistema completo de relatórios para anotadores no Doccano, conforme especificado nos requisitos do projeto.

## Funcionalidades

### 1. Filtros Disponíveis

O sistema oferece os seguintes filtros para customizar os relatórios:

- **dataset_id**: Um ou mais datasets a considerar
- **annotator_id**: Um ou mais utilizadores específicos  
- **data_inicial, data_final**: Intervalo de datas das anotações (ISO-8601)
- **categoria_label**: Etiquetas ou categorias específicas
- **perspectiva_id**: Perspetivas declaradas pelos anotadores
- **estado_desacordo**: Filtrar por concordância (todos, em desacordo, resolvido)

### 2. Métricas Calculadas

Para cada anotador, o sistema calcula:

#### Identificação
- **annotator_id**: ID único do utilizador
- **nome_anotador**: Nome a apresentar

#### Produtividade  
- **total_anotacoes**: Número total de anotações no período
- **datasets_distintos**: Quantos datasets diferentes anotou
- **tempo_total_min**: Tempo total (minutos) dedicado
- **tempo_medio_por_anotacao_seg**: Média de segundos por anotação

#### Qualidade / Concordância
- **taxa_desacordo_%**: Percentagem de anotações que geraram desacordo
- **desacordos_resolvidos**: Número de desacordos já resolvidos
- **score_concordancia_medio**: Cohen's κ ou F1 médio

#### Perspetiva
- **perspectivas_usadas**: Lista de perspetivas registadas

#### Conteúdo
- **categorias_mais_frequentes**: Top-3 categorias mais usadas

#### Temporal
- **primeira_anotacao**: Data/hora da 1.ª anotação no intervalo
- **ultima_anotacao**: Data/hora da última anotação no intervalo

## APIs Disponíveis

### 1. Gerar Relatório
```
GET /v1/projects/{project_id}/reports/annotators
```

**Parâmetros de Query:**
- Todos os filtros mencionados acima
- `sort_by`: Campo para ordenação
- `order`: asc|desc  
- `page`: Número da página
- `page_size`: Itens por página

**Resposta:**
```json
{
  "filtros_aplicados": { ... },
  "resumo_global": {
    "total_anotadores": 12,
    "total_anotacoes": 8450,
    "taxa_desacordo_global_%": 17.2
  },
  "detalhe_anotadores": [
    {
      "annotator_id": "u17",
      "nome_anotador": "Ana Silva",
      "total_anotacoes": 1240,
      "datasets_distintos": 3,
      "tempo_total_min": 590,
      "tempo_medio_por_anotacao_seg": 28.5,
      "taxa_desacordo_%": 14.8,
      "desacordos_resolvidos": 102,
      "score_concordancia_medio": 0.82,
      "perspectivas_usadas": ["jurídica", "linguística"],
      "categorias_mais_frequentes": ["LOC", "ORG", "PER"],
      "primeira_anotacao": "2025-03-01T09:14:11Z",
      "ultima_anotacao": "2025-04-15T17:06:32Z"
    }
  ]
}
```

### 2. Exportar Relatório
```
GET /v1/projects/{project_id}/reports/annotators/export?format=csv|pdf
```

Aceita os mesmos filtros da API principal. Retorna ficheiro para download.

### 3. Metadados para Filtros
```
GET /v1/projects/{project_id}/reports/annotators/metadata
```

Retorna listas de valores disponíveis para construir filtros dinamicamente:

```json
{
  "annotators": [
    {"id": "1", "name": "Ana Silva", "username": "ana.silva"}
  ],
  "categories": ["LOC", "ORG", "PER"],
  "perspectives": [
    {"id": "1", "name": "Jurídica"}
  ],
  "datasets": [
    {"id": "dataset_1", "name": "Dataset Principal"}
  ],
  "sort_options": [
    {"value": "total_anotacoes", "label": "Total de Anotações"}
  ],
  "disagreement_states": [
    {"value": "todos", "label": "Todos"}
  ]
}
```

## Autorização

Apenas utilizadores com permissões de **project admin** e **manager** podem aceder aos relatórios.

## Frontend

A interface web oferece:

1. **Formulário de Filtros**: Interface intuitiva para todos os filtros
2. **Resumo Global**: Cards com métricas agregadas
3. **Tabela Detalhada**: Lista de anotadores com todas as métricas
4. **Gráficos**: Visualizações opcionais (barras, donuts)
5. **Exportação**: Botões para CSV e PDF

### Localização
```
/projects/{id}/annotator-report
```

## Instalação e Configuração

### Backend

1. Adicionar `'reports'` ao `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... outras apps
    'reports',
]
```

2. Incluir URLs:
```python
# config/urls.py
urlpatterns = [
    # ... outras URLs
    path("v1/", include("reports.urls")),
]
```

3. Executar migrações:
```bash
python manage.py makemigrations reports
python manage.py migrate
```

### Dependências Opcionais

Para exportação PDF:
```bash
pip install reportlab
```

Para métricas avançadas de concordância:
```bash
pip install scikit-learn pandas
```

## Estrutura do Código

```
backend/reports/
├── __init__.py
├── apps.py          # Configuração da app
├── models.py        # Modelo AnnotatorReportConfig
├── serializers.py   # Serializers para APIs
├── services.py      # Lógica de negócio principal
├── views.py         # Views da API
├── urls.py          # Configuração de rotas
└── tests.py         # Testes abrangentes
```

```
frontend/pages/projects/_id/
└── annotator-report.vue  # Interface completa
```

## Testes

Execute os testes com:
```bash
python manage.py test reports
```

Os testes cobrem:
- Cada filtro individual
- Combinações múltiplas de filtros
- Exportações CSV e PDF
- Permissões de acesso
- Performance com datasets grandes
- Integração completa frontend-backend

## Exemplos de Uso

### Filtrar por Anotador e Período
```bash
GET /v1/projects/1/reports/annotators?annotator_id=5&data_inicial=2025-01-01T00:00:00Z&data_final=2025-12-31T23:59:59Z
```

### Exportar CSV com Filtros
```bash
GET /v1/projects/1/reports/annotators/export?format=csv&categoria_label=LOC,ORG&estado_desacordo=em_desacordo
```

### Ordenar por Taxa de Desacordo
```bash
GET /v1/projects/1/reports/annotators?sort_by=taxa_desacordo_percent&order=desc&page_size=20
```

## Personalização

### Adicionar Nova Métrica

1. Modificar `AnnotatorReportService._calculate_annotator_metrics()`
2. Atualizar `AnnotatorDetailSerializer`
3. Adicionar coluna na tabela frontend
4. Adicionar testes

### Novo Formato de Exportação

1. Implementar método no `AnnotatorReportService`
2. Adicionar handling na `AnnotatorReportExportAPIView`
3. Atualizar frontend para novo botão

## Limitações Conhecidas

1. **Métricas de Tempo**: Atualmente simuladas. Requer tracking real de sessões.
2. **Score de Concordância**: Implementação básica. Para Cohen's Kappa real, comparar anotações entre utilizadores.
3. **Datasets**: Lógica simplificada. Adaptar conforme organização real dos datasets.

## Contribuição

Ao modificar este módulo:

1. Manter compatibilidade com a API especificada
2. Adicionar testes para novas funcionalidades
3. Atualizar documentação
4. Seguir padrões de código do projeto Doccano

## Suporte

Para questões específicas sobre implementação, consultar:
- Código fonte em `backend/reports/`
- Testes em `backend/reports/tests.py` 
- Interface em `frontend/pages/projects/_id/annotator-report.vue` 