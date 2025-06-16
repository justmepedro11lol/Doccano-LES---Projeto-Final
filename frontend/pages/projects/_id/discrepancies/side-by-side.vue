<template>
  <v-container fluid>
    <!-- Cabeçalho -->
    <v-row class="mb-4">
      <v-col cols="12">
        <div class="d-flex align-center mb-2">
          <v-btn
            icon
            @click="$router.go(-1)"
          >
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
          <h1 class="text-h4 ml-3">Comparação Lado a Lado com Discrepâncias</h1>
          <v-spacer />
          <!-- Botão de Debug -->
          <v-btn 
            small 
            color="info" 
            outlined 
            class="ml-2"
            @click="debugDataStatus"
          >
            <v-icon small class="mr-1">mdi-bug</v-icon>
            Debug
          </v-btn>
        </div>
        <p class="text-subtitle-1 ml-12">
          Analise e resolva as divergências de anotação entre os membros da equipe.
        </p>
      </v-col>
    </v-row>

    <!-- Filtros de Comparação -->
    <v-card class="mb-4">
      <v-card-title>
        <v-icon class="mr-2">mdi-filter-variant</v-icon>
        Filtros de Comparação
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.dataset"
              :items="datasetOptions"
              label="Filtrar por Dataset"
              outlined
              dense
              prepend-inner-icon="mdi-database"
              clearable
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.annotators"
              :items="annotatorOptions"
              label="Selecionar Anotadores (2 ou mais)"
              multiple
              chips
              deletable-chips
              outlined
              dense
              prepend-inner-icon="mdi-account-multiple"
              :rules="[v => v.length >= 2 || 'Selecione pelo menos 2 anotadores']"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.disagreementStatus"
              :items="disagreementStatusOptions"
              label="Estado do Desacordo"
              outlined
              dense
              prepend-inner-icon="mdi-alert-circle-check"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" md="8">
            <v-select
              v-model="filters.categories"
              :items="categoryOptions"
              label="Filtrar por Categorias/Etiquetas"
              multiple
              chips
              deletable-chips
              outlined
              dense
              prepend-inner-icon="mdi-tag-multiple"
            />
          </v-col>
          <v-col cols="12" md="4">
             <v-text-field
                v-model="filters.recordRange"
                label="Intervalo de Registos (ex: 1-100 ou 50)"
                outlined
                dense
                prepend-inner-icon="mdi-numeric"
                clearable
                hint="Use '1-100' para intervalo ou '50' para ID específico"
              />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Resumo Estatístico e Navegação -->
    <v-card class="mb-4" color="blue-grey lighten-5">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="4">
            <div class="d-flex flex-wrap">
              <v-chip color="error" class="mr-2 mb-1" outlined>
                <v-icon left>mdi-alert-octagon</v-icon>
                Total: {{ summary.totalDiscrepancies }}
              </v-chip>
              <v-chip color="success" class="mr-2 mb-1" outlined>
                <v-icon left>mdi-check-circle</v-icon>
                Resolvidas: {{ summary.resolved }}
              </v-chip>
              <v-chip color="warning" class="mb-1" outlined>
                <v-icon left>mdi-progress-alert</v-icon>
                Pendentes: {{ summary.pending }}
              </v-chip>
            </div>
          </v-col>
          <v-col cols="12" md="4" class="text-center">
                         <v-btn 
               class="mx-1" 
               :disabled="navigation.current === 0 || summary.totalDiscrepancies === 0" 
               color="primary"
               outlined
               @click="prevDiscrepancy"
             >
              <v-icon>mdi-chevron-left</v-icon>
              Anterior
            </v-btn>
            <span class="mx-4 text-subtitle-1 font-weight-bold">
              {{ summary.totalDiscrepancies > 0 ? navigation.current + 1 : 0 }} / {{ summary.totalDiscrepancies }}
            </span>
                         <v-btn 
               class="mx-1" 
               :disabled="navigation.current >= summary.totalDiscrepancies - 1 || summary.totalDiscrepancies === 0" 
               color="primary"
               outlined
               @click="nextDiscrepancy"
             >
              Próximo
              <v-icon>mdi-chevron-right</v-icon>
            </v-btn>
          </v-col>
          <v-col cols="12" md="4" class="text-right">
            <div class="text-caption mb-1">Progresso de Resolução</div>
            <v-progress-linear
              :value="progress"
              height="20"
              rounded
              color="success"
              background-color="grey lighten-2"
            >
              <strong>{{ Math.ceil(progress) }}%</strong>
            </v-progress-linear>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Legenda de Cores -->
         <v-card v-if="selectedAnnotators.length >= 2" class="mb-4">
      <v-card-title class="py-2">
        <v-icon class="mr-2" small>mdi-palette</v-icon>
        Legenda de Discrepâncias
      </v-card-title>
      <v-card-text class="py-2">
        <div class="d-flex flex-wrap">
          <v-chip class="mr-3 mb-1" small outlined>
            <span class="legend-color different-label"></span>
            Etiqueta Diferente
          </v-chip>
          <v-chip class="mr-3 mb-1" small outlined>
            <span class="legend-color different-span"></span>
            Span Diferente
          </v-chip>
          <v-chip class="mr-3 mb-1" small outlined>
            <span class="legend-color missing-annotation"></span>
            Etiqueta Ausente
          </v-chip>
          <v-chip class="mr-3 mb-1" small outlined>
            <span class="legend-color no-discrepancy"></span>
            Sem Discrepância
          </v-chip>
        </div>
      </v-card-text>
    </v-card>

    <!-- Visualização Lado-a-Lado -->
    <div v-if="selectedAnnotators.length >= 2 && summary.totalDiscrepancies > 0">
      <v-row>
        <v-col
          v-for="(annotator, index) in selectedAnnotators"
          :key="annotator.id"
          :cols="12"
          :md="Math.floor(12 / selectedAnnotators.length)"
        >
          <v-card class="discrepancy-column" :class="`annotator-${index}`">
            <v-card-title class="py-2">
              <v-avatar :color="getAnnotatorColor(index)" class="mr-2" size="32">
                <span class="white--text font-weight-bold">{{ annotator.text[0].toUpperCase() }}</span>
              </v-avatar>
              {{ annotator.text }}
              <v-spacer></v-spacer>
              <v-chip small :color="getAnnotatorColor(index)" outlined>
                {{ getAnnotatorStats(annotator.value).total }} anotações
              </v-chip>
            </v-card-title>
            <v-divider />
            <v-card-text class="text-body-1 pa-4" style="line-height: 2.8; min-height: 300px;">
                             <!-- eslint-disable-next-line vue/no-v-html -->
               <div class="annotated-text" v-html="getAnnotatedText(annotator.value)" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
    
    <!-- Estado Vazio -->
    <v-card v-else-if="selectedAnnotators.length < 2" class="pa-8 text-center">
        <v-icon size="80" color="grey lighten-1">mdi-account-multiple-outline</v-icon>
        <h3 class="mt-4 mb-2">Selecione Anotadores</h3>
        <p class="text-body-1">Selecione 2 ou mais anotadores nos filtros acima para iniciar a comparação lado-a-lado.</p>
    </v-card>
    
    <v-card v-else-if="summary.totalDiscrepancies === 0" class="pa-8 text-center">
        <v-icon size="80" color="info">mdi-magnify-scan</v-icon>
        <h3 class="mt-4 mb-2">Nenhuma Discrepância Encontrada</h3>
        <p class="text-body-1 mb-4">Não há discrepâncias registradas entre os anotadores selecionados com os filtros aplicados.</p>
        <v-btn 
          color="primary" 
          :loading="detectingDiscrepancies"
          class="mr-2"
          @click="detectDiscrepancies"
        >
          <v-icon left>mdi-auto-fix</v-icon>
          Detectar Discrepâncias Automaticamente
        </v-btn>
        <v-btn 
          color="info" 
          outlined 
          @click="debugDataStatus"
        >
          <v-icon left>mdi-bug</v-icon>
          Diagnosticar Problema
        </v-btn>
    </v-card>

    <!-- Painel de Discussão e Resolução -->
    <v-navigation-drawer
      v-model="discussionPanel"
      app
      right
      temporary
      width="450"
      class="discussion-panel"
    >
      <DiscrepancyDiscussionPanel
        v-if="selectedDiscrepancy"
        :discrepancy-context="selectedDiscrepancy"
        :project-members="projectMembers"
        @resolved="onDiscrepancyResolved"
        @vote-submitted="onVoteSubmitted"
        @consensus-proposed="onConsensusProposed"
      />
    </v-navigation-drawer>

    <!-- Atalhos de Teclado -->
    <v-snackbar
      v-model="showKeyboardHelp"
      timeout="3000"
      color="info"
      bottom
      right
    >
      <v-icon class="mr-2">mdi-keyboard</v-icon>
      Use ← → para navegar, ESC para fechar painéis
    </v-snackbar>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'
