<template>
  <v-container fluid class="pa-0">
    <!-- Header Section -->
    <div class="hero-section">
      <v-container>
        <v-row align="center" class="py-8">
          <v-col cols="12" class="text-center">
            <v-icon size="64" color="white" class="mb-4">mdi-account-group</v-icon>
            <h1 class="display-1 font-weight-bold white--text mb-2">
              Relatórios de Anotadores
            </h1>
            <p class="subtitle-1 white--text">
              Análise completa do desempenho e progresso da equipe de anotação
            </p>
          </v-col>
        </v-row>
      </v-container>
    </div>

    <!-- Main Content -->
    <v-container class="py-8">
      <!-- Summary Cards -->
      <v-row v-if="report">
        <v-col cols="12" md="4">
          <v-card class="text-center pa-4" elevation="2">
            <v-icon size="48" color="primary" class="mb-3">mdi-account-multiple</v-icon>
            <h3 class="headline font-weight-bold">{{ filteredSummary.total_anotadores }}</h3>
            <p class="body-2 grey--text">Total de Anotadores</p>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card class="text-center pa-4" elevation="2">
            <v-icon size="48" color="success" class="mb-3">mdi-check-circle</v-icon>
            <h3 class="headline font-weight-bold">{{ filteredSummary.total_anotacoes }}</h3>
            <p class="body-2 grey--text">Anotações Concluídas</p>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card class="text-center pa-4" elevation="2">
            <v-icon size="48" color="warning" class="mb-3">mdi-alert-circle</v-icon>
            <h3 class="headline font-weight-bold">{{ filteredSummary.taxa_desacordo_global_percent }}%</h3>
            <p class="body-2 grey--text">Taxa de Desacordo Global</p>
          </v-card>
        </v-col>
      </v-row>

      <v-row class="mt-6">
        <!-- Filters Panel -->
        <v-col cols="12" lg="3">
          <v-card elevation="2">
            <v-card-title class="primary white--text">
              <v-icon left color="white">mdi-filter</v-icon>
              Filtros
            </v-card-title>
            <v-card-text class="pa-4">
              <v-form @submit.prevent="applyFilters">
                <!-- Anotadores -->
                <v-select
                  v-model="filters.annotator_id"
                  :items="metadata.annotators"
                  item-text="name"
                  item-value="id"
                  label="Anotadores"
                  multiple
                  chips
                  small-chips
                  deletable-chips
                  class="mb-3"
                ></v-select>

                <!-- Datasets -->
                <v-select
                  v-model="filters.dataset_id"
                  :items="metadata.datasets"
                  item-text="name"
                  item-value="id"
                  label="Datasets"
                  multiple
                  chips
                  small-chips
                  deletable-chips
                  class="mb-3"
                ></v-select>

                <!-- Período -->
                <v-text-field
                  v-model="filters.data_inicial"
                  label="Data Inicial"
                  type="date"
                  class="mb-3"
                ></v-text-field>

                <v-text-field
                  v-model="filters.data_final"
                  label="Data Final"
                  type="date"
                  class="mb-3"
                ></v-text-field>

                <!-- Categorias -->
                <v-select
                  v-model="filters.categoria_label"
                  :items="metadata.categories"
                  label="Categorias"
                  multiple
                  chips
                  small-chips
                  deletable-chips
                  class="mb-3"
                ></v-select>

                <!-- Perspetivas -->
                <v-select
                  v-model="filters.perspectiva_id"
                  :items="metadata.perspectives"
                  item-text="name"
                  item-value="id"
                  label="Perspetivas"
                  multiple
                  chips
                  small-chips
                  deletable-chips
                  class="mb-3"
                ></v-select>

                <!-- Estado de Desacordo -->
                <v-select
                  v-model="filters.estado_desacordo"
                  :items="metadata.disagreement_states"
                  item-text="label"
                  item-value="value"
                  label="Estado de Desacordo"
                  class="mb-4"
                ></v-select>

                <!-- Ordenação -->
                <v-select
                  v-model="filters.sort_by"
                  :items="metadata.sort_options"
                  item-text="label"
                  item-value="value"
                  label="Ordenar por"
                  class="mb-3"
                ></v-select>

                <v-select
                  v-model="filters.order"
                  :items="[
                    { text: 'Crescente', value: 'asc' },
                    { text: 'Decrescente', value: 'desc' }
                  ]"
                  label="Ordem"
                  class="mb-4"
                ></v-select>

                <v-btn color="primary" type="submit" block class="mb-2" :loading="isLoading">
                  <v-icon left>mdi-magnify</v-icon>
                  Aplicar Filtros
                </v-btn>

                <v-btn color="grey" block @click="clearFilters">
                  <v-icon left>mdi-filter-off</v-icon>
                  Limpar Filtros
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- Export Panel -->
          <v-card elevation="2" class="mt-4">
            <v-card-title class="success white--text">
              <v-icon left color="white">mdi-download</v-icon>
              Exportar
            </v-card-title>
            <v-card-text class="pa-4">
              <v-btn color="success" block class="mb-2" :loading="isExporting" @click="exportReport('csv')">
                <v-icon left>mdi-file-delimited</v-icon>
                Exportar CSV
              </v-btn>
              <v-btn color="red" block :loading="isExporting" @click="exportReport('pdf')">
                <v-icon left>mdi-file-pdf-box</v-icon>
                Exportar PDF
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Results Table -->
        <v-col cols="12" lg="9">
          <v-card elevation="2">
            <v-card-title class="info white--text">
              <v-icon left color="white">mdi-table</v-icon>
              Relatório de Anotadores
              <v-spacer></v-spacer>
              <span class="caption">{{ filteredAnnotators.length }} resultados</span>
            </v-card-title>
            
            <v-card-text class="pa-0">
              <v-skeleton-loader
                v-if="isLoading"
                type="table-tbody"
              ></v-skeleton-loader>

              <v-data-table
                v-else-if="report && report.detalhe_anotadores.length > 0"
                :headers="tableHeaders"
                :items="filteredAnnotators"
                :page="currentPage"
                :items-per-page="itemsPerPage"
                :server-items-length="totalItems"
                class="elevation-0"
                @update:page="updatePage"
                @update:items-per-page="updateItemsPerPage"
              >
                <!-- Nome do Anotador -->
                <template #[`item.nome_anotador`]="{ item }">
                  <div class="d-flex align-center">
                    <v-avatar size="32" color="primary" class="white--text mr-2">
                      {{ getInitials(item.nome_anotador) }}
                    </v-avatar>
                    <div>
                      <div class="font-weight-medium">{{ item.nome_anotador }}</div>
                      <div class="caption grey--text">ID: {{ item.annotator_id }}</div>
                    </div>
                  </div>
                </template>

                <!-- Taxa de Desacordo -->
                <template #[`item.taxa_desacordo_percent`]="{ item }">
                  <v-chip 
                    :color="getDisagreementColor(item.taxa_desacordo_percent)" 
                    text-color="white" 
                    small
                  >
                    {{ item.taxa_desacordo_percent.toFixed(1) }}%
                  </v-chip>
                </template>

                <!-- Score de Concordância -->
                <template #[`item.score_concordancia_medio`]="{ item }">
                  <div class="text-center">
                    <v-progress-circular
                      :value="item.score_concordancia_medio * 100"
                      :color="getScoreColor(item.score_concordancia_medio)"
                      size="40"
                      width="4"
                    >
                      {{ (item.score_concordancia_medio * 100).toFixed(0) }}
                    </v-progress-circular>
                  </div>
                </template>

                <!-- Perspetivas -->
                <template #[`item.perspectivas_usadas`]="{ item }">
                  <v-chip 
                    v-for="perspectiva in item.perspectivas_usadas.slice(0, 2)" 
                    :key="perspectiva"
                    small 
                    class="ma-1"
                  >
                    {{ perspectiva }}
                  </v-chip>
                  <v-chip v-if="item.perspectivas_usadas.length > 2" small class="ma-1">
                    +{{ item.perspectivas_usadas.length - 2 }}
                  </v-chip>
                </template>

                <!-- Categorias -->
                <template #[`item.categorias_mais_frequentes`]="{ item }">
                  <v-chip 
                    v-for="categoria in item.categorias_mais_frequentes.slice(0, 3)" 
                    :key="categoria"
                    small 
                    color="grey lighten-2"
                    class="ma-1"
                  >
                    {{ categoria }}
                  </v-chip>
                </template>

                <!-- Tempo Total -->
                <template #[`item.tempo_total_min`]="{ item }">
                  {{ formatTime(item.tempo_total_min) }}
                </template>

                <!-- Tempo Médio -->
                <template #[`item.tempo_medio_por_anotacao_seg`]="{ item }">
                  {{ item.tempo_medio_por_anotacao_seg.toFixed(1) }}s
                </template>

                <!-- Data -->
                <template #[`item.primeira_anotacao`]="{ item }">
                  {{ formatDate(item.primeira_anotacao) }}
                </template>

                <template #[`item.ultima_anotacao`]="{ item }">
                  {{ formatDate(item.ultima_anotacao) }}
                </template>
              </v-data-table>

              <div v-else-if="!isLoading" class="text-center py-8">
                <v-icon size="80" color="grey lighten-2" class="mb-4">mdi-file-search</v-icon>
                <h3 class="headline grey--text mb-2">Nenhum resultado encontrado</h3>
                <p class="body-1 grey--text">
                  Tente ajustar os filtros para encontrar dados.
                </p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script>
