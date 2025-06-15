<template>
  <v-container>
    <!-- Cabeçalho -->
    <v-row>
      <v-col cols="12">
        <v-alert
          v-if="!hasDiscrepancies"
          type="info"
          class="mb-4"
        >
          No different perspectives were found in the annotations.
        </v-alert>
        
        <!-- Database error message -->
        <v-alert
          v-if="showDatabaseError || !isDatabaseConnected"
          type="error"
          class="mb-4"
          dismissible
          @input="dismissDatabaseError"
        >
          <div v-if="!isDatabaseConnected">
            <v-icon left>mdi-database-off</v-icon>
            Database unavailable please try again
          </div>
          <div v-else>
            Database connection error. Some data may be unavailable.
          </div>
        </v-alert>
        
        <!-- Botão quase transparente -->
        <v-btn
          absolute
          top
          right
          fab
          x-small
          class="debug-button"
          @click="toggleDatabaseError"
        >
          <v-icon small>mdi-database-alert</v-icon>
        </v-btn>
      </v-col>
    </v-row>

    <!-- PARTE 1: FILTROS E CONTROLES -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-title class="headline primary white--text">
            <v-icon left dark>mdi-filter</v-icon>
            Filters and Export Options
            <v-spacer></v-spacer>
            <v-chip 
              v-if="hasActiveFilters" 
              color="white" 
              text-color="primary" 
              class="ml-2"
            >
              {{ activeFiltersCount }} active filters
            </v-chip>
          </v-card-title>

          <v-card-text class="pt-4">
            <!-- Primeira linha: Filtros principais -->
            <v-row class="mb-2 mx-0">
              <!-- Utilizadores -->
              <v-col cols="12" sm="6" md="4" class="px-3">
                <v-select
                  v-model="filters.users"
                  :items="availableUsers"
                  item-text="username"
                  item-value="id"
                  label="Filter by Users"
                  hint="If blank, all users will be included"
                  persistent-hint
                  multiple
                  clearable
                  outlined
                  dense
                  prepend-icon="mdi-account-multiple"
                  :loading="loadingUsers"
                >
                  <template #selection="{ item, index }">
                    <v-chip
                      v-if="index < 2"
                      small
                      close
                      @click:close="removeUser(item)"
                    >
                      {{ getSelectedUserText(item) }}
                    </v-chip>
                    <span
                      v-if="index === 2"
                      class="grey--text text-caption"
                    >
                      (+{{ filters.users.length - 2 }} others)
                    </span>
                  </template>
                </v-select>
              </v-col>

              <!-- Labels -->
              <v-col cols="12" sm="6" md="4" class="px-3">
                <v-select
                  v-model="filters.labels"
                  :items="availableLabels"
                  item-text="text"
                  item-value="id"
                  label="Filter by Labels"
                  hint="If blank, all label categories will be included"
                  persistent-hint
                  multiple
                  clearable
                  outlined
                  dense
                  prepend-icon="mdi-label"
                  :loading="loadingLabels"
                >
                  <template #selection="{ item, index }">
                    <v-chip
                      v-if="index < 2"
                      small
                      close
                      :color="getLabelTypeColor(getSelectedLabelType(item))"
                      @click:close="removeLabel(item)"
                    >
                      {{ getSelectedLabelText(item) }}
                    </v-chip>
                    <span
                      v-if="index === 2"
                      class="grey--text text-caption"
                    >
                      (+{{ filters.labels.length - 2 }} others)
                    </span>
                  </template>
                </v-select>
              </v-col>

              <!-- Datasets -->
              <v-col cols="12" sm="6" md="4" class="px-3">
                <v-select
                  v-model="filters.datasets"
                  :items="availableDatasets"
                  item-text="name"
                  item-value="name"
                  label="Filter by Datasets"
                  hint="If blank, all datasets will be included"
                  persistent-hint
                  multiple
                  clearable
                  outlined
                  dense
                  prepend-icon="mdi-database"
                  :loading="loadingDatasets"
                >
                  <template #selection="{ item, index }">
                    <v-chip
                      v-if="index < 2"
                      small
                      close
                      @click:close="removeDataset(getDatasetDisplayName(item))"
                    >
                      {{ getDatasetDisplayName(item) }}
                    </v-chip>
                    <span
                      v-if="index === 2"
                      class="grey--text text-caption"
                    >
                      (+{{ filters.datasets.length - 2 }} others)
                    </span>
                  </template>
                </v-select>
              </v-col>
            </v-row>

            <!-- Segunda linha: Filtros de data, perspectivas e exportação -->
            <v-row class="mb-2 mx-0">
              <v-col cols="12" sm="6" md="3" class="px-3">
                <v-text-field
                  v-model="filters.date_from"
                  label="From Date"
                  hint="If blank, no start date limit"
                  persistent-hint
                  type="date"
                  outlined
                  dense
                  prepend-icon="mdi-calendar-start"
                  clearable
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6" md="3" class="px-3">
                <v-text-field
                  v-model="filters.date_to"
                  label="To Date"
                  hint="If blank, no end date limit"
                  persistent-hint
                  type="date"
                  outlined
                  dense
                  prepend-icon="mdi-calendar-end"
                  clearable
                ></v-text-field>
              </v-col>

              <!-- Perspectivas -->
              <v-col cols="12" sm="6" md="3" class="px-3">
                <v-select
                  v-model="filters.perspectives"
                  :items="availablePerspectives"
                  item-text="name"
                  item-value="id"
                  label="Filter by Perspectives"
                  hint="If blank, all perspectives will be included"
                  persistent-hint
                  multiple
                  clearable
                  outlined
                  dense
                  prepend-icon="mdi-eye"
                  :loading="loadingPerspectives"
                >
                  <template #selection="{ item, index }">
                    <v-chip
                      v-if="index < 1"
                      small
                      close
                      @click:close="removePerspective(item)"
                    >
                      {{ getPerspectiveNameById(item) }}
                    </v-chip>
                    <span
                      v-if="index === 1"
                      class="grey--text text-caption"
                    >
                      (+{{ filters.perspectives.length - 1 }} others)
                    </span>
                  </template>
                </v-select>
              </v-col>

              <!-- Formatos de exportação -->
              <v-col cols="12" sm="6" md="3" class="px-3">
                <v-select
                  v-model="filters.export_formats"
                  :items="['csv', 'pdf']"
                  label="Export Formats"
                  multiple
                  clearable
                  outlined
                  dense
                  prepend-icon="mdi-file-export"
                >
                  <template #selection="{ item, index }">
                    <v-chip
                      v-if="index < 2"
                      small
                      close
                      :color="getExportFormatColor(item)"
                      @click:close="removeExportFormat(item)"
                    >
                      {{ item.toUpperCase() }}
                    </v-chip>
                  </template>
                </v-select>
              </v-col>
            </v-row>

            <!-- Terceira linha: Barra de pesquisa -->
            <v-row class="mx-0">
              <v-col cols="12" class="px-3">
                <v-text-field
                  v-model="search"
                  label="Search in results"
                  hint="Search by annotator name, labels, or any field"
                  persistent-hint
                  prepend-inner-icon="mdi-magnify"
                  outlined
                  dense
                  clearable
                ></v-text-field>
              </v-col>
            </v-row>

            <!-- Botões de ação -->
            <v-row class="mt-2">
              <v-col cols="12" class="d-flex align-center justify-space-between">
                <div>
                  <v-btn
                    color="primary"
                    :loading="isGenerating"
                    :disabled="!hasActiveFilters"
                    class="mr-2"
                    @click="generateAndExportReport"
                  >
                    <v-icon left>mdi-play</v-icon>
                    Generate Report
                  </v-btn>
                  <v-btn
                    color="secondary"
                    :disabled="!hasActiveFilters"
                    @click="clearFilters"
                  >
                    <v-icon left>mdi-filter-remove</v-icon>
                    Clear Filters
                  </v-btn>
                </div>
                <div>
                  <v-btn
                    color="error"
                    @click="cancelReport"
                  >
                    <v-icon left>mdi-close</v-icon>
                    Cancel
                  </v-btn>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- PARTE 2: TABELA DE RESULTADOS -->
    <v-row v-if="hasDiscrepancies">
      <v-col cols="12">
        <v-card>
          <v-card-title class="headline primary white--text">
            <v-icon left dark>mdi-table</v-icon>
            Annotations Report (preview)
            <v-spacer></v-spacer>
            <v-chip color="white" text-color="primary" class="ml-2">
              Threshold: {{ safeProject.minPercentage }}%
            </v-chip>
            <v-chip color="white" text-color="primary" class="ml-2">
              Total: {{ totalDiscrepancies }} agreements
            </v-chip>
            <v-chip 
              v-if="reportData && reportData.length > 0"
              color="white" 
              text-color="primary" 
              class="ml-2"
            >
              Showing: {{ filteredDiscrepancyItems.length }} items
            </v-chip>
          </v-card-title>

          <v-card-text class="pt-4">
            <div v-if="loading" class="d-flex justify-center align-center" style="height: 200px">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </div>
            
            <div v-else-if="reportData && reportData.length > 0">
              <v-data-table
                :headers="headers"
                :items="filteredDiscrepancyItems"
                :items-per-page="10"
                class="elevation-1"
                :search="search"
                :loading="isGenerating"
                loading-text="Loading data..."
              >
                <template #[`item.tempo_medio_por_anotacao_seg`]="{ item }">
                  {{ item.tempo_medio_por_anotacao_seg ? item.tempo_medio_por_anotacao_seg.toFixed(1) : '0.0' }}s
                </template>
                
                <template #[`item.taxa_desacordo_percent`]="{ item }">
                  <v-chip 
                    color="error" 
                    dark 
                    small
                  >
                    {{ item.taxa_desacordo_percent ? item.taxa_desacordo_percent.toFixed(1) : '0.0' }}%
                  </v-chip>
                </template>
                
                <template #[`item.score_concordancia_medio`]="{ item }">
                  <v-chip 
                    :color="getScoreConcordanciaColor(item.score_concordancia_medio)" 
                    dark 
                    small
                  >
                    {{ item.score_concordancia_medio ? (item.score_concordancia_medio * 100).toFixed(1) : '0.0' }}%
                  </v-chip>
                </template>
                
                <template #[`item.categorias_mais_frequentes`]="{ item }">
                  <div class="text-truncate" style="max-width: 300px;" :title="item.categorias_mais_frequentes ? item.categorias_mais_frequentes.join(', ') : 'None'">
                    {{ item.categorias_mais_frequentes ? item.categorias_mais_frequentes.join(', ') : 'None' }}
                  </div>
                </template>
              </v-data-table>
            </div>

            <div v-else-if="!loading && (!reportData || reportData.length === 0)">
              <v-alert type="info" class="text-center">
                <v-icon large class="mb-2">mdi-information</v-icon>
                <div class="headline mb-2">No Data Available</div>
                <div>
                  Please select filters above and click "Generate Report" to view disagreement data.
                </div>
              </v-alert>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="600px">
      <v-card>
        <v-card-title class="headline primary white--text">
          Agreement Details
          <v-spacer></v-spacer>
          <v-btn icon dark @click="detailsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-list>
            <v-list-item v-for="(value, key) in filteredSelectedItem" :key="key">
              <v-list-item-content>
                <v-list-item-title class="font-weight-bold">{{ formatKey(key) }}</v-list-item-title>
                <v-list-item-subtitle class="mt-1">{{ value }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  
  data() {
    return {
      loading: true,
      generatingReport: false,
      reportGenerated: false,
      items: {},
      search: '',
      showDatabaseError: false,
      isDatabaseConnected: true,
      databaseCheckInterval: null,
      filters: {
        users: [],
        labels: [],
        datasets: [],
        date_from: null,
        date_to: null,
        perspectives: [],
        export_formats: ['pdf']
      },
      labels: [],
      annotators: [],
      textTypes: [],
      perspectives: [],
      detailsDialog: false,
      selectedItem: null,
      headers: [
          { text: 'Annotator', value: 'nome_anotador', width: '15%' },
          { text: 'Total Annotations', value: 'total_anotacoes', align: 'center', width: '12%' },
          { text: 'Datasets', value: 'datasets_distintos', align: 'center', width: '10%' },
          { text: 'Average Time (sec)', value: 'tempo_medio_por_anotacao_seg', align: 'center', width: '12%' },
          { text: 'Disagreement Rate (%)', value: 'taxa_desacordo_percent', align: 'center', width: '12%' },
          { text: 'Agreement Score (%)', value: 'score_concordancia_medio', align: 'center', width: '14%' },
          { text: 'Labels Used', value: 'categorias_mais_frequentes', width: '25%' }
        ],

      categoryMap: {},
      exampleNameMap: {},
      exampleAnnotators: {},
      loadingUsers: false,
      loadingLabels: false,
      loadingDatasets: false,
      loadingPerspectives: false,
      reportData: [],
      availableUsers: [],
      availableLabels: [],
      availableDatasets: [],
      availablePerspectives: [],
      isGenerating: false,
      isExporting: false,
      updateTimeout: null
    }
  },

  async fetch() {
    this.loading = true
    try {
      // Carregar opções de filtros primeiro
      await this.loadFilterOptions()
      
      if (this.project.canDefineCategory) {
        this.items = await this.$repositories.metrics.fetchCategoryPercentage(this.projectId)
        
        try {
          const categoryTypes = await this.$services.categoryType.list(this.projectId)
          this.categoryMap = {};
          
          categoryTypes.forEach(category => {
            this.categoryMap[category.id] = category.text;
          });
          
          console.log('CategoryMap criado:', this.categoryMap)
          console.log('CategoryTypes recebidos:', categoryTypes)
        } catch (error) {
          console.error('Error loading category types:', error)
        }
      }
      if (this.project.canDefineSpan) {
        this.items = await this.$repositories.metrics.fetchSpanPercentage(this.projectId)
      }
      if (this.project.canDefineRelation) {
        this.items = await this.$repositories.metrics.fetchRelationPercentage(this.projectId)
      }
      
      console.log('Items carregados:', this.items)
      
      try {
        const stats = await this.$repositories.metrics.fetchDisagreementStats(this.projectId)
        console.log('Stats carregadas:', stats)
        
        this.textTypes = stats.textTypes || []
        if (this.textTypes.length === 0 || !this.textTypes.includes('Not defined')) {
          this.textTypes.push('Not defined')
        }
        
        this.perspectives = (stats.perspectives || []).filter(p => p !== 'Not defined')
        
        // Carregar anotadores reais do projeto
        await this.loadProjectAnnotators()
        
        // Carregar anotadores por example
        await this.loadExampleAnnotators()
        
        // Labels serão extraídas após carregar os examples
      } catch (error) {
        console.error('Error loading stats:', error)
        this.perspectives = []
      }
    } catch (error) {
      console.error('Error loading disagreements:', error)
      
      if (this.$toast) {
        this.$toast.error('Error loading disagreement data')
      } else {
        console.error('Error loading disagreement data')
      }
    } finally {
      this.loading = false
    }
  },

  computed: {
    ...mapGetters('projects', ['project']),
    safeProject() {
      return this.project || { minPercentage: 80 }
    },
    projectId() {
      return this.$route.params.id
    },
    hasDiscrepancies() {
      return true;
    },
    totalDiscrepancies() {
      return this.discrepancyItems.filter(item => 
        item.consensus === 'No'
      ).length
    },

    discrepancyItems() {
      if (!this.items || Object.keys(this.items).length === 0) {
        return []
      }
      
      const items = []
      
      // Processar os dados reais dos items (metrics)
      Object.entries(this.items).forEach(([exampleId, labelPercentages]) => {
        // Aguardar o nome do example ser carregado
        if (!this.exampleNameMap[exampleId]) {
          return
        }
        
        const exampleText = this.exampleNameMap[exampleId]
        
        // Extrair labels (categorias) e seus percentuais - APENAS as que foram realmente anotadas (> 0%)
        const labelEntries = Object.entries(labelPercentages)
          .filter(([, percentage]) => percentage > 0) // FILTRAR apenas labels com anotações
        
        if (labelEntries.length === 0) return
        

        
        // Calcular agreement rate máximo
        const maxAgreementRate = Math.max(...labelEntries.map(([, percentage]) => percentage))
        
        // Extrair nomes das labels usando categoryMap - apenas as que foram realmente anotadas
        const usedLabelNames = labelEntries
          .map(([labelId]) => this.categoryMap[labelId] || `Label ${labelId}`)
          .filter(name => name) // Remove valores vazios
        
        // Buscar anotadores reais que anotaram este example específico
        const annotatorNames = this.exampleAnnotators[exampleId] || ['No annotators']
          
          items.push({
          exampleId,
          text: exampleText,
          labels: usedLabelNames.join(', '), // Apenas labels usadas neste texto
          annotators: annotatorNames.join(', '),
          agreementRate: maxAgreementRate,
          consensus: maxAgreementRate >= this.safeProject.minPercentage ? 'Yes' : 'No',
          details: labelPercentages
        })
      })
      
      return items
    },
    filteredDiscrepancyItems() {
      if (!this.reportData || this.reportData.length === 0) {
        return []
      }

      let filtered = [...this.reportData]
      
      // Corrigir nomes duplicados (ex: "a1 a1" -> "a1")
      filtered = filtered.map(annotator => ({
        ...annotator,
        nome_anotador: this.cleanDuplicatedName(annotator.nome_anotador)
      }))

      // Aplicar filtro por usuários/anotadores
      if (this.filters.users.length > 0) {
        filtered = filtered.filter(annotator => {
          // Verificar se o ID do usuário está nos filtros selecionados
          return this.filters.users.some(userId => {
            // Encontrar o usuário correspondente
            const user = this.availableUsers.find(u => u.id === userId)
            if (user) {
              // Comparar username do filtro com nome do anotador
              return annotator.nome_anotador === user.username
            }
            return false
          })
        })
      }

      // Aplicar filtro por labels/categorias
      if (this.filters.labels.length > 0) {
        filtered = filtered.filter(annotator => {
          if (!annotator.categorias_mais_frequentes || annotator.categorias_mais_frequentes.length === 0) {
            return false
          }
          
          // Verificar se alguma das categorias do anotador está nos filtros
          return this.filters.labels.some(labelId => {
            const label = this.availableLabels.find(l => l.id === labelId)
            if (label) {
              return annotator.categorias_mais_frequentes.includes(label.text)
            }
            return false
          })
        })
      }

             // Aplicar filtro por datasets
       if (this.filters.datasets.length > 0) {
         // Para datasets, como não temos informação específica sobre quais datasets
         // cada anotador trabalhou, vamos manter todos os anotadores que têm anotações
         // Este filtro pode ser refinado quando o backend fornecer mais detalhes
         filtered = filtered.filter(annotator => {
           return annotator.datasets_distintos > 0
         })
       }

      // Aplicar filtro por perspectivas
      if (this.filters.perspectives.length > 0) {
        // Para perspectivas, como não temos essa informação no relatório atual,
        // vamos manter todos os dados (pode ser implementado futuramente)
        // filtered = filtered (sem alteração)
      }

      // Aplicar filtro por datas
      if (this.filters.date_from || this.filters.date_to) {
        filtered = filtered.filter(annotator => {
          const primeiraAnotacao = new Date(annotator.primeira_anotacao)
          const ultimaAnotacao = new Date(annotator.ultima_anotacao)
          
          let passaFiltroData = true
          
          if (this.filters.date_from) {
            const dataInicial = new Date(this.filters.date_from)
            passaFiltroData = passaFiltroData && (primeiraAnotacao >= dataInicial || ultimaAnotacao >= dataInicial)
          }
          
          if (this.filters.date_to) {
            const dataFinal = new Date(this.filters.date_to)
            dataFinal.setHours(23, 59, 59, 999) // Incluir o dia todo
            passaFiltroData = passaFiltroData && (primeiraAnotacao <= dataFinal || ultimaAnotacao <= dataFinal)
          }
          
          return passaFiltroData
        })
      }

      console.log('[FILTER DEBUG] Dados originais:', this.reportData.length)
      console.log('[FILTER DEBUG] Dados filtrados:', filtered.length)
      console.log('[FILTER DEBUG] Filtros aplicados:', {
        users: this.filters.users.length,
        labels: this.filters.labels.length,
        datasets: this.filters.datasets.length,
        perspectives: this.filters.perspectives.length,
        date_from: this.filters.date_from,
        date_to: this.filters.date_to
      })
      
      return filtered
    },
    
    filteredSelectedItem() {
      if (!this.selectedItem) return {}
      
      // Remover categoria e tipo de texto dos detalhes
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { category, textType, ...filteredItem } = this.selectedItem
      return filteredItem
    },
    hasActiveFilters() {
      return (
        this.filters.users.length > 0 ||
        this.filters.labels.length > 0 ||
        this.filters.datasets.length > 0 ||
        this.filters.perspectives.length > 0 ||
        this.filters.export_formats.length > 0 ||
        this.filters.date_from ||
        this.filters.date_to
      )
    },
    activeFiltersCount() {
      let count = 0
      if (this.filters.users.length > 0) count += this.filters.users.length
      if (this.filters.labels.length > 0) count += this.filters.labels.length
      if (this.filters.datasets.length > 0) count += this.filters.datasets.length
      if (this.filters.perspectives.length > 0) count += this.filters.perspectives.length
      if (this.filters.export_formats.length > 0) count += this.filters.export_formats.length
      if (this.filters.date_from) count++
      if (this.filters.date_to) count++
      return count
    }
  },

  watch: {
    items: {
      immediate: true,
      async handler(newItems) {
        if (newItems && Object.keys(newItems).length > 0) {
          // Carregar nomes dos examples
          for (const exampleId of Object.keys(newItems)) {
            await this.resolveExampleName(exampleId)
          }
          
          // Após carregar os examples, extrair labels e anotadores únicos
          this.extractUniqueLabelsAndAnnotators()
        }
      }
    },

    // Watchers para atualização em tempo real da tabela
    'filters.users': {
      handler() {
        this.updateReportInRealTime()
      },
      deep: true
    },

    'filters.labels': {
      handler() {
        this.updateReportInRealTime()
      },
      deep: true
    },

    'filters.datasets': {
      handler() {
        this.updateReportInRealTime()
      },
      deep: true
    },

    'filters.perspectives': {
      handler() {
        this.updateReportInRealTime()
      },
      deep: true
    },

    'filters.date_from': {
      handler() {
        this.updateReportInRealTime()
      }
    },

    'filters.date_to': {
      handler() {
        this.updateReportInRealTime()
      }
    }
  },

  async mounted() {
    // Iniciar verificação de conectividade quando o componente for montado
    this.startDatabaseConnectionCheck()
    
    // Carregar dados iniciais do relatório
    try {
      await this.loadAllReportData()
    } catch (error) {
      console.error('Error loading initial data:', error)
    }
  },
  
  beforeDestroy() {
    // Parar verificação quando o componente for destruído
    this.stopDatabaseConnectionCheck()
    
    // Limpar timeout de atualização
    if (this.updateTimeout) {
      clearTimeout(this.updateTimeout)
    }
  },

  methods: {
    // Método para atualizar a tabela em tempo real
    updateReportInRealTime() {
      // Debounce para evitar muitas chamadas seguidas
      if (this.updateTimeout) {
        clearTimeout(this.updateTimeout)
      }

      this.updateTimeout = setTimeout(async () => {
        console.log('[REAL-TIME] Filtros alterados:', this.filters)
        
        // Se não há dados carregados ainda, carregar todos os dados primeiro
        if (!this.reportData || this.reportData.length === 0) {
          try {
            this.isGenerating = true
            await this.loadAllReportData()
          } catch (error) {
            console.error('[REAL-TIME] Error loading data:', error)
          } finally {
            this.isGenerating = false
          }
        }
        
        // Os filtros serão aplicados automaticamente pelo computed filteredDiscrepancyItems
        console.log('[REAL-TIME] Filtros aplicados automaticamente via computed')
      }, 300) // Reduzido para 300ms para resposta mais rápida
    },

    // Método para limpar nomes duplicados
    cleanDuplicatedName(name) {
      if (!name || typeof name !== 'string') {
        return name
      }
      
      // Dividir por espaços e verificar se há duplicação
      const parts = name.trim().split(' ')
      
      // Se há apenas uma parte, retornar como está
      if (parts.length <= 1) {
        return name
      }
      
      // Se todas as partes são iguais, retornar apenas uma
      if (parts.every(part => part === parts[0])) {
        return parts[0]
      }
      
      // Se há duplicação consecutiva (ex: "a1 a1"), remover duplicatas
      const cleaned = []
      for (let i = 0; i < parts.length; i++) {
        if (i === 0 || parts[i] !== parts[i - 1]) {
          cleaned.push(parts[i])
        }
      }
      
      return cleaned.join(' ')
    },

    // Método para carregar todos os dados sem filtros
    async loadAllReportData() {
      try {
        console.log('[LOAD ALL] Carregando todos os dados do relatório...')
        
        // Fazer chamada para a API sem filtros para obter todos os dados
        const response = await this.$axios.get(`/v1/projects/${this.projectId}/reports/annotators`)
        console.log('[LOAD ALL] Resposta da API:', response)

        if (response.data && response.data.detalhe_anotadores) {
          this.reportData = response.data.detalhe_anotadores
          console.log('[LOAD ALL] Dados carregados:', this.reportData.length, 'anotadores')
        } else {
          console.warn('[LOAD ALL] Estrutura de resposta inesperada:', response.data)
          this.reportData = []
        }
      } catch (error) {
        console.error('[LOAD ALL] Erro ao carregar dados:', error)
        this.reportData = []
        throw error
      }
    },

    async loadFilterOptions() {
      try {
        // Carregar utilizadores do projeto
        this.loadingUsers = true
        const members = await this.$repositories.member.list(this.projectId)
        this.availableUsers = members.map((member) => ({
          id: member.user,
          username: member.username
        }))
        this.loadingUsers = false

        // Carregar projeto atual para verificar tipos disponíveis
        const currentProject = await this.$repositories.project.findById(this.projectId)

        // Carregar labels disponíveis baseado no tipo de projeto
        this.loadingLabels = true
        if (currentProject.canDefineCategory) {
          const categoryTypes = await this.$services.categoryType.list(this.projectId)
          this.availableLabels.push(
            ...categoryTypes.map((label) => ({
              id: label.id,
              text: label.text,
              type: 'category'
            }))
          )
        }

        if (currentProject.canDefineSpan) {
          const spanTypes = await this.$services.spanType.list(this.projectId)
          this.availableLabels.push(
            ...spanTypes.map((label) => ({
              id: label.id,
              text: label.text,
              type: 'span'
            }))
          )
        }

        if (currentProject.canDefineRelation) {
          const relationTypes = await this.$services.relationType.list(this.projectId)
          this.availableLabels.push(
            ...relationTypes.map((label) => ({
              id: label.id,
              text: label.text,
              type: 'relation'
            }))
          )
        }
        this.loadingLabels = false

        // Carregar perspectivas disponíveis
        this.loadingPerspectives = true
        try {
          const perspectives = await this.$repositories.perspective.list(this.projectId)
          console.log('Perspectivas carregadas:', perspectives)
          
          if (perspectives && Array.isArray(perspectives)) {
            this.availablePerspectives = perspectives.map(p => ({
              id: p.id,
              name: p.name || `Perspective ${p.id}`
            }))
          } else if (perspectives) {
            // Se retornou um único objeto, transformar em array
            this.availablePerspectives = [{
              id: perspectives.id,
              name: perspectives.name || `Perspective ${perspectives.id}`
            }]
          } else {
            this.availablePerspectives = []
          }
          
          console.log('availablePerspectives final:', this.availablePerspectives)
        } catch (error) {
          console.error('Erro ao carregar perspectivas:', error)
          this.availablePerspectives = []
        }
        this.loadingPerspectives = false

        // Carregar datasets disponíveis (filenames únicos)
        this.loadingDatasets = true
        try {
          const examples = await this.$repositories.example.list(this.projectId, {offset: '0', limit: '10000'})
          const datasetMap = new Map()

          examples.items.forEach((example) => {
            // Lógica robusta para obter o nome completo do dataset
            let datasetName = ''

            // 1. Priorizar uploadName (camelCase) com extensão
            if (example.uploadName && typeof example.uploadName === 'string' && example.uploadName.includes('.')) {
              datasetName = example.uploadName
            }
            // 2. Tentar upload_name (snake_case) com extensão
            else if (example.upload_name && typeof example.upload_name === 'string' && example.upload_name.includes('.')) {
              datasetName = example.upload_name
            }
            // 3. Filename com extensão
            else if (example.filename && typeof example.filename === 'string' && example.filename.includes('.')) {
              datasetName = example.filename
            }
            // 4. Fallback para uploadName sem extensão
            else if (example.uploadName && typeof example.uploadName === 'string') {
              datasetName = example.uploadName
            }
            // 5. Fallback para upload_name sem extensão
            else if (example.upload_name && typeof example.upload_name === 'string') {
              datasetName = example.upload_name
            }
            // 6. Último recurso: filename
            else if (example.filename && typeof example.filename === 'string') {
              datasetName = example.filename
            }

            if (datasetName && datasetName.trim()) {
              const trimmedName = datasetName.trim()
              if (datasetMap.has(trimmedName)) {
                datasetMap.set(trimmedName, datasetMap.get(trimmedName) + 1)
              } else {
                datasetMap.set(trimmedName, 1)
              }
            }
          })

          this.availableDatasets = Array.from(datasetMap.entries()).map(([name, count]) => ({
            name,
            count
          }))

          console.log('[DEBUG] Datasets finais:', this.availableDatasets)
        } catch (error) {
          console.error('Erro ao carregar datasets:', error)
        }
        this.loadingDatasets = false
      } catch (error) {
        console.error('Erro ao carregar opções de filtro:', error)
        this.showError('Erro ao carregar opções de filtro')
      }
    },

    async resolveExampleName(id) {
      if (!this.exampleNameMap[id]) {
        try {
          const example = await this.$repositories.example.findById(
            this.projectId, Number(id)
          )
          this.$set(this.exampleNameMap, id, example.text || 'Texto não disponível')
        } catch (error) {
          console.error('Erro ao buscar example:', id, error)
          this.$set(this.exampleNameMap, id, `Example ${id} - Erro ao carregar`)
        }
      }
      return this.exampleNameMap[id]
    },

    async loadProjectAnnotators() {
      try {
        const members = await this.$repositories.member.list(this.projectId)
        this.annotators = members.map((member) => member.username || `User ${member.user}`)
        console.log('Anotadores reais carregados:', this.annotators)
      } catch (error) {
        console.error('Erro ao carregar anotadores:', error)
        this.annotators = ['Unknown Annotator']
      }
    },

    async loadExampleAnnotators() {
      try {
        this.exampleAnnotators = await this.$repositories.metrics.fetchExampleAnnotators(this.projectId)
        console.log('Anotadores por example carregados:', this.exampleAnnotators)
      } catch (error) {
        console.error('Erro ao carregar anotadores por example:', error)
        this.exampleAnnotators = {}
      }
    },

    extractUniqueLabelsAndAnnotators() {
      // Extract unique labels from the processed data
      const uniqueLabels = new Set()
      
      this.discrepancyItems.forEach(item => {
        // Extract labels - apenas as que foram usadas neste texto
        item.labels.split(', ').forEach(label => {
          if (label.trim()) uniqueLabels.add(label.trim())
        })
      })
      
      this.labels = Array.from(uniqueLabels)
      
      console.log('Labels extraídas (apenas as usadas):', this.labels)
      console.log('Anotadores reais do projeto:', this.annotators)
    },

    getAgreementColor(agreementRate) {
      if (agreementRate < this.safeProject.minPercentage) return 'error'
      if (agreementRate < 80) return 'warning'
      return 'success'
    },

    showDetails(item) {
      this.selectedItem = item
      this.detailsDialog = true
    },
    formatKey(key) {
      const keyMap = {
        text: 'Dataset Text',
        labels: 'Annotated Labels',
        annotators: 'Annotators',
        agreementRate: 'Agreement Rate',
        consensus: 'Consensus',
        perspective: 'Perspective'
      }
      return keyMap[key] || key
    },
    async generateAndExportReport() {
      this.isGenerating = true
      try {
        // Primeiro gerar o relatório
        await this.generateReport()

        // Se há formatos de exportação selecionados e o relatório foi gerado com sucesso, exportar automaticamente
        if (this.filters.export_formats.length > 0 && this.reportData && this.reportData.length > 0) {
          await this.exportReport()
        }
      } catch (error) {
        console.error('Erro ao gerar e exportar relatório:', error)
        this.showError('Erro ao gerar e exportar relatório')
      } finally {
        this.isGenerating = false
      }
    },

    async generateReport() {
      try {
        // Preparar parâmetros de filtro com nomes corretos para a API
        const params = new URLSearchParams()

        // Usar os nomes corretos conforme o backend espera
        if (this.filters.users.length > 0) {
          params.append('annotator_id', this.filters.users.join(','))
        }

        if (this.filters.date_from) {
          params.append('data_inicial', this.filters.date_from)
        }

        if (this.filters.date_to) {
          params.append('data_final', this.filters.date_to)
        }

        if (this.filters.labels.length > 0) {
          params.append('categoria_label', this.filters.labels.join(','))
        }

        if (this.filters.perspectives.length > 0) {
          params.append('perspectiva_id', this.filters.perspectives.join(','))
        }

        if (this.filters.datasets.length > 0) {
          params.append('dataset_id', this.filters.datasets.join(','))
        }

        console.log('[FRONTEND DEBUG] Parâmetros enviados:', params.toString())
        console.log(
          '[FRONTEND DEBUG] URL completa:',
          `/v1/projects/${this.projectId}/reports/annotators?${params.toString()}`
        )

        // Fazer chamada para a API
        const response = await this.$axios.get(`/v1/projects/${this.projectId}/reports/annotators?${params.toString()}`)
        console.log('[FRONTEND DEBUG] Resposta da API:', response)
        console.log('[FRONTEND DEBUG] Status:', response.status)
        console.log('[FRONTEND DEBUG] Data:', response.data)

        if (response.data && response.data.detalhe_anotadores) {
          this.reportData = response.data.detalhe_anotadores
          console.log(
            '[FRONTEND DEBUG] Dados do relatório definidos:',
            this.reportData.length,
            'anotadores'
          )
        } else {
          console.warn('[FRONTEND DEBUG] Estrutura de resposta inesperada:', response.data)
          this.reportData = []
        }

        // Só mostrar mensagem de sucesso se não há exportação automática
        if (this.filters.export_formats.length === 0) {
          this.showSuccess(
            `Relatório gerado com sucesso! ${this.reportData.length} anotador(es) encontrado(s).`
          )
        }
      } catch (error) {
        console.error('[FRONTEND DEBUG] Erro completo:', error)
        console.error('[FRONTEND DEBUG] Erro response:', error.response)
        console.error('[FRONTEND DEBUG] Erro message:', error.message)

        let errorMessage = 'Erro ao gerar relatório'
        if (error.response) {
          console.error('[FRONTEND DEBUG] Status do erro:', error.response.status)
          console.error('[FRONTEND DEBUG] Data do erro:', error.response.data)

          if (error.response.data) {
            if (error.response.data.detail) {
              errorMessage = error.response.data.detail
            } else if (error.response.data.errors) {
              errorMessage = 'Parâmetros inválidos: ' + JSON.stringify(error.response.data.errors)
            }
          }
        } else if (error.request) {
          errorMessage = 'Erro de rede - servidor não respondeu'
          console.error('[FRONTEND DEBUG] Erro de request:', error.request)
        }

        throw new Error(errorMessage)
      }
    },

    async exportReport() {
      this.isExporting = true
      try {
        // Verificar se há dados para exportar
        if (!this.reportData || this.reportData.length === 0) {
          this.showError('Nenhum dado disponível para exportação. Gere o relatório primeiro.')
          return
        }

        // Usar os formatos selecionados nos filtros
        const exportFormats = this.filters.export_formats
        if (exportFormats.length === 0) {
          this.showError('Selecione pelo menos um formato de exportação.')
          return
        }

        console.log('[EXPORT DEBUG] Formatos selecionados:', exportFormats)
        console.log('[EXPORT DEBUG] Dados para exportar:', this.reportData.length, 'anotadores')

        const exportedFormats = []
        const failedFormats = []

        // Exportar para cada formato selecionado
        for (const format of exportFormats) {
          if (format === 'csv') {
            try {
              this.exportReportToCSV()
              exportedFormats.push('CSV')
            } catch (error) {
              console.error('Erro ao exportar CSV:', error)
              failedFormats.push('CSV')
            }
          } else if (format === 'pdf') {
            try {
              await this.exportReportToPDF()
              exportedFormats.push('PDF')
            } catch (error) {
              console.error('Erro ao exportar PDF:', error)
              failedFormats.push('PDF')
            }
          }
        }

        // Mostrar mensagens apropriadas
        if (exportedFormats.length > 0) {
          const message = `Relatório exportado com sucesso em: ${exportedFormats.join(', ')}`
          this.showSuccess(message)
        }

        if (failedFormats.length > 0) {
          const errorMessage = `Falha na exportação em: ${failedFormats.join(', ')}`
          this.showError(errorMessage)
        }

        if (exportedFormats.length === 0 && failedFormats.length === 0) {
          this.showError('Nenhum formato válido selecionado para exportação.')
        }
      } catch (error) {
        console.error('[EXPORT DEBUG] Erro ao exportar:', error)
        this.showError('Erro ao exportar relatório')
      } finally {
        this.isExporting = false
      }
    },

    exportReportToCSV() {
      // Criar cabeçalhos CSV
      const headers = [
        'Nome do Anotador',
        'Total de Anotações',
        'Datasets Distintos',
        'Tempo Total (min)',
        'Tempo Médio por Anotação (seg)',
        'Taxa de Desacordo (%)',
        'Score de Concordância',
        'Categorias Mais Frequentes',
        'Primeira Anotação',
        'Última Anotação'
      ]

      // Criar linhas CSV
      const rows = this.reportData.map(annotator => [
        annotator.nome_anotador,
        annotator.total_anotacoes,
        annotator.datasets_distintos,
        annotator.tempo_total_min.toFixed(2),
        annotator.tempo_medio_por_anotacao_seg.toFixed(2),
        annotator.taxa_desacordo_percent.toFixed(1),
        annotator.score_concordancia_medio.toFixed(2),
        annotator.categorias_mais_frequentes.join('; '),
        new Date(annotator.primeira_anotacao).toLocaleString('pt-BR'),
        new Date(annotator.ultima_anotacao).toLocaleString('pt-BR')
      ])

      // Combinar cabeçalhos e dados
      const csvContent = [headers, ...rows]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n')

      // Criar e baixar arquivo
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `relatorio_anotadores_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    },

    async exportReportToPDF() {
      try {
        // Load jsPDF dynamically
        const { jsPDF } = await import('jspdf')
        const { default: autoTable } = await import('jspdf-autotable')
        
        // eslint-disable-next-line new-cap
        const doc = new jsPDF()
        
        // Title
        doc.setFontSize(20)
        doc.text('Relatório de Anotadores', 14, 20)
        
        // Project information
        doc.setFontSize(12)
        doc.text(`Projeto: ${this.safeProject.name || 'Sem nome'}`, 14, 30)
        doc.text(`Total de anotadores: ${this.reportData.length}`, 14, 38)
        doc.text(`Data do relatório: ${new Date().toLocaleDateString('pt-BR')}`, 14, 46)
        
        // Prepare data for table
        const tableData = this.reportData.map(annotator => [
          annotator.nome_anotador,
          annotator.total_anotacoes.toString(),
          annotator.datasets_distintos.toString(),
          annotator.tempo_total_min.toFixed(2),
          annotator.tempo_medio_por_anotacao_seg.toFixed(2),
          annotator.taxa_desacordo_percent.toFixed(1) + '%',
          annotator.score_concordancia_medio.toFixed(2),
          annotator.categorias_mais_frequentes.slice(0, 3).join(', '), // Limit categories
          new Date(annotator.primeira_anotacao).toLocaleDateString('pt-BR'),
          new Date(annotator.ultima_anotacao).toLocaleDateString('pt-BR')
        ])
        
        // Create table
        autoTable(doc, {
          startY: 55,
          head: [[
            'Anotador',
            'Total Anotações',
            'Datasets',
            'Tempo Total (min)',
            'Tempo Médio (seg)',
            'Taxa Desacordo',
            'Score Concordância',
            'Categorias Principais',
            'Primeira Anotação',
            'Última Anotação'
          ]],
          body: tableData,
          styles: {
            fontSize: 8,
            cellPadding: 2
          },
          columnStyles: {
            0: { cellWidth: 20 }, // Anotador
            1: { cellWidth: 15 }, // Total Anotações
            2: { cellWidth: 12 }, // Datasets
            3: { cellWidth: 18 }, // Tempo Total
            4: { cellWidth: 18 }, // Tempo Médio
            5: { cellWidth: 18 }, // Taxa Desacordo
            6: { cellWidth: 18 }, // Score Concordância
            7: { cellWidth: 25 }, // Categorias
            8: { cellWidth: 20 }, // Primeira Anotação
            9: { cellWidth: 20 }  // Última Anotação
          },
          margin: { top: 55, left: 14, right: 14 }
        })
        
        // Generate filename
        const filename = `relatorio_anotadores_${new Date().toISOString().split('T')[0]}.pdf`
        
        // Save PDF
        const pdfOutput = doc.output('blob')
        
        // For old browsers like IE
        if (window.navigator && window.navigator.msSaveOrOpenBlob) {
          window.navigator.msSaveOrOpenBlob(pdfOutput, filename)
          return
        }
        
        // For modern browsers
        const url = URL.createObjectURL(pdfOutput)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        link.style.display = 'none'
        document.body.appendChild(link)
        link.click()
        
        // Clean up
        setTimeout(() => {
          URL.revokeObjectURL(url)
          document.body.removeChild(link)
        }, 100)
        
      } catch (error) {
        console.error('Erro ao gerar PDF:', error)
        throw new Error('Não foi possível gerar o PDF: ' + error.message)
      }
    },

    toggleDatabaseError() {
      this.showDatabaseError = !this.showDatabaseError
    },
    cancelReport() {
      this.$router.push(`/projects/${this.projectId}/reports`);
    },
    onReportTypeChange(value) {
      this.filters.export_formats = [value];
    },
    
    async checkDatabaseConnection() {
      try {
        // Tentar fazer uma chamada simples à API para verificar conectividade
        await this.$repositories.user.checkHealth()
        this.isDatabaseConnected = true
      } catch (error) {
        console.error('Database connectivity error:', error)
        this.isDatabaseConnected = false
      }
    },
    
    startDatabaseConnectionCheck() {
      // Check connectivity every 2 seconds
      this.databaseCheckInterval = setInterval(() => {
        this.checkDatabaseConnection()
      }, 2000)
    },
    
    stopDatabaseConnectionCheck() {
      if (this.databaseCheckInterval) {
        clearInterval(this.databaseCheckInterval)
        this.databaseCheckInterval = null
      }
    },
    
    dismissDatabaseError() {
      if (this.isDatabaseConnected) {
        this.showDatabaseError = false
      }
      // If no connection, don't allow closing the alert
     },
     
     async exportToPDF(filename) {
       try {
         // Load jsPDF dynamically (to not include in initial bundle)
         const { jsPDF } = await import('jspdf');
         const { default: autoTable } = await import('jspdf-autotable');
         
         // eslint-disable-next-line new-cap
         const doc = new jsPDF();
         
         // Title
         doc.setFontSize(20);
         doc.text('Annotations and Disagreements Report', 14, 20);
         
         // Project information
         doc.setFontSize(12);
         doc.text(`Project: ${this.safeProject.name || 'No name'}`, 14, 30);
         doc.text(`Agreement threshold: ${this.safeProject.minPercentage}%`, 14, 38);
         doc.text(`Total disagreements: ${this.totalDiscrepancies}`, 14, 46);
         doc.text(`Report date: ${new Date().toLocaleDateString()}`, 14, 54);
         
         // Disagreement details
         doc.setFontSize(16);
         doc.text('Disagreement Details', 14, 70);
         
         const detailsData = this.filteredDiscrepancyItems
           .filter(item => item.consensus === 'No')
           .map(item => [
             item.text.substring(0, 50) + (item.text.length > 50 ? '...' : ''), // Truncate text
             item.labels,
             item.annotators,
             `${item.agreementRate.toFixed(2)}%`,
             item.consensus
           ]);
         
                   autoTable(doc, {
            startY: 75,
            head: [['Text', 'Labels', 'Annotators', 'Agreement Rate', 'Consensus']],
            body: detailsData,
            columnStyles: {
              0: { cellWidth: 60 }, // Text column
              1: { cellWidth: 40 }, // Labels column
              2: { cellWidth: 40 }, // Annotators column
              3: { cellWidth: 30 }, // Agreement Rate column
              4: { cellWidth: 20 }  // Consensus column
            }
          });
         
         // Salvar o PDF usando output com método compatível com navegadores
         const pdfOutput = doc.output('blob');
         const url = URL.createObjectURL(pdfOutput);
         
         // For old browsers like IE
         if (window.navigator && window.navigator.msSaveOrOpenBlob) {
           window.navigator.msSaveOrOpenBlob(pdfOutput, `${filename}.pdf`);
           
           // Redirect after download
           setTimeout(() => {
             window.location.href = `/projects/${this.projectId}/reports`;
           }, 500);
           
           return;
         }
         
         // For modern browsers
         const link = document.createElement('a');
         link.href = url;
         link.download = `${filename}.pdf`;
         link.style.display = 'none';
         document.body.appendChild(link);
         link.click();
         
         // Clean URL after download and redirect
         setTimeout(() => {
           URL.revokeObjectURL(url);
           document.body.removeChild(link);
           
           // Redirect to reports page
           this.$router.push(`/projects/${this.projectId}/reports`);
         }, 500);
       } catch (error) {
         console.error('Error generating PDF:', error);
         throw new Error('Could not generate PDF. Please check that all required libraries are available.');
       }
     },
    removeUser(item) {
      this.filters.users = this.filters.users.filter(u => u.id !== item.id)
    },
    removeLabel(item) {
      this.filters.labels = this.filters.labels.filter(l => l.id !== item.id)
    },
    removeDataset(item) {
      this.filters.datasets = this.filters.datasets.filter(d => d.name !== item)
    },
    removePerspective(item) {
      // Se item é um objeto, usar item.id, senão usar item diretamente
      const perspectiveId = typeof item === 'object' ? item.id : item
      this.filters.perspectives = this.filters.perspectives.filter(p => p !== perspectiveId)
    },
    removeExportFormat(item) {
      this.filters.export_formats = this.filters.export_formats.filter(f => f !== item)
    },
         clearFilters() {
       this.filters = {
         users: [],
         labels: [],
         datasets: [],
         date_from: null,
         date_to: null,
         perspectives: [],
         export_formats: ['pdf']
       }
       this.reportData = []
     },

     getDatasetDisplayName(dataset) {
       if (typeof dataset === 'object') {
         // Se é um objeto, usar a propriedade name
         return dataset.name || dataset
       }
       // Se é uma string, retornar diretamente
       return dataset
     },

     showSuccess(message) {
       // Only log to console, no popup
       console.log('SUCCESS:', message)
     },

     showError(message) {
       // Only log to console, no popup
       console.error('ERROR:', message)
     },

      getSelectedUserText(user) {
        if (typeof user === 'object') {
          return user.username;
        } else if (typeof user === 'string') {
          return user;
        }
        return '';
      },

      getSelectedLabelText(label) {
        if (typeof label === 'object') {
          return label.text;
        } else if (typeof label === 'string') {
          return label;
        }
        return '';
      },

      getSelectedLabelType(label) {
        if (typeof label === 'object') {
          return label.type;
        } else if (typeof label === 'string') {
          return 'category'; // Assuming a default type if not provided
        }
        return '';
      },

      getSelectedPerspectiveText(perspective) {
        if (typeof perspective === 'object') {
          return perspective.name;
        } else if (typeof perspective === 'string') {
          return perspective;
        }
        return '';
      },

      getPerspectiveNameById(perspectiveId) {
        if (!perspectiveId) {
          return 'Unknown'
        }
        
        // Se perspectiveId é um objeto, extrair o ID
        let id = perspectiveId
        if (typeof perspectiveId === 'object') {
          id = perspectiveId.id
        }
        
        // Buscar a perspectiva pelo ID na lista de perspectivas disponíveis
        const perspective = this.availablePerspectives.find(p => p.id === id)
        if (perspective) {
          return perspective.name || `Perspective ${id}`
        }
        
        // Se não encontrar, retornar o ID como fallback
        return `Perspective ${id}`
      },

      getLabelTypeColor(type) {
        const colors = {
          category: 'blue',
          span: 'green',
          relation: 'orange'
        }
        return colors[type] || 'grey'
      },

      getExportFormatColor(format) {
        const colors = {
          csv: 'green',
          pdf: 'red'
        }
        return colors[format] || 'grey'
      },

      getScoreConcordanciaColor(score) {
        if (!score) return 'grey'
        const percentage = score * 100
        if (percentage >= 80) return 'success'
        if (percentage >= 70) return 'warning'
        return 'error'
      }
   }
 }
</script>

<style scoped>
.container {
  max-width: 1200px;
}
.h-100 {
  height: 100%;
}
.chart {
  width: 100%;
  height: 550px !important;
}
.chart-wrapper {
  width: 100%;
  position: relative;
  margin: 20px 0 40px 0;
}
.debug-button {
  opacity: 1;
  transition: opacity 0.3s;
  position: fixed;
  z-index: 999;
  top: 10px;
  right: 10px;
}
.debug-button:hover {
  opacity: 1;
}
.clickable-select {
  cursor: pointer;
}

.v-chip {
  margin: 2px;
}

.v-card-title.primary {
  background: linear-gradient(45deg, #1976d2, #42a5f5);
}

.v-data-table >>> .v-data-table__wrapper {
  border-radius: 8px;
}

.v-card {
  border-radius: 12px;
}

.text-caption {
  font-size: 0.75rem !important;
}
</style> 