import DiscrepancyDiscussionPanel from '~/components/discrepancy/DiscrepancyDiscussionPanel.vue'

// Tipos de Discrepância
const DISCREPANCY_TYPES = {
  DIFFERENT_LABEL: 'etiqueta-diferente',
  DIFFERENT_SPAN: 'span-diferente',
  MISSING_ANNOTATION: 'etiqueta-ausente'
}

export default Vue.extend({
  name: 'DiscrepancySideBySide',
  components: { DiscrepancyDiscussionPanel },
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      // Filtros
      filters: {
        dataset: null,
        annotators: [],
        disagreementStatus: 'pending',
        categories: [],
        recordRange: ''
      },
      datasetOptions: [],
      annotatorOptions: [],
      categoryOptions: [],
      disagreementStatusOptions: [
        { text: 'Apenas em Desacordo', value: 'pending' },
        { text: 'Já Resolvidos', value: 'resolved' },
        { text: 'Todos', value: 'all' }
      ],

      // Resumo e Navegação
      summary: {
        totalDiscrepancies: 0,
        resolved: 0,
        pending: 0
      },
      navigation: {
        current: 0, // índice da discrepância atual
        discrepancyDocs: [] // lista de documentos com discrepâncias
      },

      // Dados da comparação
      comparisonData: [], // Array de documentos com texto e anotações por anotador
      
      // Painel de Discussão
      discussionPanel: false,
      selectedDiscrepancy: null,

      // Cache e Performance
      allExamples: [],
      allAnnotations: {},
      
      // UI States
      showKeyboardHelp: false,
      detectingDiscrepancies: false,
      
      // Members
      projectMembers: [],
      
      // WebSocket/Polling
      realtimeUpdates: null,
      
      // Cores dos anotadores
      annotatorColors: [
        'blue', 'green', 'purple', 'orange', 'red', 'teal', 'pink', 'indigo'
      ]
    }
  },

  computed: {
    ...mapGetters('projects', ['project']),
    
    projectId(): string {
      return this.$route.params.id
    },

    progress(): number {
      if (this.summary.totalDiscrepancies === 0) {
        return 100
      }
      return (this.summary.resolved / this.summary.totalDiscrepancies) * 100
    },

    selectedAnnotators(): any[] {
        if (this.filters.annotators.length < 2) {
            return []
        }
        return this.annotatorOptions.filter(a => this.filters.annotators.includes(a.value))
    }
  },

  watch: {
    filters: {
      handler: 'fetchDiscrepancies',
      deep: true
    }
  },

  async mounted() {
      await this.loadFilterOptions()
      await this.fetchDiscrepancies()
      this.setupKeyboardShortcuts()
      this.setupRealtimeUpdates()
      
      // Mostrar ajuda de teclado brevemente
      setTimeout(() => {
        this.showKeyboardHelp = true
      }, 1000)
  },

  beforeDestroy() {
    this.cleanupRealtimeUpdates()
    this.removeKeyboardShortcuts()
  },

  methods: {
    async debugDataStatus() {
      console.log('🔧 === STATUS DE DEBUG ===')
      console.log('👤 Usuário logado:', this.$auth.user)
      console.log('📁 Projeto ID:', this.projectId)
      console.log('🏗️ Projeto:', this.project)
      console.log('📊 Filtros atuais:', this.filters)
      console.log('📈 Resumo:', this.summary)
      console.log('🧭 Navegação:', this.navigation)
      console.log('📄 Total de exemplos carregados:', this.allExamples.length)
      console.log('📝 Cache de anotações:', Object.keys(this.allAnnotations).length)
      
      // Testar carregamento de dados específicos
      try {
        console.log('🧪 Testando APIs...')
        
        // Teste de exemplos
        const testExamples = await this.$repositories.example.list(this.projectId, { limit: 5 })
        console.log('✅ Exemplos (teste):', testExamples)
        
        // Teste de membros
        const testMembers = await this.$repositories.member.list(this.projectId)
        console.log('✅ Membros (teste):', testMembers)
        
        // Teste de categorias
        if (this.project.canDefineCategory) {
          const testCategories = await this.$repositories.categoryType.list(this.projectId)
          console.log('✅ Tipos de categoria (teste):', testCategories)
          
          // Se houver exemplos, testar anotações
          if (testExamples.items && testExamples.items.length > 0) {
            const firstExampleId = testExamples.items[0].id
            const testAnnotations = await this.$repositories.category.list(this.projectId, firstExampleId)
            console.log(`✅ Anotações do exemplo ${firstExampleId}:`, testAnnotations)
          }
        }
        
        // Teste de spans
        if (this.project.canDefineSpan) {
          const testSpanTypes = await this.$repositories.spanType.list(this.projectId)
          console.log('✅ Tipos de span (teste):', testSpanTypes)
          
          if (testExamples.items && testExamples.items.length > 0) {
            const firstExampleId = testExamples.items[0].id
            const testSpans = await this.$repositories.span.list(this.projectId, firstExampleId)
            console.log(`✅ Spans do exemplo ${firstExampleId}:`, testSpans)
          }
        }
        
        // Teste de discrepâncias
        const testDiscrepancies = await this.$repositories.discrepancy.list(this.projectId)
        console.log('✅ Discrepâncias registradas:', testDiscrepancies)
        
        // Teste de estatísticas
        try {
          const discrepancyStats = await this.$repositories.discrepancy.getStatistics(this.projectId)
          console.log('✅ Estatísticas de discrepâncias:', discrepancyStats)
        } catch (e) {
          console.log('⚠️ Estatísticas de discrepâncias não disponíveis:', e.message)
        }
        
        // Resumo do diagnóstico
        const hasExamples = testExamples.items && testExamples.items.length > 0
        const hasMembers = testMembers.length > 0
        const hasDiscrepancies = testDiscrepancies.length > 0
        const hasAnnotations = testExamples.items && testExamples.items.length > 0 && 
          (this.project.canDefineCategory || this.project.canDefineSpan)
        
        let diagnosisMessage = `🔧 Diagnóstico:\n`
        diagnosisMessage += `• Exemplos: ${hasExamples ? '✅' : '❌'} (${testExamples.items?.length || 0})\n`
        diagnosisMessage += `• Membros: ${hasMembers ? '✅' : '❌'} (${testMembers.length})\n`
        diagnosisMessage += `• Discrepâncias: ${hasDiscrepancies ? '✅' : '❌'} (${testDiscrepancies.length})\n`
        diagnosisMessage += `• Capacidades: ${hasAnnotations ? '✅' : '❌'}`
        
        console.log(diagnosisMessage)
        
        this.$nuxt.$emit('show-snackbar', {
          text: hasDiscrepancies ? 
            'Debug executado! Discrepâncias encontradas.' : 
            'Debug executado! Nenhuma discrepância registrada.',
          color: hasDiscrepancies ? 'success' : 'warning'
        })
        
      } catch (error) {
        console.error('❌ Erro no teste de debug:', error)
        this.$nuxt.$emit('show-snackbar', {
          text: 'Erro no debug: ' + error.message,
          color: 'error'
        })
      }
    },

    async detectDiscrepancies() {
      this.detectingDiscrepancies = true
      try {
        console.log('🤖 Iniciando detecção automática de discrepâncias...')
        
        // Chamar a API para detectar discrepâncias automaticamente
        const response = await this.$repositories.discrepancy.detectDiscrepancies(this.projectId)
        console.log('✅ Resultado da detecção:', response)
        
        this.$nuxt.$emit('show-snackbar', {
          text: `${response.discrepancies?.length || 0} discrepâncias detectadas automaticamente!`,
          color: 'success'
        })
        
        // Recarregar as discrepâncias
        await this.fetchDiscrepancies()
        
      } catch (error) {
        console.error('❌ Erro ao detectar discrepâncias:', error)
        this.$nuxt.$emit('show-snackbar', {
          text: 'Erro ao detectar discrepâncias: ' + error.message,
          color: 'error'
        })
      } finally {
        this.detectingDiscrepancies = false
      }
    },

    async loadFilterOptions() {
        try {
            console.log('🔧 Carregando opções de filtro...')
            
            const [stats, categories, members] = await Promise.all([
                this.$repositories.metrics.fetchDisagreementStats(this.projectId).catch(e => {
                  console.error('❌ Erro ao carregar stats:', e)
                  return { textTypes: [] }
                }),
                this.$repositories.categoryType.list(this.projectId).catch(e => {
                  console.error('❌ Erro ao carregar categorias:', e)
                  return []
                }),
                this.$repositories.member.list(this.projectId).catch(e => {
                  console.error('❌ Erro ao carregar membros:', e)
                  return []
                })
            ])

            console.log('📊 Stats carregadas:', stats)
            console.log('🏷️ Categorias carregadas:', categories)
            console.log('👥 Membros carregados:', members)

            this.annotatorOptions = members.map((member: any) => ({
                text: member.username,
                value: member.user
            }))
            
            console.log('👤 Opções de anotadores configuradas:', this.annotatorOptions)
            
            this.projectMembers = members

            if (stats.textTypes) {
                this.datasetOptions = stats.textTypes.map((tt: string) => ({ text: tt, value: tt }))
            }
            
            console.log('📁 Opções de dataset configuradas:', this.datasetOptions)
            
            this.categoryOptions = categories.map((cat: any) => ({
                text: cat.text,
                value: cat.id
            }))

            console.log('🏷️ Opções de categoria configuradas:', this.categoryOptions)

        } catch(e) {
            console.error('❌ Erro ao carregar opções de filtro:', e)
        }
    },

    async fetchDiscrepancies() {
      if (this.filters.annotators.length < 2) {
        this.comparisonData = []
        this.navigation.discrepancyDocs = []
        this.summary.totalDiscrepancies = 0
        this.summary.pending = 0
        this.summary.resolved = 0
        return
      }
      
      try {
        console.log('🔍 Buscando discrepâncias registradas no sistema...')
        
        // 1. Buscar discrepâncias já identificadas no sistema usando a API do backend
        const discrepancyParams: any = {}
        
        // Filtrar por status
        if (this.filters.disagreementStatus === 'pending') {
          discrepancyParams.status = 'pending'
        } else if (this.filters.disagreementStatus === 'resolved') {
          discrepancyParams.status = 'resolved'
        }
        
        // Buscar discrepâncias usando o repositório
        const discrepancies = await this.$repositories.discrepancy.list(this.projectId, discrepancyParams)
        console.log('📋 Discrepâncias encontradas no sistema:', discrepancies)
        
        // 2. Filtrar discrepâncias pelos anotadores selecionados
        let filteredDiscrepancies = discrepancies.filter((disc: any) => {
          const involvedUserIds = disc.users_involved || []
          // Verificar se pelo menos um dos usuários envolvidos está selecionado
          return this.filters.annotators.some(annotatorId => 
            involvedUserIds.includes(annotatorId)
          )
        })
        
        console.log('👥 Discrepâncias filtradas por anotador:', filteredDiscrepancies)
        
        // 3. Aplicar filtros adicionais
        if (this.filters.recordRange) {
          try {
            const rangeInput = this.filters.recordRange.trim()
            if (rangeInput.includes('-')) {
              const [start, end] = rangeInput.split('-').map(Number)
              if (!isNaN(start) && !isNaN(end)) {
                filteredDiscrepancies = filteredDiscrepancies.filter((disc: any) => 
                  disc.example_id >= start && disc.example_id <= end
                )
              }
            } else {
              const singleId = Number(rangeInput)
              if (!isNaN(singleId)) {
                filteredDiscrepancies = filteredDiscrepancies.filter((disc: any) => 
                  disc.example_id === singleId
                )
              }
            }
          } catch(e) {
            console.error("Intervalo de registos inválido:", e)
          }
        }
        
        // 4. Filtrar por categorias se especificado
        if (this.filters.categories.length > 0) {
          filteredDiscrepancies = filteredDiscrepancies.filter((disc: any) => {
            const conflictingAnnotations = disc.conflicting_annotations || {}
            // Verificar se alguma das anotações conflitantes envolve as categorias selecionadas
            return Object.values(conflictingAnnotations).some((annData: any) => {
              if (Array.isArray(annData)) {
                return annData.some((ann: any) => this.filters.categories.includes(ann.label))
              }
              return this.filters.categories.includes(annData.label)
            })
          })
        }
        
        console.log('🎯 Discrepâncias após todos os filtros:', filteredDiscrepancies)
        
        // 5. Carregar dados completos para cada discrepância
        const discrepancyDocs = []
        let resolvedCount = 0
        
        for (const discrepancy of filteredDiscrepancies) {
          console.log('📄 Processando discrepância:', discrepancy)
          
          // Buscar dados do exemplo
          const example = await this.$repositories.example.findById(this.projectId, discrepancy.example_id)
          console.log('📄 Exemplo carregado:', example)
          
          // Buscar anotações para o exemplo
          const annotations = await this.getAnnotationsForExample(discrepancy.example_id)
          
          // Agrupar anotações por usuário
          const userAnnotations = {}
          for(const ann of annotations) {
              if (!userAnnotations[ann.user]) {
                  userAnnotations[ann.user] = []
              }
              userAnnotations[ann.user].push(ann)
          }
          
          discrepancyDocs.push({
            docId: discrepancy.example_id,
            text: example.text,
            annotations: userAnnotations,
            isResolved: discrepancy.status === 'resolved',
            discrepancyData: discrepancy, // Dados completos da discrepância
            discrepancyTypes: [discrepancy.discrepancy_type]
          })
          
          if (discrepancy.status === 'resolved') {
            resolvedCount++
          }
        }
        
        console.log(`✅ Total de documentos com discrepâncias: ${discrepancyDocs.length}`)
        console.log(`✅ Resolvidas: ${resolvedCount}, Pendentes: ${discrepancyDocs.length - resolvedCount}`)

        this.navigation.discrepancyDocs = discrepancyDocs
        this.summary.totalDiscrepancies = discrepancyDocs.length
        this.summary.resolved = resolvedCount
        this.summary.pending = discrepancyDocs.length - resolvedCount
        
        // Reset navigation if necessary
        if (this.navigation.current >= discrepancyDocs.length) {
          this.navigation.current = Math.max(0, discrepancyDocs.length - 1)
        }
        
        // Se não houver discrepâncias, sugerir detectar automaticamente
        if (discrepancyDocs.length === 0) {
          console.log('💡 Nenhuma discrepância encontrada. Considere executar detecção automática.')
          this.$nuxt.$emit('show-snackbar', {
            text: 'Nenhuma discrepância encontrada. Use o botão Debug para verificar se há anotações no projeto.',
            color: 'info'
          })
        }
        
      } catch (error) {
        console.error('❌ Erro ao buscar discrepâncias:', error)
        this.$nuxt.$emit('show-snackbar', {
          text: 'Erro ao carregar discrepâncias: ' + error.message,
          color: 'error'
        })
      }
    },

    async getAnnotationsForExample(exampleId: number) {
        if (this.allAnnotations[exampleId]) {
            return this.allAnnotations[exampleId]
        }

        console.log(`🔍 Buscando anotações para exemplo ${exampleId}`)
        console.log('🎯 Capacidades do projeto:', {
          canDefineCategory: this.project.canDefineCategory,
          canDefineSpan: this.project.canDefineSpan,
          canDefineRelation: this.project.canDefineRelation
        })

        const annotationPromises = []
        try {
          if (this.project.canDefineCategory) {
              console.log(`📝 Buscando categorias para exemplo ${exampleId}`)
              annotationPromises.push(
                this.$repositories.category.list(this.projectId, exampleId)
                  .then(categories => {
                    console.log(`📝 Categorias encontradas para exemplo ${exampleId}:`, categories)
                    return categories || []
                  })
                  .catch(error => {
                    console.error(`❌ Erro ao buscar categorias para exemplo ${exampleId}:`, error)
                    return []
                  })
              )
          }
          if (this.project.canDefineSpan) {
              console.log(`🏷️ Buscando spans para exemplo ${exampleId}`)
              annotationPromises.push(
                this.$repositories.span.list(this.projectId, exampleId)
                  .then(spans => {
                    console.log(`🏷️ Spans encontrados para exemplo ${exampleId}:`, spans)
                    return spans || []
                  })
                  .catch(error => {
                    console.error(`❌ Erro ao buscar spans para exemplo ${exampleId}:`, error)
                    return []
                  })
              )
          }
          if (this.project.canDefineRelation) {
              console.log(`🔗 Buscando relações para exemplo ${exampleId}`)
              annotationPromises.push(
                this.$repositories.relation.list(this.projectId, exampleId)
                  .then(relations => {
                    console.log(`🔗 Relações encontradas para exemplo ${exampleId}:`, relations)
                    return relations || []
                  })
                  .catch(error => {
                    console.error(`❌ Erro ao buscar relações para exemplo ${exampleId}:`, error)
                    return []
                  })
              )
          }

          const annotationSets = await Promise.all(annotationPromises)
          const allAnns = annotationSets.flat()
          
          console.log(`✅ Total de anotações para exemplo ${exampleId}:`, allAnns.length)
          console.log(`📋 Anotações detalhadas:`, allAnns)
          
          this.$set(this.allAnnotations, exampleId, allAnns)
          return allAnns
          
        } catch (error) {
          console.error(`❌ Erro geral ao buscar anotações para exemplo ${exampleId}:`, error)
          this.$set(this.allAnnotations, exampleId, [])
          return []
        }
    },
    
    getDiscrepancyInfo(userAnnotations: any): { hasDiscrepancy: boolean, involvedLabels: number[] } {
        const annotatorIds = this.filters.annotators
        console.log(`🔍 Verificando discrepâncias entre anotadores:`, annotatorIds)
        
        if (annotatorIds.length < 2) {
            console.log(`❌ Menos de 2 anotadores selecionados (${annotatorIds.length})`)
            return { hasDiscrepancy: false, involvedLabels: [] }
        }

        const involvedLabels = new Set<number>()
        const firstAnnotatorId = annotatorIds[0]
        const otherAnnotatorIds = annotatorIds.slice(1)
        const firstUserAnns = userAnnotations[firstAnnotatorId] || []

        console.log(`👤 Primeiro anotador (${firstAnnotatorId}):`, firstUserAnns.length, 'anotações')
        console.log(`📝 Anotações do primeiro anotador:`, firstUserAnns)

        for (const otherId of otherAnnotatorIds) {
            const otherUserAnns = userAnnotations[otherId] || []
            console.log(`👤 Comparando com anotador (${otherId}):`, otherUserAnns.length, 'anotações')
            console.log(`📝 Anotações do outro anotador:`, otherUserAnns)

            // Quick check: different number of annotations
            if (firstUserAnns.length !== otherUserAnns.length) {
                console.log(`⚡ Discrepância detectada: números diferentes de anotações (${firstUserAnns.length} vs ${otherUserAnns.length})`)
                firstUserAnns.forEach((ann: any) => involvedLabels.add(ann.label))
                otherUserAnns.forEach((ann: any) => involvedLabels.add(ann.label))
                return { hasDiscrepancy: true, involvedLabels: Array.from(involvedLabels) }
            }

            // Detailed comparison
            for (const ann of firstUserAnns) {
                console.log(`🔍 Verificando anotação:`, ann)
                const correspondingAnn = otherUserAnns.find((o: any) => 
                    (o.start_offset === ann.start_offset && o.end_offset === ann.end_offset) ||
                    (o.label === ann.label)
                )
                console.log(`🔍 Anotação correspondente encontrada:`, correspondingAnn)
                
                if (!correspondingAnn) {
                    console.log(`⚡ Discrepância detectada: anotação sem correspondência`)
                    involvedLabels.add(ann.label)
                    return { hasDiscrepancy: true, involvedLabels: Array.from(involvedLabels) }
                }
                if (correspondingAnn.label !== ann.label) {
                    console.log(`⚡ Discrepância detectada: labels diferentes (${ann.label} vs ${correspondingAnn.label})`)
                    involvedLabels.add(ann.label)
                    involvedLabels.add(correspondingAnn.label)
                    return { hasDiscrepancy: true, involvedLabels: Array.from(involvedLabels) }
                }
            }
        }
        
        console.log(`✅ Nenhuma discrepância detectada`)
        return { hasDiscrepancy: false, involvedLabels: [] }
    },

    getCurrentDocument() {
        if (this.navigation.discrepancyDocs.length > 0 && this.navigation.current < this.navigation.discrepancyDocs.length) {
            return this.navigation.discrepancyDocs[this.navigation.current]
        }
        return null
    },

    getAnnotatedText(annotatorId: number): string {
      const doc = this.getCurrentDocument()
      if (!doc) {
        return '<div class="text-center text-grey">Nenhum documento para exibir.</div>'
      }

      const annotations = (doc.annotations[annotatorId] || []).map((a: any) => ({
        ...a, 
        type: a.start_offset !== undefined ? 'span' : 'category'
      }))
      const otherAnnotatorIds = this.selectedAnnotators.map(a => a.value).filter(id => id !== annotatorId)

      let html = doc.text
      
      // Process span annotations (reverse order to maintain positions)
      const spanAnnotations = annotations.filter(a => a.type === 'span').sort((a, b) => b.start_offset - a.start_offset)
      
      for (const ann of spanAnnotations) {
        const discrepancyType = this.findDiscrepancy(ann, doc.annotations, otherAnnotatorIds)
        const colorClass = this.getDiscrepancyColorClass(discrepancyType)
        const labelText = this.getCategoryLabel(ann.label)
        
        const beforeText = html.substring(0, ann.start_offset)
        const annotatedText = html.substring(ann.start_offset, ann.end_offset)
        const afterText = html.substring(ann.end_offset)
        
        html = beforeText +
            `<span class="annotation ${colorClass}" 
                   onclick="this.dispatchEvent(new CustomEvent('annotation-click', {detail: {id: ${ann.id}, type: '${discrepancyType || 'none'}'}, bubbles: true}))"
                   title="Clique para discutir esta anotação">` +
            annotatedText +
            ` <strong class="annotation-label">${labelText}</strong></span>` +
            afterText
      }

      // Handle category-level annotations
      const categoryAnnotations = annotations.filter(a => a.type === 'category')
      if (categoryAnnotations.length > 0) {
        const categoryHtml = categoryAnnotations.map(ann => {
          const discrepancyType = this.findDiscrepancyForCategory(ann, doc.annotations, otherAnnotatorIds)
          const colorClass = this.getDiscrepancyColorClass(discrepancyType)
          const labelText = this.getCategoryLabel(ann.label)
          
          return `<div class="category-annotation ${colorClass}" 
                       onclick="this.dispatchEvent(new CustomEvent('annotation-click', {detail: {id: ${ann.id}, type: '${discrepancyType || 'none'}'}, bubbles: true}))"
                       title="Clique para discutir esta categoria">
                    <strong><v-icon small>mdi-tag</v-icon> ${labelText}</strong>
                  </div>`
        }).join('')
        
        html = categoryHtml + html
      }

      return html
    },

    findDiscrepancy(annotation: any, allAnnotations: any, otherAnnotatorIds: number[]) {
        let hasMissing = false
        for (const otherId of otherAnnotatorIds) {
            const otherAnns = allAnnotations[otherId] || []
            
            // Exact match: same span, same label
            const exactMatch = otherAnns.find((a: any) => 
                a.start_offset === annotation.start_offset && 
                a.end_offset === annotation.end_offset &&
                a.label === annotation.label
            )
            if (exactMatch) continue // Found a perfect match with this annotator

            // Same span, different label
            const sameSpan = otherAnns.find((a: any) => 
                a.start_offset === annotation.start_offset && 
                a.end_offset === annotation.end_offset
            )
            if (sameSpan) return DISCREPANCY_TYPES.DIFFERENT_LABEL

            // Overlapping span
            const overlappingAnn = otherAnns.find((a: any) => 
              a.start_offset < annotation.end_offset && a.end_offset > annotation.start_offset
            )
            if (overlappingAnn) return DISCREPANCY_TYPES.DIFFERENT_SPAN
            
            // If we reach here, no match found for this annotator
            hasMissing = true
        }
        
        if (hasMissing) {
            return DISCREPANCY_TYPES.MISSING_ANNOTATION
        }
        return null // No discrepancy found
    },

    findDiscrepancyForCategory(annotation: any, allAnnotations: any, otherAnnotatorIds: number[]) {
        for (const otherId of otherAnnotatorIds) {
            const otherAnns = allAnnotations[otherId] || []
            const hasCategory = otherAnns.some((a: any) => a.label === annotation.label && a.start_offset === undefined)
            if (!hasCategory) {
                return DISCREPANCY_TYPES.MISSING_ANNOTATION
            }
        }
        return null
    },

    getDiscrepancyColorClass(type: string | null): string {
      if (type === null) {
          return 'no-discrepancy'
      }
      switch (type) {
        case DISCREPANCY_TYPES.DIFFERENT_LABEL:
          return 'different-label'
        case DISCREPANCY_TYPES.DIFFERENT_SPAN:
          return 'different-span'
        case DISCREPANCY_TYPES.MISSING_ANNOTATION:
          return 'missing-annotation'
        default:
          return 'no-discrepancy'
      }
    },

    getAnnotatorColor(index: number): string {
      return this.annotatorColors[index % this.annotatorColors.length]
    },

    getAnnotatorStats(annotatorId: number): any {
      const doc = this.getCurrentDocument()
      if (!doc) return { total: 0, spans: 0, categories: 0 }
      
      const annotations = doc.annotations[annotatorId] || []
      const spans = annotations.filter((a: any) => a.start_offset !== undefined).length
      const categories = annotations.filter((a: any) => a.start_offset === undefined).length
      
      return {
        total: annotations.length,
        spans,
        categories
      }
    },

    getCategoryLabel(labelId: number): string {
        const category = this.categoryOptions.find(c => c.value === labelId)
        return category ? category.text : `Label ${labelId}`
    },

    prevDiscrepancy() {
      if (this.navigation.current > 0) {
        this.navigation.current--
      }
    },

    nextDiscrepancy() {
      if (this.navigation.current < this.summary.totalDiscrepancies - 1) {
        this.navigation.current++
      }
    },

    openDiscussion(annotationData: any) {
        const doc = this.getCurrentDocument()
        if (!doc) return
        
        this.selectedDiscrepancy = {
            docId: doc.docId,
            annotation: annotationData,
            text: doc.text,
            involvedAnnotators: this.selectedAnnotators
        }
        this.discussionPanel = true
    },

    onDiscrepancyResolved(context: any) {
        console.log('Discrepancy resolved:', context)
        
        // Update the current document as resolved
        const currentIndex = this.navigation.current
        if (this.navigation.discrepancyDocs[currentIndex]) {
          this.$set(this.navigation.discrepancyDocs[currentIndex], 'isResolved', true)
        }

        // Update summary
        this.summary.resolved++
        this.summary.pending--

        // Close panel and move to next unresolved discrepancy
        this.discussionPanel = false
        
        // Find next unresolved discrepancy
        let nextIndex = currentIndex
        for (let i = currentIndex + 1; i < this.navigation.discrepancyDocs.length; i++) {
          if (!this.navigation.discrepancyDocs[i].isResolved) {
            nextIndex = i
            break
          }
        }
        
        if (nextIndex === currentIndex) {
          // Look backwards
          for (let i = currentIndex - 1; i >= 0; i--) {
            if (!this.navigation.discrepancyDocs[i].isResolved) {
              nextIndex = i
              break
            }
          }
        }
        
        this.navigation.current = nextIndex
        
        this.$nuxt.$emit('show-snackbar', {
          text: 'Discrepância marcada como resolvida!',
          color: 'success'
        })
    },

    onVoteSubmitted(voteData: any) {
        console.log('Vote submitted:', voteData)
        this.$nuxt.$emit('show-snackbar', {
          text: 'Voto registado com sucesso!',
          color: 'info'
        })
    },

    onConsensusProposed(consensusData: any) {
        console.log('Consensus proposed:', consensusData)
        this.$nuxt.$emit('show-snackbar', {
          text: 'Proposta de consenso enviada!',
          color: 'info'
        })
    },

    setupKeyboardShortcuts() {
      this.keyboardHandler = (event: KeyboardEvent) => {
        if (event.target && (event.target as HTMLElement).tagName === 'INPUT' || 
            (event.target as HTMLElement).tagName === 'TEXTAREA') {
          return // Don't handle shortcuts when typing
        }
        
        switch (event.key) {
          case 'ArrowLeft':
            event.preventDefault()
            this.prevDiscrepancy()
            break
          case 'ArrowRight':
            event.preventDefault()
            this.nextDiscrepancy()
            break
          case 'Escape':
            event.preventDefault()
            this.discussionPanel = false
            break
          case '?':
            event.preventDefault()
            this.showKeyboardHelp = true
            break
        }
      }
      
      document.addEventListener('keydown', this.keyboardHandler)
      
      // Handle annotation clicks
      this.annotationClickHandler = (event: any) => {
        if (event.detail && event.detail.id) {
          this.openDiscussion(event.detail)
        }
      }
      
      document.addEventListener('annotation-click', this.annotationClickHandler)
    },

    removeKeyboardShortcuts() {
      if (this.keyboardHandler) {
        document.removeEventListener('keydown', this.keyboardHandler)
      }
      if (this.annotationClickHandler) {
        document.removeEventListener('annotation-click', this.annotationClickHandler)
      }
    },

    setupRealtimeUpdates() {
      // Poll for updates every 30 seconds
      this.realtimeUpdates = setInterval(() => {
        this.refreshCurrentDiscrepancy()
      }, 30000)
    },

    cleanupRealtimeUpdates() {
      if (this.realtimeUpdates) {
        clearInterval(this.realtimeUpdates)
      }
    },

    async refreshCurrentDiscrepancy() {
      const doc = this.getCurrentDocument()
      if (!doc) return
      
      try {
        // Refresh annotations for current document
        delete this.allAnnotations[doc.docId]
        await this.getAnnotationsForExample(doc.docId)
        
        // Check if still has discrepancy
        const userAnnotations = {}
        const annotations = this.allAnnotations[doc.docId] || []
        
        for(const ann of annotations) {
            if (!userAnnotations[ann.user]) {
                userAnnotations[ann.user] = []
            }
            userAnnotations[ann.user].push(ann)
        }
        
        const discrepancyInfo = this.getDiscrepancyInfo(userAnnotations)
        if (!discrepancyInfo.hasDiscrepancy) {
          // Document no longer has discrepancy, remove it
          this.navigation.discrepancyDocs.splice(this.navigation.current, 1)
          this.summary.totalDiscrepancies--
          
          if (this.navigation.current >= this.navigation.discrepancyDocs.length) {
            this.navigation.current = Math.max(0, this.navigation.discrepancyDocs.length - 1)
          }
        } else {
          // Update annotations
          this.$set(this.navigation.discrepancyDocs[this.navigation.current], 'annotations', userAnnotations)
        }
      } catch (error) {
        console.error('Error refreshing discrepancy:', error)
      }
    }
  }
})
</script>

