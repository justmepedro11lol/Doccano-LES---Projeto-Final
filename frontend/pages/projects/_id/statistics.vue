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
            <v-col cols="12" md="4">
              <v-select
                v-model="selectedQuestions"
                :items="availableQuestions"
                item-text="question"
                item-value="id"
                label="Perguntas da Perspetiva"
                multiple
                chips
                deletable-chips
                outlined
                dense
                prepend-inner-icon="mdi-help-circle"
                :disabled="isLoading"
              >
                <template #selection="{ item, index }">
                  <v-chip
                    v-if="index < 2"
                    small
                    close
                    @click:close="removeQuestion(item.id)"
                  >
                    {{ item.question.substring(0, 30) }}{{ item.question.length > 30 ? '...' : '' }}
                  </v-chip>
                  <span v-if="index === 2" class="grey--text text-caption">
                    (+{{ selectedQuestions.length - 2 }} mais)
                  </span>
                </template>
              </v-select>
            </v-col>

            <!-- Filtro de Anotadores -->
            <v-col cols="12" md="4">
              <v-select
                v-model="selectedAnnotators"
                :items="availableAnnotators"
                item-text="name"
                item-value="id"
                label="Anotadores"
                multiple
                chips
                deletable-chips
                outlined
                dense
                prepend-inner-icon="mdi-account-multiple"
                :disabled="isLoading"
              >
                <template #selection="{ item, index }">
                  <v-chip
                    v-if="index < 2"
                    small
                    close
                    @click:close="removeAnnotator(item.id)"
                  >
                    {{ item.name }}
                  </v-chip>
                  <span v-if="index === 2" class="grey--text text-caption">
                    (+{{ selectedAnnotators.length - 2 }} mais)
                  </span>
                </template>
              </v-select>
            </v-col>

            <!-- Filtro de Exemplos do Dataset -->
            <v-col cols="12" md="4">
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
                <v-col cols="12" sm="6" md="3" class="pa-1">
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
                
                <v-col cols="12" sm="6" md="3" class="pa-1">
                  <v-btn
                    color="success"
                    large
                    block
                    :loading="isExporting"
                    :disabled="!hasStatistics"
                    @click="exportStatistics"
                  >
                    <v-icon left>mdi-download</v-icon>
                    Exportar
                  </v-btn>
                </v-col>

                <v-col cols="12" sm="6" md="3" class="pa-1">
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

                <v-col cols="12" sm="6" md="3" class="pa-1">
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
            <!-- Gráficos de Respostas por Pergunta (um para cada pergunta selecionada) -->
            <template v-for="(question, index) in selectedQuestionsData">
              <v-col :key="`question-${question.id}`" cols="12" md="6">
                <v-card elevation="2" class="perspective-chart-card">
                  <v-card-title class="text-h6 perspective-chart-header">
                    <v-icon left color="white">mdi-chart-pie</v-icon>
                    <span class="white--text question-title">
                      {{ question.question }}
                    </span>
                  </v-card-title>
                  <v-card-text class="pa-4">
                    <canvas :ref="`questionChart${index}`" width="400" height="300"></canvas>
                  </v-card-text>
                </v-card>
              </v-col>
            </template>

            <!-- Gráficos de Discrepâncias por Exemplo (um para cada exemplo selecionado) -->
            <template v-for="(example, index) in selectedExamplesData">
              <v-col v-if="visibleDiscrepancyCharts[index]" :key="`example-${example.id}`" cols="12" md="6">
                <v-card elevation="2" class="discrepancy-chart-card">
                  <v-card-title class="text-h6 discrepancy-chart-header">
                    <v-icon left color="white">mdi-alert-circle</v-icon>
                    <span class="white--text">{{ example.text }}</span>
                  </v-card-title>
                  <v-card-text class="pa-4">
                    <canvas :ref="`discrepancyChart${index}`" width="400" height="300"></canvas>
                  </v-card-text>
                </v-card>
              </v-col>
            </template>

            <!-- Mensagem quando há dados mas nenhum gráfico para mostrar -->
            <v-col v-if="selectedQuestionsData.length === 0 && selectedExamplesData.length === 0" cols="12">
              <v-alert type="warning" outlined>
                <v-icon slot="prepend">mdi-information</v-icon>
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
import { jsPDF } from 'jspdf'
import 'jspdf-autotable'

