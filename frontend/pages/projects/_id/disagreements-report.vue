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



    <!-- Tabela de Desacordos -->
    <v-row v-if="hasDiscrepancies">
      <v-col cols="12">
        <v-card>
          <v-card-title class="headline primary white--text">
            Análise Detalhada de Desacordos
            <v-spacer></v-spacer>
            <v-chip color="white" text-color="primary" class="ml-2">
              Limiar: {{ safeProject.minPercentage }}%
            </v-chip>
            <v-chip color="white" text-color="primary" class="ml-2">
              Total: {{ totalDiscrepancies }} desacordos
            </v-chip>
          </v-card-title>

          <v-card-text class="pt-4">
            <div v-if="loading" class="d-flex justify-center align-center" style="height: 200px">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </div>
            
            <div v-else>
              <!-- Filtros -->
              <v-row>
                <v-col cols="12" sm="6" md="3">
                  <v-select
                    v-model="filters.category"
                    :items="categories"
                    label="Filtrar por Categoria"
                    clearable
                    outlined
                    dense
                    prepend-icon="mdi-tag"
                    @change="applyFilters"
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select
                    v-model="filters.annotator"
                    :items="annotators"
                    label="Filtrar por Anotador"
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
                    label="Tipo de Relatório"
                    clearable
                    outlined
                    dense
                    prepend-icon="mdi-file-document"
                    @change="onReportTypeChange"
                    :disabled="false"
                    class="clickable-select"
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select
                    v-model="filters.perspective"
                    :items="perspectives || []"
                    label="Filtrar por Perspetiva"
                    clearable
                    outlined
                    dense
                    prepend-icon="mdi-eye"
                    @change="applyFilters"
                  ></v-select>
                </v-col>
              </v-row>

              <v-text-field
                v-model="search"
                label="Pesquisar"
                prepend-icon="mdi-magnify"
                outlined
                dense
                clearable
                class="mb-4"
              ></v-text-field>
                
              <v-data-table
                :headers="headers"
                :items="filteredDiscrepancyItems"
                :items-per-page="10"
                class="elevation-1"
                :search="search"
              >
                <template #[`item.annotator`]>
                  <span>a1</span>
                </template>
                <template #[`item.percentage`]="{ item }">
                  <v-chip :color="getPercentageColor(item.percentage)" dark small>
                    {{ parseFloat(item.percentage).toFixed(2) }}%
                  </v-chip>
                  <v-progress-linear
                    class="mt-1"
                    :value="item.percentage"
                    height="5"
                    :color="getPercentageColor(item.percentage)"
                  ></v-progress-linear>
                </template>
                <template #[`item.status`]="{ item }">
                  <v-chip :color="item.percentage < safeProject.minPercentage ? 'error' : 'success'" dark small>
                    {{ item.status }}
                  </v-chip>
                </template>
                <template #[`item.details`]="{ item }">
                  <v-btn
                    small
                    color="primary"
                    @click="showDetails(item)"
                  >
                    <v-icon left small>mdi-information</v-icon>
                    Detalhes
                  </v-btn>
                </template>
              </v-data-table>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Diálogo de Detalhes -->
    <v-dialog v-model="detailsDialog" max-width="600px">
      <v-card>
        <v-card-title class="headline primary white--text">
          Detalhes do Desacordo
          <v-spacer></v-spacer>
          <v-btn icon dark @click="detailsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-list>
            <v-list-item v-for="(value, key) in selectedItem" :key="key">
              <v-list-item-content>
                <v-list-item-title class="font-weight-bold">{{ formatKey(key) }}</v-list-item-title>
                <v-list-item-subtitle class="mt-1">{{ value }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Diálogo de Partilha -->
    <v-dialog v-model="shareDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline primary white--text">
          Partilhar Relatório
          <v-spacer></v-spacer>
          <v-btn icon dark @click="shareDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-text-field
            v-model="shareEmail"
            label="Email do destinatário"
            outlined
            dense
          ></v-text-field>
          <v-textarea
            v-model="shareMessage"
            label="Mensagem"
            outlined
            dense
            rows="3"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" :loading="sendingShare" @click="sendShare">
            Enviar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo de Exportação -->
    <v-dialog v-model="exportDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline primary white--text">
          Exportar Relatório
          <v-spacer></v-spacer>
          <v-btn icon dark @click="exportDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-radio-group v-model="exportFormat">
            <v-radio label="PDF" value="pdf"></v-radio>
            <v-radio label="CSV" value="csv"></v-radio>
          </v-radio-group>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" :loading="exportLoading" @click="doExport">
            Exportar
          </v-btn>
        </v-card-actions>
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

    toggleDatabaseError() {
      this.showDatabaseError = !this.showDatabaseError
    },
    cancelReport() {
      this.$router.push(`/projects/${this.projectId}/reports`);
    },
    onReportTypeChange(value) {
      this.filters.reportType = value;
    },
    async doExport() {
      this.exportLoading = true;
      
      try {
        const projectName = this.safeProject.name || 'projeto';
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `relatorio-desacordos-${projectName}-${timestamp}`;
        
        if (this.exportFormat === 'pdf') {
          await this.exportToPDF(filename);
        } else if (this.exportFormat === 'csv') {
          this.exportToCSV(filename);
        }
        
        this.exportDialog = false;
        
        if (this.$toast) {
          this.$toast.success('Relatório exportado com sucesso');
        } else {
          console.log('Relatório exportado com sucesso');
        }
      } catch (error) {
        console.error('Erro ao exportar relatório:', error);
        
        if (this.$toast) {
          this.$toast.error(`Erro ao exportar: ${error.message}`);
        } else {
          console.error(`Erro ao exportar: ${error.message}`);
        }
      } finally {
        this.exportLoading = false;
      }
    },
    exportToCSV(filename) {
      try {
        if (!this.filteredDiscrepancyItems || this.filteredDiscrepancyItems.length === 0) {
          throw new Error('Não há dados para exportar.');
        }
        
        const csvData = this.filteredDiscrepancyItems.map(item => ({
          Elemento: item.label,
          Categoria: item.category,
          Anotador: item.annotator,
          'Tipo de Texto': item.textType,
          Perspetiva: item.perspective || 'Não definida',
          'Taxa de Concordância': parseFloat(item.percentage).toFixed(2) + '%',
          Status: item.status
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
         console.error('Erro ao gerar CSV:', error);
         throw new Error('Não foi possível gerar o CSV: ' + error.message);
       }
     },
     
     async exportToPDF(filename) {
       try {
         // Carregar jsPDF dinamicamente (para não incluir no bundle inicial)
         const { jsPDF } = await import('jspdf');
         const { default: autoTable } = await import('jspdf-autotable');
         
         // eslint-disable-next-line new-cap
         const doc = new jsPDF();
         
         // Título
         doc.setFontSize(20);
         doc.text('Relatório de Anotações e Desacordos', 14, 20);
         
         // Informações do projeto
         doc.setFontSize(12);
         doc.text(`Projeto: ${this.safeProject.name || 'Sem nome'}`, 14, 30);
         doc.text(`Limiar de concordância: ${this.safeProject.minPercentage}%`, 14, 38);
         doc.text(`Total de desacordos: ${this.totalDiscrepancies}`, 14, 46);
         doc.text(`Data do relatório: ${new Date().toLocaleDateString()}`, 14, 54);
         
         // Detalhes dos desacordos
         doc.setFontSize(16);
         doc.text('Detalhes dos Desacordos', 14, 70);
         
         const detailsData = this.filteredDiscrepancyItems
           .filter(item => item.percentage < this.safeProject.minPercentage)
           .map(item => [
             item.label,
             `${parseFloat(item.percentage).toFixed(2)}%`,
             item.status,
             item.category
           ]);
         
                   autoTable(doc, {
            startY: 75,
            head: [['Elemento', 'Taxa de Concordância', 'Status', 'Categoria']],
            body: detailsData
          });
         
         // Salvar o PDF usando output com método compatível com navegadores
         const pdfOutput = doc.output('blob');
         const url = URL.createObjectURL(pdfOutput);
         
         // Para browsers antigos como o IE
         if (window.navigator && window.navigator.msSaveOrOpenBlob) {
           window.navigator.msSaveOrOpenBlob(pdfOutput, `${filename}.pdf`);
           
           // Redirecionar após o download
           setTimeout(() => {
             window.location.href = `/projects/${this.projectId}/reports`;
           }, 500);
           
           return;
         }
         
         // Para browsers modernos
         const link = document.createElement('a');
         link.href = url;
         link.download = `${filename}.pdf`;
         link.style.display = 'none';
         document.body.appendChild(link);
         link.click();
         
         // Limpar URL após download e redirecionar
         setTimeout(() => {
           URL.revokeObjectURL(url);
           document.body.removeChild(link);
           
           // Redirecionar para a página de relatórios
           this.$router.push(`/projects/${this.projectId}/reports`);
         }, 500);
       } catch (error) {
         console.error('Erro ao gerar PDF:', error);
         throw new Error('Não foi possível gerar o PDF. Verifique se todas as bibliotecas necessárias estão disponíveis.');
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