<style scoped>
.annotation {
  padding: 3px 6px;
  margin: 0 1px;
  border-radius: 4px;
  cursor: pointer;
  display: inline-block;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.annotation:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.annotation-label {
  font-size: 0.75em;
  font-weight: bold;
  margin-left: 4px;
  opacity: 0.9;
}

.category-annotation {
    border-left: 4px solid;
    padding: 8px 12px;
    margin-bottom: 8px;
    background-color: #f8f9fa;
    border-radius: 0 4px 4px 0;
    cursor: pointer;
    transition: all 0.2s ease;
}

.category-annotation:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transform: translateX(2px);
}

/* Cores das discrepâncias */
.different-label {
  background-color: rgba(255, 152, 0, 0.6);
  border-color: #ff9800;
}

.different-span {
  background-color: rgba(244, 67, 54, 0.6);
  border-color: #f44336;
}

.missing-annotation {
  background-color: rgba(158, 158, 158, 0.6);
  border-color: #9e9e9e;
}

.no-discrepancy {
  background-color: rgba(76, 175, 80, 0.4);
  border-color: #4caf50;
}

/* Legenda */
.legend-color {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 3px;
  margin-right: 8px;
  border: 1px solid rgba(0,0,0,0.2);
}

.legend-color.different-label {
  background-color: rgba(255, 152, 0, 0.6);
}