export default {
  layout: 'project',
  data() {
    return {
      isLoading: false,
      isExporting: false,
      report: null,
      metadata: {
        annotators: [],
        categories: [],
        perspectives: [],
        datasets: [],
        sort_options: [],
        disagreement_states: []
      },
      filters: {
        dataset_id: [],
        annotator_id: [],
        data_inicial: '',
        data_final: '',
        categoria_label: [],
        perspectiva_id: [],
        estado_desacordo: 'todos',
        sort_by: 'total_anotacoes',
        order: 'desc',
        page: 1,
        page_size: 10
      },
      currentPage: 1,
      itemsPerPage: 10,
      totalItems: 0,
      tableHeaders: [
        { text: 'Anotador', value: 'nome_anotador', sortable: false, width: '200px' },
        { text: 'Total Anotações', value: 'total_anotacoes', align: 'center' },
        { text: 'Datasets', value: 'datasets_distintos', align: 'center' },
        { text: 'Tempo Total', value: 'tempo_total_min', align: 'center' },
        { text: 'Tempo Médio', value: 'tempo_medio_por_anotacao_seg', align: 'center' },
        { text: 'Taxa Desacordo', value: 'taxa_desacordo_percent', align: 'center' },
        { text: 'Desacordos Resolvidos', value: 'desacordos_resolvidos', align: 'center' },
        { text: 'Score Concordância', value: 'score_concordancia_medio', align: 'center' },
        { text: 'Perspetivas', value: 'perspectivas_usadas', sortable: false },
        { text: 'Categorias Top', value: 'categorias_mais_frequentes', sortable: false },
        { text: 'Primeira Anotação', value: 'primeira_anotacao', align: 'center' },
        { text: 'Última Anotação', value: 'ultima_anotacao', align: 'center' }
      ]
    }
  },
  computed: {
    projectId() {
      return this.$route.params.id
    },
    
    // Filtrar anotadores baseado nos critérios selecionados
    filteredAnnotators() {
      if (!this.report || !this.report.detalhe_anotadores) {
        return []
      }
      
      let filtered = [...this.report.detalhe_anotadores]
      
      console.log('DEBUG: Aplicando filtros locais aos dados:', this.filters)
      console.log('DEBUG: Dados originais:', filtered.length, 'anotadores')
      
      // Filtrar por anotador específico
      if (this.filters.annotator_id && this.filters.annotator_id.length > 0) {
        filtered = filtered.filter(annotator => 
          this.filters.annotator_id.includes(annotator.annotator_id)
        )
        console.log('DEBUG: Após filtro de anotador:', filtered.length, 'anotadores')
      }
      
      // Filtrar por categoria
      if (this.filters.categoria_label && this.filters.categoria_label.length > 0) {
        filtered = filtered.filter(annotator => {
          return annotator.categorias_mais_frequentes.some(categoria =>
            this.filters.categoria_label.includes(categoria)
          )
        })
        console.log('DEBUG: Após filtro de categoria:', filtered.length, 'anotadores')
      }
      
      // Filtrar por estado de desacordo
      if (this.filters.estado_desacordo && this.filters.estado_desacordo !== 'todos') {
        if (this.filters.estado_desacordo === 'em_desacordo') {
          filtered = filtered.filter(annotator => annotator.taxa_desacordo_percent > 10)
        } else if (this.filters.estado_desacordo === 'resolvido') {
          filtered = filtered.filter(annotator => annotator.taxa_desacordo_percent <= 10)
        }
        console.log('DEBUG: Após filtro de estado:', filtered.length, 'anotadores')
      }
      
      // Aplicar ordenação
      const sortBy = this.filters.sort_by || 'total_anotacoes'
      const order = this.filters.order || 'desc'
      
      filtered.sort((a, b) => {
        let valueA = a[sortBy]
        let valueB = b[sortBy]
        
        // Tratar valores string vs numéricos
        if (typeof valueA === 'string' && typeof valueB === 'string') {
          valueA = valueA.toLowerCase()
          valueB = valueB.toLowerCase()
        } else if (typeof valueA === 'number' && typeof valueB === 'number') {
          // Valores numéricos
        } else {
          // Converter para string se tipos mistos
          valueA = String(valueA || 0)
          valueB = String(valueB || 0)
        }
        
        if (order === 'desc') {
          return valueA > valueB ? -1 : valueA < valueB ? 1 : 0
        } else {
          return valueA < valueB ? -1 : valueA > valueB ? 1 : 0
        }
      })
      
      console.log('DEBUG: Após ordenação:', filtered.length, 'anotadores')
      
      // Aplicar paginação (simplificada - mostrar todos por enquanto)
      return filtered
    },
    
    // Atualizar resumo baseado nos dados filtrados
    filteredSummary() {
      if (!this.filteredAnnotators.length) {
        return {
          total_anotadores: 0,
          total_anotacoes: 0,
          taxa_desacordo_global_percent: 0
        }
      }
      
      const totalAnotacoes = this.filteredAnnotators.reduce((sum, a) => sum + a.total_anotacoes, 0)
      const taxaDesacordoMedia = this.filteredAnnotators.reduce((sum, a) => 
        sum + (a.taxa_desacordo_percent * a.total_anotacoes), 0
      ) / totalAnotacoes
      
      return {
        total_anotadores: this.filteredAnnotators.length,
        total_anotacoes: totalAnotacoes,
        taxa_desacordo_global_percent: Math.round(taxaDesacordoMedia * 10) / 10
      }
    }
  },
  watch: {
    // Aplicar filtros automaticamente quando mudarem
    'filters.annotator_id'() {
      console.log('DEBUG: Filtro de anotador mudou')
    },
    'filters.categoria_label'() {
      console.log('DEBUG: Filtro de categoria mudou')
    },
    'filters.estado_desacordo'() {
      console.log('DEBUG: Filtro de estado mudou')
    },
    'filters.sort_by'() {
      console.log('DEBUG: Ordenação mudou')
    },
    'filters.order'() {
      console.log('DEBUG: Ordem mudou')
    }
  },
  async created() {
    console.log('DEBUG: Página criada, projectId:', this.projectId)
    await this.loadInitialData()
  },
  methods: {
    async loadInitialData() {
      try {
        this.isLoading = true
        
        console.log('DEBUG: Iniciando carregamento de dados...')
        console.log('DEBUG: Project ID:', this.projectId)
        
        // Carregar metadados
        console.log('DEBUG: Carregando metadados...')
        this.metadata = await this.$repositories.annotatorReport.fetchMetadata(this.projectId)
        console.log('DEBUG: Metadados carregados:', this.metadata)
        
        // Carregar relatório inicial
        console.log('DEBUG: Carregando relatório inicial...')
        await this.loadReport()
        
      } catch (error) {
        console.error('DEBUG: Erro ao carregar dados:', error)
        console.error('DEBUG: Detalhes do erro:', error.response?.data)
        this.$toast.error('Erro ao carregar dados do relatório')
      } finally {
        this.isLoading = false
      }
    },
    
    async loadReport() {
      try {
        // Só carrega dados se ainda não foram carregados
        if (this.report && this.report.detalhe_anotadores && this.report.detalhe_anotadores.length > 0) {
          console.log('DEBUG: Dados já carregados, usando dados existentes')
          return
        }
        
        this.isLoading = true
        console.log('DEBUG: Carregando relatório com filtros básicos (sem filtros aplicados):', { sort_by: 'total_anotacoes', order: 'desc' })
        
        // Carregar dados sem filtros aplicados - os filtros serão aplicados localmente
        const basicFilters = {
          sort_by: 'total_anotacoes',
          order: 'desc',
          page: 1,
          page_size: 100  // Carregar todos os dados
        }
        
        const reportData = await this.$repositories.annotatorReport.fetchReport(this.projectId, basicFilters)
        console.log('DEBUG: Dados do relatório carregados:', reportData)
        
        this.report = reportData
        this.totalItems = reportData.detalhe_anotadores.length
        
        console.log('DEBUG: Total de itens carregados:', this.totalItems)
        
      } catch (error) {
        console.error('DEBUG: Erro ao carregar relatório:', error)
        console.error('DEBUG: Detalhes do erro do relatório:', error.response?.data)
        this.$toast.error('Erro ao carregar relatório')
      } finally {
        this.isLoading = false
      }
    },
    
    applyFilters() {
      // Os filtros agora são aplicados localmente via computed property
      // Não é necessário recarregar dados da API
      console.log('DEBUG: Filtros aplicados localmente:', this.filters)
      console.log('DEBUG: Resultados filtrados:', this.filteredAnnotators.length)
    },
    
    clearFilters() {
      this.filters = {
        dataset_id: [],
        annotator_id: [],
        data_inicial: '',
        data_final: '',
        categoria_label: [],
        perspectiva_id: [],
        estado_desacordo: 'todos',
        sort_by: 'total_anotacoes',
        order: 'desc',
        page: 1,
        page_size: 10
      }
      console.log('DEBUG: Filtros limpos')
    },
    
    async updatePage(page) {
      this.currentPage = page
      this.filters.page = page
      await this.loadReport()
    },
    
    async updateItemsPerPage(itemsPerPage) {
      this.itemsPerPage = itemsPerPage
      this.filters.page_size = itemsPerPage
      this.currentPage = 1
      this.filters.page = 1
      await this.loadReport()
    },
    
    async exportReport(format) {
      try {
        this.isExporting = true
        
        // Usar dados filtrados localmente em vez de chamar API
        if (!this.filteredAnnotators || this.filteredAnnotators.length === 0) {
          this.$toast.error('Não há dados para exportar com os filtros aplicados')
          return
        }
        
        console.log('DEBUG: Exportando', this.filteredAnnotators.length, 'registros em formato', format)
        
        // Criar dados para exportação baseados nos dados filtrados
        const exportData = {
          ...this.report,
          detalhe_anotadores: this.filteredAnnotators,
          resumo_global: this.filteredSummary,
          filtros_aplicados: this.filters
        }
        
        // Simular exportação local para CSV
        if (format === 'csv') {
          this.exportToCSVLocal(exportData)
        } else {
          // Para PDF, ainda usar a API mas com dados filtrados
          const blob = await this.$repositories.annotatorReport.exportReport(this.projectId, {
            ...this.filters,
            format
          })
          
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `relatorio-anotadores-${this.projectId}.${format}`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
        }
        
        this.$toast.success(`Relatório exportado em ${format.toUpperCase()}`)
        
      } catch (error) {
        console.error('Erro ao exportar:', error)
        this.$toast.error('Erro ao exportar relatório')
      } finally {
        this.isExporting = false
      }
    },
    
    exportToCSVLocal(data) {
      // Criar CSV localmente
      const headers = [
        'ID Anotador', 'Nome', 'Total Anotações', 'Datasets Distintos',
        'Tempo Total (min)', 'Tempo Médio por Anotação (seg)',
        'Taxa Desacordo (%)', 'Desacordos Resolvidos', 'Score Concordância',
        'Perspectivas Usadas', 'Categorias Mais Frequentes',
        'Primeira Anotação', 'Última Anotação'
      ]
      
      let csvContent = headers.join(',') + '\n'
      
      data.detalhe_anotadores.forEach(annotator => {
        const row = [
          annotator.annotator_id,
          `"${annotator.nome_anotador}"`,
          annotator.total_anotacoes,
          annotator.datasets_distintos,
          annotator.tempo_total_min.toFixed(1),
          annotator.tempo_medio_por_anotacao_seg.toFixed(1),
          annotator.taxa_desacordo_percent.toFixed(1),
          annotator.desacordos_resolvidos,
          annotator.score_concordancia_medio.toFixed(2),
          `"${annotator.perspectivas_usadas.join(', ')}"`,
          `"${annotator.categorias_mais_frequentes.join(', ')}"`,
          annotator.primeira_anotacao ? new Date(annotator.primeira_anotacao).toLocaleDateString('pt-PT') : '',
          annotator.ultima_anotacao ? new Date(annotator.ultima_anotacao).toLocaleDateString('pt-PT') : ''
        ]
        csvContent += row.join(',') + '\n'
      })
      
      // Download CSV
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `relatorio-anotadores-${this.projectId}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    },
    
    getInitials(name) {
      if (!name) return 'A'
      return name
        .split(' ')
        .map(part => part.charAt(0).toUpperCase())
        .slice(0, 2)
        .join('')
    },
    
    getDisagreementColor(percent) {
      if (percent < 10) return 'green'
      if (percent < 25) return 'orange'
      return 'red'
    },
    
    getScoreColor(score) {
      if (score > 0.8) return 'green'
      if (score > 0.6) return 'orange'
      return 'red'
    },
    
    formatTime(minutes) {
      if (minutes < 60) return `${minutes.toFixed(0)}min`
      const hours = Math.floor(minutes / 60)
      const mins = Math.floor(minutes % 60)
      return `${hours}h ${mins}min`
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('pt-PT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
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

.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-2px);
}
</style> 