export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      isLoading: false,
      isExporting: false,
      
      // Filtros
      selectedQuestions: [] as number[],
      selectedAnnotators: [] as number[],
      selectedExamples: [] as number[],
      annotationType: 'all',
      exportFormat: 'pdf',
      
      // Dados disponíveis
      availableQuestions: [] as any[],
      availableAnnotators: [] as any[],
      availableExamples: [] as any[],
      
      // Opções
      annotationTypes: [
        { text: 'Todas as Anotações', value: 'all' },
        { text: 'Com Discrepância', value: 'with_discrepancy' },
        { text: 'Sem Discrepância', value: 'without_discrepancy' }
      ],
      exportFormats: [
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
      visibleDiscrepancyCharts: [] as boolean[]
    }
  },

  computed: {
    projectId(): string {
      return this.$route.params.id
    },
    
    canGenerateStatistics(): boolean {
      // Só permite gerar estatísticas se houver pelo menos um filtro selecionado
      return this.availableQuestions.length > 0 && (
        this.selectedQuestions.length > 0 || 
        this.selectedAnnotators.length > 0 || 
        this.selectedExamples.length > 0
      )
    },
    
    hasStatistics(): boolean {
      return this.statisticsGenerated && (
        this.statistics.detailedData.length > 0 || 
        this.selectedExamples.length > 0
      )
    },

    selectedQuestionsData() {
      return this.availableQuestions.filter(q => this.selectedQuestions.includes(q.id))
    },

    selectedExamplesData() {
      return this.availableExamples.filter(e => this.selectedExamples.includes(e.id))
    }
  },

  watch: {
    selectedQuestions: {
      handler() {
        // Quando as perguntas mudam, pode afetar os dados disponíveis
      },
      deep: true
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
          this.loadAnnotators(),
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

    async loadAnnotators() {
      try {
        const members = await this.$repositories.member.list(this.projectId)
        this.availableAnnotators = members.map((member: any) => ({
          id: member.user,
          name: member.username || `User ${member.user}`
        }))
      } catch (error) {
        console.error('Erro ao carregar anotadores:', error)
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
      // Verificar se pelo menos um filtro está selecionado OU se há dados disponíveis
      const hasFilters = this.selectedQuestions.length > 0 || 
                        this.selectedAnnotators.length > 0 || 
                        this.selectedExamples.length > 0
      
      const hasAvailableData = this.availableQuestions.length > 0 || 
                              this.availableAnnotators.length > 0 || 
                              this.availableExamples.length > 0
      
      if (!hasFilters && !hasAvailableData) {
        alert('Por favor, selecione pelo menos um filtro ou certifique-se de que há dados disponíveis para gerar as estatísticas.')
        return
      }
      
      this.isLoading = true
      try {
        // Só recarregar dados se não há dados ou se os filtros mudaram significativamente
        let needsDataReload = false
        
        if (!this.statisticsGenerated || this.statistics.detailedData.length === 0) {
          needsDataReload = true
        }
        
        if (needsDataReload) {
          // Resetar estado anterior apenas se necessário
          this.statisticsGenerated = false
          this.statistics = {
            detailedData: []
          }

          // Carregar dados reais baseados nos filtros
          const statisticsData = await this.loadStatisticsData()
          
          // Se não houver dados reais E não há exemplos selecionados para discrepância, mostrar mensagem
          if (statisticsData.length === 0 && this.selectedExamples.length === 0) {
            alert('Nenhum dado encontrado com os filtros selecionados.')
            return
          }
            
          this.statistics = {
            detailedData: statisticsData
          }
          this.statisticsGenerated = true
        }

        // Gerar gráficos com dados existentes
        await this.$nextTick()
        await this.generateCharts()
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
        
        // Lógica de filtros corrigida
        let questionsToProcess = []
        
        if (this.selectedQuestions.length > 0) {
          // Se há perguntas selecionadas, usar apenas essas
          questionsToProcess = questions.filter(q => this.selectedQuestions.includes(q.id))
        } else if (this.selectedAnnotators.length > 0 || this.selectedExamples.length > 0) {
          // Se não há perguntas selecionadas mas há outros filtros, usar todas as perguntas
          questionsToProcess = questions
        } else {
          // Se nenhum filtro está selecionado, usar todas as perguntas disponíveis
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
            // Aplicar filtros de anotadores se selecionados
            if (this.selectedAnnotators.length > 0) {
              const annotatorMatch = this.selectedAnnotators.includes(answer.user_id) ||
                                   this.selectedAnnotators.includes(answer.user) ||
                                   this.selectedAnnotators.includes(answer.annotator_id)
              if (!annotatorMatch) {
                return
              }
            }
            
            // Aplicar filtros de exemplos se selecionados
            if (this.selectedExamples.length > 0) {
              const exampleMatch = this.selectedExamples.includes(answer.example_id) ||
                                 this.selectedExamples.includes(answer.example) ||
                                 this.selectedExamples.includes(answer.exampleId)
              if (!exampleMatch) {
                return
              }
            }
            
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

    async generateCharts() {
      console.log('📊 Iniciando geração de todos os gráficos...')
      
      try {
        // Gerar gráficos de perspectiva primeiro
        this.generateQuestionCharts()
        
        // Aguardar um momento para garantir que os gráficos de perspectiva estão prontos
        await this.$nextTick()
        
        // Depois gerar gráficos de discrepância
        await this.generateDiscrepancyCharts()
        
        console.log('📊 Geração de todos os gráficos completa')
      } catch (error) {
        console.error('❌ Erro durante geração de gráficos:', error)
      }
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

    exportStatistics() {
      this.isExporting = true
      try {
        if (this.exportFormat === 'pdf' || this.exportFormat === 'both') {
          this.exportToPDF()
        }
        if (this.exportFormat === 'csv' || this.exportFormat === 'both') {
          this.exportToCSV()
        }
      } catch (error) {
        console.error('Erro ao exportar estatísticas:', error)
      } finally {
        this.isExporting = false
      }
    },

    exportToPDF() {
      try {
        console.log('📄 Iniciando exportação PDF...')
        
        // Verificar se há dados para exportar
        if (!this.statistics.detailedData || this.statistics.detailedData.length === 0) {
          alert('Não há dados para exportar. Gere as estatísticas primeiro.')
          return
        }

        // Tentar diferentes formas de importar jsPDF para compatibilidade
        let jsPDFConstructor
        try {
          jsPDFConstructor = jsPDF
        } catch (error: any) {
          jsPDFConstructor = (window as any).jsPDF || (window as any).jspdf?.jsPDF
        }

        if (!jsPDFConstructor) {
          alert('Erro: Biblioteca PDF não carregada. Tente recarregar a página.')
          return
        }

        // eslint-disable-next-line new-cap
        const doc = new jsPDFConstructor()
        
        // Título
        doc.setFontSize(20)
        doc.text('Estatisticas de Anotacoes', 20, 20)
        
        // Data
        doc.setFontSize(12)
        doc.text(`Data: ${new Date().toLocaleDateString('pt-PT')}`, 20, 35)
        
        let yPosition = 50
        
        // Resumo dos filtros aplicados
        doc.setFontSize(14)
        doc.text('Filtros Aplicados:', 20, yPosition)
        yPosition += 10
        
        doc.setFontSize(10)
        if (this.selectedQuestions.length > 0) {
          doc.text(`Perguntas: ${this.selectedQuestions.length} selecionadas`, 25, yPosition)
          yPosition += 8
        }
        if (this.selectedAnnotators.length > 0) {
          doc.text(`Anotadores: ${this.selectedAnnotators.length} selecionados`, 25, yPosition)
          yPosition += 8
        }
        if (this.selectedExamples.length > 0) {
          doc.text(`Exemplos: ${this.selectedExamples.length} selecionados`, 25, yPosition)
          yPosition += 8
        }
        
        yPosition += 15
        
        // Capturar e adicionar gráficos de perspectiva
        if (this.selectedQuestionsData.length > 0) {
          doc.setFontSize(16)
          doc.text('Graficos de Perspectivas', 20, yPosition)
          yPosition += 10
          
          for (let i = 0; i < this.selectedQuestionsData.length; i++) {
            const question = this.selectedQuestionsData[i]
            const canvas = this.$refs[`questionChart${i}`] as HTMLCanvasElement[]
            
            if (canvas && canvas[0]) {
              // Verificar se há espaço na página
              if (yPosition > 200) {
                doc.addPage()
                yPosition = 20
              }
              
              // Título da pergunta
              doc.setFontSize(12)
              const questionText = question.question.length > 60 
                ? question.question.substring(0, 60) + '...'
                : question.question
              doc.text(questionText, 20, yPosition)
              yPosition += 10
              
              try {
                // Capturar imagem do canvas
                const imgData = canvas[0].toDataURL('image/png')
                doc.addImage(imgData, 'PNG', 20, yPosition, 80, 60)
                yPosition += 70
              } catch (error) {
                console.error('Erro ao capturar gráfico:', error)
                doc.text('Erro ao capturar grafico', 20, yPosition)
                yPosition += 10
              }
            }
          }
        }
        
        // Capturar e adicionar gráficos de discrepância
        const visibleDiscrepancyCount = this.visibleDiscrepancyCharts.filter(v => v).length
        if (visibleDiscrepancyCount > 0) {
          // Verificar se há espaço na página
          if (yPosition > 200) {
            doc.addPage()
            yPosition = 20
          }
          
          doc.setFontSize(16)
          doc.text('Graficos de Discrepancias', 20, yPosition)
          yPosition += 10
          
          for (let i = 0; i < this.selectedExamplesData.length; i++) {
            if (!this.visibleDiscrepancyCharts[i]) continue
            
            const example = this.selectedExamplesData[i]
            const canvas = this.$refs[`discrepancyChart${i}`] as HTMLCanvasElement[]
            
            if (canvas && canvas[0]) {
              // Verificar se há espaço na página
              if (yPosition > 200) {
                doc.addPage()
                yPosition = 20
              }
              
              // Título do exemplo
              doc.setFontSize(12)
              const exampleText = example.text.length > 60 
                ? example.text.substring(0, 60) + '...'
                : example.text
              doc.text(exampleText, 20, yPosition)
              yPosition += 10
              
              try {
                // Capturar imagem do canvas
                const imgData = canvas[0].toDataURL('image/png')
                doc.addImage(imgData, 'PNG', 20, yPosition, 80, 60)
                yPosition += 70
              } catch (error) {
                console.error('Erro ao capturar gráfico de discrepância:', error)
                doc.text('Erro ao capturar grafico', 20, yPosition)
                yPosition += 10
              }
            }
          }
        }
        
        // Download do PDF
        const filename = `estatisticas_${new Date().toISOString().split('T')[0]}.pdf`
        doc.save(filename)
        
        console.log('✅ PDF exportado com sucesso:', filename)
        alert('PDF exportado com sucesso!')
        
      } catch (error: any) {
        console.error('❌ Erro ao exportar PDF:', error)
        alert(`Erro ao exportar PDF: ${error.message || 'Erro desconhecido'}`)
      }
    },

    exportToCSV() {
      const headers = ['Pergunta', 'Resposta', 'Anotador', 'Label', 'Exemplo', 'Discrepância', 'Data']
      const csvContent = [
        headers.join(','),
        ...this.statistics.detailedData.map((item: any) => [
          `"${item.question}"`,
          `"${item.answer}"`,
          `"${item.annotator}"`,
          `"${item.label}"`,
          `"${item.example}"`,
          item.discrepancy ? 'Sim' : 'Não',
          item.date
        ].join(','))
      ].join('\n')

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

    removeQuestion(questionId: number) {
      this.selectedQuestions = this.selectedQuestions.filter(id => id !== questionId)
    },

    removeAnnotator(annotatorId: number) {
      this.selectedAnnotators = this.selectedAnnotators.filter(id => id !== annotatorId)
    },

    removeExample(exampleId: number) {
      this.selectedExamples = this.selectedExamples.filter(id => id !== exampleId)
    },

    clearAllFilters() {
      console.log('🧹 Limpando todos os filtros...')
      this.selectedQuestions = []
      this.selectedAnnotators = []
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