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
          <h1 class="text-h4 ml-3">Comparação Lado a Lado das Anotações</h1>
        </div>
        <v-alert
          v-if="!hasDiscrepancies"
          type="info"
          class="mb-4"
        >
          Não foram encontradas discrepâncias neste projeto.
        </v-alert>
      </v-col>
    </v-row>

    <!-- Métricas Gerais -->
    <v-row class="mb-4">
      <v-col cols="12" md="6" lg="3">
        <v-card class="text-center pa-4 metric-card">
          <v-icon size="48" color="primary" class="mb-2">mdi-percent</v-icon>
          <div class="text-h4 primary--text">{{ globalDiscrepancyPercentage }}%</div>
          <div class="text-subtitle-1">Taxa de Discrepância Geral</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" lg="3">
        <v-card class="text-center pa-4 metric-card">
          <v-icon size="48" color="orange" class="mb-2">mdi-account-group</v-icon>
          <div class="text-h4 orange--text">{{ totalAnnotators }}</div>
          <div class="text-subtitle-1">Anotadores Envolvidos</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" lg="3">
        <v-card class="text-center pa-4 metric-card">
          <v-icon size="48" color="error" class="mb-2">mdi-alert-circle</v-icon>
          <div class="text-h4 error--text">{{ totalDiscrepancies }}</div>
          <div class="text-subtitle-1">Total de Discrepâncias</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" lg="3">
        <v-card class="text-center pa-4 metric-card">
          <v-icon size="48" color="success" class="mb-2">mdi-check-circle</v-icon>
          <div class="text-h4 success--text">{{ consistentExamples }}</div>
          <div class="text-subtitle-1">Exemplos Consistentes</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filtros -->
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <v-select
          v-model="selectedExample"
          :items="exampleOptions"
          label="Filtrar por exemplo"
          clearable
          outlined
          dense
          prepend-inner-icon="mdi-filter"
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="selectedDataset"
          :items="datasetOptions"
          label="Escolher dataset"
          clearable
          outlined
          dense
          prepend-inner-icon="mdi-database"
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="selectedAnnotator1"
          :items="nonAdminAnnotatorOptions"
          label="Primeiro anotador"
          clearable
          outlined
          dense
          prepend-inner-icon="mdi-account"
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="selectedAnnotator2"
          :items="nonAdminAnnotatorOptions"  
          label="Segundo anotador"
          clearable
          outlined
          dense
          prepend-inner-icon="mdi-account-plus"
        />
      </v-col>
    </v-row>

    <!-- Informação sobre comparação específica -->
    <v-alert
      v-if="selectedAnnotator1 && selectedAnnotator2"
      type="info"
      outlined
      class="mb-4"
    >
      <v-icon left>mdi-information</v-icon>
      Comparando anotações entre <strong>{{ selectedAnnotator1 }}</strong> e <strong>{{ selectedAnnotator2 }}</strong>
      <span v-if="selectedDataset"> no dataset <strong>{{ selectedDataset }}</strong></span>
    </v-alert>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-center align-center" style="height: 300px">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <!-- Comparações -->
    <div v-else>
      <v-row v-for="comparison in filteredComparisons" :key="comparison.exampleId" class="mb-6">
        <v-col cols="12">
          <v-card class="elevation-2">
            <v-card-title class="primary white--text">
              <v-icon left color="white">mdi-text-box</v-icon>
              Exemplo: {{ comparison.exampleText }}
              <v-spacer></v-spacer>
              <v-chip
                color="white"
                text-color="primary"
                small
                class="mr-2"
              >
                {{ comparison.dataset }}
              </v-chip>
              <v-chip
                :color="comparison.hasDiscrepancy ? 'error' : 'success'"
                dark
                small
              >
                {{ comparison.hasDiscrepancy ? 'Discrepância' : 'Consenso' }}
              </v-chip>
            </v-card-title>

            <v-card-text class="pa-0">
              <!-- Texto do exemplo -->
              <div class="pa-4 bg-grey-lighten-5">
                <div class="text-subtitle-2 mb-2">Texto do Exemplo:</div>
                <div class="text-body-1 example-text">{{ comparison.exampleText }}</div>
              </div>

              <!-- Comparação das anotações -->
              <div v-if="comparison.annotations.length === 0" class="pa-4 text-center">
                <v-icon size="48" color="grey">mdi-clipboard-outline</v-icon>
                <div class="text-subtitle-1 grey--text mt-2">Nenhuma anotação encontrada</div>
                <div class="text-caption grey--text">Este exemplo ainda não foi anotado por nenhum utilizador.</div>
              </div>
              
              <v-row v-else no-gutters>
                <v-col
                  v-for="(annotation, index) in comparison.annotations"
                  :key="index"
                  :cols="getColumnSize(comparison.annotations.length)"
                  class="annotation-column"
                >
                  <div class="pa-4" :class="getAnnotationBackgroundClass(index)">
                    <div class="d-flex align-center mb-3">
                      <v-avatar :color="getUserColor(annotation.annotator)" size="32" class="mr-2">
                        <span class="white--text text-caption">{{ getInitials(annotation.annotator) }}</span>
                      </v-avatar>
                      <div>
                        <div class="font-weight-bold">{{ annotation.annotator }}</div>
                        <div class="text-caption text--secondary">
                          {{ new Date(annotation.createdAt).toLocaleDateString('pt-PT') }}
                        </div>
                      </div>
                    </div>

                    <!-- Labels da anotação -->
                    <div class="mb-3">
                      <div class="text-subtitle-2 mb-2">Etiquetas:</div>
                      <div v-if="annotation.labels.length === 0" class="text-caption text--secondary">
                        Nenhuma etiqueta atribuída
                      </div>
                      <v-chip
                        v-for="label in annotation.labels"
                        :key="label.id"
                        small
                        :color="getLabelColor(label.name)"
                        class="mr-1 mb-1"
                        dark
                      >
                        {{ label.name }}
                      </v-chip>
                    </div>

                    <!-- Estatísticas da anotação -->
                    <div class="annotation-stats">
                      <div class="d-flex justify-space-between mb-2">
                        <span class="text-caption">Concordância:</span>
                        <span class="text-caption font-weight-bold">{{ annotation.agreementPercentage }}%</span>
                      </div>
                      <v-progress-linear
                        :value="annotation.agreementPercentage"
                        :color="getPercentageColor(annotation.agreementPercentage)"
                        height="6"
                        rounded
                      ></v-progress-linear>
                    </div>
                  </div>
                </v-col>
              </v-row>

              <!-- Análise detalhada da discrepância -->
              <div v-if="comparison.hasDiscrepancy" class="pa-4 bg-red-lighten-5">
                <div class="text-subtitle-2 mb-2 red--text">
                  <v-icon color="red" class="mr-1">mdi-alert-circle</v-icon>
                  Análise da Discrepância:
                </div>
                <v-row>
                  <v-col cols="12" md="6">
                    <div class="text-body-2 mb-1">
                      <strong>Diferenças principais:</strong>
                    </div>
                    <ul class="text-body-2">
                      <li v-for="diff in comparison.differences" :key="diff">{{ diff }}</li>
                    </ul>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-body-2 mb-1">
                      <strong>Percentagem de concordância:</strong>
                    </div>
                    <div class="text-h6 red--text">{{ comparison.overallAgreement }}%</div>
                    <div class="text-body-2 mb-1 mt-2">
                      <strong>Limiar do projeto:</strong>
                    </div>
                    <div class="text-body-2">{{ project.minPercentage }}%</div>
                  </v-col>
                </v-row>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- Sem dados para mostrar -->
    <div v-if="!loading && filteredComparisons.length === 0" class="text-center py-8">
      <v-icon size="64" color="grey">mdi-file-search</v-icon>
      <div class="text-h6 grey--text mt-2">Nenhuma anotação encontrada</div>
      <div class="text-body-2 grey--text">
        Os exemplos ainda não foram anotados ou não há discrepâncias com anotações reais no projeto.
        <br>
        Ajuste os filtros ou verifique se existem anotações nos exemplos.
      </div>
    </div>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'
