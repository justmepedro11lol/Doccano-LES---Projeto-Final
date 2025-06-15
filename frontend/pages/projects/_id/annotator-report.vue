<template>
  <v-container fluid class="pa-0">
    <!-- Header Section -->
    <div class="hero-section">
      <v-container>
        <v-row align="center" class="py-4">
          <v-col cols="12" class="text-center">
            <v-icon size="48" color="white" class="mb-2">mdi-account-group</v-icon>
            <h1 class="display-1 font-weight-bold white--text mb-2">
              Relatórios de Anotadores
            </h1>
            <p class="subtitle-1 white--text">
              Análise detalhada do desempenho e produtividade dos anotadores
            </p>
          </v-col>
        </v-row>
      </v-container>
    </div>

    <!-- Main Content -->
    <v-container fluid class="py-4">

      <!-- Filtros Avançados -->
      <v-card class="mb-4">
        <v-card-title>
          <v-icon class="mr-2">mdi-filter</v-icon>
          Filtros Avançados
          <v-spacer />
          <v-chip v-if="hasActiveFilters" small color="primary" outlined>
            {{ activeFiltersCount }} filtro{{ activeFiltersCount > 1 ? 's' : '' }} ativo{{ activeFiltersCount > 1 ? 's' : '' }}
          </v-chip>
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.annotator_id"
                :items="annotatorOptions"
                label="Filtrar por Anotador"
                multiple
                chips
                deletable-chips
                clearable
                outlined
                dense
                prepend-inner-icon="mdi-account"
                @change="onAnnotatorFilterChange"
                @input="onAnnotatorFilterInput"
                :key="'annotator-select-' + annotatorOptions.length"
              >
                <template #selection="{ item, index }">
                  <v-chip
                    v-if="index < 2"
                    small
                    close
                    @click:close="removeAnnotatorFilter(item.value)"
                  >
                    {{ item.text }}
                  </v-chip>
                  <span v-if="index === 2" class="grey--text text-caption">
                    (+{{ filters.annotator_id.length - 2 }} mais)
                  </span>
                </template>
              </v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.dataset_id"
                :items="datasetOptions"
                label="Filtrar por Dataset"
                multiple
                chips
                deletable-chips
                clearable
                outlined
                dense
                prepend-inner-icon="mdi-database"
              >
                <template #selection="{ item, index }">
                  <v-chip
                    v-if="index < 2"
                    small
                    close
                    @click:close="removeDatasetFilter(item.value)"
                  >
                    {{ item.text }}
                  </v-chip>
                  <span v-if="index === 2" class="grey--text text-caption">
                    (+{{ filters.dataset_id.length - 2 }} mais)
                  </span>
                </template>
              </v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.categoria_label"
                :items="categoryOptions"
                label="Filtrar por Categoria"
                multiple
                chips
                deletable-chips
                clearable
                outlined
                dense
                prepend-inner-icon="mdi-tag"
              >
                <template #selection="{ item, index }">
                  <v-chip
                    v-if="index < 2"
                    small
                    close
                    @click:close="removeCategoryFilter(item.value)"
                  >
                    {{ item.text }}
                  </v-chip>
                  <span v-if="index === 2" class="grey--text text-caption">
                    (+{{ filters.categoria_label.length - 2 }} mais)
                  </span>
                </template>
              </v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.estado_desacordo"
                :items="disagreementStates"
                label="Estado de Desacordo"
                clearable
                outlined
                dense
                prepend-inner-icon="mdi-alert-circle"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" md="3">
              <v-menu
                v-model="startDateMenu"
                :close-on-content-click="false"
                :nudge-right="40"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template #activator="{ on, attrs }">
                  <v-text-field
                    v-model="filters.data_inicial"
                    label="Data Inicial"
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
                  v-model="filters.data_inicial"
                  @input="startDateMenu = false"
                />
              </v-menu>
            </v-col>
            <v-col cols="12" md="3">
              <v-menu
                v-model="endDateMenu"
                :close-on-content-click="false"
                :nudge-right="40"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template #activator="{ on, attrs }">
                  <v-text-field
                    v-model="filters.data_final"
                    label="Data Final"
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
                  v-model="filters.data_final"
                  @input="endDateMenu = false"
                />
              </v-menu>
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="searchQuery"
                label="Pesquisar"
                prepend-inner-icon="mdi-magnify"
                outlined
                dense
                clearable
                hide-details
              />
            </v-col>
            <v-col cols="12" md="3" class="d-flex align-center">
              <v-btn
                color="success"
                class="mr-2"
                @click="forceApplyFilters"
              >
                <v-icon left>mdi-filter-check</v-icon>
                Aplicar Filtros
              </v-btn>
              <v-btn
                color="primary"
                outlined
                @click="resetFilters"
              >
                <v-icon left>mdi-refresh</v-icon>
                Limpar Filtros
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- DEBUG CARD - REMOVER DEPOIS DE FUNCIONAR -->
      <v-card v-if="true" class="mb-4" color="orange lighten-5">
        <v-card-title class="orange--text">
          🔧 DEBUG - Estado dos Filtros
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <strong>Filtros Atuais:</strong>
              <pre>{{ JSON.stringify(filters, null, 2) }}</pre>
            </v-col>
            <v-col cols="12" md="6">
              <strong>Anotadores Disponíveis:</strong>
              <pre>{{ JSON.stringify(annotators, null, 2) }}</pre>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <strong>Opções do Select:</strong>
              <pre>{{ JSON.stringify(annotatorOptions, null, 2) }}</pre>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-btn color="warning" @click="debugFilters">
                <v-icon left>mdi-bug</v-icon>
                Debug Completo
              </v-btn>
              <v-btn color="success" class="ml-2" @click="testFilter">
                <v-icon left>mdi-test-tube</v-icon>
                Testar Filtro
              </v-btn>
              <v-btn color="primary" class="ml-2" @click="forceApplyFilters">
                <v-icon left>mdi-refresh</v-icon>
                Forçar Aplicar
              </v-btn>
              <v-btn color="orange" class="ml-2" @click="resetAnnotatorFilters">
                <v-icon left>mdi-restart</v-icon>
                Reset Anotadores
              </v-btn>
              <v-btn color="info" class="ml-2" @click="cleanAnnotatorFilters">
                <v-icon left>mdi-broom</v-icon>
                Limpar Inválidos
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Results Summary -->
      <v-card v-if="reportData" class="mb-4">
        <v-card-title>
          <v-icon class="mr-2">mdi-chart-line</v-icon>
          Resumo Global
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="3">
              <v-card color="primary" dark>
                <v-card-text>
                  <div class="d-flex align-center">
                    <v-icon size="40" class="mr-3">mdi-account-group</v-icon>
                    <div>
                      <div class="text-h4 font-weight-bold">{{ reportData.resumo_global.total_anotadores }}</div>
                      <div class="text-subtitle-2">Total de Anotadores</div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card color="success" dark>
                <v-card-text>
                  <div class="d-flex align-center">
                    <v-icon size="40" class="mr-3">mdi-tag-multiple</v-icon>
                    <div>
                      <div class="text-h4 font-weight-bold">{{ reportData.resumo_global.total_anotacoes }}</div>
                      <div class="text-subtitle-2">Total de Anotações</div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card color="warning" dark>
                <v-card-text>
                  <div class="d-flex align-center">
                    <v-icon size="40" class="mr-3">mdi-alert-circle</v-icon>
                    <div>
                      <div class="text-h4 font-weight-bold">{{ reportData.resumo_global.taxa_desacordo_global_percent }}%</div>
                      <div class="text-subtitle-2">Taxa de Desacordo Global</div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card color="info" dark>
                <v-card-text>
                  <div class="d-flex align-center">
                    <v-icon size="40" class="mr-3">mdi-check-circle</v-icon>
                    <div>
                      <div class="text-h4 font-weight-bold">{{ reportData.resumo_global.score_concordancia_global || 0 }}%</div>
                      <div class="text-subtitle-2">Média de Concordância</div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Results Table -->
      <v-card v-if="reportData">
        <v-card-title class="pb-2">
          <v-icon class="mr-2">mdi-table</v-icon>
          Detalhes dos Anotadores
          <v-spacer />
          
          <!-- Export Buttons -->
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn
                :loading="exporting"
                color="success"
                outlined
                small
                class="mr-2"
                v-bind="attrs"
                v-on="on"
                @click="exportReport('csv')"
              >
                <v-icon left small>mdi-download</v-icon>
                <v-icon left small>mdi-file-excel</v-icon>
                Exportar CSV
              </v-btn>
            </template>
            <span>Exportar relatório em formato CSV (Excel)</span>
          </v-tooltip>
          
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn
                :loading="exporting"
                color="error"
                outlined
                small
                v-bind="attrs"
                v-on="on"
                @click="exportReport('pdf')"
              >
                <v-icon left small>mdi-download</v-icon>
                <v-icon left small>mdi-file-pdf</v-icon>
                Exportar PDF
              </v-btn>
            </template>
            <span>Exportar relatório em formato PDF</span>
          </v-tooltip>
        </v-card-title>
        
        <v-data-table
          :headers="tableHeaders"
          :items="reportData.detalhe_anotadores"
          :options.sync="tableOptions"
          :server-items-length="reportData.pagination?.total || reportData.detalhe_anotadores.length"
          :loading="loading"
          class="elevation-0"
          @update:options="updateTableOptions"
        >
          <!-- Custom columns -->
          <template #[`item.nome_anotador`]="{ item }">
            <div class="d-flex align-center">
              <v-avatar size="32" class="mr-2">
                <v-icon>mdi-account</v-icon>
              </v-avatar>
              <div>
                <div class="font-weight-medium">{{ item.nome_anotador }}</div>
                <div class="text-caption text--secondary">ID: {{ item.annotator_id }}</div>
              </div>
            </div>
          </template>

          <template #[`item.total_anotacoes`]="{ item }">
            <v-chip
              :color="getAnnotationCountColor(item.total_anotacoes)"
              dark
              small
            >
              {{ item.total_anotacoes }}
            </v-chip>
          </template>

          <template #[`item.taxa_desacordo_percent`]="{ item }">
            <v-progress-linear
              :value="item.taxa_desacordo_percent"
              :color="getDisagreementColor(item.taxa_desacordo_percent)"
              height="20"
              rounded
            >
              <strong>{{ item.taxa_desacordo_percent }}%</strong>
            </v-progress-linear>
          </template>

          <template #[`item.score_concordancia_medio`]="{ item }">
            <v-rating
              :value="item.score_concordancia_medio"
              readonly
              dense
              half-increments
              color="yellow darken-2"
              background-color="grey lighten-1"
              small
            />
            <span class="text-caption ml-2">{{ (item.score_concordancia_medio * 100).toFixed(1) }}%</span>
          </template>

          <template #[`item.tempo_total_min`]="{ item }">
            {{ formatTime(item.tempo_total_min) }}
          </template>

          <template #[`item.tempo_medio_por_anotacao_seg`]="{ item }">
            {{ formatDuration(item.tempo_medio_por_anotacao_seg) }}
          </template>

          <template #[`item.categorias_mais_frequentes`]="{ item }">
            <div class="d-flex flex-wrap">
              <v-chip
                v-for="category in item.categorias_mais_frequentes.slice(0, 3)"
                :key="category"
                x-small
                class="ma-1"
                outlined
              >
                {{ category }}
              </v-chip>
              <v-chip
                v-if="item.categorias_mais_frequentes.length > 3"
                x-small
                class="ma-1"
                outlined
              >
                +{{ item.categorias_mais_frequentes.length - 3 }}
              </v-chip>
            </div>
          </template>

          <template #[`item.primeira_anotacao`]="{ item }">
            {{ formatDate(item.primeira_anotacao) }}
          </template>

          <template #[`item.ultima_anotacao`]="{ item }">
            {{ formatDate(item.ultima_anotacao) }}
          </template>

          <template #[`item.actions`]="{ item }">
            <v-btn
              icon
              small
              @click="viewAnnotatorDetails(item)"
            >
              <v-icon>mdi-eye</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card>

      <!-- No Data State -->
      <v-card v-else-if="!loading && !reportData">
        <v-card-text class="text-center py-8">
          <v-icon size="64" color="grey lighten-1">mdi-chart-line</v-icon>
          <h3 class="text-h6 grey--text mt-4">Nenhum dado encontrado</h3>
          <p class="grey--text">Aplique filtros para visualizar o relatório de anotadores</p>
          <v-btn color="primary" class="mr-2" @click="loadInitialData">
            <v-icon left>mdi-refresh</v-icon>
            Carregar Dados
          </v-btn>
          <v-btn color="secondary" @click="manualApplyFilters">
            <v-icon left>mdi-filter</v-icon>
            Aplicar Filtros
          </v-btn>
        </v-card-text>
      </v-card>

      <!-- Loading State -->
      <v-card v-else-if="loading">
        <v-card-text class="text-center py-8">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
            class="mb-4"
          />
          <h3 class="text-h6">Carregando relatório...</h3>
        </v-card-text>
      </v-card>
    </v-container>

    <!-- Annotator Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="800">
      <v-card v-if="selectedAnnotator">
        <v-card-title>
          <v-icon class="mr-2">mdi-account-circle</v-icon>
          Detalhes do Anotador
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Nome</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedAnnotator.nome_anotador }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
            <v-col cols="12" md="6">
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Total de Anotações</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedAnnotator.total_anotacoes }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
            <!-- More details can be added here -->
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="detailsDialog = false">Fechar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  layout: 'project',
  
  data() {
    return {
      loading: false,
      exporting: false,
      reportData: null,
      detailsDialog: false,
      selectedAnnotator: null,
      filterTimeout: null,
      searchQuery: '',
      startDateMenu: false,
      endDateMenu: false,
      
      // Filters
      filters: {
        dataset_id: [],
        annotator_id: [],
        data_inicial: null,
        data_final: null,
        categoria_label: [],
        perspectiva_id: [],
        estado_desacordo: 'todos'
      },
      
      // Filter options
      datasets: [],
      annotators: [],
      perspectives: [],
      categories: [],
      disagreementStates: [
        { text: 'Todos', value: 'todos' },
        { text: 'Com Discrepâncias', value: 'com_discrepancias' },
        { text: 'Sem Discrepâncias', value: 'sem_discrepancias' },
        { text: 'Em Desacordo', value: 'em_desacordo' },
        { text: 'Resolvido', value: 'resolvido' }
      ],
      
      // Table configuration
      tableOptions: {
        page: 1,
        itemsPerPage: 10,
        sortBy: ['total_anotacoes'],
        sortDesc: [true]
      },
      
      tableHeaders: [
        {
          text: 'Anotador',
          value: 'nome_anotador',
          sortable: true,
          width: '200px'
        },
        {
          text: 'Total Anotações',
          value: 'total_anotacoes',
          sortable: true,
          align: 'center'
        },
        {
          text: 'Datasets',
          value: 'datasets_distintos',
          sortable: true,
          align: 'center'
        },
        {
          text: 'Tempo Total',
          value: 'tempo_total_min',
          sortable: true,
          align: 'center'
        },
        {
          text: 'Tempo/Anotação',
          value: 'tempo_medio_por_anotacao_seg',
          sortable: true,
          align: 'center'
        },
        {
          text: 'Taxa Desacordo',
          value: 'taxa_desacordo_percent',
          sortable: true,
          align: 'center'
        },
        {
          text: 'Concordância',
          value: 'score_concordancia_medio',
          sortable: true,
          align: 'center'
        },
        {
          text: 'Categorias Frequentes',
          value: 'categorias_mais_frequentes',
          sortable: false,
          width: '200px'
        },
        {
          text: 'Primeira Anotação',
          value: 'primeira_anotacao',
          sortable: true,
          align: 'center'
        },
        {
          text: 'Última Anotação',
          value: 'ultima_anotacao',
          sortable: true,
          align: 'center'
        },
        {
          text: 'Ações',
          value: 'actions',
          sortable: false,
          align: 'center'
        }
      ]
    }
  },

  async fetch() {
    console.log('🔄 Fetch iniciado - carregando dados do relatório...')
    this.loading = true
    
    try {
      await this.loadData()
    } catch (error) {
      console.error('❌ Erro no fetch:', error)
      this.loadMinimalData()
    } finally {
      this.loading = false
    }
  },
  
  computed: {
    ...mapGetters('projects', ['project']),
    
    safeProject() {
      return this.project || { name: 'Projeto Sem Nome', minPercentage: 80 }
    },
    
    // Computed properties para filtros
    hasActiveFilters() {
      return !!(
        this.filters.annotator_id.length > 0 ||
        this.filters.dataset_id.length > 0 ||
        this.filters.categoria_label.length > 0 ||
        this.filters.perspectiva_id.length > 0 ||
        (this.filters.estado_desacordo && this.filters.estado_desacordo !== 'todos') ||
        this.filters.data_inicial ||
        this.filters.data_final ||
        this.searchQuery
      )
    },
    
    activeFiltersCount() {
      let count = 0
      if (this.filters.annotator_id.length > 0) count++
      if (this.filters.dataset_id.length > 0) count++
      if (this.filters.categoria_label.length > 0) count++
      if (this.filters.perspectiva_id.length > 0) count++
      if (this.filters.estado_desacordo && this.filters.estado_desacordo !== 'todos') count++
      if (this.filters.data_inicial) count++
      if (this.filters.data_final) count++
      if (this.searchQuery) count++
      return count
    },
    
    annotatorOptions() {
      console.log('🔧 GERANDO ANNOTATOR OPTIONS:')
      console.log('- Anotadores raw:', this.annotators)
      
      // CORREÇÃO CRÍTICA: Filtrar anotadores válidos e evitar duplicatas
      const validAnnotators = this.annotators.filter(annotator => {
        // Remover anotadores sem ID ou nome válido
        const hasId = annotator.id !== null && annotator.id !== undefined && annotator.id !== ''
        const hasName = annotator.name !== null && annotator.name !== undefined && annotator.name !== ''
        const isNotUndefined = annotator.name !== 'Usuário undefined' && !annotator.name?.includes('undefined')
        
        console.log(`🔧 Validando anotador:`, annotator, `ID válido: ${hasId}, Nome válido: ${hasName}, Não undefined: ${isNotUndefined}`)
        
        return hasId && hasName && isNotUndefined
      })
      
      // Remover duplicatas por ID
      const uniqueAnnotators = validAnnotators.filter((annotator, index, self) => 
        index === self.findIndex(a => a.id === annotator.id)
      )
      
      const options = [
        { text: 'Todos os Anotadores', value: null },
        ...uniqueAnnotators.map(annotator => {
          const option = {
            text: annotator.name,
            value: annotator.id
          }
          console.log(`🔧 Opção criada:`, option)
          return option
        })
      ]
      
      console.log('🔧 OPTIONS FINAIS:', options)
      return options
    },
    
    datasetOptions() {
      return [
        { text: 'Todos os Datasets', value: null },
        ...this.datasets.map(dataset => ({
          text: dataset.name || dataset,
          value: dataset.id || dataset
        }))
      ]
    },
    
    categoryOptions() {
      return [
        { text: 'Todas as Categorias', value: null },
        ...this.categories.map(category => ({
          text: category.name || category,
          value: category.id || category
        }))
      ]
    },
    
    projectId() {
      const id = this.$route.params.id
      console.log('🆔 Project ID from route:', id)
      
      if (!id) {
        console.error('❌ Project ID não encontrado na rota!')
        // Verificar se $toast existe antes de usar
        if (this.$toast && this.$toast.error) {
          this.$toast.error('Erro: ID do projeto não encontrado')
        }
        return null
      }
      
      return id
    }
  },

  watch: {
    // Observar mudanças nos filtros e aplicar automaticamente com debounce
    filters: {
      handler(newFilters, oldFilters) {
        console.log('🔄 FILTROS MUDARAM - WATCHER ATIVADO!')
        console.log('🔄 Novos filtros:', JSON.stringify(newFilters, null, 2))
        console.log('🔄 Filtros antigos:', JSON.stringify(oldFilters, null, 2))
        console.log('🔄 Específico annotator_id:', newFilters.annotator_id)
        
        // CORREÇÃO CRÍTICA: Limpar filtros inválidos antes de aplicar
        this.cleanAnnotatorFilters()
        
        // Debounce para evitar múltiplas chamadas
        if (this.filterTimeout) {
          clearTimeout(this.filterTimeout)
        }
        
        this.filterTimeout = setTimeout(() => {
          console.log('⏰ APLICANDO FILTROS APÓS DEBOUNCE!')
          console.log('⏰ Estado atual dos filtros:', this.filters)
          this.applyFilters()
        }, 300)
      },
      deep: true,
      immediate: false
    },
    
    // Observar mudanças na pesquisa
    searchQuery: {
      handler(newQuery) {
        console.log('🔍 Busca mudou:', newQuery)
        
        // Aplicar filtros com debounce menor para busca
        if (this.filterTimeout) {
          clearTimeout(this.filterTimeout)
        }
        
        this.filterTimeout = setTimeout(() => {
          console.log('⏰ Aplicando filtro de busca...')
          this.applyFilters()
        }, 400)
      }
    }
  },
  
  mounted() {
    try {
      console.log('🚀 Iniciando carregamento da página do relatório de anotadores')
      console.log('📍 Project ID:', this.projectId)
      console.log('📍 Route params:', this.$route.params)
      console.log('📍 Route path:', this.$route.path)
      
      // Verificar se temos um projectId válido
      if (!this.projectId) {
        console.error('❌ Project ID é necessário mas não foi encontrado')
        if (this.$toast && this.$toast.error) {
          this.$toast.error('Erro: ID do projeto não encontrado na URL')
        }
        this.loadMinimalData()
        return
      }
      
      // Carregar dados iniciais através do método fetch
      console.log('⚠️ Carregamento via computed. Dados serão carregados pelo método fetch.')
      
      console.log('✅ Página carregada com sucesso')
    } catch (error) {
      console.error('❌ Erro crítico no carregamento da página:', error)
      // Não propagar o erro para não quebrar a página
      if (this.$toast && this.$toast.error) {
        this.$toast.error('Erro ao carregar a página. Usando dados de exemplo.')
      }
      
      // Carregar dados mínimos para funcionar
      this.loadMinimalData()
    }
  },
  
  beforeDestroy() {
    if (this.filterTimeout) {
      clearTimeout(this.filterTimeout)
    }
  },
  
  methods: {
    async loadData() {
      console.log('🔄 Iniciando carregamento de dados...')
      
      try {
        // Seguir o padrão do disagreements-report
        // Carregamento baseado no tipo de projeto
        let reportItems = {}
        
        if (this.project && this.project.canDefineCategory) {
          try {
            reportItems = await this.$repositories.metrics.fetchCategoryPercentage(this.projectId)
            console.log('🏷️ Dados de categoria carregados:', reportItems)
          } catch (error) {
            console.warn('⚠️ Erro ao carregar dados de categoria:', error)
          }
        }
        
        if (this.project && this.project.canDefineSpan) {
          try {
            reportItems = await this.$repositories.metrics.fetchSpanPercentage(this.projectId)
            console.log('📏 Dados de span carregados:', reportItems)
          } catch (error) {
            console.warn('⚠️ Erro ao carregar dados de span:', error)
          }
        }
        
        if (this.project && this.project.canDefineRelation) {
          try {
            reportItems = await this.$repositories.metrics.fetchRelationPercentage(this.projectId)
            console.log('🔗 Dados de relação carregados:', reportItems)
          } catch (error) {
            console.warn('⚠️ Erro ao carregar dados de relação:', error)
          }
        }
        
        // Carregar stats de anotadores (seguindo padrão disagreements-report)
        try {
          const stats = await this.$repositories.metrics.fetchDisagreementStats(this.projectId)
          console.log('📊 Stats carregadas:', stats)
          
          // Carregar anotadores das stats
          this.annotators = (stats.annotators || []).map(name => ({
            id: name,
            name
          }))
          
          // Adicionar anotadores de exemplo se não houver
          if (this.annotators.length === 0) {
            this.annotators = [
              { id: 'a1', name: 'Anotador 1' },
              { id: 'a2', name: 'Anotador 2' }
            ]
          }
          
          // Carregar perspectivas
          this.perspectives = (stats.perspectives || []).filter(p => p && p !== 'Não definida').map(name => ({
            id: name,
            name
          }))
          
          // Carregar datasets das stats
          this.datasets = (stats.textTypes || []).map(name => ({
            id: name,
            name
          }))
          
        } catch (error) {
          console.warn('⚠️ Erro ao carregar stats:', error)
          // Fallback para dados básicos
          this.annotators = [
            { id: 'a1', name: 'Anotador 1' },
            { id: 'a2', name: 'Anotador 2' }
          ]
          this.perspectives = [
            { id: 'p1', name: 'Perspectiva 1' },
            { id: 'p2', name: 'Perspectiva 2' }
          ]
          this.datasets = [
            { id: 'dataset1', name: 'Dataset Principal' }
          ]
        }
        
        // Carregar categorias (seguindo padrão disagreements-report)
        try {
          const categoryTypes = await this.$services.categoryType.list(this.projectId)
          this.categories = categoryTypes.map(category => ({
            text: category.text,
            value: category.text
          }))
          console.log('🏷️ Categorias carregadas:', this.categories)
        } catch (error) {
          console.warn('⚠️ Erro ao carregar categorias:', error)
          this.categories = []
        }
        
        // Carregar membros do projeto como alternativa para anotadores
        try {
          const members = await this.$repositories.member.list(this.projectId)
          if (members && members.length > 0) {
            const memberAnnotators = members.map(member => {
              const user = member.user || member
              const name = (user.first_name && user.last_name) 
                ? `${user.first_name} ${user.last_name}`
                : user.username || user.name || `Usuário ${user.id}`
              
              return {
                id: user.id,
                name
              }
            })
            
            // Mesclar com anotadores das stats
            const allAnnotators = [...this.annotators, ...memberAnnotators]
            this.annotators = allAnnotators.filter((annotator, index, self) => 
              index === self.findIndex(a => a.id === annotator.id)
            )
          }
        } catch (error) {
          console.warn('⚠️ Erro ao carregar membros:', error)
        }
        
        console.log('📋 Filtros carregados finalmente:')
        console.log('- Anotadores:', this.annotators.length)
        console.log('- Datasets:', this.datasets.length)
        console.log('- Categorias:', this.categories.length)
        console.log('- Perspectivas:', this.perspectives.length)
        
        // Carregar dados iniciais do relatório
        await this.applyFilters()
        
        console.log('✅ Dados carregados com sucesso')
        
      } catch (error) {
        console.error('❌ Erro ao carregar dados:', error)
        throw error
      }
    },

    loadMinimalData() {
      console.log('📋 Carregando apenas dados reais...')
      
      // Dados básicos para funcionamento - mas apenas se houver dados reais
      this.annotators = []
      this.datasets = []
      this.categories = []
      this.perspectives = []
      
      // Não gerar dados mockados - deixar vazio para mostrar apenas dados reais
      this.reportData = {
        filtros_aplicados: {},
        resumo_global: {
          total_anotadores: 0,
          total_anotacoes: 0,
          taxa_desacordo_global_percent: 0,
          score_concordancia_global: 0
        },
        detalhe_anotadores: [],
        pagination: {
          total: 0,
          page: 1,
          pages: 0,
          per_page: 10
        }
      }
      
      console.log('✅ Inicialização com dados vazios concluída - apenas dados reais serão mostrados')
    },
    
    async loadFilterOptions() {
      try {
        // Verificar se temos projectId antes de fazer qualquer chamada
        if (!this.projectId) {
          console.warn('⚠️ Sem projectId, usando dados padrão para filtros')
          this.annotators = []
          this.datasets = []
          this.categories = []
          this.perspectives = []
          return
        }
        
        // Load annotators (membros do projeto)
        try {
          const members = await this.$repositories.member.list(this.projectId)
          console.log('🧑‍💼 MEMBROS CARREGADOS:', members)
          
          this.annotators = members.map(member => {
            // Verificar diferentes estruturas possíveis do objeto user
            const user = member.user || member
            const name = (user.first_name && user.last_name) 
              ? `${user.first_name} ${user.last_name}`
              : user.username || user.name || `Usuário ${user.id}`
            
            const annotator = {
              id: user.id,
              name
            }
            console.log(`🧑‍💼 Processando membro:`, member, `-> Resultado:`, annotator)
            return annotator
          })
          
          console.log('🧑‍💼 ANOTADORES PROCESSADOS FINAL:', this.annotators)
          
          // FALLBACK: Se não há membros, deixar vazio para mostrar apenas dados reais
          if (this.annotators.length === 0) {
            console.log('⚠️ NENHUM MEMBRO ENCONTRADO - não utilizando dados de exemplo')
            this.annotators = []
          }
        } catch (error) {
          console.warn('⚠️ ERRO AO CARREGAR MEMBROS:', error)
          console.log('🔄 Não utilizando dados de fallback - apenas dados reais')
          this.annotators = []
        }
        
        // Load categories
        try {
          const categories = await this.$repositories.categoryType.list(this.projectId)
          console.log('Categorias carregadas:', categories)
          this.categories = categories.map(cat => ({
            text: cat.text || cat.name || cat.title,
            value: cat.text || cat.name || cat.title
          }))
        } catch (error) {
          console.warn('Erro ao carregar categorias:', error)
          this.categories = []
        }
        
        // Load perspectives
        try {
          const perspectives = await this.$repositories.perspective.list(this.projectId)
          console.log('Perspectivas carregadas:', perspectives)
          this.perspectives = perspectives.map(perspective => ({
            id: perspective.id,
            name: perspective.name
          }))
        } catch (error) {
          console.warn('Erro ao carregar perspectivas:', error)
          this.perspectives = []
        }
        
        // Load datasets (buscar todos os exemplos para extrair nomes únicos de upload e ficheiros)
        try {
          console.log('Carregando exemplos para extrair datasets/ficheiros...')
          const examples = await this.$repositories.example.list(this.projectId, { 
            limit: '1000',
            offset: '0' 
          })
          console.log('Exemplos carregados:', examples)
          
          const datasetMap = new Map() // Para evitar duplicatas e manter informações adicionais
          
          if (examples.results && examples.results.length > 0) {
            examples.results.forEach(example => {
              // Priorizar upload_name (nome do ficheiro carregado)
              let datasetName = null
              let datasetType = 'dataset'
              
              // 1º Prioridade: upload_name (nome do ficheiro original)
              if (example.upload_name && example.upload_name.trim() !== '') {
                datasetName = example.upload_name
                datasetType = 'ficheiro'
              }
              // 2º Prioridade: uploadName (variação do campo)
              else if (example.uploadName && example.uploadName.trim() !== '') {
                datasetName = example.uploadName
                datasetType = 'ficheiro'
              }
              // 3º Prioridade: filename (nome do ficheiro)
              else if (example.filename && example.filename.trim() !== '') {
                datasetName = example.filename
                datasetType = 'ficheiro'
              }
              // 4º Prioridade: campo dataset nos metadados
              else if (example.meta && example.meta.dataset && example.meta.dataset.trim() !== '') {
                datasetName = example.meta.dataset
                datasetType = 'dataset'
              }
              // 5º Prioridade: text (primeiros caracteres como identificador)
              else if (example.text && example.text.length > 10) {
                datasetName = `Texto_${example.id || 'sem_id'}`
                datasetType = 'texto'
              }
              
              if (datasetName) {
                // Limpar e normalizar o nome
                datasetName = datasetName.trim()
                
                if (!datasetMap.has(datasetName)) {
                  datasetMap.set(datasetName, {
                    id: datasetName,
                    name: datasetName,
                    type: datasetType,
                    count: 1,
                    // Adicionar extensão se for ficheiro
                    displayName: datasetType === 'ficheiro' && !datasetName.includes('.') 
                      ? `${datasetName} (ficheiro)` 
                      : datasetName
                  })
                } else {
                  // Incrementar contador
                  datasetMap.get(datasetName).count++
                }
              }
            })
          }
          
          // Converter Map para array e ordenar por tipo (ficheiros primeiro) e nome
          this.datasets = Array.from(datasetMap.values())
            .sort((a, b) => {
              // Ficheiros primeiro, depois datasets, depois textos
              const typeOrder = { 'ficheiro': 1, 'dataset': 2, 'texto': 3 }
              if (typeOrder[a.type] !== typeOrder[b.type]) {
                return typeOrder[a.type] - typeOrder[b.type]
              }
              return a.name.localeCompare(b.name)
            })
            .map(item => ({
              id: item.id,
              name: `${item.displayName} (${item.count} exemplos)`,
              originalName: item.name,
              type: item.type,
              count: item.count
            }))
          
          console.log('Datasets/ficheiros processados:', this.datasets)
          
          // Se não há datasets dos exemplos, buscar informações do projeto
          if (this.datasets.length === 0) {
            try {
              const projectInfo = await this.$repositories.project.findById(this.projectId)
              console.log('Info do projeto:', projectInfo)
              
              // Se o projeto tem informações sobre datasets
              if (projectInfo.datasets && projectInfo.datasets.length > 0) {
                this.datasets = projectInfo.datasets.map(dataset => ({
                  id: dataset.id || dataset.name,
                  name: dataset.name || dataset.title
                }))
              } else {
                // Não utilizar fallback - apenas dados reais
                this.datasets = []
              }
            } catch (projectError) {
              console.warn('Erro ao carregar info do projeto:', projectError)
              this.datasets = []
            }
          }
          
        } catch (error) {
          console.warn('Erro ao carregar datasets:', error)
          this.datasets = []
        }
        
        // Log final de todos os filtros carregados
        console.log('=== FILTROS CARREGADOS FINALMENTE ===')
        console.log('Anotadores:', this.annotators)
        console.log('Datasets/Ficheiros:', this.datasets)
        console.log('Categorias:', this.categories)
        console.log('Perspectivas:', this.perspectives)
        console.log('=====================================')
        
        // Contar ficheiros vs datasets
        const ficheiros = this.datasets.filter(d => d.type === 'ficheiro').length
        const datasets = this.datasets.filter(d => d.type === 'dataset').length
        
        // Mostrar notificação de sucesso com informação detalhada
        if (this.annotators.length > 0 || this.datasets.length > 0) {
          if (this.$toast && this.$toast.success) {
            let message = `Filtros carregados: ${this.annotators.length} anotadores`
            if (ficheiros > 0) {
              message += `, ${ficheiros} ficheiros`
            }
            if (datasets > 0) {
              message += `, ${datasets} datasets`
            }
            this.$toast.success(message)
          }
        }
        
      } catch (error) {
        console.error('Erro ao carregar opções de filtro:', error)
        if (this.$toast && this.$toast.error) {
          this.$toast.error('Erro ao carregar opções de filtro')
        }
      }
    },
    
    loadAnnotatorsFromAnnotations() {
      try {
        console.log('Carregando anotadores das anotações...')
        
        // Se já temos anotadores dos membros, não precisamos buscar mais
        if (this.annotators && this.annotators.length > 0) {
          console.log('✅ Já temos anotadores dos membros, pulando busca nas anotações')
          return
        }
        
        console.log('⚠️ Não encontramos membros, tentando buscar das anotações...')
        // Implementação simplificada se necessário no futuro
        
      } catch (error) {
        console.warn('Erro ao carregar anotadores das anotações:', error)
      }
    },
    
    loadDatasetsFromAssignments() {
      try {
        console.log('Carregando datasets dos assignments...')
        
        // Se já temos datasets suficientes, não precisamos buscar mais
        if (this.datasets && this.datasets.length > 0) {
          console.log('✅ Já temos datasets, pulando busca nos assignments')
          return
        }
        
        console.log('⚠️ Não encontramos datasets - não utilizando dados de fallback')
        this.datasets = []
        
      } catch (error) {
        console.warn('Erro ao carregar datasets dos assignments:', error)
      }
    },
    
    async loadInitialData() {
      await this.applyFilters()
    },
    
    async applyFilters() {
      console.log('🔄 ApplyFilters iniciado')
      console.log('📊 Filtros recebidos:', JSON.stringify(this.filters, null, 2))
      
      this.loading = true
      try {
        const params = {
          ...this.filters,
          page: this.tableOptions.page,
          page_size: this.tableOptions.itemsPerPage,
          sort_by: this.tableOptions.sortBy[0] || 'total_anotacoes',
          order: this.tableOptions.sortDesc[0] ? 'desc' : 'asc'
        }
        
        console.log('📋 Parâmetros finais:', JSON.stringify(params, null, 2))
        
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === null || params[key] === '' || 
              (Array.isArray(params[key]) && params[key].length === 0)) {
            delete params[key]
          }
        })
        
        try {
          const response = await this.$repositories.reports.getAnnotatorReport(this.projectId, params)
          this.reportData = response
        } catch (error) {
          console.warn('⚠️ API DE RELATÓRIOS NÃO DISPONÍVEL - Mostrando apenas dados reais!')
          console.log('🔄 Erro da API:', error)
          
          // Não utilizar dados mockados - apenas indicar que não há dados
          this.reportData = {
            filtros_aplicados: params,
            resumo_global: {
              total_anotadores: 0,
              total_anotacoes: 0,
              taxa_desacordo_global_percent: 0,
              score_concordancia_global: 0
            },
            detalhe_anotadores: [],
            pagination: {
              total: 0,
              page: 1,
              pages: 0,
              per_page: params.page_size || 10
            }
          }
        }
        
        console.log('🎯 Dados finais do relatório:', this.reportData ? this.reportData.detalhe_anotadores.length : 'nenhum')
        console.log('📊 Resumo global:', this.reportData ? this.reportData.resumo_global : 'nenhum')
        
      } catch (error) {
        console.error('Erro ao gerar relatório:', error)
        if (this.$toast && this.$toast.error) {
          this.$toast.error('Erro ao gerar relatório de anotadores')
        }
      } finally {
        this.loading = false
        console.log('🏁 ApplyFilters finalizado')
      }
    },

    applyLocalFilters(data, filters) {
      console.log('🔍 Aplicando filtros locais:', filters)
      console.log('📊 Dados originais:', data.length, 'itens')
      
      let filtered = [...data]
      
      // Filtro por busca textual
      if (this.searchQuery && this.searchQuery.trim()) {
        const searchTerm = this.searchQuery.toLowerCase().trim()
        filtered = filtered.filter(item =>
          (item.nome_anotador && item.nome_anotador.toLowerCase().includes(searchTerm)) ||
          (item.annotator_id && item.annotator_id.toString().includes(searchTerm)) ||
          (item.categorias_mais_frequentes && 
           (Array.isArray(item.categorias_mais_frequentes) 
             ? item.categorias_mais_frequentes.some(cat => cat.toLowerCase().includes(searchTerm))
             : item.categorias_mais_frequentes.toLowerCase().includes(searchTerm)
           )) ||
          (item.perspectivas_usadas && 
           (Array.isArray(item.perspectivas_usadas) 
             ? item.perspectivas_usadas.some(persp => persp.toLowerCase().includes(searchTerm))
             : item.perspectivas_usadas.toLowerCase().includes(searchTerm)
           ))
        )
        console.log('🔍 Após filtro de busca:', filtered.length, 'itens')
      }
      
      // Filtro por anotador - DEBUG DETALHADO
      if (filters.annotator_id && filters.annotator_id.length > 0) {
        console.log('🔍 FILTRO ANOTADOR - ANTES:')
        console.log('- Filtros selecionados:', filters.annotator_id)
        console.log('- Total de itens antes:', filtered.length)
        console.log('- Primeiro item exemplo:', filtered[0])
        console.log('- Estruturas de annotator_id encontradas:', filtered.map(item => ({
          annotator_id: item.annotator_id,
          nome_anotador: item.nome_anotador,
          user_id: item.user_id,
          user: item.user
        })))
        
        // CORREÇÃO CRÍTICA: Filtro de anotador simplificado e corrigido
        filtered = filtered.filter(item => {
          // COMPARAÇÃO DIRETA E SIMPLES
          const itemId = String(item.annotator_id || item.user_id || item.id || '').trim()
          const match = filters.annotator_id.some(selectedId => {
            const selectedIdStr = String(selectedId || '').trim()
            const directMatch = itemId === selectedIdStr
            
            console.log(`🔍 Comparando: "${itemId}" === "${selectedIdStr}" = ${directMatch}`)
            return directMatch
          })
          
          if (match) {
            console.log(`✅ FILTRO PASSOU: ${item.nome_anotador} (ID: ${itemId})`)
          } else {
            console.log(`❌ FILTRO NÃO PASSOU: ${item.nome_anotador} (ID: ${itemId})`)
          }
          
          return match
        })
        
        console.log('📝 APÓS filtro anotador:', filtered.length, 'itens')
        console.log('📝 Itens que passaram:', filtered.map(item => item.nome_anotador))
      }
      
      // Filtro por dataset
      if (filters.dataset_id && filters.dataset_id.length > 0) {
        filtered = filtered.filter(item => 
          item.dataset_ids && item.dataset_ids.some(id => filters.dataset_id.includes(id))
        )
        console.log('💾 Após filtro dataset:', filtered.length, 'itens')
      }
      
      // Filtro por categoria
      if (filters.categoria_label && filters.categoria_label.length > 0) {
        filtered = filtered.filter(item => 
          item.categoria_labels && item.categoria_labels.some(label => filters.categoria_label.includes(label))
        )
        console.log('🏷️ Após filtro categoria:', filtered.length, 'itens')
      }
      
      // Filtro por perspectiva
      if (filters.perspectiva_id && filters.perspectiva_id.length > 0) {
        filtered = filtered.filter(item => 
          item.perspectiva_ids && item.perspectiva_ids.some(id => filters.perspectiva_id.includes(id))
        )
        console.log('👁️ Após filtro perspectiva:', filtered.length, 'itens')
      }
      
      // Filtro por data inicial
      if (filters.data_inicial) {
        const dataInicial = new Date(filters.data_inicial)
        filtered = filtered.filter(item => {
          const primeiraAnotacao = new Date(item.primeira_anotacao)
          return primeiraAnotacao >= dataInicial
        })
        console.log('📅 Após filtro data inicial:', filtered.length, 'itens')
      }
      
      // Filtro por data final
      if (filters.data_final) {
        const dataFinal = new Date(filters.data_final)
        filtered = filtered.filter(item => {
          const ultimaAnotacao = new Date(item.ultima_anotacao)
          return ultimaAnotacao <= dataFinal
        })
        console.log('📅 Após filtro data final:', filtered.length, 'itens')
      }
      
      // Filtro por estado de desacordo
      if (filters.estado_desacordo && filters.estado_desacordo !== 'todos') {
        if (filters.estado_desacordo === 'em_desacordo') {
          filtered = filtered.filter(item => item.taxa_desacordo_percent > 15)
        } else if (filters.estado_desacordo === 'resolvido') {
          filtered = filtered.filter(item => item.desacordos_resolvidos > 0)
        }
        console.log('⚖️ Após filtro estado desacordo:', filtered.length, 'itens')
      }
      
      // Aplicar ordenação
      if (filters.sort_by) {
        const sortBy = filters.sort_by
        const order = filters.order === 'desc' ? -1 : 1
        
        filtered.sort((a, b) => {
          const aVal = a[sortBy]
          const bVal = b[sortBy]
          
          // Tratar valores numéricos
          if (typeof aVal === 'number' && typeof bVal === 'number') {
            return (aVal - bVal) * order
          }
          
          // Tratar strings
          if (typeof aVal === 'string' && typeof bVal === 'string') {
            return aVal.localeCompare(bVal) * order
          }
          
          return 0
        })
        console.log('🔄 Dados ordenados por:', sortBy, filters.order)
      }
      
      console.log('✅ Filtros aplicados, retornando:', filtered.length, 'itens')
      return filtered
    },
    
    async updateTableOptions() {
      await this.applyFilters()
    },
    
    clearFilters() {
      this.filters = {
        dataset_id: [],
        annotator_id: [],
        data_inicial: null,
        data_final: null,
        categoria_label: [],
        perspectiva_id: [],
        estado_desacordo: 'todos'
      }
      this.applyFilters()
    },
    
    manualApplyFilters() {
      console.log('🔧 Aplicação manual de filtros solicitada')
      console.log('📊 Estado atual dos filtros:', JSON.stringify(this.filters, null, 2))
      console.log('📊 Dados atuais:', this.reportData ? this.reportData.detalhe_anotadores.length : 'nenhum')
      console.log('📊 Total de dados disponíveis:', this.reportData ? this.reportData.pagination?.total : 'desconhecido')
      this.applyFilters()
    },
    
    // Métodos para remover filtros específicos
    removeAnnotatorFilter(annotatorId) {
      const index = this.filters.annotator_id.indexOf(annotatorId)
      if (index > -1) {
        this.filters.annotator_id.splice(index, 1)
      }
    },
    
    removeDatasetFilter(datasetId) {
      const index = this.filters.dataset_id.indexOf(datasetId)
      if (index > -1) {
        this.filters.dataset_id.splice(index, 1)
      }
    },
    
    removeCategoryFilter(categoryId) {
      const index = this.filters.categoria_label.indexOf(categoryId)
      if (index > -1) {
        this.filters.categoria_label.splice(index, 1)
      }
    },
    
    resetFilters() {
      this.filters = {
        dataset_id: [],
        annotator_id: [],
        data_inicial: null,
        data_final: null,
        categoria_label: [],
        perspectiva_id: [],
        estado_desacordo: 'todos'
      }
      this.searchQuery = ''
      this.applyFilters()
    },
    
    // DEBUG METHODS para v-select
    onAnnotatorFilterChange(value) {
      console.log('🎯 ANNOTATOR FILTER CHANGE EVENT!')
      console.log('🎯 Novo valor:', value)
      console.log('🎯 this.filters.annotator_id:', this.filters.annotator_id)
      console.log('🎯 Opções disponíveis:', this.annotatorOptions)
      
      // CORREÇÃO CRÍTICA: Limpar valores inválidos
      this.cleanAnnotatorFilters()
    },
    
    onAnnotatorFilterInput(value) {
      console.log('🎯 ANNOTATOR FILTER INPUT EVENT!')
      console.log('🎯 Valor input:', value)
      console.log('🎯 this.filters.annotator_id:', this.filters.annotator_id)
      
      // CORREÇÃO CRÍTICA: Limpar valores inválidos
      this.cleanAnnotatorFilters()
      
      // CORREÇÃO FORÇADA: Aplicar filtros imediatamente
      this.$nextTick(() => {
        console.log('🚀 FORÇANDO APLICAÇÃO DE FILTROS!')
        this.applyFilters()
      })
    },
    
    // MÉTODO CRÍTICO: Limpar filtros de anotadores inválidos
    cleanAnnotatorFilters() {
      console.log('🧹 LIMPANDO FILTROS DE ANOTADORES INVÁLIDOS')
      console.log('🧹 Filtros antes da limpeza:', this.filters.annotator_id)
      
      // Obter IDs válidos dos anotadores disponíveis
      const validIds = this.annotatorOptions
        .filter(option => option.value !== null)
        .map(option => String(option.value))
      
      console.log('🧹 IDs válidos disponíveis:', validIds)
      
      // Filtrar apenas valores válidos
      const cleanFilters = this.filters.annotator_id.filter(id => {
        const idStr = String(id || '').trim()
        const isValid = idStr !== '' && idStr !== 'null' && idStr !== 'undefined' && validIds.includes(idStr)
        console.log(`🧹 Validando ID "${idStr}": ${isValid}`)
        return isValid
      })
      
      console.log('🧹 Filtros após limpeza:', cleanFilters)
      
      // Aplicar filtros limpos
      if (JSON.stringify(this.filters.annotator_id) !== JSON.stringify(cleanFilters)) {
        this.filters.annotator_id = cleanFilters
        console.log('🧹 Filtros atualizados para:', this.filters.annotator_id)
      }
    },
    
    // MÉTODOS DE DEBUG - SOLUÇÃO DEFINITIVA
    debugFilters() {
      console.log('🐛 ===== DEBUG COMPLETO DOS FILTROS =====')
      console.log('🐛 Filtros atuais:', this.filters)
      console.log('🐛 Anotadores raw:', this.annotators)
      console.log('🐛 Opções do select:', this.annotatorOptions)
      console.log('🐛 Dados do relatório:', this.reportData)
      console.log('🐛 HasActiveFilters:', this.hasActiveFilters)
      console.log('🐛 ActiveFiltersCount:', this.activeFiltersCount)
      console.log('🐛 ======================================')
      
      if (this.$toast) {
        this.$toast.info('Debug completo executado - veja o console!')
      }
    },
    
    testFilter() {
      console.log('🧪 ===== TESTE DE FILTRO ESPECÍFICO U3 =====')
      
      // Limpar filtros primeiro
      this.filters.annotator_id = []
      
      // Testar especificamente com U3
      this.filters.annotator_id = ['U3']
      console.log('🧪 Filtro definido para U3:', this.filters.annotator_id)
      
      // Limpar filtros inválidos
      this.cleanAnnotatorFilters()
      
      // Aplicar imediatamente
      this.forceApplyFilters()
      
      if (this.$toast) {
        this.$toast.success('Teste de filtro U3 executado!')
      }
      
      console.log('🧪 ==========================================')
    },
    
    async exportReport(format) {
      this.exporting = true
      try {
        // Gerar nome do arquivo
        const projectName = this.safeProject.name || 'projeto'
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
        const filename = `relatorio-anotadores-${projectName}-${timestamp}`
        
        // Exportar baseado no formato
        if (format === 'pdf') {
          await this.exportToPDF(filename)
        } else if (format === 'csv') {
          this.exportToCSV(filename)
        } else {
          // Default para PDF se não especificado
          await this.exportToPDF(filename)
        }
        
        if (this.$toast && this.$toast.success) {
          this.$toast.success(`Relatório ${format.toUpperCase()} exportado com sucesso`)
        }
        
      } catch (error) {
        console.error('Erro ao exportar relatório:', error)
        if (this.$toast && this.$toast.error) {
          this.$toast.error(`Erro ao exportar: ${error.message}`)
        }
      } finally {
        this.exporting = false
      }
    },

    exportToCSV(filename) {
      try {
        if (!this.reportData || !this.reportData.detalhe_anotadores || this.reportData.detalhe_anotadores.length === 0) {
          throw new Error('Não há dados para exportar.')
        }
        
        // Cabeçalho profissional do CSV
        const projectName = this.safeProject.name || 'Projeto'
        const reportDate = new Date().toLocaleDateString('pt-PT', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
        const reportTime = new Date().toLocaleTimeString('pt-PT', {
          hour: '2-digit',
          minute: '2-digit'
        })
        
        let csvContent = `RELATÓRIO DE ANOTADORES\n`
        csvContent += `Projeto: ${projectName}\n`
        csvContent += `Data de Geração: ${reportDate} às ${reportTime}\n`
        
        // Resumo executivo
        if (this.reportData.resumo_global) {
          csvContent += `\nRESUMO EXECUTIVO\n`
          csvContent += `Total de Anotadores: ${this.reportData.resumo_global.total_anotadores}\n`
          csvContent += `Total de Anotações: ${this.reportData.resumo_global.total_anotacoes}\n`
          csvContent += `Taxa de Desacordo Global: ${this.reportData.resumo_global.taxa_desacordo_global_percent}%\n`
          csvContent += `Score de Concordância Global: ${this.reportData.resumo_global.score_concordancia_global}%\n`
        }
        
        csvContent += `\nDETALHES POR ANOTADOR\n`
        
        // Dados dos anotadores com formatação profissional
        const csvData = this.reportData.detalhe_anotadores.map((item, index) => ({
          'Nº': index + 1,
          'Nome do Anotador': item.nome_anotador || 'N/A',
          'Total de Anotações': item.total_anotacoes || 0,
          'Datasets Utilizados': item.datasets_distintos || 0,
          'Tempo Total': this.formatTime(item.tempo_total_min),
          'Tempo Médio/Anotação': this.formatDuration(item.tempo_medio_por_anotacao_seg),
          'Taxa de Desacordo': `${parseFloat(item.taxa_desacordo_percent || 0).toFixed(1)}%`,
          'Desacordos Resolvidos': item.desacordos_resolvidos || 0,
          'Score de Concordância': parseFloat(item.score_concordancia_medio || 0).toFixed(3),
          'Perspectivas': Array.isArray(item.perspectivas_usadas) 
            ? item.perspectivas_usadas.join(' | ') 
            : (item.perspectivas_usadas || 'N/A'),
          'Categorias Principais': Array.isArray(item.categorias_mais_frequentes) 
            ? item.categorias_mais_frequentes.slice(0, 3).join(' | ') 
            : (item.categorias_mais_frequentes || 'N/A'),
          'Período de Atividade': `${this.formatDate(item.primeira_anotacao)} - ${this.formatDate(item.ultima_anotacao)}`
        }))
        
        const columns = Object.keys(csvData[0])
        csvContent += columns.join(',') + '\n'
        
        csvData.forEach(row => {
          const rowValues = columns.map(col => {
            const cell = row[col] ? String(row[col]) : 'N/A'
            return cell.includes(',') || cell.includes('"') || cell.includes('\n')
              ? '"' + cell.replace(/"/g, '""') + '"' 
              : cell
          })
          csvContent += rowValues.join(',') + '\n'
        })
        
        // Rodapé profissional
        csvContent += `\nRELATÓRIO GERADO AUTOMATICAMENTE\n`
        csvContent += `Sistema: Doccano - Plataforma de Anotação\n`
        csvContent += `Versão: 1.0.0\n`
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        
        if (window.navigator && window.navigator.msSaveOrOpenBlob) {
          window.navigator.msSaveOrOpenBlob(blob, `${filename}.csv`)
          return
        }
        
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${filename}.csv`
        
        document.body.appendChild(link)
        link.click()
        
        setTimeout(() => {
          document.body.removeChild(link)
          URL.revokeObjectURL(url)
        }, 100)
      } catch (error) {
        console.error('Erro ao gerar CSV:', error)
        throw new Error('Não foi possível gerar o CSV: ' + error.message)
      }
    },
    
    async exportToPDF(filename) {
      try {
        // Carregar jsPDF dinamicamente (para não incluir no bundle inicial)
        const { jsPDF } = await import('jspdf')
        const { default: autoTable } = await import('jspdf-autotable')
        
        // eslint-disable-next-line new-cap
        const doc = new jsPDF()
        
        // Cores profissionais
        const primaryColor = [25, 118, 210] // Azul corporativo
        const secondaryColor = [245, 245, 245] // Cinza claro
        const textColor = [33, 33, 33] // Cinza escuro
        
        // Cabeçalho profissional com fundo
        doc.setFillColor(...primaryColor)
        doc.rect(0, 0, 210, 35, 'F')
        
        // Logo/Título principal
        doc.setTextColor(255, 255, 255)
        doc.setFontSize(24)
        doc.setFont('helvetica', 'bold')
        doc.text('RELATÓRIO DE ANOTADORES', 14, 20)
        
        // Subtítulo
        doc.setFontSize(12)
        doc.setFont('helvetica', 'normal')
        doc.text('Análise Detalhada de Performance', 14, 28)
        
        // Informações do projeto em caixa
        doc.setFillColor(...secondaryColor)
        doc.rect(14, 40, 182, 35, 'F')
        doc.setDrawColor(200, 200, 200)
        doc.rect(14, 40, 182, 35, 'S')
        
        doc.setTextColor(...textColor)
        doc.setFontSize(14)
        doc.setFont('helvetica', 'bold')
        doc.text('INFORMAÇÕES DO PROJETO', 18, 50)
        
        doc.setFontSize(11)
        doc.setFont('helvetica', 'normal')
        const projectName = this.safeProject.name || 'Projeto Sem Nome'
        const reportDate = new Date().toLocaleDateString('pt-PT', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
        const reportTime = new Date().toLocaleTimeString('pt-PT', {
          hour: '2-digit',
          minute: '2-digit'
        })
        
        doc.text(`Projeto: ${projectName}`, 18, 58)
        doc.text(`Data de Geração: ${reportDate} às ${reportTime}`, 18, 65)
        
        // Resumo executivo em destaque
        let currentY = 85
        if (this.reportData && this.reportData.resumo_global) {
          doc.setFillColor(250, 250, 250)
          doc.rect(14, currentY, 182, 30, 'F')
          doc.setDrawColor(primaryColor[0], primaryColor[1], primaryColor[2])
          doc.setLineWidth(0.5)
          doc.rect(14, currentY, 182, 30, 'S')
          
          doc.setTextColor(...primaryColor)
          doc.setFontSize(14)
          doc.setFont('helvetica', 'bold')
          doc.text('RESUMO EXECUTIVO', 18, currentY + 8)
          
          doc.setTextColor(...textColor)
          doc.setFontSize(10)
          doc.setFont('helvetica', 'normal')
          
          const resumo = this.reportData.resumo_global
          doc.text(`Total de Anotadores: ${resumo.total_anotadores}`, 18, currentY + 16)
          doc.text(`Total de Anotações: ${resumo.total_anotacoes}`, 100, currentY + 16)
          doc.text(`Taxa de Desacordo Global: ${resumo.taxa_desacordo_global_percent}%`, 18, currentY + 23)
          doc.text(`Score de Concordância: ${resumo.score_concordancia_global}%`, 100, currentY + 23)
          
          currentY += 40
        }
        
        // Título da tabela
        doc.setTextColor(...primaryColor)
        doc.setFontSize(16)
        doc.setFont('helvetica', 'bold')
        doc.text('DETALHES POR ANOTADOR', 14, currentY)
        currentY += 10
        
        // Tabela principal com design profissional
        if (this.reportData && this.reportData.detalhe_anotadores) {
          const detailsData = this.reportData.detalhe_anotadores.map((item, index) => [
            (index + 1).toString(),
            item.nome_anotador || 'N/A',
            (item.total_anotacoes || 0).toString(),
            (item.datasets_distintos || 0).toString(),
            this.formatTime(item.tempo_total_min),
            `${parseFloat(item.taxa_desacordo_percent || 0).toFixed(1)}%`,
            parseFloat(item.score_concordancia_medio || 0).toFixed(3)
          ])
          
          autoTable(doc, {
            startY: currentY,
            head: [['Nº', 'Nome do Anotador', 'Anotações', 'Datasets', 'Tempo Total', 'Taxa Desacordo', 'Concordância']],
            body: detailsData,
            theme: 'striped',
            styles: {
              fontSize: 9,
              cellPadding: 4,
              textColor,
              lineColor: [200, 200, 200],
              lineWidth: 0.1
            },
            headStyles: {
              fillColor: primaryColor,
              textColor: [255, 255, 255],
              fontSize: 10,
              fontStyle: 'bold',
              halign: 'center'
            },
            alternateRowStyles: {
              fillColor: [248, 249, 250]
            },
            columnStyles: {
              0: { halign: 'center', cellWidth: 15 },
              1: { cellWidth: 45 },
              2: { halign: 'center', cellWidth: 25 },
              3: { halign: 'center', cellWidth: 20 },
              4: { halign: 'center', cellWidth: 25 },
              5: { halign: 'center', cellWidth: 25 },
              6: { halign: 'center', cellWidth: 25 }
            }
          })
          
          currentY = doc.lastAutoTable.finalY + 15
        }
        
        // Rodapé profissional
        const pageHeight = doc.internal.pageSize.height
        doc.setFillColor(...primaryColor)
        doc.rect(0, pageHeight - 20, 210, 20, 'F')
        
        doc.setTextColor(255, 255, 255)
        doc.setFontSize(8)
        doc.setFont('helvetica', 'normal')
        doc.text('Doccano - Plataforma de Anotação | Relatório gerado automaticamente', 14, pageHeight - 12)
        doc.text(`Página 1 | ${new Date().toLocaleDateString('pt-PT')}`, 14, pageHeight - 6)
        
        // Número da página (canto direito)
        doc.text('v1.0.0', 180, pageHeight - 6)
        
        // Salvar o PDF usando output com método compatível com navegadores
        const pdfOutput = doc.output('blob')
        const url = URL.createObjectURL(pdfOutput)
        
        // Para browsers antigos como o IE
        if (window.navigator && window.navigator.msSaveOrOpenBlob) {
          window.navigator.msSaveOrOpenBlob(pdfOutput, `${filename}.pdf`)
          
          // Redirecionar após o download
          setTimeout(() => {
            this.$router.push(`/projects/${this.projectId}/reports`)
          }, 500)
          
          return
        }
        
        // Para browsers modernos
        const link = document.createElement('a')
        link.href = url
        link.download = `${filename}.pdf`
        link.style.display = 'none'
        document.body.appendChild(link)
        link.click()
        
        // Limpar URL após download
        setTimeout(() => {
          URL.revokeObjectURL(url)
          document.body.removeChild(link)
        }, 500)
      } catch (error) {
        console.error('Erro ao gerar PDF:', error)
        throw new Error('Não foi possível gerar o PDF. Verifique se todas as bibliotecas necessárias estão disponíveis.')
      }
    },
    
    viewAnnotatorDetails(annotator) {
      this.selectedAnnotator = annotator
      this.detailsDialog = true
    },
    
    getActiveFiltersText() {
      const active = []
      if (this.filters.annotator_id.length) active.push(`${this.filters.annotator_id.length} anotador(es)`)
      if (this.filters.dataset_id.length) active.push(`${this.filters.dataset_id.length} dataset(s)`)
      if (this.filters.categoria_label.length) active.push(`${this.filters.categoria_label.length} categoria(s)`)
      if (this.filters.data_inicial) active.push('data inicial')
      if (this.filters.data_final) active.push('data final')
      
      return active.length ? active.join(', ') : 'Nenhum filtro aplicado'
    },
    
    getAnnotationCountColor(count) {
      if (count >= 100) return 'success'
      if (count >= 50) return 'warning'
      return 'error'
    },
    
    getDisagreementColor(percent) {
      if (percent <= 10) return 'success'
      if (percent <= 25) return 'warning'
      return 'error'
    },
    
    formatTime(minutes) {
      if (!minutes) return '0min'
      const hours = Math.floor(minutes / 60)
      const mins = Math.floor(minutes % 60)
      if (hours > 0) {
        return `${hours}h ${mins}min`
      }
      return `${mins}min`
    },
    
    formatDuration(seconds) {
      if (!seconds) return '0s'
      if (seconds >= 60) {
        return `${Math.floor(seconds / 60)}min ${Math.floor(seconds % 60)}s`
      }
      return `${Math.floor(seconds)}s`
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        return new Date(dateString).toLocaleDateString('pt-PT', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        })
      } catch (error) {
        return 'Data Inválida'
      }
    },
    
    // MÉTODO FORÇADO para aplicar filtros - SOLUÇÃO DEFINITIVA
    forceApplyFilters() {
      console.log('🚨 FORÇANDO APLICAÇÃO DE FILTROS MANUALMENTE!')
      console.log('🚨 Estado atual dos filtros:', JSON.stringify(this.filters, null, 2))
      console.log('🚨 Anotadores disponíveis:', this.annotators)
      console.log('🚨 Opções de anotadores:', this.annotatorOptions)
      
      // Limpar filtros inválidos primeiro
      this.cleanAnnotatorFilters()
      
      // Limpar timeout se existir
      if (this.filterTimeout) {
        clearTimeout(this.filterTimeout)
      }
      
      // Aplicar imediatamente sem debounce
      this.applyFilters()
    },
    
    // MÉTODO PARA REINICIALIZAR FILTROS DE ANOTADORES
    resetAnnotatorFilters() {
      console.log('🔄 REINICIALIZANDO FILTROS DE ANOTADORES')
      
      // Limpar completamente os filtros de anotadores
      this.filters.annotator_id = []
      
      // Forçar atualização do componente
      this.$forceUpdate()
      
      // Aplicar filtros
      this.$nextTick(() => {
        this.applyFilters()
      })
    }
  }
}
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  color: white;
}

.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 16px;
}
</style> 