<template>
  <v-container fluid>
    <!-- Título Principal -->
    <div class="text-center mb-8">
      <h1 class="display-1 font-weight-light primary--text mb-4">
        Comparação Lado a Lado
      </h1>
      <v-divider class="mx-auto mb-4" style="max-width: 200px;"></v-divider>
      <p class="text-h6 grey--text text--darken-1">
        Análise de Discrepâncias
      </p>
    </div>

    <!-- Barra de Filtros Completa -->
    <v-card class="mb-6">
      <v-card-title>
        <v-icon class="mr-2">mdi-filter</v-icon>
        Filtros de Comparação
        <v-spacer />
        <v-chip v-if="hasActiveFilters" color="primary" outlined small>
          {{ activeFiltersCount }} filtros ativos
        </v-chip>
      </v-card-title>
      <v-card-text>
        <!-- Primeira linha de filtros -->
        <v-row class="mb-2">
          <!-- Seletor de Dataset -->
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedDataset"
              :items="availableDatasets"
              item-text="name"
              item-value="id"
              label="Selecionar Dataset"
              outlined
              dense
              clearable
              prepend-inner-icon="mdi-database"
              :loading="loadingDatasets"
            />
          </v-col>

          <!-- Seletor de Anotadores -->
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedAnnotators"
              :items="availableAnnotators"
              item-text="username"
              item-value="user"
              label="Escolher Anotadores (min. 2)"
              multiple
              chips
              deletable-chips
              outlined
              dense
              :rules="[v => v.length >= 2 || 'Selecione pelo menos 2 anotadores']"
              prepend-inner-icon="mdi-account-multiple"
            />
          </v-col>

          <!-- Estado do Desacordo -->
          <v-col cols="12" md="4">
            <v-select
              v-model="disagreementStatus"
              :items="disagreementStatusOptions"
              item-text="text"
              item-value="value"
              label="Estado do Desacordo"
              outlined
              dense
              prepend-inner-icon="mdi-alert-circle"
            />
          </v-col>
        </v-row>

        <!-- Segunda linha de filtros -->
        <v-row class="mb-2">
          <!-- Intervalo de Registos - Tipo -->
          <v-col cols="12" md="3">
            <v-select
              v-model="recordRangeType"
              :items="recordRangeTypes"
              item-text="text"
              item-value="value"
              label="Tipo de Intervalo"
              outlined
              dense
              prepend-inner-icon="mdi-format-list-numbered"
            />
          </v-col>

          <!-- Intervalo de Registos - De -->
          <v-col cols="12" md="3">
            <v-text-field
              v-model="recordRangeFrom"
              :label="recordRangeFromLabel"
              outlined
              dense
              :disabled="!recordRangeType"
              :type="recordRangeType === 'id' ? 'number' : 'text'"
            />
          </v-col>

          <!-- Intervalo de Registos - Até -->
          <v-col cols="12" md="3">
            <v-text-field
              v-model="recordRangeTo"
              :label="recordRangeToLabel"
              outlined
              dense
              :disabled="!recordRangeType"
              :type="recordRangeType === 'id' ? 'number' : 'text'"
            />
          </v-col>

          <!-- Categorias/Etiquetas -->
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedCategories"
              :items="availableCategories"
              item-text="text"
              item-value="id"
              label="Categorias/Etiquetas"
              multiple
              chips
              deletable-chips
              outlined
              dense
              clearable
              prepend-inner-icon="mdi-tag-multiple"
              :loading="loadingCategories"
            />
          </v-col>
        </v-row>

        <!-- Botões de Ação -->
        <v-row>
          <v-col cols="12">
            <v-btn
              color="primary"
              class="mr-2"
              :disabled="selectedAnnotators.length < 2"
              :loading="loadingAnnotations"
              @click="loadComparison"
            >
              <v-icon left>mdi-compare</v-icon>
              Comparar Anotações
            </v-btn>
            
            <v-btn
              color="secondary"
              outlined
              :disabled="!hasActiveFilters"
              @click="clearAllFilters"
            >
              <v-icon left>mdi-filter-remove</v-icon>
              Limpar Filtros
            </v-btn>

            <v-btn
              color="success"
              outlined
              class="ml-2"
              :disabled="!showComparison || allExamplesData.length === 0"
              @click="exportComparison"
            >
              <v-icon left>mdi-download</v-icon>
              Exportar
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Resumo dos Exemplos -->
    <v-card v-if="showComparison && allExamplesData.length > 0" class="mb-4">
      <v-card-title>
        <v-icon class="mr-2">mdi-file-multiple</v-icon>
        Comparação de Todos os Exemplos
        <v-spacer />
        <v-chip color="primary" outlined>
          {{ filteredExamplesCount }} exemplos encontrados
        </v-chip>
        <v-chip v-if="hasDiscrepancies" color="error" outlined class="ml-2">
          {{ discrepanciesCount }} em desacordo
        </v-chip>
        <v-chip v-if="hasResolved" color="success" outlined class="ml-2">
          {{ resolvedCount }} resolvidos
        </v-chip>
      </v-card-title>
    </v-card>

    <!-- Lista de Todos os Exemplos -->
    <div v-if="showComparison && allExamplesData.length > 0">
      <div 
        v-for="(exampleData, exampleIndex) in allExamplesData" 
        :key="exampleData.example.id"
        class="mb-6"
      >
        <!-- Informações do Exemplo -->
        <v-card class="mb-4">
          <v-card-title class="pb-2">
            <v-chip color="primary" class="mr-3">
              Exemplo #{{ exampleData.example.id }}
          </v-chip>
            <span class="text-subtitle-1">{{ exampleIndex + 1 }} / {{ allExamplesData.length }}</span>
          </v-card-title>
          <v-card-text>
            <div class="text-body-1 pa-3" style="background-color: #f5f5f5; border-radius: 4px; border-left: 4px solid #1976d2;">
              {{ exampleData.example.text }}
        </div>
      </v-card-text>
    </v-card>

        <!-- Comparação Lado a Lado para este Exemplo -->
      <v-row>
        <v-col
            v-for="(annotatorData, annotatorIndex) in exampleData.annotators"
            :key="annotatorData.annotatorId"
          :cols="12"
            :md="Math.floor(12 / exampleData.annotators.length)"
          >
            <v-card :color="`${getAnnotatorColor(annotatorIndex)} lighten-5`" class="h-100">
              <v-card-title :class="`${getAnnotatorColor(annotatorIndex)} white--text`" class="py-3">
                <v-avatar :color="getAnnotatorColor(annotatorIndex)" class="mr-2" size="32">
                  <span class="white--text font-weight-bold">
                    {{ annotatorData.username[0].toUpperCase() }}
                  </span>
              </v-avatar>
                {{ annotatorData.username }}
              <v-spacer></v-spacer>
                <v-chip small color="white" :text-color="getAnnotatorColor(annotatorIndex)">
                  {{ annotatorData.annotations.length }} anotações
              </v-chip>
            </v-card-title>
            <v-divider />
              <v-card-text class="pa-4">
                <!-- Anotações do Anotador -->
                <div v-if="annotatorData.annotations.length > 0">
                  <div 
                    v-for="annotation in annotatorData.annotations" 
                    :key="annotation.id"
                    class="annotation-item mb-2 pa-2"
                    :style="`border-left: 4px solid var(--v-${getAnnotatorColor(annotatorIndex)}-base);`"
                  >
                    <div class="d-flex align-center mb-1">
                      <v-icon small class="mr-1">{{ getAnnotationIcon(annotation) }}</v-icon>
                      <strong>{{ getLabelText(annotation.label) }}</strong>
                      <v-spacer />
                      <v-chip x-small :color="getAnnotatorColor(annotatorIndex)" outlined>
                        {{ getAnnotationType(annotation) }}
                      </v-chip>
                    </div>
                    
                    <!-- Texto da Anotação (para spans) -->
                    <div v-if="annotation.start_offset !== undefined" class="text-caption mb-1">
                      "{{ getAnnotationText(annotation, exampleData.example) }}"
                    </div>
                    
                    <!-- Posição (para spans) -->
                    <div v-if="annotation.start_offset !== undefined" class="text-caption grey--text">
                      Posição: {{ annotation.start_offset }} - {{ annotation.end_offset }}
                    </div>
                  </div>
                </div>
                
                <!-- Caso não tenha anotações -->
                <div v-else class="text-center text-grey pa-4">
                  <v-icon size="40" color="grey lighten-1">mdi-file-outline</v-icon>
                  <p class="mt-2">Nenhuma anotação encontrada</p>
                </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
        
        <!-- Divider entre exemplos -->
        <v-divider v-if="exampleIndex < allExamplesData.length - 1" class="my-6"></v-divider>
      </div>
    </div>
    
    <!-- Estado Vazio -->
    <v-card v-else-if="showComparison && allExamplesData.length === 0" class="pa-8 text-center">
      <v-icon size="80" color="grey lighten-1">mdi-file-search-outline</v-icon>
      <h3 class="mt-4 mb-2">Nenhum Exemplo Encontrado</h3>
      <p class="text-body-1">Não foram encontrados exemplos no projeto ou os anotadores selecionados não fizeram anotações.</p>
    </v-card>
    
    <!-- Placeholder inicial -->
    <v-card v-else class="pa-8 text-center">
      <v-icon size="80" color="grey lighten-1">mdi-compare</v-icon>
      <h3 class="mt-4 mb-2">Pronto para Comparar</h3>
      <p class="text-body-1">Selecione 2 ou mais anotadores e um exemplo para iniciar a comparação.</p>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'