import type { Percentage } from '~/domain/models/metrics/metrics'

interface AnnotationComparison {
  exampleId: string
  exampleText: string
  dataset: string
  hasDiscrepancy: boolean
  overallAgreement: number
  annotations: Array<{
    annotator: string
    labels: Array<{ id: number; name: string }>
    agreementPercentage: number
    createdAt: string
  }>
  differences: string[]
}

export default Vue.extend({
  name: 'DiscrepancySideBySide',
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      loading: true,
      items: {} as Percentage,
      comparisons: [] as AnnotationComparison[],
      selectedExample: null as string | null,
      selectedDataset: null as string | null,
      selectedAnnotator1: null as string | null,
      selectedAnnotator2: null as string | null,
      exampleNames: {} as Record<string, string>,
      annotators: [] as string[],
      datasets: [] as string[]
    }
  },

  async fetch() {
    this.loading = true
    try {
      // Buscar dados de percentagens
      if (this.project.canDefineCategory) {
        this.items = await this.$repositories.metrics.fetchCategoryPercentage(this.projectId)
      } else if (this.project.canDefineSpan) {
        this.items = await this.$repositories.metrics.fetchSpanPercentage(this.projectId)
      } else if (this.project.canDefineRelation) {
        this.items = await this.$repositories.metrics.fetchRelationPercentage(this.projectId)
      }

      // Buscar estatísticas de anotadores reais
      try {
        const stats = await this.$repositories.metrics.fetchDisagreementStats(this.projectId)
        if (stats.annotators && stats.annotators.length > 0) {
          // Filtrar administradores
          this.annotators = stats.annotators.filter(annotator => 
            !annotator.toLowerCase().includes('admin') && 
            !annotator.toLowerCase().includes('administrador')
          )
        }
        
        // Buscar datasets disponíveis (assumindo que há uma propriedade ou método para isso)
        if (stats.textTypes && stats.textTypes.length > 0) {
          this.datasets = stats.textTypes
        } else {
          // Fallback para datasets simulados
          this.datasets = ['Dataset Principal', 'Dataset Teste', 'Dataset Validação']
        }
      } catch (error) {
        console.warn('Não foi possível carregar dados reais dos anotadores:', error)
        // Fallback para datasets simulados
        this.datasets = ['Dataset Principal', 'Dataset Teste', 'Dataset Validação']
      }

      // Processar dados para comparações
      await this.processDiscrepancyData()
    } catch (error) {
      console.error('Erro ao carregar dados de comparação:', error)
    } finally {
      this.loading = false
    }
  },

  computed: {
    ...mapGetters('projects', ['project']),
    
    projectId(): string {
      return this.$route.params.id
    },

    hasDiscrepancies(): boolean {
      return this.comparisons.some(comp => comp.hasDiscrepancy)
    },

    globalDiscrepancyPercentage(): number {
      if (this.comparisons.length === 0) return 0
      const discrepantCount = this.comparisons.filter(comp => comp.hasDiscrepancy).length
      return Math.round((discrepantCount / this.comparisons.length) * 100)
    },

    totalAnnotators(): number {
      return this.annotators.length
    },

    totalDiscrepancies(): number {
      return this.comparisons.filter(comp => comp.hasDiscrepancy).length
    },

    consistentExamples(): number {
      return this.comparisons.filter(comp => !comp.hasDiscrepancy).length
    },

    exampleOptions() {
      return [
        { text: 'Todos os exemplos', value: null },
        ...Object.entries(this.exampleNames).map(([id, name]) => ({
          text: name,
          value: id
        }))
      ]
    },

    datasetOptions() {
      return [
        { text: 'Todos os datasets', value: null },
        ...this.datasets.map(dataset => ({
          text: dataset,
          value: dataset
        }))
      ]
    },

    nonAdminAnnotators() {
      // Filtrar admins (assumindo que nomes com 'admin' são administradores)
      return this.annotators.filter(annotator => 
        !annotator.toLowerCase().includes('admin') && 
        !annotator.toLowerCase().includes('administrador')
      )
    },

    nonAdminAnnotatorOptions() {
      return [
        { text: 'Selecionar anotador', value: null },
        ...this.nonAdminAnnotators.map(annotator => ({
          text: annotator,
          value: annotator
        }))
      ]
    },

    filteredComparisons(): AnnotationComparison[] {
      return this.comparisons.filter(comp => {
        // Filtro por exemplo
        if (this.selectedExample && comp.exampleId !== this.selectedExample) {
          return false
        }
        
        // Filtro por dataset (se implementado)
        if (this.selectedDataset && comp.dataset !== this.selectedDataset) {
          return false
        }
        
        // Filtro por anotadores específicos
        if (this.selectedAnnotator1 || this.selectedAnnotator2) {
          const hasAnnotator1 = !this.selectedAnnotator1 || comp.annotations.some(ann => ann.annotator === this.selectedAnnotator1)
          const hasAnnotator2 = !this.selectedAnnotator2 || comp.annotations.some(ann => ann.annotator === this.selectedAnnotator2)
          
          // Se ambos os anotadores foram selecionados, ambos devem estar presentes
          if (this.selectedAnnotator1 && this.selectedAnnotator2) {
            return hasAnnotator1 && hasAnnotator2
          }
          
          // Se apenas um foi selecionado, deve estar presente
          return hasAnnotator1 || hasAnnotator2
        }
        
        return true
      }).map(comp => {
        // Se anotadores específicos foram selecionados, filtrar apenas suas anotações
        if (this.selectedAnnotator1 || this.selectedAnnotator2) {
          const filteredAnnotations = comp.annotations.filter(ann => {
            if (this.selectedAnnotator1 && this.selectedAnnotator2) {
              return ann.annotator === this.selectedAnnotator1 || ann.annotator === this.selectedAnnotator2
            }
            return !this.selectedAnnotator1 || ann.annotator === this.selectedAnnotator1 ||
                   !this.selectedAnnotator2 || ann.annotator === this.selectedAnnotator2
          })
          
          return {
            ...comp,
            annotations: filteredAnnotations
          }
        }
        
        return comp
      })
    }
  },

  methods: {
    async processDiscrepancyData() {
      const comparisons: AnnotationComparison[] = []
      
      console.log('Processando dados de discrepância...')
      console.log('Items encontrados:', Object.keys(this.items).length)
      console.log('Tipo de projeto:', {
        canDefineCategory: this.project.canDefineCategory,
        canDefineSpan: this.project.canDefineSpan,
        canDefineRelation: this.project.canDefineRelation
      })
      console.log('Repositórios disponíveis:', {
        category: !!this.$repositories.category,
        span: !!this.$repositories.span,
        relation: !!this.$repositories.relation,
        textLabel: !!this.$repositories.textLabel,
        segmentation: !!this.$repositories.segmentation,
        boundingBox: !!this.$repositories.boundingBox
      })
      
      for (const [exampleId, labels] of Object.entries(this.items)) {
        try {
          console.log(`Processando exemplo ${exampleId} com labels:`, labels)
          
          // Buscar informações do exemplo
          const example = await this.$repositories.example.findById(this.projectId, parseInt(exampleId))
          this.exampleNames[exampleId] = example.text || `Exemplo ${exampleId}`

          // Buscar dados de anotações reais
          const annotations = await this.generateAnnotationData(exampleId, labels)
          
          // Só incluir comparações se há anotações reais E há discrepância
          if (annotations.length > 0) {
            // Calcular concordância geral baseado nas anotações reais
            const percentages = Object.values(labels)
            const maxAgreement = percentages.length > 0 ? Math.max(...percentages) : 0
            const hasDiscrepancy = maxAgreement < this.project.minPercentage && maxAgreement > 0

                         // Incluir TODAS as anotações que existem (mesmo de um só anotador)
             const uniqueAnnotators = new Set(annotations.map(ann => ann.annotator))
             
             // Identificar diferenças
             const differences = this.identifyDifferences(labels)

             // Atribuir dataset (simulado baseado no ID do exemplo ou usar dados reais)
             const datasetName = this.datasets[parseInt(exampleId) % this.datasets.length] || 'Dataset Principal'

             comparisons.push({
               exampleId,
               exampleText: this.exampleNames[exampleId],
               dataset: datasetName,
               hasDiscrepancy,
               overallAgreement: Math.round(maxAgreement),
               annotations,
               differences
             })
             
             console.log(`Exemplo ${exampleId}: incluído - ${uniqueAnnotators.size} anotador(es), ${annotations.length} anotações`)
          } else {
            console.log(`Exemplo ${exampleId} ignorado - sem anotações`)
          }

          // Coletar anotadores únicos das anotações reais
          annotations.forEach(ann => {
            // Filtrar administradores
            if (!ann.annotator.toLowerCase().includes('admin') && 
                !ann.annotator.toLowerCase().includes('administrador') &&
                !this.annotators.includes(ann.annotator)) {
              this.annotators.push(ann.annotator)
            }
          })

        } catch (error) {
          console.error(`Erro ao processar exemplo ${exampleId}:`, error)
        }
      }

      this.comparisons = comparisons.sort((a, b) => {
        // Ordenar por discrepâncias primeiro, depois por ID
        if (a.hasDiscrepancy && !b.hasDiscrepancy) return -1
        if (!a.hasDiscrepancy && b.hasDiscrepancy) return 1
        return parseInt(a.exampleId) - parseInt(b.exampleId)
      })
      
      console.log(`Processamento concluído: ${this.comparisons.length} comparações criadas`)
      console.log('Comparações:', this.comparisons)
    },

    async generateAnnotationData(exampleId: string, labels: Record<string, number>) {
      const annotations = []
      
      // Buscar anotações reais baseadas no tipo de projeto
      try {
        let realAnnotations = []
        
        // Tentar buscar anotações de TODOS os tipos disponíveis
        const allRepositories = ['category', 'span', 'relation', 'textLabel', 'segmentation', 'boundingBox']
        
        for (const repoType of allRepositories) {
          if (this.$repositories[repoType] && realAnnotations.length === 0) {
            try {
              console.log(`Tentando buscar anotações de ${repoType} para exemplo ${exampleId}`)
              const annotations = await this.$repositories[repoType].list(this.projectId, parseInt(exampleId))
              if (annotations && annotations.length > 0) {
                realAnnotations = annotations
                console.log(`Encontradas ${annotations.length} anotações de ${repoType}`)
                break
              }
            } catch (e) {
              console.warn(`Erro ao buscar anotações de ${repoType}:`, e)
            }
          }
        }
        
        // Fallback: tentar baseado no tipo do projeto
        if (realAnnotations.length === 0) {
          if (this.project.canDefineCategory && this.$repositories.category) {
            try {
              realAnnotations = await this.$repositories.category.list(this.projectId, parseInt(exampleId))
            } catch (e) {
              console.warn('Erro ao buscar anotações de categoria:', e)
            }
          }
          
          if (this.project.canDefineSpan && this.$repositories.span) {
            try {
              realAnnotations = await this.$repositories.span.list(this.projectId, parseInt(exampleId))
            } catch (e) {
              console.warn('Erro ao buscar anotações de span:', e)
            }
          }
          
          if (this.project.canDefineRelation && this.$repositories.relation) {
            try {
              realAnnotations = await this.$repositories.relation.list(this.projectId, parseInt(exampleId))
            } catch (e) {
              console.warn('Erro ao buscar anotações de relação:', e)
            }
          }
        }
        
        console.log(`Exemplo ${exampleId}: encontradas ${realAnnotations.length} anotações`)
        
        if (realAnnotations && realAnnotations.length > 0) {
          // Processar anotações reais
          const annotatorGroups = new Map()
          
          realAnnotations.forEach((annotation, index) => {
            console.log(`Processando anotação ${index}:`, annotation)
            
            // Usar ID do usuário ou nome disponível - ser mais flexível
            let annotatorName = `Usuário ${annotation.user || annotation.userId || annotation.author || annotation.created_by || index + 1}`
            
            // Tentar obter nome mais específico se disponível
            if (annotation.username) {
              annotatorName = annotation.username
            } else if (annotation.annotator) {
              annotatorName = annotation.annotator
            } else if (annotation.user_name) {
              annotatorName = annotation.user_name
            } else if (annotation.author_name) {
              annotatorName = annotation.author_name
            }
            
            // Não filtrar administradores temporariamente para ver todos os dados
            // if (annotatorName.toLowerCase().includes('admin') || 
            //     annotatorName.toLowerCase().includes('administrador')) {
            //   return
            // }
            
            if (!annotatorGroups.has(annotatorName)) {
              annotatorGroups.set(annotatorName, {
                labels: [],
                createdAt: annotation.created_at || annotation.createdAt || annotation.date || new Date().toISOString()
              })
            }
            
            // Extrair label real baseado no tipo de projeto e estrutura da anotação - ser mais flexível
            let labelName = 'Sem etiqueta'
            
            if (annotation.label) {
              labelName = typeof annotation.label === 'object' ? annotation.label.text || annotation.label.name || JSON.stringify(annotation.label) : annotation.label
            } else if (annotation.text) {
              labelName = annotation.text
            } else if (annotation.category) {
              labelName = typeof annotation.category === 'object' ? annotation.category.text || annotation.category.name || JSON.stringify(annotation.category) : annotation.category
            } else if (annotation.type) {
              labelName = annotation.type
            } else if (annotation.name) {
              labelName = annotation.name
            } else if (annotation.value) {
              labelName = annotation.value
            } else {
              // Fallback para mostrar algo útil
              labelName = `Anotação ${annotation.id || index + 1}`
            }
            
            annotatorGroups.get(annotatorName).labels.push({
              id: annotation.id || index + 1,
              name: labelName
            })
            
            console.log(`Adicionada label "${labelName}" para anotador "${annotatorName}"`)
          })

          // Converter grupos de anotadores em dados de comparação
          for (const [annotator, data] of annotatorGroups) {
            // Obter percentagem de concordância dos dados de métricas
            const labelNames = data.labels.map(l => l.name)
            let agreementPercentage = 0
            
            // Tentar encontrar percentagem para qualquer uma das labels
            for (const labelName of labelNames) {
              if (labels[labelName]) {
                agreementPercentage = Math.max(agreementPercentage, labels[labelName])
              }
            }
            
            // Se não encontrou nas métricas, usar uma percentagem baseada no número de labels
            if (agreementPercentage === 0 && data.labels.length > 0) {
              agreementPercentage = Math.min(100, data.labels.length * 25)
            }
            
            annotations.push({
              annotator,
              labels: data.labels,
              agreementPercentage: Math.round(agreementPercentage),
              createdAt: data.createdAt
            })
          }
        }
        
      } catch (error) {
        console.error('Erro ao buscar anotações:', error)
      }

      console.log(`Exemplo ${exampleId}: processadas ${annotations.length} anotações de anotadores`)
      return annotations
    },

    identifyDifferences(labels: Record<string, number>): string[] {
      const differences = []
      const entries = Object.entries(labels)
      
      if (entries.length > 1) {
        const [bestLabel, bestPerc] = entries.reduce((a, b) => a[1] > b[1] ? a : b)
        const [worstLabel, worstPerc] = entries.reduce((a, b) => a[1] < b[1] ? a : b)
        
        differences.push(`Maior concordância: ${bestLabel} (${bestPerc.toFixed(1)}%)`)
        differences.push(`Menor concordância: ${worstLabel} (${worstPerc.toFixed(1)}%)`)
        differences.push(`Diferença: ${(bestPerc - worstPerc).toFixed(1)} pontos percentuais`)
      }
      
      return differences
    },

    getAnnotationBackgroundClass(index: number): string {
      const classes = ['bg-blue-lighten-5', 'bg-green-lighten-5', 'bg-orange-lighten-5']
      return classes[index % classes.length] || 'bg-grey-lighten-5'
    },

    getUserColor(annotator: string): string {
      const colors = ['#1976D2', '#388E3C', '#F57C00', '#7B1FA2', '#D32F2F']
      const index = this.annotators.indexOf(annotator)
      return colors[index % colors.length] || '#757575'
    },

    getInitials(name: string): string {
      return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)
    },

    getLabelColor(labelName: string): string {
      const colors = ['primary', 'secondary', 'accent', 'error', 'info', 'success', 'warning']
      const hash = labelName.split('').reduce((a, b) => a + b.charCodeAt(0), 0)
      return colors[hash % colors.length]
    },

    getPercentageColor(percentage: number): string {
      if (percentage < this.project.minPercentage) return 'error'
      if (percentage < 70) return 'warning'
      return 'success'
    },

    getColumnSize(annotationCount: number): number {
      // Otimizar layout baseado no número de anotações
      if (annotationCount === 1) return 12
      if (annotationCount === 2) return 6  // Comparação lado a lado perfeita
      if (annotationCount === 3) return 4
      return Math.floor(12 / Math.min(annotationCount, 4))
    }
  }
})
</script>

<style scoped>
.metric-card {
  transition: transform 0.2s ease-in-out;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.annotation-column {
  border-right: 1px solid #e0e0e0;
}

.annotation-column:last-child {
  border-right: none;
}

.example-text {
  font-family: 'Roboto Mono', monospace;
  background: white;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.annotation-stats {
  background: rgba(255, 255, 255, 0.7);
  padding: 8px;
  border-radius: 4px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

::v-deep .v-progress-linear {
  border-radius: 3px !important;
}
</style> 