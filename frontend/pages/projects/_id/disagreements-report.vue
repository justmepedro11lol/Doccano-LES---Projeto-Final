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

    <!-- Tabela de Desacordos -->
    <v-row v-if="hasDiscrepancies">
      <v-col cols="12">
        <v-card>
          <v-card-title class="headline primary white--text">
            Annotations and Disagreements Report
            <v-spacer></v-spacer>
            <v-chip color="white" text-color="primary" class="ml-2">
              Threshold: {{ safeProject.minPercentage }}%
            </v-chip>
            <v-chip color="white" text-color="primary" class="ml-2">
              Total: {{ totalDiscrepancies }} disagreements
            </v-chip>
          </v-card-title>

          <v-card-text class="pt-4">
            <div v-if="loading" class="d-flex justify-center align-center" style="height: 200px">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </div>
            
            <div v-else>
              <!-- Filters -->
              <v-row>
                <v-col cols="12" sm="6" md="3">
                  <v-select
                    v-model="filters.label"
                    :items="labels"
                    label="Filter by Label"
                    clearable
                    outlined
                    dense
                    prepend-icon="mdi-label"
                    @change="applyFilters"
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select
                    v-model="filters.annotator"
                    :items="annotators"
                    label="Filter by Annotator"
                    clearable
                    outlined
                    dense
                    prepend-icon="mdi-account"
                    @change="applyFilters"
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select
                    v-model="filters.reportType"
                    :items="['CSV', 'PDF']"
                    label="Report Type"
                    clearable
                    outlined
                    dense
                    prepend-icon="mdi-file-document"
                    :disabled="false"
                    class="clickable-select"
                    @change="onReportTypeChange"
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select
                    v-model="filters.perspective"
                    :items="perspectives || []"
                    label="Filter by Perspective"
                    clearable
                    outlined
                    dense
                    prepend-icon="mdi-eye"
                    @change="applyFilters"
                  ></v-select>
                </v-col>
              </v-row>

              <!-- Search bar with buttons -->
              <v-row class="mb-4">
                <v-col cols="12" md="6" class="d-flex align-center">
                  <v-text-field
                    v-model="search"
                    label="Search"
                    prepend-icon="mdi-magnify"
                    outlined
                    dense
                    clearable
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="6" class="d-flex align-center justify-end">
                  <v-btn
                    color="primary"
                    :loading="generatingReport"
                    class="mr-2"
                    @click="generateAndExportReport"
                  >
                    <v-icon left>mdi-download</v-icon>
                    Generate and Export
                  </v-btn>
                  <v-btn
                    color="error"
                    @click="cancelReport"
                  >
                    <v-icon left>mdi-close</v-icon>
                    Cancel
                  </v-btn>
                </v-col>
              </v-row>
                
              <v-data-table
                :headers="headers"
                :items="filteredDiscrepancyItems"
                :items-per-page="10"
                class="elevation-1"
                :search="search"
              >
                <template #[`item.text`]="{ item }">
                  <div class="text-truncate" style="max-width: 300px;" :title="item.text">
                    {{ item.text }}
                  </div>
                </template>
                <template #[`item.agreementRate`]="{ item }">
                  <v-chip :color="getAgreementColor(item.agreementRate)" dark small>
                    {{ item.agreementRate.toFixed(2) }}%
                  </v-chip>
                  <v-progress-linear
                    class="mt-1"
                    :value="item.agreementRate"
                    height="5"
                    :color="getAgreementColor(item.agreementRate)"
                  ></v-progress-linear>
                </template>
                <template #[`item.consensus`]="{ item }">
                  <v-chip :color="item.consensus === 'Yes' ? 'success' : 'error'" dark small>
                    {{ item.consensus }}
                  </v-chip>
                </template>
                <template #[`item.details`]="{ item }">
                  <v-btn
                    small
                    color="primary"
                    @click="showDetails(item)"
                  >
                    <v-icon left small>mdi-information</v-icon>
                    Details
                  </v-btn>
                </template>
              </v-data-table>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="600px">
      <v-card>
        <v-card-title class="headline primary white--text">
          Disagreement Details
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
        label: null,
        annotator: null,
        reportType: 'PDF',
        perspective: null
      },
      labels: [],
      annotators: [],
      textTypes: [],
      perspectives: [],
      detailsDialog: false,
      selectedItem: null,
      headers: [
        { text: 'Text', value: 'text', width: '30%' },
        { text: 'Labels', value: 'labels', width: '20%' },
        { text: 'Annotators', value: 'annotators', width: '20%' },
        { 
          text: 'Agreement Rate', 
          value: 'agreementRate',
          align: 'center',
          width: '15%'
        },
        { 
          text: 'Consensus', 
          value: 'consensus',
          align: 'center',
          width: '10%'
        },
        {
          text: 'Details',
          value: 'details',
          align: 'center',
          sortable: false,
          width: '5%'
        }
      ],

      categoryMap: {},
      exampleNameMap: {},
      exampleAnnotators: {}
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
      let filtered = this.discrepancyItems
      
      // Apply label filter
      if (this.filters.label) {
        filtered = filtered.filter(item => item.labels.includes(this.filters.label))
      }
      
      // Apply annotator filter
      if (this.filters.annotator) {
        filtered = filtered.filter(item => item.annotators.includes(this.filters.annotator))
      }
      
      // Apply perspective filter (mantido para compatibilidade)
      if (this.filters.perspective) {
        filtered = filtered.filter(item => (item.perspective || 'Not defined') === this.filters.perspective)
      }
      
      return filtered
    },
    
    filteredSelectedItem() {
      if (!this.selectedItem) return {}
      
      // Remover categoria e tipo de texto dos detalhes
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { category, textType, ...filteredItem } = this.selectedItem
      return filteredItem
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
    }
  },

  mounted() {
    // Iniciar verificação de conectividade quando o componente for montado
    this.startDatabaseConnectionCheck()
  },
  
  beforeDestroy() {
    // Parar verificação quando o componente for destruído
    this.stopDatabaseConnectionCheck()
  },

  methods: {
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

    applyFilters() {
      console.log('Aplicando filtros:', this.filters)
      console.log('Items antes do filtro:', this.discrepancyItems.length)
      console.log('Items após filtro:', this.filteredDiscrepancyItems.length)
      console.log('Labels disponíveis:', this.labels)
      console.log('Primeiro item para debug:', this.discrepancyItems[0])
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
      this.generatingReport = true
      try {
        console.log('Generating and exporting report...');
        
        // Check if there's data to export
        if (!this.filteredDiscrepancyItems || this.filteredDiscrepancyItems.length === 0) {
          throw new Error('No data to export. Please check the applied filters.');
        }
        
        // Generate filename
        const projectName = this.safeProject.name || 'project';
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `disagreements-report-${projectName}-${timestamp}`;
        
        // Export based on selected filter type
        const exportType = this.filters.reportType?.toLowerCase() || 'pdf';
        
        if (exportType === 'pdf') {
          await this.exportToPDF(filename);
        } else if (exportType === 'csv') {
          this.exportToCSV(filename);
        } else {
          // Default to PDF if not specified
          await this.exportToPDF(filename);
        }
        
        this.reportGenerated = true
        
        if (this.$toast) {
          this.$toast.success(`${exportType.toUpperCase()} report exported successfully`);
        } else {
          console.log(`${exportType.toUpperCase()} report exported successfully`);
        }
      } catch (error) {
        console.error('Error generating and exporting report:', error);
        
        if (this.$toast) {
          this.$toast.error(`Export error: ${error.message}`);
        } else {
          alert('Error generating report: ' + error.message);
        }
      } finally {
        this.generatingReport = false
      }
    },
    toggleDatabaseError() {
      this.showDatabaseError = !this.showDatabaseError
    },
    cancelReport() {
      this.$router.push(`/projects/${this.projectId}/reports`);
    },
    onReportTypeChange(value) {
      this.filters.reportType = value;
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
    exportToCSV(filename) {
      try {
        if (!this.filteredDiscrepancyItems || this.filteredDiscrepancyItems.length === 0) {
          throw new Error('No data to export.');
        }
        
        const csvData = this.filteredDiscrepancyItems.map(item => ({
          Text: item.text,
          Labels: item.labels,
          Annotators: item.annotators,
          'Agreement Rate': item.agreementRate.toFixed(2) + '%',
          Consensus: item.consensus
        }));
        
        const columns = Object.keys(csvData[0]);
        let csvContent = columns.join(',');
        
        csvData.forEach(row => {
          const rowValues = columns.map(col => {
            const cell = row[col] ? String(row[col]) : '';
            return cell.includes(',') || cell.includes('"') 
              ? '"' + cell.replace(/"/g, '""') + '"' 
              : cell;
          });
          csvContent += '\n' + rowValues.join(',');
        });
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        
        if (window.navigator && window.navigator.msSaveOrOpenBlob) {
          window.navigator.msSaveOrOpenBlob(blob, `${filename}.csv`);
          return;
        }
        
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${filename}.csv`;
        
        document.body.appendChild(link);
        link.click();
        
        setTimeout(() => {
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        }, 100);
             } catch (error) {
         console.error('Error generating CSV:', error);
         throw new Error('Could not generate CSV: ' + error.message);
       }
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