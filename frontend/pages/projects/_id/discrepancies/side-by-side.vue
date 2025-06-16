<template>
  <v-container fluid>
    <!-- Alerta de Erro de Base de Dados -->
    <v-alert
      v-if="databaseError"
      type="error"
      dense
      class="mb-4"
    >
      <v-icon left>mdi-database-off</v-icon>
      Database unavailable. Please try again later.
    </v-alert>

        <!-- Main Title -->
    <v-card class="mb-6" elevation="2">
      <v-card-title class="primary white--text text-center justify-center py-6">
        <div>
          <v-icon class="mr-3" size="40">mdi-compare-horizontal</v-icon>
          <span class="text-h4 font-weight-light">Side-by-Side Comparison</span>
        </div>
      </v-card-title>
      <v-card-subtitle class="text-center py-3 text-h6">
        Discrepancy Analysis Tool
      </v-card-subtitle>
    </v-card>

    <!-- Statistical Summary Bar -->
    <v-card v-if="showStatistics" class="mb-6" color="primary" dark>
      <v-card-title>
        <v-icon class="mr-2">mdi-chart-line</v-icon>
        Statistical Summary
        <v-spacer />
        <v-chip color="white" text-color="primary" class="ml-2">
          <v-icon left small>mdi-clock</v-icon>
          Updated {{ timeSinceLastUpdate }}s ago
        </v-chip>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <div class="text-center">
              <div class="text-h4 mb-1">{{ totalDiscrepanciesFiltered }}</div>
              <div class="text-subtitle-1">Total Discrepancies</div>
            </div>
          </v-col>
          <v-col cols="12" md="3">
            <div class="text-center">
              <div class="text-h4 mb-1 error--text">{{ pendingDiscrepancies }}</div>
              <div class="text-subtitle-1">Pending</div>
            </div>
          </v-col>
          <v-col cols="12" md="3">
            <div class="text-center">
              <div class="text-h4 mb-1 success--text">{{ resolvedDiscrepancies }}</div>
              <div class="text-subtitle-1">Resolved</div>
            </div>
          </v-col>
          <v-col cols="12" md="3">
            <div class="text-center">
              <div class="text-h4 mb-1">{{ Math.round(resolutionProgress) }}%</div>
              <div class="text-subtitle-1">Progress</div>
              <v-progress-linear
                :value="resolutionProgress"
                color="success"
                class="mt-1"
              />
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

        <!-- Comparison Filters -->
    <v-card class="mb-6" elevation="2">
      <v-card-title class="primary white--text">
        <v-icon class="mr-2">mdi-filter</v-icon>
        Comparison Filters
        <v-spacer />
        <v-chip v-if="hasActiveFilters" color="white" text-color="primary" small>
          {{ activeFiltersCount }} active filters
        </v-chip>
      </v-card-title>
      
      <v-card-text class="pt-4">
        <!-- Main Filters Row -->
        <v-row class="mb-3">
          <!-- Dataset Selector -->
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedDataset"
              :items="availableDatasets"
              item-text="name"
              item-value="id"
              label="Select Dataset"
              outlined
              dense
              clearable
              prepend-inner-icon="mdi-database"
              :loading="loadingDatasets"
            />
          </v-col>

          <!-- Annotators Selector -->
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedAnnotators"
              :items="availableAnnotators"
              item-text="username"
              item-value="user"
              label="Choose Annotators"
              multiple
              chips
              deletable-chips
              outlined
              dense
              prepend-inner-icon="mdi-account-multiple"
            />
          </v-col>

          <!-- Disagreement Status -->
          <v-col cols="12" md="4">
            <v-select
              v-model="disagreementStatus"
              :items="disagreementStatusOptions"
              item-text="text"
              item-value="value"
              label="Disagreement Status"
              outlined
              dense
              prepend-inner-icon="mdi-alert-circle"
            />
          </v-col>
        </v-row>

        <!-- Secondary Filters Row -->
        <v-row class="mb-3">
          <!-- Text Filter -->
          <v-col cols="12" md="4">
            <v-text-field
              v-model="textFilter"
              label="Filter by Text Content"
              outlined
              dense
              clearable
              prepend-inner-icon="mdi-text-search"
              placeholder="Search in example text..."
            />
          </v-col>

          <!-- Date From -->
          <v-col cols="12" md="4">
            <v-menu
              v-model="dateFromMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              max-width="290px"
              min-width="290px"
            >
              <template #activator="{ on, attrs }">
             <v-text-field
                  v-model="dateFrom"
                  label="Date From"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                outlined
                dense
                clearable
                  v-bind="attrs"
                  v-on="on"
                />
              </template>
              <v-date-picker
                v-model="dateFrom"
                @input="dateFromMenu = false"
              />
            </v-menu>
          </v-col>

          <!-- Date To -->
          <v-col cols="12" md="4">
            <v-menu
              v-model="dateToMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              max-width="290px"
              min-width="290px"
            >
              <template #activator="{ on, attrs }">
                <v-text-field
                  v-model="dateTo"
                  label="Date To"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  outlined
                  dense
                  clearable
                  v-bind="attrs"
                  v-on="on"
                />
              </template>
              <v-date-picker
                v-model="dateTo"
                @input="dateToMenu = false"
              />
            </v-menu>
          </v-col>
        </v-row>

        <!-- Categories Filter Row -->
        <v-row class="mb-3">
          <v-col cols="12">
            <v-select
              v-model="selectedCategories"
              :items="availableCategories"
              item-text="text"
              item-value="id"
              label="Filter by Categories/Labels"
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

        <!-- Action Buttons -->
        <v-divider class="mb-3" />
        <v-row>
          <v-col cols="12">
                         <v-btn 
               color="primary"
              class="mr-2"
              :disabled="selectedAnnotators.length === 0"
              :loading="loadingAnnotations"
              @click="loadComparison"
            >
              <v-icon left>mdi-compare</v-icon>
              Compare Annotations
            </v-btn>
            
                         <v-btn 
              color="secondary"
               outlined
              :disabled="!hasActiveFilters"
              @click="clearAllFilters"
             >
              <v-icon left>mdi-filter-remove</v-icon>
              Clear Filters
            </v-btn>

            <v-btn
              color="success"
              outlined
              class="ml-2"
              :disabled="!showComparison || allExamplesData.length === 0"
              @click="exportComparison"
            >
              <v-icon left>mdi-download</v-icon>
              Export
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

        <!-- Examples Summary -->
    <v-card v-if="showComparison && allExamplesData.length > 0" class="mb-4" elevation="2">
      <v-card-title class="primary white--text">
        <v-icon class="mr-2">mdi-file-multiple</v-icon>
        Examples Overview
        <v-spacer />
        <v-chip color="white" text-color="primary" outlined>
          {{ filteredExamplesCount }} examples found
          </v-chip>
        <v-chip v-if="hasDiscrepancies" color="error" outlined class="ml-2">
          {{ discrepanciesCount }} with discrepancies
          </v-chip>
        <v-chip v-if="hasResolved" color="success" outlined class="ml-2">
          {{ resolvedCount }} resolved
          </v-chip>
      </v-card-title>
    </v-card>

        <!-- Examples List -->
    <div v-if="showComparison && allExamplesData.length > 0">
      <div 
        v-for="(exampleData, exampleIndex) in allExamplesData" 
        :key="exampleData.example.id"
        class="mb-6"
      >
        <!-- Example Information -->
        <v-card 
          :id="`example-${exampleData.example.id}`"
          class="mb-4"
          elevation="2"
          :class="{ 'discrepancy-highlight': exampleData.hasDiscrepancy }"
        >
          <v-card-title class="pb-2 primary white--text">
            <v-chip color="white" text-color="primary" class="mr-3">
              Example #{{ exampleData.example.id }}
          </v-chip>
            <span class="text-subtitle-1">{{ exampleIndex + 1 }} / {{ allExamplesData.length }}</span>
            <v-spacer />
            
            <!-- Discrepancy Indicators -->
            <v-chip
              v-if="exampleData.hasDiscrepancy"
              color="error"
              small
              class="ml-2"
            >
              <v-icon left small>mdi-alert</v-icon>
              {{ exampleData.discrepancyCount }} discrepancy(ies)
            </v-chip>
            
            <v-chip
              v-if="exampleData.isResolved"
              color="success"
              small
              class="ml-2"
            >
              <v-icon left small>mdi-check</v-icon>
              Resolved
            </v-chip>
          </v-card-title>
          
          <v-card-text class="pt-4">
            <!-- Example Text with Highlights -->
            <div class="text-body-1 pa-3 example-text-container" style="background-color: #f5f5f5; border-radius: 4px; border-left: 4px solid #1976d2;">
              <span>
                <template v-for="(segment, index) in getTextSegments(exampleData)">
                  <span
                    v-if="segment.highlighted"
                    :key="`highlight-${index}`"
                    :class="`discrepancy-highlight-${segment.type}`"
                    :style="{ backgroundColor: segment.color }"
                  >
                    {{ segment.text }}
                  </span>
                  <span 
                    v-else
                    :key="`normal-${index}`"
                  >
                    {{ segment.text }}
                  </span>
                </template>
              </span>
        </div>
            
            <!-- Color Legend -->
            <v-row v-if="exampleData.hasDiscrepancy" class="mt-3">
              <v-col cols="12">
                <v-divider class="mb-2" />
                <div class="text-caption font-weight-bold mb-2">Discrepancy Legend:</div>
                <v-chip
                  v-for="legendItem in getDiscrepancyLegend(exampleData)"
                  :key="legendItem.type"
                  :color="legendItem.color"
                  small
                  class="mr-1 mb-1"
                >
                  {{ legendItem.label }}
                </v-chip>
              </v-col>
            </v-row>
      </v-card-text>
    </v-card>

        <!-- Side-by-Side Comparison for this Example -->
      <v-row>
        <v-col
            v-for="(annotatorData, annotatorIndex) in exampleData.annotators"
            :key="annotatorData.annotatorId"
          :cols="12"
            :md="Math.floor(12 / exampleData.annotators.length)"
          >
            <v-card :color="`${getAnnotatorColor(annotatorIndex)} lighten-5`" class="h-100" elevation="1">
              <v-card-title :class="`${getAnnotatorColor(annotatorIndex)} white--text`" class="py-3">
                <v-avatar :color="getAnnotatorColor(annotatorIndex)" class="mr-2" size="32">
                  <span class="white--text font-weight-bold">
                    {{ annotatorData.username[0].toUpperCase() }}
                  </span>
              </v-avatar>
                {{ annotatorData.username }}
              <v-spacer></v-spacer>
                <v-chip small color="white" :text-color="getAnnotatorColor(annotatorIndex)">
                  {{ annotatorData.annotations.length }} annotation{{ annotatorData.annotations.length !== 1 ? 's' : '' }}
              </v-chip>
            </v-card-title>
            <v-divider />
              <v-card-text class="pa-4">
                <!-- Annotator's Annotations -->
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
                    
                    <!-- Annotation Text (for spans) -->
                    <div v-if="annotation.start_offset !== undefined" class="text-caption mb-1">
                      "{{ getAnnotationText(annotation, exampleData.example) }}"
                    </div>
                    
                    <!-- Position (for spans) -->
                    <div v-if="annotation.start_offset !== undefined" class="text-caption grey--text">
                      Position: {{ annotation.start_offset }} - {{ annotation.end_offset }}
                    </div>
                  </div>
                </div>
                
                <!-- No annotations case -->
                <div v-else class="text-center text-grey pa-4">
                  <v-icon size="40" color="grey lighten-1">mdi-file-outline</v-icon>
                  <p class="mt-2">No annotations found</p>
                </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
        
        <!-- Divider entre exemplos -->
        <v-divider v-if="exampleIndex < allExamplesData.length - 1" class="my-6"></v-divider>
      </div>
    </div>
    
    <!-- Empty State -->
    <v-card v-else-if="showComparison && allExamplesData.length === 0" class="pa-8 text-center" elevation="2">
      <v-icon size="80" color="grey lighten-1">mdi-file-search-outline</v-icon>
      <h3 class="mt-4 mb-2">No Examples Found</h3>
      <p class="text-body-1">No examples were found in the project or the selected annotators have no annotations matching the current filters.</p>
    </v-card>
    
    <!-- Initial Placeholder -->
    <v-card v-else class="pa-8 text-center" elevation="2">
      <v-icon size="80" color="grey lighten-1">mdi-compare</v-icon>
      <h3 class="mt-4 mb-2">Ready to Compare</h3>
      <p class="text-body-1">Select annotators and apply filters to start the comparison analysis.</p>
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

                      // Filters
       selectedDataset: null,
       availableDatasets: [],
       disagreementStatus: 'all',
       disagreementStatusOptions: [
         { text: 'All', value: 'all' },
         { text: 'Only Disagreements', value: 'disagreement' },
         { text: 'Already Resolved', value: 'resolved' }
       ],
       textFilter: '',
       dateFrom: null,
       dateTo: null,
       dateFromMenu: false,
       dateToMenu: false,
       selectedCategories: [],
       availableCategories: [],
       loadingDatasets: false,
       loadingCategories: false,
       discrepanciesCount: 0,
       resolvedCount: 0,

       // Database checking
       databaseError: false,
       checkInterval: null,
       lastUpdateTime: null,

       // Statistics
       showStatistics: false,
       discrepancyExamples: [],
       
       // Cores para realce de discrepâncias
       discrepancyColors: {
         labelDifferent: '#ffeb3b',      // Amarelo - etiqueta diferente
         spanDifferent: '#ff9800',       // Laranja - span diferente  
         labelMissing: '#f44336',        // Vermelho - etiqueta ausente
         spanOverlap: '#9c27b0',         // Roxo - sobreposição de spans
         consensus: '#4caf50'            // Verde - consenso
       }
    }
  },

  computed: {
    ...mapGetters('projects', ['project']),
    
    projectId(): string {
      return this.$route.params.id
    },

    // Filter computed properties
    hasActiveFilters(): boolean {
      return !!(
        this.selectedDataset ||
        this.selectedAnnotators.length > 0 ||
        (this.disagreementStatus !== 'all' && this.disagreementStatus !== null) ||
        this.textFilter ||
        this.dateFrom ||
        this.dateTo ||
        this.selectedCategories.length > 0
      )
    },

    activeFiltersCount(): number {
      let count = 0
      if (this.selectedDataset) count++
      if (this.selectedAnnotators.length > 0) count++
      if (this.disagreementStatus && this.disagreementStatus !== 'all') count++
      if (this.textFilter) count++
      if (this.dateFrom || this.dateTo) count++
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

    // Statistical computed properties
    totalDiscrepanciesFiltered(): number {
      return this.discrepancyExamples.length
    },

    pendingDiscrepancies(): number {
      return this.discrepancyExamples.filter(ex => !ex.isResolved).length
    },

    resolvedDiscrepancies(): number {
      return this.discrepancyExamples.filter(ex => ex.isResolved).length
    },

    resolutionProgress(): number {
      return this.totalDiscrepanciesFiltered > 0 
        ? (this.resolvedDiscrepancies / this.totalDiscrepanciesFiltered) * 100 
        : 0
    },

    timeSinceLastUpdate(): number {
      return this.lastUpdateTime 
        ? Math.floor((Date.now() - this.lastUpdateTime) / 1000)
        : 0
    }
  },

  async mounted() {
    await this.loadAnnotators()
    await this.loadLabelTypes()
    this.loadDatasets()
    await this.loadCategories()
    this.initializeFilters()
    this.startDatabaseCheck()
  },

  beforeDestroy() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
    }
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
      // Initialize filters with default values
      this.disagreementStatus = 'all'
      console.log('Filters initialized')
    },

    async loadComparison() {
      if (this.selectedAnnotators.length < 2) {
        return
      }

      this.loadingAnnotations = true
      this.allExamplesData = []
      
      try {
        // Load all available examples
        console.log('Loading all project examples...')
        const examplesResponse = await this.$repositories.example.list(this.projectId, { limit: 100 })
        let examples = examplesResponse.items || examplesResponse
        
        console.log(`${examples.length} examples found`)
        
        if (examples.length === 0) {
          this.$nuxt.$emit('show-snackbar', {
            text: 'No examples found in the project',
            color: 'warning'
          })
          return
        }

        // Apply text and date filters
        examples = this.applyAllFilters(examples)
        console.log(`${examples.length} examples after text/date filtering`)

        // Load annotations for all examples
        const allExamplesPromises = examples.map(async (example) => {
          return await this.loadExampleAnnotations(example)
        })

        let allExamplesData = await Promise.all(allExamplesPromises)
        
        // Filter only examples that have at least one annotation from selected annotators
        allExamplesData = allExamplesData.filter(exampleData => 
          exampleData.annotators.some(annotator => annotator.annotations.length > 0)
        )

        // Process each example with filters and discrepancy detection
        const processedExamples = []
        let discrepanciesCount = 0
        let resolvedCount = 0

        for (const exampleData of allExamplesData) {
          // Apply category filter if selected
          if (this.selectedCategories.length > 0) {
            const hasSelectedCategories = this.checkSelectedCategories(exampleData)
            if (!hasSelectedCategories) {
              continue
            }
          }

          // Detect detailed discrepancies
          const discrepancyInfo = this.detectDetailedDiscrepancies(exampleData)
          exampleData.hasDiscrepancy = discrepancyInfo.hasDiscrepancy
          exampleData.isResolved = discrepancyInfo.isResolved
          exampleData.discrepancyCount = discrepancyInfo.discrepancyCount
          exampleData.discrepancyDetails = discrepancyInfo.details
          
          if (discrepancyInfo.hasDiscrepancy) {
            discrepanciesCount++
            exampleData.discrepancyIndex = this.discrepancyExamples.length
            this.discrepancyExamples.push(exampleData)
          }
          if (discrepancyInfo.isResolved) resolvedCount++

          // Apply disagreement status filter
          if (this.shouldIncludeExample(exampleData)) {
            processedExamples.push(exampleData)
          }
        }

        this.allExamplesData = processedExamples
        this.discrepanciesCount = discrepanciesCount
        this.resolvedCount = resolvedCount
        this.lastUpdateTime = Date.now()

        this.showComparison = true
        this.showStatistics = true
        
        console.log(`Comparison loaded for ${this.allExamplesData.length} examples with annotations`)
        console.log(`Discrepancies: ${discrepanciesCount}, Resolved: ${resolvedCount}`)
        console.log(`Examples with discrepancies: ${this.discrepancyExamples.length}`)
        
      } catch (error) {
        console.error('Error loading comparison:', error)
        this.$nuxt.$emit('show-snackbar', {
          text: 'Error loading comparison: ' + error.message,
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
      // Search in all label types
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
      
      // Infer type based on structure
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
        console.log('Loading annotations for example:', example.id)

        // Load ALL example annotations using direct query (like discuss page)
        const allAnnotations = []

        // Search for category annotations
        try {
          const categoryResponse = await this.$repositories.category.request.get(
            `/projects/${this.projectId}/examples/${example.id}/categories?show_all=true`
          )
          console.log(`Example ${example.id} - Category annotations found:`, categoryResponse.data.length)
          
          for (const annotation of categoryResponse.data) {
            allAnnotations.push({
              ...annotation,
              type: 'category',
              userId: annotation.user
            })
          }
      } catch (error) {
          console.log(`Example ${example.id} - Error loading category annotations:`, error)
        }

        // Search for span annotations
        try {
          const spanResponse = await this.$repositories.span.request.get(
            `/projects/${this.projectId}/examples/${example.id}/spans?show_all=true`
          )
          console.log(`Example ${example.id} - Span annotations found:`, spanResponse.data.length)
          
          for (const annotation of spanResponse.data) {
            allAnnotations.push({
              ...annotation,
              type: 'span',
              userId: annotation.user
            })
          }
        } catch (error) {
          console.log(`Example ${example.id} - Error loading span annotations:`, error)
        }

        // Search for relation annotations
        try {
          const relationResponse = await this.$repositories.relation.request.get(
            `/projects/${this.projectId}/examples/${example.id}/relations?show_all=true`
          )
          console.log(`Example ${example.id} - Relation annotations found:`, relationResponse.data.length)
          
          for (const annotation of relationResponse.data) {
            allAnnotations.push({
              ...annotation,
              type: 'relation',
              userId: annotation.user
            })
          }
        } catch (error) {
          console.log(`Example ${example.id} - Error loading relation annotations:`, error)
        }

        console.log(`Example ${example.id} - Total annotations found:`, allAnnotations.length)

        // Create comparison data for each selected annotator
        const annotators = this.selectedAnnotators.map(annotatorId => {
          const annotator = this.availableAnnotators.find(a => a.user === annotatorId)
          
          // Filter annotations from this specific annotator
          const annotatorAnnotations = allAnnotations.filter(ann => {
            // Check different ways userId can be represented
            const match = ann.userId === annotatorId || 
                         ann.user === annotatorId || 
                         parseInt(ann.user) === annotatorId ||
                         parseInt(ann.userId) === annotatorId
            
            return match
          })

          console.log(`Example ${example.id} - User ${annotatorId} (${annotator?.username}):`, annotatorAnnotations.length, 'annotations')

          return {
            annotatorId,
            username: annotator?.username || `User ${annotatorId}`,
            annotations: annotatorAnnotations
          }
        })

        return {
          example,
          annotators
        }

      } catch (error) {
        console.error(`Error loading annotations for example ${example.id}:`, error)
        return {
          example,
          annotators: this.selectedAnnotators.map(annotatorId => {
            const annotator = this.availableAnnotators.find(a => a.user === annotatorId)
            return {
              annotatorId,
              username: annotator?.username || `User ${annotatorId}`,
              annotations: []
            }
          })
        }
      }
    },

    // Filter methods
    applyTextFilter(examples) {
      if (!this.textFilter) {
        return examples
      }

      const searchTerm = this.textFilter.toLowerCase()
      return examples.filter(example => 
        example.text && example.text.toLowerCase().includes(searchTerm)
      )
    },

    applyDateFilter(examples) {
      if (!this.dateFrom && !this.dateTo) {
        return examples
      }

      return examples.filter(example => {
        // If examples have a date field, use it for filtering
        // For now, we'll implement basic filtering based on creation date if available
        if (example.created_at || example.date) {
          const exampleDate = new Date(example.created_at || example.date)
          
          if (this.dateFrom) {
            const fromDate = new Date(this.dateFrom)
            if (exampleDate < fromDate) return false
          }
          
          if (this.dateTo) {
            const toDate = new Date(this.dateTo)
            if (exampleDate > toDate) return false
          }
        }
        
        return true
      })
    },

    applyAllFilters(examples) {
      let filtered = examples

      // Apply text filter
      filtered = this.applyTextFilter(filtered)

      // Apply date filter
      filtered = this.applyDateFilter(filtered)

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

    // Verificação da base de dados
    startDatabaseCheck() {
      this.checkDatabaseConnection()
      this.checkInterval = setInterval(this.checkDatabaseConnection, 1000)
    },

    async checkDatabaseConnection() {
      try {
        await this.$repositories.member.list(this.projectId)
        this.databaseError = false
      } catch (error) {
        console.error('Erro na verificação da conexão:', error)
        this.databaseError = true
      }
    },

    // Detecção detalhada de discrepâncias
    detectDetailedDiscrepancies(exampleData) {
      const annotators = exampleData.annotators
      let hasDiscrepancy = false
      let isResolved = false
      let discrepancyCount = 0
      const details = []

      if (annotators.length < 2) {
        return { hasDiscrepancy: false, isResolved: false, discrepancyCount: 0, details: [] }
      }

      // Agrupar anotações por posição e tipo
      const spanGroups = {}
      const categoryGroups = {}
      const relationGroups = {}

      // Processar anotações de cada anotador
      for (const annotator of annotators) {
        for (const annotation of annotator.annotations) {
          const type = this.getAnnotationType(annotation)

          if (type === 'span') {
            const key = `${annotation.start_offset}-${annotation.end_offset}`
            if (!spanGroups[key]) spanGroups[key] = []
            spanGroups[key].push({ annotator: annotator.annotatorId, annotation })
          } else if (type === 'category') {
            const key = 'document'
            if (!categoryGroups[key]) categoryGroups[key] = []
            categoryGroups[key].push({ annotator: annotator.annotatorId, annotation })
          } else if (type === 'relation') {
            const key = `${annotation.from_id}-${annotation.to_id}`
            if (!relationGroups[key]) relationGroups[key] = []
            relationGroups[key].push({ annotator: annotator.annotatorId, annotation })
          }
        }
      }

      // Verificar discrepâncias em spans
      for (const [position, group] of Object.entries(spanGroups)) {
        const uniqueLabels = new Set(group.map(item => item.annotation.label))
        const uniqueAnnotators = new Set(group.map(item => item.annotator))

        if (uniqueLabels.size > 1) {
          hasDiscrepancy = true
          discrepancyCount++
          details.push({
            type: 'labelDifferent',
            position,
            description: `Etiquetas diferentes na posição ${position}`,
            annotators: Array.from(uniqueAnnotators),
            labels: Array.from(uniqueLabels)
          })
        }

        // Verificar se algum anotador não anotou esta posição
        if (uniqueAnnotators.size < annotators.length) {
          hasDiscrepancy = true
          discrepancyCount++
          details.push({
            type: 'labelMissing',
            position,
            description: `Etiqueta ausente na posição ${position}`,
            presentAnnotators: Array.from(uniqueAnnotators),
            missingAnnotators: annotators
              .filter(a => !uniqueAnnotators.has(a.annotatorId))
              .map(a => a.annotatorId)
          })
        }
      }

      // Verificar discrepâncias em categorias
      for (const [, group] of Object.entries(categoryGroups)) {
        const uniqueLabels = new Set(group.map(item => item.annotation.label))
        const uniqueAnnotators = new Set(group.map(item => item.annotator))

        if (uniqueLabels.size > 1) {
          hasDiscrepancy = true
          discrepancyCount++
          details.push({
            type: 'labelDifferent',
            position: 'document',
            description: 'Categorias diferentes para o documento',
            annotators: Array.from(uniqueAnnotators),
            labels: Array.from(uniqueLabels)
          })
        }
      }

      // Verificar sobreposições de spans (spans que se sobrepõem mas não são idênticos)
      const allSpans = []
      for (const annotator of annotators) {
        for (const annotation of annotator.annotations) {
          if (this.getAnnotationType(annotation) === 'span') {
            allSpans.push({
              annotator: annotator.annotatorId,
              start: annotation.start_offset,
              end: annotation.end_offset,
              label: annotation.label
            })
          }
        }
      }

      for (let i = 0; i < allSpans.length; i++) {
        for (let j = i + 1; j < allSpans.length; j++) {
          const span1 = allSpans[i]
          const span2 = allSpans[j]

          // Verificar sobreposição mas não identidade
          if (span1.annotator !== span2.annotator &&
              ((span1.start < span2.end && span1.end > span2.start) &&
               !(span1.start === span2.start && span1.end === span2.end))) {
            hasDiscrepancy = true
            discrepancyCount++
            details.push({
              type: 'spanOverlap',
              position: `${span1.start}-${span1.end} vs ${span2.start}-${span2.end}`,
              description: `Sobreposição de spans entre anotadores`,
              annotators: [span1.annotator, span2.annotator],
              spans: [span1, span2]
            })
          }
        }
      }

      // Por enquanto, considerar como resolvido se não há discrepâncias
      isResolved = !hasDiscrepancy

      return { hasDiscrepancy, isResolved, discrepancyCount, details }
    },

    // Segmentação segura do texto com realces
    getTextSegments(exampleData) {
      if (!exampleData.hasDiscrepancy || !exampleData.discrepancyDetails) {
        return [{ text: exampleData.example.text, highlighted: false }]
      }

      const text = exampleData.example.text
      const highlights = []

      // Coletar todas as posições que precisam ser destacadas
      for (const detail of exampleData.discrepancyDetails) {
        if (detail.position && detail.position !== 'document') {
          const [start, end] = detail.position.split('-').map(Number)
          if (!isNaN(start) && !isNaN(end) && start >= 0 && end <= text.length) {
            highlights.push({
              start,
              end,
              type: detail.type,
              color: this.discrepancyColors[detail.type] || '#ffeb3b'
            })
          }
        }
      }

      if (highlights.length === 0) {
        return [{ text, highlighted: false }]
      }

      // Ordenar por posição inicial
      highlights.sort((a, b) => a.start - b.start)

      const segments = []
      let lastEnd = 0

      for (const highlight of highlights) {
        // Adicionar texto antes do highlight
        if (highlight.start > lastEnd) {
          segments.push({
            text: text.substring(lastEnd, highlight.start),
            highlighted: false
          })
        }

        // Adicionar o highlight
        segments.push({
          text: text.substring(highlight.start, highlight.end),
          highlighted: true,
          type: highlight.type,
          color: highlight.color
        })

        lastEnd = Math.max(lastEnd, highlight.end)
      }

      // Adicionar texto restante
      if (lastEnd < text.length) {
        segments.push({
          text: text.substring(lastEnd),
          highlighted: false
        })
      }

      return segments
    },

    // Legenda das cores de discrepância
    getDiscrepancyLegend(exampleData) {
      const legend = []
      const usedTypes = new Set()

      for (const detail of exampleData.discrepancyDetails) {
        if (!usedTypes.has(detail.type)) {
          usedTypes.add(detail.type)
          
          let label = ''
          let color = ''
          
                    switch (detail.type) {
            case 'labelDifferent':
              label = 'Different Label'
              color = 'warning'
              break
            case 'spanDifferent':
              label = 'Different Span'
              color = 'orange'
              break
            case 'labelMissing':
              label = 'Missing Label'
              color = 'error'
              break
            case 'spanOverlap':
              label = 'Span Overlap'
              color = 'purple'
              break
            default:
              label = detail.type
              color = 'grey'
          }

          legend.push({ type: detail.type, label, color })
        }
      }

      return legend
    },



    clearAllFilters() {
      this.selectedDataset = null
      this.selectedAnnotators = []
      this.disagreementStatus = 'all'
      this.textFilter = ''
      this.dateFrom = null
      this.dateTo = null
      this.dateFromMenu = false
      this.dateToMenu = false
      this.selectedCategories = []
      this.showComparison = false
      this.showStatistics = false
      this.allExamplesData = []
      this.discrepancyExamples = []
      this.discrepanciesCount = 0
      this.resolvedCount = 0
      this.lastUpdateTime = null
    },

    exportComparison() {
      // Implement comparison data export
      const exportData = {
        project: this.project.name,
        annotators: this.selectedAnnotators.map(id => {
          const annotator = this.availableAnnotators.find(a => a.user === id)
          return annotator?.username || `User ${id}`
        }),
        filters: {
          dataset: this.selectedDataset,
          disagreementStatus: this.disagreementStatus,
          textFilter: this.textFilter,
          dateRange: {
            from: this.dateFrom,
            to: this.dateTo
          },
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

      // Create and download JSON file
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `annotator_comparison_${this.projectId}_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      this.$nuxt.$emit('show-snackbar', {
        text: 'Comparison exported successfully!',
        color: 'success'
      })
    }
  }
})
</script>

<style scoped>

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

/* Discrepancy highlighting */
.discrepancy-highlight {
  border: 2px solid #ff5722;
  box-shadow: 0 0 10px rgba(255, 87, 34, 0.3);
}

.example-text-container {
  position: relative;
}

.discrepancy-highlight-labelDifferent {
  background-color: #ffeb3b !important;
  color: #333 !important;
  font-weight: bold;
}

.discrepancy-highlight-spanDifferent {
  background-color: #ff9800 !important;
  color: white !important;
  font-weight: bold;
}

.discrepancy-highlight-labelMissing {
  background-color: #f44336 !important;
  color: white !important;
  font-weight: bold;
  border: 2px dashed #d32f2f;
}

.discrepancy-highlight-spanOverlap {
  background-color: #9c27b0 !important;
  color: white !important;
  font-weight: bold;
  border: 2px dotted #7b1fa2;
}

/* Highlight animation */
.pulse-highlight {
  animation: pulse-glow 2s ease-in-out;
}

@keyframes pulse-glow {
  0% {
    box-shadow: 0 0 5px rgba(33, 150, 243, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(33, 150, 243, 0.8), 0 0 30px rgba(33, 150, 243, 0.6);
    transform: scale(1.02);
  }
  100% {
    box-shadow: 0 0 5px rgba(33, 150, 243, 0.5);
  }
}

/* Text discrepancy highlighting */
::v-deep .discrepancy-highlight-labelDifferent {
  background-color: #ffeb3b;
  color: #333;
  font-weight: bold;
  padding: 2px 4px;
  border-radius: 3px;
  border: 1px solid #fbc02d;
}

::v-deep .discrepancy-highlight-spanDifferent {
  background-color: #ff9800;
  color: white;
  font-weight: bold;
  padding: 2px 4px;
  border-radius: 3px;
  border: 1px solid #f57c00;
}

::v-deep .discrepancy-highlight-labelMissing {
  background-color: #f44336;
  color: white;
  font-weight: bold;
  padding: 2px 4px;
  border-radius: 3px;
  border: 2px dashed #d32f2f;
}

::v-deep .discrepancy-highlight-spanOverlap {
  background-color: #9c27b0;
  color: white;
  font-weight: bold;
  padding: 2px 4px;
  border-radius: 3px;
  border: 2px dotted #7b1fa2;
}

/* Smooth transition animations */
.v-card {
  transition: all 0.3s ease;
}

.v-card.discrepancy-highlight {
  border-left: 4px solid #ff5722;
}

/* Custom progress indicators */
.v-progress-linear {
  border-radius: 10px;
}

/* Status chips */
.v-chip {
  transition: all 0.2s ease;
}

.v-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
</style> 