.legend-color.different-span {
  background-color: rgba(244, 67, 54, 0.6);
}

.legend-color.missing-annotation {
  background-color: rgba(158, 158, 158, 0.6);
}

.legend-color.no-discrepancy {
  background-color: rgba(76, 175, 80, 0.4);
}

/* Colunas dos anotadores */
.discrepancy-column {
  height: 100%;
  border-top: 3px solid transparent;
}

.annotator-0 { border-top-color: #2196f3; }
.annotator-1 { border-top-color: #4caf50; }
.annotator-2 { border-top-color: #9c27b0; }
.annotator-3 { border-top-color: #ff9800; }
.annotator-4 { border-top-color: #f44336; }
.annotator-5 { border-top-color: #009688; }
.annotator-6 { border-top-color: #e91e63; }
.annotator-7 { border-top-color: #3f51b5; }

.annotated-text {
  min-height: 200px;
  line-height: 2.2;
  font-size: 1.1em;
}

.discussion-panel {
  z-index: 1000;
}

/* Responsivo */
@media (max-width: 960px) {
  .annotated-text {
    font-size: 1em;
    line-height: 2;
  }
  
  .annotation {
    padding: 2px 4px;
  }
  
  .annotation-label {
    font-size: 0.7em;
  }
}
</style> 