<template>
  <div class="statistics-container">
    <v-card class="main-card" elevation="3">
      <v-card-title class="primary white--text d-flex align-center">
        <v-icon left color="white" size="28">mdi-chart-line</v-icon>
        <span class="text-h5">Estatísticas de Anotações</span>
      </v-card-title>

      <!-- Filtros -->
      <v-card class="filters-card ma-4" elevation="2">
        <v-card-title class="text-h6 pb-2">
          <v-icon left color="primary">mdi-filter</v-icon>
          Filtros
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <!-- Filtro de Perguntas da Perspetiva -->
            <v-col cols="12" md="6">
              <v-select
                v-model="selectedQuestions"
                :items="availableQuestions"
                item-text="question"
                item-value="id"
                label="Perguntas da Perspetiva"
                multiple
                chips
                outlined
                dense
                prepend-inner-icon="mdi-help-circle"
                :disabled="isLoading"
              >
                <template #selection="{ item, index }">
                  <v-chip
                    v-if="index < 2"
                    small
                  >
                    {{ item.question.substring(0, 30) }}{{ item.question.length > 30 ? '...' : '' }}
                  </v-chip>
                  <span v-if="index === 2" class="grey--text text-caption">
                    (+{{ selectedQuestions.length - 2 }} mais)
                  </span>
                </template>
              </v-select>
            </v-col>



            <!-- Filtro de Exemplos do Dataset -->
            <v-col cols="12" md="6">
              <v-select
                v-model="selectedExamples"
                :items="availableExamples"
                item-text="displayText"
                item-value="id"
                label="Exemplos do Dataset"
                multiple
                chips
                deletable-chips
                outlined
                dense
                prepend-inner-icon="mdi-database"
                :disabled="isLoading"
              >
                <template #selection="{ item, index }">
                  <v-chip
                    v-if="index < 2"
                    small
                    close
                    @click:close="removeExample(item.id)"
                  >
                    {{ item.displayText }}
                  </v-chip>
                  <span v-if="index === 2" class="grey--text text-caption">
                    (+{{ selectedExamples.length - 2 }} mais)
                  </span>
                </template>
              </v-select>
            </v-col>

            <!-- Filtro de Tipo de Anotações -->
            <v-col cols="12" md="6">
              <v-select
                v-model="annotationType"
                :items="annotationTypes"
                label="Tipo de Anotações"
                outlined
                dense
                prepend-inner-icon="mdi-format-list-checks"
              />
            </v-col>

            <!-- Formato de Exportação -->
            <v-col cols="12" md="6">
              <v-select
                v-model="exportFormat"
                :items="exportFormats"
                label="Formato de Exportação"
                outlined
                dense
                prepend-inner-icon="mdi-file-export"
              />
            </v-col>

                        <!-- Botões de Ação -->
            <v-col cols="12">
              <v-row class="no-gutters">
                <v-col cols="12" sm="6" md="4" class="pa-1">
                  <v-btn
                    color="primary"
                    large
                    block
                    :loading="isLoading"
                    :disabled="!canGenerateStatistics"
                    @click="generateStatistics"
                  >
                    <v-icon left>mdi-chart-bar</v-icon>
                    Gerar Estatísticas
                  </v-btn>
                </v-col>

                <v-col cols="12" sm="6" md="4" class="pa-1">
                  <v-btn
                    color="orange"
                    large
                    block
                    :disabled="isLoading"
                    @click="clearAllFilters"
                  >
                    <v-icon left>mdi-filter-remove</v-icon>
                    Limpar Filtros
                  </v-btn>
                </v-col>

                <v-col cols="12" sm="6" md="4" class="pa-1">
                  <v-btn
                    color="info"
                    large
                    block
                    :disabled="isLoading"
                    @click="goToHome"
                  >
                    <v-icon left>mdi-home</v-icon>
                    Página Inicial
                  </v-btn>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Área de Resultados -->
      <v-card v-if="hasStatistics" class="results-card ma-4" elevation="2">
        <v-card-title class="text-h6">
          <v-icon left color="success">mdi-chart-bar</v-icon>
          Resultados das Estatísticas
        </v-card-title>
        
        <v-card-text>
          <!-- Gráficos -->
          <v-row class="mb-4">
            <!-- Estatísticas de Perspectivas -->
            <v-col v-if="hasPerspectiveStatistics" cols="12">
              <v-card elevation="2" class="perspective-summary-card">
                <v-card-title class="text-h6 perspective-summary-header">
                  <v-icon left color="white">mdi-account-group</v-icon>
                  <span class="white--text">Estatísticas de Perspectivas</span>
                </v-card-title>
                <v-card-text class="pa-4">
                  <v-row>
                    <v-col cols="12" md="6">
                      <div class="text-center">
                        <div class="text-h3 primary--text">{{ totalPerspectiveResponses }}</div>
                        <div class="text-subtitle-1">Total de Respostas</div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="text-center">
                        <div class="text-h3 info--text">{{ selectedQuestionsData.length }}</div>
                        <div class="text-subtitle-1">Perguntas Analisadas</div>
                      </div>
                    </v-col>
                  </v-row>

                  <!-- Tabela detalhada das perspectivas -->
                  <v-data-table
                    :headers="perspectiveHeaders"
                    :items="perspectiveItems"
                    class="mt-4"
                    dense
                    :items-per-page="10"
                    group-by="question"
                  >
                    <template #[`item.answer`]="{ item }">
                      <v-tooltip bottom>
                        <template #activator="{ on, attrs }">
                          <span 
                            class="text-truncate cursor-pointer" 
                            style="max-width: 200px; display: inline-block;"
                            v-bind="attrs"
                            v-on="on"
                          >
                            {{ item.answer }}
                          </span>
                        </template>
                        <span>{{ item.answer }}</span>
                      </v-tooltip>
                    </template>

                    <template #[`item.count`]="{ item }">
                      <v-chip color="primary" x-small dark>
                        {{ item.count }}
                      </v-chip>
                    </template>

                    <template #[`item.percentage`]="{ item }">
                      <div class="d-flex align-center">
                        <v-progress-linear
                          :value="item.percentage"
                          color="primary"
                          height="12"
                          rounded
                          class="mr-2"
                          style="flex-grow: 1; max-width: 80px;"
                        >
                          <template #default="{ value }">
                            <span class="white--text text-caption font-weight-bold">
                              {{ Math.round(value) }}%
                            </span>
                          </template>
                        </v-progress-linear>
                        <span class="primary--text font-weight-bold text-caption">
                          {{ item.percentage.toFixed(1) }}%
                        </span>
                      </div>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </v-col>



            <!-- Gráfico de Estatísticas de Discrepâncias -->
            <v-col v-if="hasDiscrepancyStatistics" cols="12">
              <v-card elevation="2" class="statistics-summary-card">
                <v-card-title class="text-h6 statistics-summary-header">
                  <v-icon left color="white">mdi-chart-line</v-icon>
                  <span class="white--text">Resumo de Estatísticas de Discrepâncias</span>
                </v-card-title>
                <v-card-text class="pa-4">
                  <v-row>
                    <v-col cols="12" md="6">
                      <div class="text-center">
                        <div class="text-h3 error--text">{{ totalDiscrepantLabels }}</div>
                        <div class="text-subtitle-1">Com Discrepância</div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="text-center">
                        <div class="text-h3 success--text">{{ totalConsistentLabels }}</div>
                        <div class="text-subtitle-1">Consistentes</div>
                      </div>
                    </v-col>
                  </v-row>
                  
                  <!-- Resumo por exemplo -->
                  <div class="mb-4">
                    <h4 class="text-subtitle-2 mb-2">Resumo por Exemplo:</h4>
                    <v-row>
                      <v-col
                        v-for="example in uniqueExamples"
                        :key="example.exampleId"
                        cols="12"
                        md="6"
                        lg="4"
                        class="pa-2"
                      >
                        <v-card outlined class="example-summary-card">
                          <v-card-text class="pa-3">
                            <div class="d-flex align-center mb-2">
                              <v-chip
                                :color="example.hasDiscrepancy ? 'error' : 'success'"
                                x-small
                                dark
                                class="mr-2"
                              >
                                {{ example.hasDiscrepancy ? 'Discrepante' : 'Consistente' }}
                              </v-chip>
                              <span class="text-caption">Max: {{ example.maxPercentage.toFixed(1) }}%</span>
                            </div>
                            <div class="text-body-2 font-weight-medium mb-2 text-truncate">
                              {{ example.text }}
                            </div>
                            <div class="text-caption grey--text">
                              {{ example.labelCount }} anotações
                            </div>
                          </v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>
                  </div>

                  <!-- Tabela detalhada das discrepâncias -->
                  <v-data-table
                    :headers="dynamicDiscrepancyHeaders"
                    :items="discrepancyItems"
                    class="mt-4"
                    dense
                    :items-per-page="10"
                  >
                    <template #[`item.hasExampleDiscrepancy`]="{ item }">
                      <v-chip
                        :color="item.hasExampleDiscrepancy ? 'error' : 'success'"
                        dark
                        x-small
                      >
                        {{ item.hasExampleDiscrepancy ? 'Discrepante' : 'Consistente' }}
                      </v-chip>
                    </template>
                    
                    <template #[`item.maxPercentage`]="{ item }">
                      <span class="font-weight-bold">
                        {{ item.maxPercentage.toFixed(1) }}%
                      </span>
                    </template>
                    
                    <template #[`item.example`]="{ item }">
                      <v-tooltip bottom>
                        <template #activator="{ on, attrs }">
                          <span 
                            class="text-truncate cursor-pointer" 
                            style="max-width: 300px; display: inline-block;"
                            v-bind="attrs"
                            v-on="on"
                          >
                            {{ item.example }}
                          </span>
                        </template>
                        <span>{{ item.example }}</span>
                      </v-tooltip>
                    </template>

                    <!-- Templates dinâmicos para cada label -->
                    <template
                      v-for="header in dynamicDiscrepancyHeaders.filter(h => h.value.startsWith('label_'))"
                      #[`item.${header.value}`]="{ item }"
                    >
                      <div v-if="item[header.value]" :key="`progress-${header.value}`" class="d-flex align-center">
                        <v-progress-linear
                          :value="item[header.value].percentage || 0"
                          :color="item[header.value].isDiscrepant ? 'error' : 'success'"
                          height="8"
                          rounded
                          class="mr-1"
                          style="flex-grow: 1; max-width: 40px;"
                        />
                        <span 
                          :class="item[header.value].isDiscrepant ? 'error--text' : 'success--text'" 
                          class="font-weight-bold text-caption"
                        >
                          {{ item[header.value].percentage ? item[header.value].percentage.toFixed(1) : '0.0' }}%
                        </span>
                      </div>
                      <span v-else :key="`empty-${header.value}`" class="grey--text">-</span>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Mensagem quando há dados mas nenhum gráfico para mostrar -->
            <v-col v-if="selectedQuestionsData.length === 0 && selectedExamplesData.length === 0 && !hasDiscrepancyStatistics" cols="12">
              <v-alert type="warning" outlined>
                <template #prepend>
                  <v-icon>mdi-information</v-icon>
                </template>
                <strong>Dados carregados mas sem gráficos para exibir.</strong><br>
                Para ver gráficos de perspetivas, selecione pelo menos uma pergunta.<br>
                Para ver gráficos de discrepâncias, selecione pelo menos um exemplo.
              </v-alert>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Estado Vazio -->
      <v-card v-else-if="!isLoading" class="empty-state-card ma-4" elevation="1">
        <v-card-text class="text-center pa-8">
          <v-icon size="80" color="grey lighten-1" class="mb-4">mdi-chart-line</v-icon>
          <h3 class="text-h5 grey--text text--darken-1 mb-2">Nenhuma Estatística Gerada</h3>
          <p class="text-body-1 grey--text">Configure os filtros e clique em "Gerar Estatísticas" para ver os resultados.</p>
        </v-card-text>
      </v-card>

      <!-- Loading -->
      <v-card v-if="isLoading" class="loading-card ma-4" elevation="1">
        <v-card-text class="text-center pa-8">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
            class="mb-4"
          />
          <h3 class="text-h6">Gerando Estatísticas...</h3>
          <p class="text-body-2 grey--text">Por favor, aguarde enquanto processamos os dados.</p>
        </v-card-text>
      </v-card>
    </v-card>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import Chart from 'chart.js'
