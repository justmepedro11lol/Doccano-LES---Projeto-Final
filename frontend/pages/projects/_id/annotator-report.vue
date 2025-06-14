<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center mb-6">
          <v-btn icon class="mr-4" @click="$router.back()">
            <v-icon>{{ mdiArrowLeft }}</v-icon>
          </v-btn>
          <h1 class="text-h4">Relatório de Anotadores</h1>
        </div>
      </v-col>
    </v-row>

    <!-- Filtros -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-title>
            <v-icon left>{{ mdiFilter }}</v-icon>
            Filtros
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.annotator_id"
                  :items="metadata.annotators"
                  :loading="loadingMetadata"
                  item-text="name"
                  item-value="id"
                  label="Anotadores"
                  multiple
                  chips
                  clearable
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.dataset_id"
                  :items="metadata.datasets"
                  :loading="loadingMetadata"
                  item-text="name"
                  item-value="id"
                  label="Datasets"
                  multiple
                  chips
                  clearable
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="3">
                <v-menu
                  v-model="dateStartMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template #activator="{ on, attrs }">
                    <v-text-field
                      v-model="filters.data_inicial"
                      label="Data Inicial"
                      prepend-icon="mdi-calendar"
                      readonly
                      clearable
                      v-bind="attrs"
                      v-on="on"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="filters.data_inicial"
                    @input="dateStartMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
              
              <v-col cols="12" md="3">
                <v-menu
                  v-model="dateEndMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template #activator="{ on, attrs }">
                    <v-text-field
                      v-model="filters.data_final"
                      label="Data Final"
                      prepend-icon="mdi-calendar"
                      readonly
                      clearable
                      v-bind="attrs"
                      v-on="on"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="filters.data_final"
                    @input="dateEndMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12" md="4">
                <v-select
                  v-model="filters.categoria_label"
                  :items="metadata.categories"
                  :loading="loadingMetadata"
                  label="Categorias"
                  multiple
                  chips
                  clearable
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-select
                  v-model="filters.perspectiva_id"
                  :items="metadata.perspectives"
                  :loading="loadingMetadata"
                  item-text="name"
                  item-value="id"
                  label="Perspectivas"
                  multiple
                  chips
                  clearable
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-select
                  v-model="filters.estado_desacordo"
                  :items="metadata.disagreement_states"
                  :loading="loadingMetadata"
                  item-text="label"
                  item-value="value"
                  label="Estado do Desacordo"
                  clearable
                ></v-select>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="filters.sort_by"
                  :items="metadata.sort_options"
                  :loading="loadingMetadata"
                  item-text="label"
                  item-value="value"
                  label="Ordenar por"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.order"
                  :items="[
                    { text: 'Decrescente', value: 'desc' },
                    { text: 'Crescente', value: 'asc' }
                  ]"
                  item-text="text"
                  item-value="value"
                  label="Ordem"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.page_size"
                  :items="[5, 10, 20, 50]"
                  label="Itens por página"
                ></v-select>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12">
                <v-btn
                  :loading="loadingReport"
                  color="primary"
                  class="mr-2"
                  @click="generateReport"
                >
                  <v-icon left>{{ mdiChartBox }}</v-icon>
                  Gerar Relatório
                </v-btn>
                
                <v-btn
                  :loading="loadingExport"
                  :disabled="!reportData"
                  color="success"
                  class="mr-2"
                  @click="exportReport('csv')"
                >
                  <v-icon left>{{ mdiFileExcel }}</v-icon>
                  Exportar CSV
                </v-btn>
                
                <v-btn
                  :loading="loadingExport"
                  :disabled="!reportData"
                  color="error"
                  class="mr-2"
                  @click="exportReport('pdf')"
                >
                  <v-icon left>{{ mdiFileDocument }}</v-icon>
                  Exportar PDF
                </v-btn>
                
                <v-btn
                  color="grey"
                  outlined
                  @click="clearFilters"
                >
                  <v-icon left>{{ mdiRefresh }}</v-icon>
                  Limpar Filtros
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Resumo Global -->
    <v-row v-if="reportData">
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-title>
            <v-icon left>{{ mdiChartLine }}</v-icon>
            Resumo Global
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-card color="primary" dark>
                  <v-card-text>
                    <div class="text-h4">{{ reportData.resumo_global.total_anotadores }}</div>
                    <div>Total de Anotadores</div>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-card color="success" dark>
                  <v-card-text>
                    <div class="text-h4">{{ reportData.resumo_global.total_anotacoes.toLocaleString() }}</div>
                    <div>Total de Anotações</div>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-card color="warning" dark>
                  <v-card-text>
                    <div class="text-h4">{{ reportData.resumo_global.taxa_desacordo_global_percent }}%</div>
                    <div>Taxa de Desacordo Global</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabela de Anotadores -->
    <v-row v-if="reportData">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>{{ mdiTable }}</v-icon>
            Detalhes dos Anotadores
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="tableHeaders"
              :items="reportData.detalhe_anotadores"
              :loading="loadingReport"
              :items-per-page="filters.page_size"
              :page="filters.page"
              class="elevation-1"
              @update:page="updatePage"
            >
              <template #[`item.nome_anotador`]="{ item }">
                <div class="d-flex align-center">
                  <v-avatar size="32" color="primary" class="white--text mr-2">
                    {{ getInitials(item.nome_anotador) }}
                  </v-avatar>
                  {{ item.nome_anotador }}
                </div>
              </template>
              
              <template #[`item.tempo_total_min`]="{ item }">
                {{ item.tempo_total_min.toFixed(1) }} min
              </template>
              
              <template #[`item.tempo_medio_por_anotacao_seg`]="{ item }">
                {{ item.tempo_medio_por_anotacao_seg.toFixed(1) }} seg
              </template>
              
              <template #[`item.taxa_desacordo_percent`]="{ item }">
                <v-chip
                  :color="getDisagreementColor(item.taxa_desacordo_percent)"
                  text-color="white"
                  small
                >
                  {{ item.taxa_desacordo_percent.toFixed(1) }}%
                </v-chip>
              </template>
              
              <template #[`item.score_concordancia_medio`]="{ item }">
                <v-progress-linear
                  :value="item.score_concordancia_medio * 100"
                  :color="getAgreementColor(item.score_concordancia_medio)"
                  height="20"
                  background-color="grey lighten-3"
                >
                  <small>{{ item.score_concordancia_medio.toFixed(2) }}</small>
                </v-progress-linear>
              </template>
              
              <template #[`item.perspectivas_usadas`]="{ item }">
                <v-chip
                  v-for="perspective in item.perspectivas_usadas"
                  :key="perspective"
                  small
                  class="mr-1"
                >
                  {{ perspective }}
                </v-chip>
              </template>
              
              <template #[`item.categorias_mais_frequentes`]="{ item }">
                <v-chip
                  v-for="category in item.categorias_mais_frequentes"
                  :key="category"
                  small
                  outlined
                  class="mr-1"
                >
                  {{ category }}
                </v-chip>
              </template>
              
              <template #[`item.primeira_anotacao`]="{ item }">
                {{ formatDate(item.primeira_anotacao) }}
              </template>
              
              <template #[`item.ultima_anotacao`]="{ item }">
                {{ formatDate(item.ultima_anotacao) }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Gráficos -->
    <v-row v-if="reportData && showCharts">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Distribuição de Anotações por Anotador</v-card-title>
          <v-card-text>
            <div ref="annotationsChart" style="height: 300px;"></div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Taxa de Desacordo por Anotador</v-card-title>
          <v-card-text>
            <div ref="disagreementChart" style="height: 300px;"></div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Loading/Error States -->
    <v-row v-if="loadingReport">
      <v-col cols="12">
        <v-card>
          <v-card-text class="text-center">
            <v-progress-circular indeterminate size="64"></v-progress-circular>
            <div class="mt-4">Gerando relatório...</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="error">
      <v-col cols="12">
        <v-alert type="error" class="mb-4">
          {{ error }}
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import {
  mdiArrowLeft,
  mdiFilter,
  mdiChartBox,
  mdiFileExcel,
  mdiFileDocument,
  mdiRefresh,
  mdiChartLine,
  mdiTable
} from '@mdi/js'

export default {
  layout: 'project',
  
  data() {
    return {
      // Icons
      mdiArrowLeft,
      mdiFilter,
      mdiChartBox,
      mdiFileExcel,
      mdiFileDocument,
      mdiRefresh,
      mdiChartLine,
      mdiTable,
      
      // State
      loadingMetadata: false,
      loadingReport: false,
      loadingExport: false,
      error: null,
      dateStartMenu: false,
      dateEndMenu: false,
      showCharts: true,
      
      // Data
      metadata: {
        annotators: [],
        categories: [],
        perspectives: [],
        datasets: [],
        sort_options: [],
        disagreement_states: []
      },
      
      reportData: null,
      
      // Filters
      filters: {
        dataset_id: [],
        annotator_id: [],
        data_inicial: null,
        data_final: null,
        categoria_label: [],
        perspectiva_id: [],
        estado_desacordo: 'todos',
        sort_by: 'total_anotacoes',
        order: 'desc',
        page: 1,
        page_size: 10
      },
      
      // Table configuration
      tableHeaders: [
        { text: 'Anotador', value: 'nome_anotador', sortable: false },
        { text: 'Total Anotações', value: 'total_anotacoes', align: 'center' },
        { text: 'Datasets', value: 'datasets_distintos', align: 'center' },
        { text: 'Tempo Total', value: 'tempo_total_min', align: 'center' },
        { text: 'Tempo Médio', value: 'tempo_medio_por_anotacao_seg', align: 'center' },
        { text: 'Taxa Desacordo', value: 'taxa_desacordo_percent', align: 'center' },
        { text: 'Score Concordância', value: 'score_concordancia_medio', align: 'center' },
        { text: 'Perspectivas', value: 'perspectivas_usadas', sortable: false },
        { text: 'Categorias Top', value: 'categorias_mais_frequentes', sortable: false },
        { text: 'Primeira Anotação', value: 'primeira_anotacao', align: 'center' },
        { text: 'Última Anotação', value: 'ultima_anotacao', align: 'center' }
      ]
    }
  },
  
  computed: {
    projectId() {
      return this.$route.params.id
    }
  },
  
  async created() {
    await this.loadMetadata()
  },
  
  methods: {
    async loadMetadata() {
      this.loadingMetadata = true
      this.error = null
      
      try {
        // Para demonstração, vou simular os metadados
        // Na implementação real, chamaria a API: /projects/{id}/reports/annotators/metadata
        
        // Carregar dados básicos do projeto existente
        const members = await this.$repositories.member.list(this.projectId)
        
        this.metadata = {
          annotators: members.map(member => ({
            id: member.user.toString(),
            name: member.username,
            username: member.username
          })),
          categories: ['LOC', 'ORG', 'PER', 'MISC', 'DATE', 'TIME'],
          perspectives: [
            { id: '1', name: 'Jurídica' },
            { id: '2', name: 'Linguística' },
            { id: '3', name: 'Técnica' }
          ],
          datasets: [
            { id: 'dataset_1', name: 'Dataset Principal' },
            { id: 'dataset_2', name: 'Dataset Teste' },
            { id: 'dataset_3', name: 'Dataset Validação' }
          ],
          sort_options: [
            { value: 'total_anotacoes', label: 'Total de Anotações' },
            { value: 'nome_anotador', label: 'Nome do Anotador' },
            { value: 'taxa_desacordo_percent', label: 'Taxa de Desacordo' },
            { value: 'score_concordancia_medio', label: 'Score de Concordância' },
            { value: 'tempo_total_min', label: 'Tempo Total' }
          ],
          disagreement_states: [
            { value: 'todos', label: 'Todos' },
            { value: 'em_desacordo', label: 'Em Desacordo' },
            { value: 'resolvido', label: 'Resolvido' }
          ]
        }
        
      } catch (error) {
        console.error('Erro ao carregar metadados:', error)
        this.error = 'Erro ao carregar metadados do relatório'
      } finally {
        this.loadingMetadata = false
      }
    },
    
    generateReport() {
      this.loadingReport = true
      this.error = null
      
      try {
        // Para demonstração, vou simular dados do relatório
        // Na implementação real, chamaria: /projects/{id}/reports/annotators
        
        // Simular dados realistas
        const mockAnnotators = this.metadata.annotators.map((annotator) => ({
          annotator_id: annotator.id,
          nome_anotador: annotator.name,
          total_anotacoes: Math.floor(Math.random() * 2000) + 100,
          datasets_distintos: Math.floor(Math.random() * 3) + 1,
          tempo_total_min: Math.floor(Math.random() * 500) + 50,
          tempo_medio_por_anotacao_seg: Math.floor(Math.random() * 60) + 15,
          taxa_desacordo_percent: Math.random() * 25,
          desacordos_resolvidos: Math.floor(Math.random() * 50) + 5,
          score_concordancia_medio: 0.5 + Math.random() * 0.5,
          perspectivas_usadas: ['Jurídica', 'Linguística'].slice(0, Math.floor(Math.random() * 2) + 1),
          categorias_mais_frequentes: ['LOC', 'ORG', 'PER'].slice(0, 3),
          primeira_anotacao: new Date(2024, 0, Math.floor(Math.random() * 30) + 1).toISOString(),
          ultima_anotacao: new Date(2024, 11, Math.floor(Math.random() * 30) + 1).toISOString()
        }))
        
        this.reportData = {
          filtros_aplicados: { ...this.filters },
          resumo_global: {
            total_anotadores: mockAnnotators.length,
            total_anotacoes: mockAnnotators.reduce((sum, ann) => sum + ann.total_anotacoes, 0),
            taxa_desacordo_global_percent: 17.2
          },
          detalhe_anotadores: mockAnnotators
        }
        
        // Gerar gráficos após carregar dados
        this.$nextTick(() => {
          this.generateCharts()
        })
        
      } catch (error) {
        console.error('Erro ao gerar relatório:', error)
        this.error = 'Erro ao gerar relatório de anotadores'
      } finally {
        this.loadingReport = false
      }
    },
    
    exportReport(format) {
      this.loadingExport = true
      
      try {
        // Para demonstração, vou simular a exportação
        // Na implementação real, chamaria: /projects/{id}/reports/annotators/export?format={format}
        
        if (format === 'csv') {
          this.exportToCSV()
        } else if (format === 'pdf') {
          this.exportToPDF()
        }
        
        this.$toast.success(`Relatório ${format.toUpperCase()} exportado com sucesso`)
        
      } catch (error) {
        console.error('Erro ao exportar:', error)
        this.$toast.error('Erro ao exportar relatório')
      } finally {
        this.loadingExport = false
      }
    },
    
    exportToCSV() {
      const csvData = this.reportData.detalhe_anotadores.map(item => ({
        'ID Anotador': item.annotator_id,
        'Nome': item.nome_anotador,
        'Total Anotações': item.total_anotacoes,
        'Datasets Distintos': item.datasets_distintos,
        'Tempo Total (min)': item.tempo_total_min.toFixed(1),
        'Tempo Médio (seg)': item.tempo_medio_por_anotacao_seg.toFixed(1),
        'Taxa Desacordo (%)': item.taxa_desacordo_percent.toFixed(1),
        'Desacordos Resolvidos': item.desacordos_resolvidos,
        'Score Concordância': item.score_concordancia_medio.toFixed(2),
        'Perspectivas': item.perspectivas_usadas.join(', '),
        'Categorias Frequentes': item.categorias_mais_frequentes.join(', '),
        'Primeira Anotação': this.formatDate(item.primeira_anotacao),
        'Última Anotação': this.formatDate(item.ultima_anotacao)
      }))
      
      const columns = Object.keys(csvData[0])
      let csvContent = columns.join(',')
      
      csvData.forEach(row => {
        const rowValues = columns.map(col => {
          const cell = row[col] ? String(row[col]) : ''
          return cell.includes(',') || cell.includes('"') 
            ? '"' + cell.replace(/"/g, '""') + '"' 
            : cell
        })
        csvContent += '\n' + rowValues.join(',')
      })
      
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `relatorio-anotadores-${this.projectId}.csv`
      link.click()
    },
    
    exportToPDF() {
      // Simulação da exportação PDF
      // Na implementação real, o backend geraria o PDF
      this.$toast.info('Funcionalidade de PDF será implementada no backend')
    },
    
    generateCharts() {
      if (!this.showCharts || !this.reportData) return
      
      // Simular gráficos (na implementação real, usaria Chart.js ou similar)
      this.$toast.info('Gráficos serão implementados com Chart.js')
    },
    
    clearFilters() {
      this.filters = {
        dataset_id: [],
        annotator_id: [],
        data_inicial: null,
        data_final: null,
        categoria_label: [],
        perspectiva_id: [],
        estado_desacordo: 'todos',
        sort_by: 'total_anotacoes',
        order: 'desc',
        page: 1,
        page_size: 10
      }
      this.reportData = null
    },
    
    updatePage(page) {
      this.filters.page = page
      this.generateReport()
    },
    
    getInitials(name) {
      if (!name) return 'A'
      return name
        .split(' ')
        .map(part => part.charAt(0).toUpperCase())
        .slice(0, 2)
        .join('')
    },
    
    getDisagreementColor(percentage) {
      if (percentage < 10) return 'green'
      if (percentage < 20) return 'orange'
      return 'red'
    },
    
    getAgreementColor(score) {
      if (score > 0.8) return 'green'
      if (score > 0.6) return 'orange'
      return 'red'
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('pt-PT', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.v-card {
  transition: all 0.3s ease;
}

.v-chip {
  margin: 2px;
}

.text-h4 {
  font-weight: bold;
}
</style> 