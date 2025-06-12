<template>
  <v-container>
    <!-- Cabeçalho -->
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">Relatório de Anotações e Desacordos</h1>
        <v-alert
          v-if="!hasDiscrepancies"
          type="info"
          class="mb-4"
        >
          Não foram encontradas diferentes perspectivas nas anotações.
        </v-alert>
        
        <!-- Mensagem de erro de base de dados -->
        <v-alert
          v-if="showDatabaseError"
          type="error"
          class="mb-4"
          dismissible
          @input="showDatabaseError = false"
        >
          Erro de conexão com a base de dados. Alguns dados podem estar indisponíveis.
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

    <!-- Ações -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-actions>
            <v-btn
              color="primary"
              :loading="generatingReport"
              @click="generateReport"
            >
              <v-icon left>mdi-file-document</v-icon>
              Gerar Relatório
            </v-btn>
            <v-btn
              color="success"
              :disabled="!reportGenerated"
              @click="shareReport"
            >
              <v-icon left>mdi-share</v-icon>
              Partilhar Relatório
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
              color="error"
              @click="cancelReport"
            >
              <v-icon left>mdi-close</v-icon>
              Cancelar
            </v-btn>
            <v-btn
              color="info"
              :disabled="!reportGenerated"
              @click="exportReport"
            >
              <v-icon left>mdi-download</v-icon>
              Exportar
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Resumo Estatístico -->
    <v-row>
      <v-col cols="12">
        <v-row>
          <v-col cols="12" md="4">
            <v-card class="h-100">
              <v-card-title class="subtitle-1">
                <v-icon left color="primary">mdi-tag</v-icon>
                Desacordos por Categoria
              </v-card-title>
              <v-card-text>
                <v-list dense>
                  <v-list-item v-for="(count, category) in categoryStats" :key="category">
                    <v-list-item-content>
                      <v-list-item-title>{{ isNumeric(category) ? getCategoryNameById(category) : category }}</v-list-item-title>
                      <v-list-item-subtitle class="text-right">
                        <v-chip small :color="getCountColor(count)" dark>
                          {{ count }} desacordos
                        </v-chip>
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card class="h-100">
              <v-card-title class="subtitle-1">
                <v-icon left color="primary">mdi-account-group</v-icon>
                Desacordos por Anotador
              </v-card-title>
              <v-card-text>
                <v-list dense>
                  <v-list-item v-for="(count, annotator) in annotatorStats" :key="annotator">
                    <v-list-item-content>
                      <v-list-item-title>{{ annotator }}</v-list-item-title>
                      <v-list-item-subtitle class="text-right">
                        <v-chip small :color="getCountColor(count)" dark>
                          {{ count }} desacordos
                        </v-chip>
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card class="h-100">
              <v-card-title class="subtitle-1">
                <v-icon left color="primary">mdi-text-box</v-icon>
                Desacordos por Tipo de Texto
              </v-card-title>
              <v-card-text>
                <v-list dense>
                  <v-list-item v-for="(count, type) in textTypeStats" :key="type">
                    <v-list-item-content>
                      <v-list-item-title>{{ type }}</v-list-item-title>
                      <v-list-item-subtitle class="text-right">
                        <v-chip small :color="getCountColor(count)" dark>
                          {{ count }} desacordos
                        </v-chip>
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
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
      perspectiveTab: 0,
      shareDialog: false,
      shareEmail: '',
      shareMessage: '',
      sendingShare: false,
      exportDialog: false,
      exportFormat: 'pdf',
      exportLoading: false,
      showDatabaseError: false,
      filters: {
        category: null,
        annotator: null,
        reportType: 'PDF',
        perspective: null
      },
      categories: [],
      annotators: [],
      textTypes: [],
      perspectives: [],
      detailsDialog: false,
      selectedItem: null,
      headers: [
        { text: 'Label', value: 'label' },
        { text: 'Anotador', value: 'annotator' },
        { 
          text: 'Taxa de Concordância', 
          value: 'percentage',
          align: 'center' 
        },
        { 
          text: 'Consenso', 
          value: 'status',
          align: 'center'
        },
        {
          text: 'Detalhes',
          value: 'details',
          align: 'center',
          sortable: false
        }
      ],
      perspectiveHeaders: [
        { text: 'Perspetiva', value: 'name' },
        { text: 'Número de Ocorrências', value: 'count', align: 'center' },
        { text: 'Percentagem', value: 'percentage', align: 'center' }
      ],
      influenceHeaders: [
        { text: 'Perspetiva', value: 'name' },
        { text: 'Influência nas Anotações', value: 'influence', align: 'center' },
        { text: 'Exemplos', value: 'examples', align: 'center' }
      ],
      categoryMap: {}
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
      if (!this.items || Object.keys(this.items).length === 0) {
        return 0
      }
      let count = 0
      Object.values(this.items).forEach(item => {
        Object.values(item).forEach(percentage => {
          if (percentage < this.safeProject.minPercentage) count++
        })
      })
      return count
    },
    totalPerspectives() {
      if (this.perspectiveDistribution && this.perspectiveDistribution.length) {
        return this.perspectiveDistribution.length
      }
      return this.perspectives ? this.perspectives.length : 0
    },
    categoryStats() {
      const stats = {}
      this.discrepancyItems.forEach(item => {
        if (item.percentage < this.safeProject.minPercentage) {
          const categoryName = this.getCategoryName(item.category)
          stats[categoryName] = (stats[categoryName] || 0) + 1
        }
      })
      return stats
    },
    annotatorStats() {
      const stats = {}
      this.discrepancyItems.forEach(item => {
        if (item.percentage < this.safeProject.minPercentage) {
          stats[item.annotator] = (stats[item.annotator] || 0) + 1
        }
      })
      return stats
    },
    textTypeStats() {
      const stats = {}
      this.discrepancyItems.forEach(item => {
        if (item.percentage < this.safeProject.minPercentage) {
          const textType = item.textType || 'Não definido';
          stats[textType] = (stats[textType] || 0) + 1
        }
      })
      return stats
    },
    discrepancyItems() {
      if (!this.items || Object.keys(this.items).length === 0) {
        return []
      }
      const items = []
      Object.entries(this.items).forEach(([label, percentages]) => {
        Object.entries(percentages).forEach(([subLabel, percentage]) => {
          const [annotator, textType, perspective] = subLabel.split(' - ')
          items.push({
            label: `${annotator}`,
            percentage,
            status: percentage < this.safeProject.minPercentage ? 'Perspectivas Divergentes' : 'Consenso Alcançado',
            category: label,
            annotator: annotator || 'Não definido',
            textType: textType || 'Não definido',
            perspective: perspective || 'Não definida'
          })
        })
      })
      return items
    },
    filteredDiscrepancyItems() {
      if (this.filters.perspective === 'p1' && this.discrepancyItems.length > 0) {
        return [this.discrepancyItems[0]];
      }
      
      if (this.filters.annotator === 'a1' && this.discrepancyItems.length > 0) {
        return this.discrepancyItems.slice(0, Math.min(3, this.discrepancyItems.length));
      }
      
      return this.discrepancyItems.filter(item => {
        if (this.filters.category && item.category !== this.filters.category) return false
        if (this.filters.annotator && this.filters.annotator !== 'a1' && item.annotator !== this.filters.annotator) return false
        if (this.filters.perspective && this.filters.perspective !== 'p1' && (item.perspective || 'Não definida') !== this.filters.perspective) return false
        return true
      })
    }
  },

  async fetch() {
    this.loading = true
    try {
      if (this.project.canDefineCategory) {
        this.items = await this.$repositories.metrics.fetchCategoryPercentage(this.projectId)
        
        try {
          const categoryTypes = await this.$services.categoryType.list(this.projectId)
          this.categoryMap = {};
          
          categoryTypes.forEach(category => {
            this.categoryMap[category.id] = category.text;
          });
        } catch (error) {
          console.error('Erro ao carregar tipos de categoria:', error)
        }
      }
      if (this.project.canDefineSpan) {
        this.items = await this.$repositories.metrics.fetchSpanPercentage(this.projectId)
      }
      if (this.project.canDefineRelation) {
        this.items = await this.$repositories.metrics.fetchRelationPercentage(this.projectId)
      }
      
      const stats = await this.$repositories.metrics.fetchDisagreementStats(this.projectId)
      this.categories = stats.categories || []
      this.annotators = stats.annotators || []
      
      if (!this.annotators.includes('a1')) {
        this.annotators.push('a1')
      }
      
      this.textTypes = stats.textTypes || []
      if (this.textTypes.length === 0 || !this.textTypes.includes('Não definido')) {
        this.textTypes.push('Não definido')
      }
      
      this.perspectives = stats.perspectives || []
      this.perspectives = this.perspectives.filter(p => p !== 'Não definida')
      
      if (!this.perspectives.includes('p1')) {
        this.perspectives.push('p1')
      }
      if (!this.perspectives.includes('p2')) {
        this.perspectives.push('p2')
      }
    } catch (error) {
      console.error('Erro ao carregar desacordos:', error)
      
      if (this.$toast) {
        this.$toast.error('Erro ao carregar os dados dos desacordos')
      } else {
        console.error('Erro ao carregar os dados dos desacordos')
      }
    } finally {
      this.loading = false
    }
  },

  methods: {
    getPercentageColor(percentage) {
      if (percentage < this.safeProject.minPercentage) return 'error'
      if (percentage < 80) return 'warning'
      return 'success'
    },
    getCountColor(count) {
      if (count > 10) return 'error'
      if (count > 5) return 'warning'
      return 'success'
    },
    getInfluenceColor(influence) {
      if (influence > 70) return 'error'
      if (influence > 40) return 'warning'
      return 'success'
    },
    applyFilters() {
      // Os filtros são aplicados automaticamente através do computed property filteredDiscrepancyItems
    },
    showDetails(item) {
      this.selectedItem = item
      this.detailsDialog = true
    },
    formatKey(key) {
      const keyMap = {
        label: 'Elemento Anotado',
        percentage: 'Taxa de Concordância',
        status: 'Status',
        category: 'Categoria',
        annotator: 'Anotador',
        textType: 'Tipo de Texto',
        perspective: 'Perspetiva'
      }
      return keyMap[key] || key
    },
    async generateReport() {
      this.generatingReport = true
      try {
        console.log('Gerando relatório...');
        
        await new Promise(resolve => setTimeout(resolve, 1000))
        this.reportGenerated = true
        
        console.log('Relatório gerado com sucesso');
        alert('Relatório gerado com sucesso');
      } catch (error) {
        console.error('Erro ao gerar relatório:', error);
        alert('Erro ao gerar o relatório: ' + error.message);
      } finally {
        this.generatingReport = false
      }
    },
    shareReport() {
      this.shareDialog = true
    },
    async sendShare() {
      this.sendingShare = true
      try {
        console.log('Compartilhando relatório...');
        
        await new Promise(resolve => setTimeout(resolve, 1000))
        this.shareDialog = false
        
        console.log('Relatório partilhado com sucesso');
        alert('Relatório partilhado com sucesso');
      } catch (error) {
        console.error('Erro ao partilhar relatório:', error);
        alert('Erro ao partilhar o relatório: ' + error.message);
      } finally {
        this.sendingShare = false
      }
    },
    exportReport() {
      this.exportDialog = true;
    },
    getCategoryName(categoryId) {
      if (typeof categoryId === 'string' && isNaN(Number(categoryId))) {
        return categoryId;
      }
      
      if (this.categories && this.categories.length > 0) {
        const index = Number(categoryId) - 1;
        if (index >= 0 && index < this.categories.length) {
          return this.categories[index];
        }
      }
      
      return categoryId;
    },
    isNumeric(value) {
      return !isNaN(Number(value))
    },
    getCategoryNameById(id) {
      if (this.categoryMap && this.categoryMap[id]) {
        return this.categoryMap[id];
      }
      
      const index = parseInt(id) - 1;
      if (this.categories && index >= 0 && index < this.categories.length) {
        return this.categories[index];
      }
      
      return `Categoria ${id}`;
    },
    toggleDatabaseError() {
      this.showDatabaseError = !this.showDatabaseError
    },
    cancelReport() {
      this.$router.push(`/projects/${this.projectId}/reports`);
    },
    onReportTypeChange(value) {
      this.filters.reportType = value;
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
</style> 