// eslint-disable-next-line new-cap


export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      isLoading: false,
      isExporting: false,
      
      // Filtros
      selectedQuestions: [] as number[],
      selectedExamples: [] as number[],
      annotationType: 'all',
      exportFormat: 'none',
      
      // Dados disponíveis
      availableQuestions: [] as any[],
      availableExamples: [] as any[],
      
      // Opções
      annotationTypes: [
        { text: 'Todas as Anotações', value: 'all' },
        { text: 'Com Discrepância', value: 'with_discrepancy' },
        { text: 'Sem Discrepância', value: 'without_discrepancy' }
      ],
      exportFormats: [
        { text: 'Não exportar', value: 'none' },
        { text: 'PDF', value: 'pdf' },
        { text: 'CSV', value: 'csv' },
        { text: 'PDF e CSV', value: 'both' }
      ],
      
      // Resultados
      statistics: {
        detailedData: [] as any[]
      },
      statisticsGenerated: false,

      // Instâncias dos gráficos
      questionChartInstances: [] as Chart[],
      discrepancyChartInstances: [] as Chart[],
      
      // Controle de visibilidade dos gráficos de discrepância
      visibleDiscrepancyCharts: [] as boolean[],
      
      // Headers para tabela de discrepâncias (será definido dinamicamente)
      discrepancyHeaders: [] as any[],
      
      // Headers para tabela de perspectivas
      perspectiveHeaders: [
        { text: 'Pergunta', value: 'question', sortable: false },
        { text: 'Resposta', value: 'answer', sortable: false },
        { text: 'Número de respostas', value: 'count', sortable: true },
        { text: 'Percentagem', value: 'percentage', sortable: true }
      ]
    }
  },

  computed: {
    projectId(): string {
      return this.$route.params.id
    },
    
    canGenerateStatistics(): boolean {
      // Permite gerar estatísticas se houver perguntas disponíveis (para perspectiva) ou exemplos selecionados (para discrepância)
      const hasPerspectiveData = this.availableQuestions.length > 0
      const hasDiscrepancyData = this.selectedExamples.length > 0
      
      return hasPerspectiveData || hasDiscrepancyData
    },
    
    hasStatistics(): boolean {
      return this.statisticsGenerated && this.statistics.detailedData.length > 0
    },

    selectedQuestionsData() {
      return this.availableQuestions.filter(q => this.selectedQuestions.includes(q.id))
    },

    selectedExamplesData() {
      return this.availableExamples.filter(e => this.selectedExamples.includes(e.id))
    },

    hasDiscrepancyStatistics() {
      return this.statistics.detailedData.some((item: any) => item.questionId === 'discrepancy')
    },

    discrepancyItems() {
      const items = this.statistics.detailedData.filter((item: any) => item.questionId === 'discrepancy')
      
      // Preparar dados com as labels como propriedades planas
      return items.map((item: any) => {
        const flatItem: any = {
          exampleId: item.exampleId,
          example: item.example,
          maxPercentage: item.maxPercentage,
          hasExampleDiscrepancy: item.hasExampleDiscrepancy,
          labelCount: item.labelCount,
          labels: item.labels
        }
        
        // Adicionar cada label como uma propriedade
        if (item.labels) {
          Object.values(item.labels).forEach((label: any) => {
            const key = `label_${label.name}`
            flatItem[key] = label
          })
        }
        
        return flatItem
      })
    },

    dynamicDiscrepancyHeaders() {
      const items = this.statistics.detailedData.filter((item: any) => item.questionId === 'discrepancy')
      if (items.length === 0) return []
      
      // Coletar todas as labels únicas
      const allLabels = new Set()
      items.forEach((item: any) => {
        if (item.labels) {
          Object.values(item.labels).forEach((label: any) => {
            allLabels.add(label.name)
          })
        }
      })
      
      // Criar headers base
      const headers = [
        { text: 'Exemplo', value: 'example', width: '30%', sortable: false },
        { text: 'Status Geral', value: 'hasExampleDiscrepancy', width: '15%', sortable: true },
        { text: 'Max %', value: 'maxPercentage', width: '10%', sortable: true }
      ]
      
      // Adicionar coluna para cada label
      Array.from(allLabels).forEach((labelName: any) => {
        headers.push({
          text: labelName,
          value: `label_${labelName}`,
          width: '15%',
          sortable: false
        })
      })
      
      return headers
    },

    totalDiscrepantLabels() {
      const items = this.statistics.detailedData.filter((item: any) => item.questionId === 'discrepancy')
      let total = 0
      items.forEach((item: any) => {
        if (item.labels) {
          Object.values(item.labels).forEach((label: any) => {
            if (label.isDiscrepant) total++
          })
        }
      })
      return total
    },

    totalConsistentLabels() {
      const items = this.statistics.detailedData.filter((item: any) => item.questionId === 'discrepancy')
      let total = 0
      items.forEach((item: any) => {
        if (item.labels) {
          Object.values(item.labels).forEach((label: any) => {
            if (!label.isDiscrepant) total++
          })
        }
      })
      return total
    },

    uniqueExamples() {
      const items = this.statistics.detailedData.filter((item: any) => item.questionId === 'discrepancy')
      return items.map((item: any) => ({
        exampleId: item.exampleId,
        text: item.example,
        maxPercentage: item.maxPercentage,
        hasDiscrepancy: item.hasExampleDiscrepancy,
        labelCount: item.labelCount
      }))
    },

    hasPerspectiveStatistics() {
      return this.statistics.detailedData.some((item: any) => item.questionId !== 'discrepancy')
    },

    perspectiveItems() {
      const items = this.statistics.detailedData.filter((item: any) => item.questionId !== 'discrepancy')
      const grouped: any[] = []
      
      // Agrupar por pergunta e resposta
      const questionGroups: { [key: string]: any } = {}
      
      items.forEach((item: any) => {
        const questionKey = `${item.questionId}_${item.question}`
        if (!questionGroups[questionKey]) {
          questionGroups[questionKey] = {
            questionId: item.questionId,
            question: item.question,
            answers: new Map()
          }
        }
        
        const answerKey = item.answer || 'Sem resposta'
        if (!questionGroups[questionKey].answers.has(answerKey)) {
          questionGroups[questionKey].answers.set(answerKey, 0)
        }
        questionGroups[questionKey].answers.set(answerKey, 
          questionGroups[questionKey].answers.get(answerKey) + 1
        )
      })
      
      // Converter para formato de tabela com percentagens
      Object.values(questionGroups).forEach((questionGroup: any) => {
        const counts = Array.from(questionGroup.answers.values()) as number[]
        const totalResponses = counts.reduce((a: number, b: number) => a + b, 0)
        
        questionGroup.answers.forEach((count: number, answer: string) => {
          const percentage = totalResponses > 0 ? (count / totalResponses * 100) : 0
          grouped.push({
            questionId: questionGroup.questionId,
            question: questionGroup.question,
            answer,
            count,
            percentage,
            totalResponses
          })
        })
      })
      
      return grouped
    },

    totalPerspectiveResponses() {
      return this.statistics.detailedData.filter((item: any) => item.questionId !== 'discrepancy').length
    }
  },

  watch: {
    selectedQuestions: {
      handler() {
        // Quando as perguntas mudam, pode afetar os dados disponíveis
      },
      deep: true
    },
    
    exportFormat: {
      handler() {
        // NÃO exportar automaticamente - apenas quando clicar no botão "Gerar Estatísticas"
        // Esta funcionalidade foi removida para evitar exportação indesejada
      }
    }
  },

  async mounted() {
    await this.loadInitialData()
  },

  beforeDestroy() {
    // Limpar os gráficos ao destruir o componente
    this.questionChartInstances.forEach(chart => {
      if (chart) chart.destroy()
    })
    this.discrepancyChartInstances.forEach(chart => {
      if (chart) chart.destroy()
    })
  },

  methods: {
    async loadInitialData() {
      this.isLoading = true
      try {
        await Promise.all([
          this.loadQuestions(),
          this.loadExamples()
        ])
      } catch (error) {
        console.error('Erro ao carregar dados iniciais:', error)
      } finally {
        this.isLoading = false
      }
    },

    async loadQuestions() {
      try {
        const perspectives = await this.$services.perspective.list(this.projectId)
        
        if (perspectives.length > 0) {
          const perspectiveId = perspectives[0].id
          const questions = await this.$services.question.list(perspectiveId, this.projectId)
          
          this.availableQuestions = questions.map((q: any) => ({
            id: q.id,
            question: q.question,
            type: q.type,
            perspective_id: q.perspective_id
          }))
        } else {
          this.availableQuestions = []
        }
      } catch (error) {
        console.error('❌ Erro ao carregar perguntas:', error)
        this.availableQuestions = []
      }
    },

    async loadExamples() {
      try {
        const examples = await this.$services.example.list(this.projectId, { limit: '100', offset: '0' })
        this.availableExamples = examples.items.map((example: any) => ({
          id: example.id,
          text: example.text,
          displayText: example.text.length > 50 ? example.text.substring(0, 50) + '...' : example.text
        }))
      } catch (error) {
        console.error('Erro ao carregar exemplos:', error)
      }
    },

    async generateStatistics() {
      // Permitir gerar estatísticas de perspectiva mesmo sem filtros específicos (usar todas as perguntas disponíveis)
      // Permitir gerar estatísticas de discrepância apenas se exemplos forem selecionados
      const hasPerspectiveFilters = this.selectedQuestions.length > 0 || this.availableQuestions.length > 0
      const hasDiscrepancyFilters = this.selectedExamples.length > 0
      
      if (!hasPerspectiveFilters && !hasDiscrepancyFilters) {
        alert('Não há dados disponíveis para gerar estatísticas. Verifique se há perguntas e exemplos no projeto.')
        return
      }
      
      this.isLoading = true
      try {
        // Resetar estado
        this.statisticsGenerated = false
        this.statistics = {
          detailedData: []
        }

        console.log('🔄 Iniciando geração de estatísticas...', {
          perspectiveFilters: hasPerspectiveFilters,
          discrepancyFilters: hasDiscrepancyFilters
        })

        // Carregar dados das perspectivas (perguntas/respostas) independentemente
        let perspectiveData: any[] = []
        if (hasPerspectiveFilters) {
          console.log('📊 Carregando dados de perspectivas...')
          perspectiveData = await this.loadStatisticsData()
          console.log('✅ Perspectivas carregadas:', perspectiveData.length)
        }

        // Carregar dados das discrepâncias (exemplos) independentemente
        let discrepancyData: any[] = []
        if (hasDiscrepancyFilters) {
          console.log('📈 Carregando dados de discrepâncias...')
          discrepancyData = await this.loadDiscrepancyStatistics()
          console.log('✅ Discrepâncias carregadas:', discrepancyData.length)
        }

        // Combinar todos os dados - perspectivas primeiro, depois discrepâncias
        const allData = [...perspectiveData, ...discrepancyData]
        
        // Se não houver dados, mostrar mensagem - mas não retornar erro se apenas um tipo não tem dados
        if (allData.length === 0) {
          alert('Nenhum dado encontrado com os filtros selecionados.')
          return
        }
          
        this.statistics = {
          detailedData: allData
        }
        this.statisticsGenerated = true

        // Gerar gráficos com dados existentes
        await this.$nextTick()
        this.generateCharts()
        
        // Exportar automaticamente se um formato foi selecionado
        if (this.exportFormat && this.exportFormat !== 'none') {
          await this.exportStatistics()
        }
        
        console.log('✅ Estatísticas geradas com sucesso:', {
          perspectivas: perspectiveData.length,
          discrepancias: discrepancyData.length,
          total: allData.length,
          hasPerspectiveStats: this.hasPerspectiveStatistics,
          hasDiscrepancyStats: this.hasDiscrepancyStatistics,
          detailedDataSample: allData.slice(0, 3).map(item => ({
            questionId: item.questionId,
            question: item.question,
            type: item.questionId === 'discrepancy' ? 'DISCREPANCY' : 'PERSPECTIVE'
          }))
        })
      } catch (error) {
        console.error('❌ Erro ao gerar estatísticas:', error)
        alert('Erro ao gerar estatísticas. Verifique o console para mais detalhes.')
      } finally {
        this.isLoading = false
      }
    },

    async loadStatisticsData() {
      const data: any[] = []
      
      try {
        // Carregar perspectivas do projeto
        const perspectives = await this.$services.perspective.list(this.projectId)
        
        if (perspectives.length === 0) {
          return []
        }

        // Usar a primeira perspectiva (ou todas se necessário)
        const perspective = perspectives[0]
        
        // Carregar perguntas da perspectiva
        const questions = await this.$services.question.list(perspective.id, this.projectId)
        
        // Carregar todas as respostas
        const allAnswers = await this.$services.answer.list()
        
        // Lógica de filtros para perspectiva - independente dos exemplos selecionados
        let questionsToProcess = []
        
        if (this.selectedQuestions.length > 0) {
          // Se há perguntas selecionadas, usar apenas essas
          questionsToProcess = questions.filter(q => this.selectedQuestions.includes(q.id))
        } else {
          // Se não há perguntas selecionadas, usar todas as perguntas para permitir estatísticas de perspectiva
          questionsToProcess = questions
        }
          
        // Processar cada pergunta
        for (const question of questionsToProcess) {
          // Filtrar respostas desta pergunta - verificar diferentes campos possíveis
          const questionAnswers = allAnswers.filter((answer: any) => {
            const matches = answer.question_id === question.id || 
                           answer.question === question.id ||
                           answer.questionId === question.id
            return matches
          })
          
          // Para cada resposta, criar um registro de dados
          questionAnswers.forEach((answer: any) => {
            // Para estatísticas de perspectiva, NÃO filtrar por exemplos
            // Os filtros de exemplo só se aplicam às estatísticas de discrepância
            // Esta seção é para dados de perspectiva (perguntas/respostas)
            
            const dataItem = {
              questionId: question.id,
              question: question.question,
              answer: answer.text || answer.value || answer.answer_text || answer.answer || 'Sem resposta',
              annotator: answer.user_id || answer.user || answer.annotator_id,
              exampleId: answer.example_id || answer.example || answer.exampleId
            }
            
            data.push(dataItem)
          })
        }

        return data
      } catch (error) {
        console.error('❌ Erro ao carregar dados de estatísticas:', error)
        return []
      }
    },

    async loadDiscrepancyStatistics() {
      const discrepancyData: any[] = []
      
      try {
        const project = this.$store.getters['projects/project']
        
        if (!project || this.selectedExamples.length === 0) {
          return discrepancyData
        }

        // Carregar percentagens das labels usando a mesma API que a seção de discrepâncias
        let percentages = {}
        
        if (project.canDefineCategory) {
          percentages = await this.$repositories.metrics.fetchCategoryPercentage(this.projectId)
        } else if (project.canDefineSpan) {
          percentages = await this.$repositories.metrics.fetchSpanPercentage(this.projectId)
        } else if (project.canDefineRelation) {
          percentages = await this.$repositories.metrics.fetchRelationPercentage(this.projectId)
        }

        // Filtrar apenas os exemplos selecionados que têm anotações
        const selectedPercentages: any = {}
        for (const exampleId of this.selectedExamples) {
          if ((percentages as any)[exampleId]) {
            selectedPercentages[exampleId] = (percentages as any)[exampleId]
          }
        }

        // Carregar labels do projeto para obter nomes corretos
        let labelTypes: any[] = []
        if (project.canDefineCategory) {
          labelTypes = await this.$services.categoryType.list(this.projectId)
        } else if (project.canDefineSpan) {
          labelTypes = await this.$services.spanType.list(this.projectId)  
        } else if (project.canDefineRelation) {
          labelTypes = await this.$services.relationType.list(this.projectId)
        }

        // Criar mapa de ID para nome da label
        const labelMap: { [key: string]: string } = {}
        labelTypes.forEach((labelType: any) => {
          labelMap[labelType.id] = labelType.text || labelType.name || `Label ${labelType.id}`
        })

        // Processar cada exemplo que tem anotações
        for (const [exampleId, labels] of Object.entries(selectedPercentages)) {
          // Buscar o exemplo real para obter o texto
          const example = await this.$repositories.example.findById(this.projectId, parseInt(exampleId))
          if (!example) continue

          const exampleLabels = labels as any
          const labelEntries = Object.entries(exampleLabels) as [string, number][]
          
          // Só processar se há labels anotadas
          if (!labelEntries.length) continue

          // Encontrar a percentagem máxima para determinar se há discrepância
          const maxPercentage = Math.max(...labelEntries.map(([, perc]) => perc))
          const hasDiscrepancy = maxPercentage < project.minPercentage

          // Aplicar filtro de tipo de anotação (com/sem discrepância)
          let shouldIncludeItem = true
          if (this.annotationType === 'with_discrepancy') {
            shouldIncludeItem = hasDiscrepancy
          } else if (this.annotationType === 'without_discrepancy') {
            shouldIncludeItem = !hasDiscrepancy
          }
          // Se annotationType === 'all', incluir sempre

          if (!shouldIncludeItem) {
            continue // Pular este item se não atender ao filtro
          }

          // Criar um objeto com todas as labels como propriedades
          const labelData: any = {}
          labelEntries.forEach(([labelId, percentage]) => {
            const labelName = labelMap[labelId] || `Label ${labelId}`
            labelData[labelId] = {
              name: labelName,
              percentage,
              isDiscrepant: percentage < project.minPercentage
            }
          })

          const discrepancyItem = {
            questionId: 'discrepancy',
            question: 'Análise de Discrepâncias',
            annotator: 'Sistema',
            exampleId: parseInt(exampleId),
            example: example.text,
            maxPercentage,
            hasExampleDiscrepancy: hasDiscrepancy,
            labels: labelData,
            labelCount: labelEntries.length,
            date: new Date().toISOString().split('T')[0]
          }

          discrepancyData.push(discrepancyItem)
        }

        console.log('✅ Estatísticas de discrepâncias carregadas:', discrepancyData.length)
        return discrepancyData
      } catch (error) {
        console.error('❌ Erro ao carregar estatísticas de discrepâncias:', error)
        return discrepancyData
      }
    },

    getLabelData(item: any, labelName: string) {
      if (!item.labels) return null
      
      // Procurar a label pelo nome
      const labelEntry = Object.values(item.labels).find((label: any) => label.name === labelName)
      return labelEntry || null
    },

    generateCharts() {
      console.log('📊 Usando apenas tabelas para estatísticas')
    },

    generateQuestionCharts() {
      console.log('🔵 Iniciando geração de gráficos de perspectivas...')
      
      // Limpar gráficos existentes
      this.questionChartInstances.forEach(chart => {
        if (chart) chart.destroy()
      })
      this.questionChartInstances = []

      if (this.selectedQuestionsData.length === 0) {
        console.log('🔵 Nenhuma pergunta selecionada para gráficos de perspectiva')
        return
      }

      console.log(`🔵 Processando ${this.selectedQuestionsData.length} perguntas para perspectivas`)

      this.selectedQuestionsData.forEach((question, index) => {
        console.log(`🔵 Gerando gráfico para pergunta ${index}: ${question.question}`)
        
        const canvas = this.$refs[`questionChart${index}`] as HTMLCanvasElement[]
        if (!canvas || !canvas[0]) {
          return
        }

        const ctx = canvas[0].getContext('2d')
        if (!ctx) {
          return
        }

        // Filtrar dados desta pergunta específica
        const questionData = this.statistics.detailedData.filter((item: any) => 
          item.questionId === question.id
        )

        // Agrupar respostas por resposta (não por anotador)
        const answerCounts: { [key: string]: number } = {}
        const totalResponses = questionData.length

        questionData.forEach((item: any) => {
          const answer = item.answer || 'Sem resposta'
          answerCounts[answer] = (answerCounts[answer] || 0) + 1
        })

        // Calcular percentagens
        const answers = Object.keys(answerCounts)
        const percentages = answers.map(answer => 
          totalResponses > 0 ? (answerCounts[answer] / totalResponses * 100) : 0
        )

        const chart = new Chart(ctx, {
          type: 'pie',
          data: {
            labels: answers,
            datasets: [{
              data: percentages,
              backgroundColor: [
                'rgba(244, 67, 54, 0.8)',
                'rgba(76, 175, 80, 0.8)',
                'rgba(255, 193, 7, 0.8)',
                'rgba(33, 150, 243, 0.8)',
                'rgba(156, 39, 176, 0.8)',
                'rgba(255, 87, 34, 0.8)',
                'rgba(96, 125, 139, 0.8)',
                'rgba(233, 30, 99, 0.8)'
              ],
              borderColor: [
                'rgba(244, 67, 54, 1)',
                'rgba(76, 175, 80, 1)',
                'rgba(255, 193, 7, 1)',
                'rgba(33, 150, 243, 1)',
                'rgba(156, 39, 176, 1)',
                'rgba(255, 87, 34, 1)',
                'rgba(96, 125, 139, 1)',
                'rgba(233, 30, 99, 1)'
              ],
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
              position: 'bottom'
            },
            tooltips: {
              callbacks: {
                label(tooltipItem: any, data: any) {
                  const label = data.labels[tooltipItem.index]
                  const value = data.datasets[0].data[tooltipItem.index]
                  return `${label}: ${value.toFixed(1)}%`
                }
              }
            }
          }
        })

        this.questionChartInstances.push(chart)
        console.log(`✅ Gráfico de perspectiva ${index} criado com sucesso`)
      })
      
      console.log(`🔵 Geração de gráficos de perspectiva completa: ${this.questionChartInstances.length} gráficos criados`)
    },

    async generateDiscrepancyCharts() {
      console.log('🔶 Iniciando geração de gráficos de discrepâncias...')
      
      // Limpar gráficos existentes
      this.discrepancyChartInstances.forEach(chart => {
        if (chart) chart.destroy()
      })
      this.discrepancyChartInstances = []
      
      if (this.selectedExamplesData.length === 0) {
        console.log('🔶 Nenhum exemplo selecionado para gráficos de discrepância')
        return
      }

      // Inicializar array de visibilidade - importante para não interferir com gráficos de perspectiva
      this.visibleDiscrepancyCharts = new Array(this.selectedExamplesData.length).fill(false)

      console.log(`🔶 Processando ${this.selectedExamplesData.length} exemplos para discrepâncias`)

      // Primeira fase: determinar quais gráficos devem ser visíveis
      for (let index = 0; index < this.selectedExamplesData.length; index++) {
        const example = this.selectedExamplesData[index]
        
        try {
          console.log(`🔶 Carregando anotações para exemplo ${example.id}`)
          
          // Carregar anotações categóricas reais deste exemplo específico
          const annotations = await this.loadExampleCategoryAnnotations(example.id)

          if (annotations.length === 0) {
            console.log(`🔶 Nenhuma anotação encontrada para exemplo ${example.id}`)
            this.visibleDiscrepancyCharts[index] = false
            continue
          }

          // Verificar se deve filtrar por tipo de anotação (discrepância)
          const filteredAnnotations = this.filterAnnotationsByType(annotations)

          if (filteredAnnotations.length === 0) {
            console.log(`🔶 Nenhuma anotação após filtros para exemplo ${example.id}`)
            this.visibleDiscrepancyCharts[index] = false
            continue
          }

          console.log(`🔶 Exemplo ${example.id} tem ${filteredAnnotations.length} anotações válidas`)
          // Mostrar este gráfico
          this.visibleDiscrepancyCharts[index] = true
          
        } catch (error) {
          console.error(`❌ Erro ao verificar anotações para exemplo ${example.id}:`, error)
          this.visibleDiscrepancyCharts[index] = false
        }
      }
      
      const visibleCount = this.visibleDiscrepancyCharts.filter(v => v).length
      console.log(`🔶 ${visibleCount} gráficos de discrepância serão exibidos`)
      
      if (visibleCount === 0) {
        console.log('🔶 Nenhum gráfico de discrepância para exibir')
        return
      }
      
      // Aguardar múltiplos ticks para garantir que o DOM foi completamente atualizado
      await this.$nextTick()
      await this.$nextTick()
      
      // Aguardar um pouco mais para garantir renderização completa
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // Segunda fase: gerar os gráficos para os exemplos visíveis
      for (let index = 0; index < this.selectedExamplesData.length; index++) {
        if (!this.visibleDiscrepancyCharts[index]) {
          continue
        }
        
        const example = this.selectedExamplesData[index]
        
        console.log(`🔶 Tentando gerar gráfico ${index} para exemplo ${example.id}`)
        
        // Tentar múltiplas vezes encontrar o canvas com timeout
        let canvas = null
        let attempts = 0
        const maxAttempts = 15
        
        while (!canvas && attempts < maxAttempts) {
          canvas = this.$refs[`discrepancyChart${index}`] as HTMLCanvasElement[]
          
          if (!canvas || !canvas[0]) {
            console.log(`🔶 Tentativa ${attempts + 1}: Canvas não encontrado para gráfico ${index}`)
            await new Promise(resolve => setTimeout(resolve, 150))
            attempts++
          } else {
            console.log(`🔶 Canvas encontrado para gráfico ${index} na tentativa ${attempts + 1}`)
            break
          }
        }
        
        if (!canvas || !canvas[0]) {
          console.error(`❌ Canvas não encontrado para gráfico ${index} após ${maxAttempts} tentativas`)
          this.visibleDiscrepancyCharts[index] = false
          continue
        }

        const ctx = canvas[0].getContext('2d')
        if (!ctx) {
          console.error(`❌ Contexto não encontrado para gráfico ${index}`)
          this.visibleDiscrepancyCharts[index] = false
          continue
        }

        try {
          // Recarregar anotações para este exemplo
          const annotations = await this.loadExampleCategoryAnnotations(example.id)
          const filteredAnnotations = this.filterAnnotationsByType(annotations)

          if (filteredAnnotations.length === 0) {
            console.log(`🔶 Nenhuma anotação após filtros na segunda fase para exemplo ${example.id}`)
            this.visibleDiscrepancyCharts[index] = false
            continue
          }

          // Agrupar anotações por label para calcular percentagens
          const labelCounts: { [key: string]: number } = {}
          const labelColors: { [key: string]: string } = {}
          const totalAnnotations = filteredAnnotations.length

          filteredAnnotations.forEach((annotation: any) => {
            const labelText = annotation.labelText || annotation.label || 'Sem Label'
            labelCounts[labelText] = (labelCounts[labelText] || 0) + 1
            
            // Usar a cor da label se disponível
            if (annotation.backgroundColor) {
              labelColors[labelText] = annotation.backgroundColor
            }
          })

          // Calcular percentagens
          const labels = Object.keys(labelCounts)
          const percentages = labels.map(label => 
            totalAnnotations > 0 ? (labelCounts[label] / totalAnnotations * 100) : 0
          )

          console.log(`🔶 Criando gráfico para exemplo ${example.id} com ${labels.length} labels`)

          // Preparar cores usando as cores das labels ou cores padrão
          const backgroundColors = labels.map(label => 
            labelColors[label] || this.getDefaultColor(labels.indexOf(label))
          )
          const borderColors = backgroundColors.map(color => 
            color.includes('rgba') ? color.replace('0.8', '1') : color
          )

          const chart = new Chart(ctx, {
            type: 'pie',
            data: {
              labels,
              datasets: [{
                data: percentages,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 2
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              legend: {
                position: 'bottom'
              },
              tooltips: {
                callbacks: {
                  label(tooltipItem: any, data: any) {
                    const label = data.labels[tooltipItem.index]
                    const value = data.datasets[0].data[tooltipItem.index]
                    return `${label}: ${value.toFixed(1)}%`
                  }
                }
              }
            }
          })

          this.discrepancyChartInstances.push(chart)
          console.log(`✅ Gráfico ${index} criado com sucesso para exemplo ${example.id}`)
          
        } catch (error) {
          console.error(`❌ Erro ao gerar gráfico de discrepâncias para exemplo ${example.id}:`, error)
          // Não mostrar este gráfico em caso de erro
          this.visibleDiscrepancyCharts[index] = false
        }
      }
      
      console.log(`🔶 Geração de gráficos de discrepância completa: ${this.discrepancyChartInstances.length} gráficos criados`)
    },

    async loadExampleCategoryAnnotations(exampleId: number) {
      try {
        // Carregar anotações categóricas do exemplo específico
        const categoryAnnotations = await this.$repositories.category.list(this.projectId, exampleId)
        
        if (categoryAnnotations && categoryAnnotations.length > 0) {
          // Carregar informações das labels para obter cores
          const categoryTypes = await this.$services.categoryType.list(this.projectId)
          
          return categoryAnnotations.map((annotation: any) => {
            const labelInfo = categoryTypes.find((type: any) => type.id === annotation.label)
            return {
              id: annotation.id,
              label: annotation.label,
              labelText: labelInfo ? labelInfo.text : `Label ${annotation.label}`,
              backgroundColor: labelInfo ? labelInfo.backgroundColor : null,
              textColor: labelInfo ? labelInfo.textColor : null,
              annotator: annotation.user,
              isDiscrepant: this.checkIfDiscrepant(annotation, categoryAnnotations)
            }
          })
        }

        return []
      } catch (error) {
        console.error(`❌ Erro ao carregar anotações categóricas do exemplo ${exampleId}:`, error)
        return []
      }
    },

    checkIfDiscrepant(annotation: any, allAnnotations: any[]): boolean {
      // Verificar se há discrepância comparando com outras anotações do mesmo exemplo
      const sameExampleAnnotations = allAnnotations.filter(a => a.id !== annotation.id)
      
      if (sameExampleAnnotations.length === 0) {
        return false // Não há outras anotações para comparar
      }
      
      // Se há anotações diferentes para o mesmo exemplo, há discrepância
      return sameExampleAnnotations.some(a => a.label !== annotation.label)
    },

    filterAnnotationsByType(annotations: any[]): any[] {
      if (this.annotationType === 'all') {
        return annotations
      } else if (this.annotationType === 'with_discrepancy') {
        return annotations.filter(a => a.isDiscrepant)
      } else if (this.annotationType === 'without_discrepancy') {
        return annotations.filter(a => !a.isDiscrepant)
      }
      return annotations
    },

    getDefaultColor(index: number): string {
      const colors = [
        'rgba(244, 67, 54, 0.8)',
        'rgba(76, 175, 80, 0.8)',
        'rgba(255, 193, 7, 0.8)',
        'rgba(33, 150, 243, 0.8)',
        'rgba(156, 39, 176, 0.8)',
        'rgba(255, 87, 34, 0.8)',
        'rgba(96, 125, 139, 0.8)',
        'rgba(233, 30, 99, 0.8)'
      ]
      return colors[index % colors.length]
    },

    async exportStatistics() {
      if (this.exportFormat === 'none') {
        return
      }
      
      this.isExporting = true
      try {
        if (this.exportFormat === 'pdf' || this.exportFormat === 'both') {
          await this.exportToPDF()
        }
        if (this.exportFormat === 'csv' || this.exportFormat === 'both') {
          this.exportToCSV()
        }
        
        // Resetar para "Não exportar" após a exportação
        this.$nextTick(() => {
          this.exportFormat = 'none'
        })
      } catch (error) {
        console.error('Erro ao exportar estatísticas:', error)
      } finally {
        this.isExporting = false
      }
    },

    async exportToPDF() {
      try {
        console.log('📄 Iniciando exportação PDF...')
        
        // Verificar se há dados para exportar
        if (!this.statistics.detailedData || this.statistics.detailedData.length === 0) {
          alert('Não há dados para exportar. Gere as estatísticas primeiro.')
          return
        }

        // Load jsPDF dynamically (to not include in initial bundle)
        const { jsPDF } = await import('jspdf')
        const { default: autoTable } = await import('jspdf-autotable')

        // eslint-disable-next-line new-cap
        const doc = new jsPDF()
        
        // Título
        doc.setFontSize(20)
        doc.text('Estatisticas de Anotacoes', 14, 20)
        
        // Data
        doc.setFontSize(12)
        doc.text(`Data: ${new Date().toLocaleDateString('pt-PT')}`, 14, 30)
        
        let yPosition = 45
        
        // Resumo dos filtros aplicados
        doc.setFontSize(14)
        doc.text('Filtros Aplicados:', 14, yPosition)
        yPosition += 10
        
        doc.setFontSize(10)
        if (this.selectedQuestions.length > 0) {
          doc.text(`Perguntas: ${this.selectedQuestions.length} selecionadas`, 20, yPosition)
          yPosition += 6
        }
        if (this.selectedExamples.length > 0) {
          doc.text(`Exemplos: ${this.selectedExamples.length} selecionados`, 20, yPosition)
          yPosition += 6
        }
        
        yPosition += 10
        
        // Adicionar estatísticas de perspectivas (primeiro)
        if (this.hasPerspectiveStatistics) {
          doc.setFontSize(16)
          doc.text('Estatisticas de Perspectivas', 14, yPosition)
          yPosition += 15
          
          // Resumo das perspectivas
          doc.setFontSize(12)
          doc.text(`Total de Respostas: ${this.totalPerspectiveResponses}`, 20, yPosition)
          yPosition += 8
          doc.text(`Perguntas Analisadas: ${this.selectedQuestionsData.length}`, 20, yPosition)
          yPosition += 15
          
          // Tabela de perspectivas
          const perspectiveTableData = this.perspectiveItems.map((item: any) => [
            item.question.length > 30 ? item.question.substring(0, 30) + '...' : item.question,
            item.answer.length > 20 ? item.answer.substring(0, 20) + '...' : item.answer,
            item.count.toString(),
            `${item.percentage.toFixed(1)}%`
          ])
          
          if (perspectiveTableData.length > 0) {
            autoTable(doc, {
              startY: yPosition,
              head: [['Pergunta', 'Resposta', 'Contagem', 'Percentagem']],
              body: perspectiveTableData,
              styles: { fontSize: 8 },
              columnStyles: {
                0: { cellWidth: 60 },
                1: { cellWidth: 50 },
                2: { cellWidth: 25 },
                3: { cellWidth: 25 }
              }
            })
            yPosition = (doc as any).lastAutoTable.finalY + 20
          }
        }
        
        // Adicionar estatísticas de discrepâncias (segundo)
        if (this.hasDiscrepancyStatistics) {
          // Verificar se há espaço na página
          if (yPosition > 200) {
            doc.addPage()
            yPosition = 20
          }
          
          doc.setFontSize(16)
          doc.text('Estatisticas de Discrepancias', 14, yPosition)
          yPosition += 15
          
          // Resumo das discrepâncias
          doc.setFontSize(12)
          doc.text(`Com Discrepancia: ${this.totalDiscrepantLabels}`, 20, yPosition)
          yPosition += 8
          doc.text(`Consistentes: ${this.totalConsistentLabels}`, 20, yPosition)
          yPosition += 15
          
          // Tabela de discrepâncias simplificada
          const discrepancyTableData = this.discrepancyItems.map((item: any) => {
            const labels = Object.values(item.labels || {}) as any[]
            const labelsText = labels.map((label: any) => 
              `${label.name}: ${label.percentage.toFixed(1)}%`
            ).join(', ')
            
            return [
              item.example.length > 30 ? item.example.substring(0, 30) + '...' : item.example,
              item.hasExampleDiscrepancy ? 'Discrepante' : 'Consistente',
              `${item.maxPercentage.toFixed(1)}%`,
              labelsText.length > 50 ? labelsText.substring(0, 50) + '...' : labelsText
            ]
          })
          
          if (discrepancyTableData.length > 0) {
            autoTable(doc, {
              startY: yPosition,
              head: [['Exemplo', 'Status', 'Max %', 'Labels e Percentagens']],
              body: discrepancyTableData,
              styles: { fontSize: 8 },
              columnStyles: {
                0: { cellWidth: 50 },
                1: { cellWidth: 25 },
                2: { cellWidth: 20 },
                3: { cellWidth: 65 }
              }
            })
          }
        }
        
        // Salvar o PDF usando output com método compatível com navegadores
        const filename = `estatisticas_${new Date().toISOString().split('T')[0]}.pdf`
        const pdfOutput = doc.output('blob')
        const url = URL.createObjectURL(pdfOutput)
        
        // For old browsers like IE
        if (window.navigator && (window.navigator as any).msSaveOrOpenBlob) {
          (window.navigator as any).msSaveOrOpenBlob(pdfOutput, `${filename}.pdf`)
          return
        }
        
        // For modern browsers
        const link = document.createElement('a')
        link.href = url
        link.download = `${filename}.pdf`
        link.style.display = 'none'
        document.body.appendChild(link)
        link.click()
        
        // Clean URL after download
        setTimeout(() => {
          URL.revokeObjectURL(url)
          document.body.removeChild(link)
        }, 500)
        
        console.log('✅ PDF exportado com sucesso:', filename)
        alert('PDF exportado com sucesso!')
        
      } catch (error: any) {
        console.error('❌ Erro ao exportar PDF:', error)
        alert(`Erro ao exportar PDF: ${error.message || 'Erro desconhecido'}`)
      }
    },

    exportToCSV() {
      const csvRows: string[] = []
      
      // Cabeçalho do CSV
      csvRows.push('Tipo,Pergunta,Resposta,Contagem,Percentagem,Exemplo,Status,MaxPercentagem,Labels')
      
      // Dados de perspectivas
      this.perspectiveItems.forEach((item: any) => {
        csvRows.push([
          'Perspectiva',
          `"${item.question}"`,
          `"${item.answer}"`,
          item.count,
          `${item.percentage.toFixed(1)}%`,
          '',
          '',
          '',
          ''
        ].join(','))
      })
      
      // Dados de discrepâncias
      this.discrepancyItems.forEach((item: any) => {
        const labels = Object.values(item.labels || {}) as any[]
        const labelsText = labels.map((label: any) => 
          `${label.name}: ${label.percentage.toFixed(1)}%`
        ).join('; ')
        
        csvRows.push([
          'Discrepancia',
          '',
          '',
          '',
          '',
          `"${item.example}"`,
          item.hasExampleDiscrepancy ? 'Discrepante' : 'Consistente',
          `${item.maxPercentage.toFixed(1)}%`,
          `"${labelsText}"`
        ].join(','))
      })

      const csvContent = csvRows.join('\n')
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `estatisticas_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },

    removeExample(exampleId: number) {
      this.selectedExamples = this.selectedExamples.filter(id => id !== exampleId)
    },

    clearAllFilters() {
      console.log('🧹 Limpando todos os filtros...')
      this.selectedQuestions = []
      this.selectedExamples = []
      this.annotationType = 'all'
      
      // Limpar também os resultados de estatísticas
      this.statistics = {
        detailedData: []
      }
      this.statisticsGenerated = false

      // Limpar arrays de visibilidade
      this.visibleDiscrepancyCharts = []

      // Limpar gráficos existentes
      this.questionChartInstances.forEach(chart => {
        if (chart) chart.destroy()
      })
      this.discrepancyChartInstances.forEach(chart => {
        if (chart) chart.destroy()
      })
      this.questionChartInstances = []
      this.discrepancyChartInstances = []

      console.log('✅ Filtros limpos com sucesso!')
    },

    goToHome() {
      console.log('🏠 Redirecionando para a página inicial...')
      this.$router.push(`/projects/${this.projectId}`)
    }
  }
})
</script>

<style scoped>
.statistics-container {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  padding: 20px;
}

.main-card {
  max-width: 1400px;
  margin: 0 auto;
  border-radius: 16px !important;
  overflow: hidden;
}

/* Estatísticas de discrepâncias */
.statistics-summary-card {
  border-radius: 12px !important;
  overflow: hidden;
}

.statistics-summary-header {
  background: linear-gradient(135deg, #FF5722 0%, #F44336 100%);
  box-shadow: 0 4px 16px rgba(255, 87, 34, 0.3);
}

.perspective-summary-header {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  box-shadow: 0 4px 16px rgba(33, 150, 243, 0.3);
}

/* Cards de resumo por exemplo */
.example-summary-card {
  height: 100%;
  border-radius: 6px !important;
  transition: all 0.2s ease;
}

.example-summary-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
  transform: translateY(-1px);
}

/* Tooltip cursor */
.cursor-pointer {
  cursor: pointer;
}

.filters-card {
  border-radius: 12px !important;
  border-left: 4px solid #1976d2;
}

.results-card {
  border-radius: 12px !important;
  border-left: 4px solid #4caf50;
}

.empty-state-card {
  border-radius: 16px !important;
  background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
}

.loading-card {
  border-radius: 16px !important;
  background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
}

.v-card-title {
  border-radius: 0 !important;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.v-btn {
  border-radius: 8px !important;
  font-weight: 600;
  text-transform: none !important;
}

.v-chip {
  border-radius: 16px !important;
}

.v-data-table {
  border-radius: 12px !important;
}

/* Estilos para distinguir os gráficos de perspetiva */
.perspective-chart-card {
  transition: all 0.3s ease;
  border-radius: 12px !important;
}

.perspective-chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(33, 150, 243, 0.2) !important;
}

.perspective-chart-header {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%) !important;
  color: white !important;
  border-radius: 12px 12px 0 0 !important;
}

/* Estilos para distinguir os gráficos de discrepâncias */
.discrepancy-chart-card {
  transition: all 0.3s ease;
  border-radius: 12px !important;
}

.discrepancy-chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 152, 0, 0.2) !important;
}

.discrepancy-chart-header {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%) !important;
  color: white !important;
  border-radius: 12px 12px 0 0 !important;
}

/* Estilo para títulos das perguntas */
.question-title {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
  cursor: help;
}

/* Animações para os botões */
.v-btn {
  transition: all 0.3s ease !important;
}

.v-btn:hover {
  transform: translateY(-1px);
}
</style> 