export default Vue.extend({
  name: 'DiscrepancySideBySide',
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      // Anotadores disponíveis
      availableAnnotators: [],
      selectedAnnotators: [],
      
      // Estados de loading
      loadingAnnotators: false,
      loadingAnnotations: false,
      
      // Dados de comparação
      allExamplesData: [],
      showComparison: false,
      
      // Labels e tipos
      labelTypes: {
        categories: [],
        spans: [],
        relations: []
      },
      
      // Cores para os anotadores
      annotatorColors: [
        'blue', 'green', 'purple', 'orange', 'red', 'teal', 'pink', 'indigo'
      ],

             // Lista de exemplos
       availableExamples: [],

               // Filtros
        selectedDataset: null,
        availableDatasets: [],
        disagreementStatus: 'all',
        disagreementStatusOptions: [
          { text: 'Todos', value: 'all' },
          { text: 'Apenas em Desacordo', value: 'disagreement' },
          { text: 'Já Resolvidos', value: 'resolved' }
        ],
               recordRangeType: null,
        recordRangeTypes: [
          { text: 'ID do Exemplo', value: 'id' },
          { text: 'Posição no Texto', value: 'position' },
          { text: 'Data de Criação', value: 'date' }
        ],
               recordRangeFrom: null,
        recordRangeTo: null,
       selectedCategories: [],
       availableCategories: [],
       loadingDatasets: false,
       loadingCategories: false,
       discrepanciesCount: 0,
       resolvedCount: 0
    }
  },

    computed: {
    ...mapGetters('projects', ['project']),

    projectId(): string {
      return this.$route.params.id
    },

    // Computadas para filtros
    hasActiveFilters(): boolean {
      return !!(
        this.selectedDataset ||
        this.selectedAnnotators.length > 0 ||
        (this.disagreementStatus !== 'all' && this.disagreementStatus !== null) ||
        this.recordRangeType ||
        this.selectedCategories.length > 0
      )
    },

    activeFiltersCount(): number {
      let count = 0
      if (this.selectedDataset) count++
      if (this.selectedAnnotators.length > 0) count++
      if (this.disagreementStatus && this.disagreementStatus !== 'all') count++
      if (this.recordRangeType) count++
      if (this.selectedCategories.length > 0) count++
      return count
    },

    filteredExamplesCount(): number {
      return this.allExamplesData.length
    },

    hasDiscrepancies(): boolean {
      return this.discrepanciesCount > 0
    },

    hasResolved(): boolean {
      return this.resolvedCount > 0
    },

    recordRangeFromLabel(): string {
      if (this.recordRangeType === 'id') return 'ID de'
      if (this.recordRangeType === 'position') return 'Posição de'
      return 'De'
    },

    recordRangeToLabel(): string {
      if (this.recordRangeType === 'id') return 'ID até'
      if (this.recordRangeType === 'position') return 'Posição até'
      return 'Até'
    }
  },

  async mounted() {
    await this.loadAnnotators()
    await this.loadLabelTypes()
    this.loadDatasets()
    await this.loadCategories()
    this.initializeFilters()
  },

  methods: {
    async loadAnnotators() {
      this.loadingAnnotators = true
      try {
        const members = await this.$repositories.member.list(this.projectId)
        this.availableAnnotators = members
        console.log('Anotadores carregados:', members)
      } catch (error) {
        console.error('Erro ao carregar anotadores:', error)
        this.$nuxt.$emit('show-snackbar', {
          text: 'Erro ao carregar lista de anotadores',
          color: 'error'
        })
      } finally {
        this.loadingAnnotators = false
      }
    },

    async loadLabelTypes() {
      try {
        const [categories, spans, relations] = await Promise.all([
          this.$repositories.categoryType.list(this.projectId).catch(() => []),
          this.$repositories.spanType.list(this.projectId).catch(() => []),
          this.$repositories.relationType.list(this.projectId).catch(() => [])
        ])

        this.labelTypes = {
          categories,
          spans,
          relations
        }
        console.log('Tipos de label carregados:', this.labelTypes)
      } catch (error) {
        console.error('Erro ao carregar tipos de label:', error)
      }
    },

    loadDatasets() {
      this.loadingDatasets = true
      try {
        // Implementar carregamento de datasets se existir no sistema
        // Por enquanto, criar um dataset padrão
        this.availableDatasets = [
          { id: 'default', name: 'Dataset Principal' },
          { id: 'training', name: 'Conjunto de Treino' },
          { id: 'test', name: 'Conjunto de Teste' }
        ]
        console.log('Datasets carregados:', this.availableDatasets)
      } catch (error) {
        console.error('Erro ao carregar datasets:', error)
      } finally {
        this.loadingDatasets = false
      }
    },

    async loadCategories() {
      this.loadingCategories = true
      try {
        // Carregar todas as categorias/etiquetas disponíveis
        const [categories, spans, relations] = await Promise.all([
          this.$repositories.categoryType.list(this.projectId).catch(() => []),
          this.$repositories.spanType.list(this.projectId).catch(() => []),
          this.$repositories.relationType.list(this.projectId).catch(() => [])
        ])

        this.availableCategories = [
          ...categories.map(cat => ({ ...cat, type: 'category' })),
          ...spans.map(span => ({ ...span, type: 'span' })),
          ...relations.map(rel => ({ ...rel, type: 'relation' }))
        ]
        console.log('Categorias carregadas:', this.availableCategories)
      } catch (error) {
        console.error('Erro ao carregar categorias:', error)
      } finally {
        this.loadingCategories = false
      }
    },

    initializeFilters() {
      // Inicializar filtros com valores padrão
      this.disagreementStatus = 'all'
      console.log('Filtros inicializados')
    },

    async loadComparison() {
      if (this.selectedAnnotators.length < 2) {
        return
      }

      this.loadingAnnotations = true
      this.allExamplesData = []
      
      try {
        // Carregar todos os exemplos disponíveis
        console.log('Carregando todos os exemplos do projeto...')
        const examplesResponse = await this.$repositories.example.list(this.projectId, { limit: 100 })
        let examples = examplesResponse.items || examplesResponse
        
        console.log(`${examples.length} exemplos encontrados`)
        
        if (examples.length === 0) {
          this.$nuxt.$emit('show-snackbar', {
            text: 'Nenhum exemplo encontrado no projeto',
            color: 'warning'
          })
          return
        }

        // Aplicar filtros de intervalo
        examples = this.applyRangeFilters(examples)
        console.log(`${examples.length} exemplos após filtro de intervalo`)

        // Carregar anotações para todos os exemplos
        const allExamplesPromises = examples.map(async (example) => {
          return await this.loadExampleAnnotations(example)
        })

        let allExamplesData = await Promise.all(allExamplesPromises)
        
        // Filtrar apenas exemplos que têm pelo menos uma anotação de algum dos anotadores selecionados
        allExamplesData = allExamplesData.filter(exampleData => 
          exampleData.annotators.some(annotator => annotator.annotations.length > 0)
        )

        // Processar cada exemplo com filtros e detecção de discrepâncias
        const processedExamples = []
        let discrepanciesCount = 0
        let resolvedCount = 0

        for (const exampleData of allExamplesData) {
          // Aplicar filtro de categorias se selecionado
          if (this.selectedCategories.length > 0) {
            const hasSelectedCategories = this.checkSelectedCategories(exampleData)
            if (!hasSelectedCategories) {
              continue
            }
          }

          // Detectar discrepâncias
          const discrepancyInfo = this.detectDiscrepancies(exampleData)
          exampleData.hasDiscrepancy = discrepancyInfo.hasDiscrepancy
          exampleData.isResolved = discrepancyInfo.isResolved
          
          if (discrepancyInfo.hasDiscrepancy) discrepanciesCount++
          if (discrepancyInfo.isResolved) resolvedCount++

          // Aplicar filtro de estado de desacordo
          if (this.shouldIncludeExample(exampleData)) {
            processedExamples.push(exampleData)
          }
        }

        this.allExamplesData = processedExamples
        this.discrepanciesCount = discrepanciesCount
        this.resolvedCount = resolvedCount

        this.showComparison = true
        console.log(`Comparação carregada para ${this.allExamplesData.length} exemplos com anotações`)
        console.log(`Discrepâncias: ${discrepanciesCount}, Resolvidos: ${resolvedCount}`)
        
      } catch (error) {
        console.error('Erro ao carregar comparação:', error)
        this.$nuxt.$emit('show-snackbar', {
          text: 'Erro ao carregar comparação: ' + error.message,
          color: 'error'
        })
      } finally {
        this.loadingAnnotations = false
      }
    },

    getAnnotatorColor(index: number): string {
      return this.annotatorColors[index % this.annotatorColors.length]
    },

    getLabelText(labelId: number): string {
      // Procurar em todos os tipos de label
      const allLabels = [
        ...this.labelTypes.categories,
        ...this.labelTypes.spans,
        ...this.labelTypes.relations
      ]
      
      const label = allLabels.find(l => l.id === labelId)
      return label ? (label.text || label.name) : `Label ${labelId}`
    },

    getAnnotationType(annotation: any): string {
      if (annotation.type) {
        return annotation.type
      }
      
      // Inferir tipo baseado na estrutura
      if (annotation.start_offset !== undefined) {
        return 'span'
      } else if (annotation.from_id !== undefined || annotation.type !== undefined) {
        return 'relation'
      } else {
        return 'category'
      }
    },

    getAnnotationIcon(annotation: any): string {
      const type = this.getAnnotationType(annotation)
      switch (type) {
        case 'span':
          return 'mdi-format-color-highlight'
        case 'category':
          return 'mdi-tag'
        case 'relation':
          return 'mdi-arrow-right'
        default:
          return 'mdi-label'
      }
    },

    getAnnotationText(annotation: any, example: any): string {
      if (annotation.start_offset !== undefined && annotation.end_offset !== undefined && example) {
        return example.text.substring(annotation.start_offset, annotation.end_offset)
      }
      return ''
    },

    async loadExampleAnnotations(example) {
      try {
        console.log('Carregando anotações para exemplo:', example.id)

        // Carregar TODAS as anotações do exemplo usando query direta (como na página discuss)
        const allAnnotations = []

        // Buscar anotações categóricas
        try {
          const categoryResponse = await this.$repositories.category.request.get(
            `/projects/${this.projectId}/examples/${example.id}/categories?show_all=true`
          )
          console.log(`Exemplo ${example.id} - Anotações categóricas encontradas:`, categoryResponse.data.length)
          
          for (const annotation of categoryResponse.data) {
            allAnnotations.push({
              ...annotation,
              type: 'category',
              userId: annotation.user
            })
          }
        } catch (error) {
          console.log(`Exemplo ${example.id} - Erro ao carregar anotações categóricas:`, error)
        }

        // Buscar anotações de span
        try {
          const spanResponse = await this.$repositories.span.request.get(
            `/projects/${this.projectId}/examples/${example.id}/spans?show_all=true`
          )
          console.log(`Exemplo ${example.id} - Anotações de span encontradas:`, spanResponse.data.length)
          
          for (const annotation of spanResponse.data) {
            allAnnotations.push({
              ...annotation,
              type: 'span',
              userId: annotation.user
            })
          }
        } catch (error) {
          console.log(`Exemplo ${example.id} - Erro ao carregar anotações de span:`, error)
        }

        // Buscar anotações de relação
        try {
          const relationResponse = await this.$repositories.relation.request.get(
            `/projects/${this.projectId}/examples/${example.id}/relations?show_all=true`
          )
          console.log(`Exemplo ${example.id} - Anotações de relação encontradas:`, relationResponse.data.length)
          
          for (const annotation of relationResponse.data) {
            allAnnotations.push({
              ...annotation,
              type: 'relation',
              userId: annotation.user
            })
          }
        } catch (error) {
          console.log(`Exemplo ${example.id} - Erro ao carregar anotações de relação:`, error)
        }

        console.log(`Exemplo ${example.id} - Total de anotações encontradas:`, allAnnotations.length)

        // Criar dados de comparação para cada anotador selecionado
        const annotators = this.selectedAnnotators.map(annotatorId => {
          const annotator = this.availableAnnotators.find(a => a.user === annotatorId)
          
          // Filtrar anotações deste anotador específico
          const annotatorAnnotations = allAnnotations.filter(ann => {
            // Verificar diferentes formas que o userId pode estar representado
            const match = ann.userId === annotatorId || 
                         ann.user === annotatorId || 
                         parseInt(ann.user) === annotatorId ||
                         parseInt(ann.userId) === annotatorId
            
            return match
          })

          console.log(`Exemplo ${example.id} - Usuário ${annotatorId} (${annotator?.username}):`, annotatorAnnotations.length, 'anotações')

          return {
            annotatorId,
            username: annotator?.username || `Usuário ${annotatorId}`,
            annotations: annotatorAnnotations
          }
        })

        return {
          example,
          annotators
        }

      } catch (error) {
        console.error(`Erro ao carregar anotações do exemplo ${example.id}:`, error)
        return {
          example,
          annotators: this.selectedAnnotators.map(annotatorId => {
            const annotator = this.availableAnnotators.find(a => a.user === annotatorId)
            return {
              annotatorId,
              username: annotator?.username || `Usuário ${annotatorId}`,
              annotations: []
            }
          })
        }
      }
    },

    // Métodos de filtro
    applyRangeFilters(examples) {
      if (!this.recordRangeType || (!this.recordRangeFrom && !this.recordRangeTo)) {
        return examples
      }

      let filtered = examples

      if (this.recordRangeType === 'id') {
        if (this.recordRangeFrom) {
          filtered = filtered.filter(ex => ex.id >= parseInt(this.recordRangeFrom))
        }
        if (this.recordRangeTo) {
          filtered = filtered.filter(ex => ex.id <= parseInt(this.recordRangeTo))
        }
      } else if (this.recordRangeType === 'position') {
        // Implementar filtro por posição no texto se necessário
        // Por exemplo, baseado no comprimento do texto
        if (this.recordRangeFrom) {
          filtered = filtered.filter(ex => ex.text && ex.text.length >= parseInt(this.recordRangeFrom))
        }
        if (this.recordRangeTo) {
          filtered = filtered.filter(ex => ex.text && ex.text.length <= parseInt(this.recordRangeTo))
        }
      } else if (this.recordRangeType === 'date') {
        // Implementar filtro por data se o modelo tiver campo de data
        console.log('Filtro por data não implementado ainda')
      }

      return filtered
    },

    checkSelectedCategories(exampleData) {
      if (this.selectedCategories.length === 0) {
        return true
      }

      // Verificar se alguma anotação contém as categorias selecionadas
      for (const annotator of exampleData.annotators) {
        for (const annotation of annotator.annotations) {
          if (this.selectedCategories.includes(annotation.label)) {
            return true
          }
        }
      }
      return false
    },

    detectDiscrepancies(exampleData) {
      // Implementar detecção de discrepâncias baseada na lógica da página /discrepancies
      const annotators = exampleData.annotators
      let hasDiscrepancy = false
      let isResolved = false

      if (annotators.length < 2) {
        return { hasDiscrepancy: false, isResolved: false }
      }

      // Agrupar anotações por tipo e posição para detectar discrepâncias
      const annotationGroups = {}

      for (const annotator of annotators) {
        for (const annotation of annotator.annotations) {
          const key = this.getAnnotationKey(annotation)
          if (!annotationGroups[key]) {
            annotationGroups[key] = []
          }
          annotationGroups[key].push({
            annotatorId: annotator.annotatorId,
            annotation
          })
        }
      }

      // Verificar discrepâncias
      for (const [, group] of Object.entries(annotationGroups)) {
        const uniqueLabels = new Set(group.map(item => item.annotation.label))
        const uniqueAnnotators = new Set(group.map(item => item.annotatorId))

        // Se há mais de um label para a mesma posição/contexto, há discrepância
        if (uniqueLabels.size > 1) {
          hasDiscrepancy = true
        }

        // Se nem todos os anotadores anotaram esta posição, pode ser discrepância
        if (uniqueAnnotators.size < annotators.length) {
          // Só considerar como discrepância se pelo menos 2 anotadores discordam
          if (uniqueAnnotators.size >= 2) {
            hasDiscrepancy = true
          }
        }
      }

      // Por enquanto, considerar como resolvido se não há discrepâncias
      // Na implementação real, isso viria de um campo de status
      isResolved = !hasDiscrepancy

      return { hasDiscrepancy, isResolved }
    },

    getAnnotationKey(annotation) {
      // Criar chave única para agrupar anotações similares
      if (annotation.start_offset !== undefined && annotation.end_offset !== undefined) {
        // Para spans, usar posição no texto
        return `span_${annotation.start_offset}_${annotation.end_offset}`
      } else if (annotation.from_id !== undefined && annotation.to_id !== undefined) {
        // Para relações, usar IDs dos elementos relacionados
        return `relation_${annotation.from_id}_${annotation.to_id}`
      } else {
        // Para categorias, usar o exemplo todo
        return `category_document`
      }
    },

    shouldIncludeExample(exampleData) {
      if (!this.disagreementStatus || this.disagreementStatus === 'all') {
        return true
      }

      if (this.disagreementStatus === 'disagreement') {
        return exampleData.hasDiscrepancy
      }

      if (this.disagreementStatus === 'resolved') {
        return exampleData.isResolved
      }

      return true
    },

    clearAllFilters() {
      this.selectedDataset = null
      this.selectedAnnotators = []
      this.disagreementStatus = 'all'
      this.recordRangeType = null
      this.recordRangeFrom = null
      this.recordRangeTo = null
      this.selectedCategories = []
      this.showComparison = false
      this.allExamplesData = []
      this.discrepanciesCount = 0
      this.resolvedCount = 0
    },

    exportComparison() {
      // Implementar exportação dos dados de comparação
      const exportData = {
        project: this.project.name,
        annotators: this.selectedAnnotators.map(id => {
          const annotator = this.availableAnnotators.find(a => a.user === id)
          return annotator?.username || `Usuário ${id}`
        }),
        filters: {
          dataset: this.selectedDataset,
          disagreementStatus: this.disagreementStatus,
          recordRange: this.recordRangeType ? {
            type: this.recordRangeType,
            from: this.recordRangeFrom,
            to: this.recordRangeTo
          } : null,
          categories: this.selectedCategories
        },
        examples: this.allExamplesData.map(exampleData => ({
          id: exampleData.example.id,
          text: exampleData.example.text,
          hasDiscrepancy: exampleData.hasDiscrepancy,
          isResolved: exampleData.isResolved,
          annotations: exampleData.annotators.map(annotator => ({
            annotator: annotator.username,
            count: annotator.annotations.length,
            annotations: annotator.annotations
          }))
        })),
        summary: {
          totalExamples: this.allExamplesData.length,
          discrepancies: this.discrepanciesCount,
          resolved: this.resolvedCount,
          exportDate: new Date().toISOString()
        }
      }

      // Criar e baixar arquivo JSON
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `comparacao_anotadores_${this.projectId}_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      this.$nuxt.$emit('show-snackbar', {
        text: 'Comparação exportada com sucesso!',
        color: 'success'
      })
    }
  }
})
</script>

<style scoped>
.display-1 {
  background: linear-gradient(45deg, #1976d2, #42a5f5);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.annotation-item {
  background-color: #fafafa;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.annotation-item:hover {
  background-color: #f0f0f0;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.h-100 {
  height: 100%;
}
</style> 