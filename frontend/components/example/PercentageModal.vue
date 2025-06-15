<template>
  <v-dialog v-model="dialog" max-width="800">
    <v-card>
      <!-- Alerta de erro de base de dados -->
      <v-alert
        v-if="databaseError"
        type="error"
        dense
        class="ma-4 mb-0"
      >
       Database is currently unavailable. Please try again later.
      </v-alert>
      <v-card-title class="headline primary white--text">
        <v-icon color="white" left>mdi-flag</v-icon>
        Sinalizar Discrepância
        <v-spacer></v-spacer>
        <v-btn icon dark @click="dialog = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="pa-6">
        <div v-if="loading" class="text-center py-8">
          <v-progress-circular indeterminate color="primary" size="50"></v-progress-circular>
          <div class="mt-4">Carregando dados...</div>
        </div>

        <div v-else-if="error" class="text-center py-8">
          <v-icon color="error" size="60">mdi-alert-circle</v-icon>
          <div class="text-h6 mt-2 error--text">Erro ao carregar dados</div>
          <div class="text-body-2 mt-2">{{ error }}</div>
        </div>

        <div v-else>
          <!-- Texto do exemplo -->
          <v-card outlined class="mb-4">
            <v-card-subtitle class="text-subtitle-2 font-weight-bold">
              Texto do Exemplo:
            </v-card-subtitle>
            <v-card-text class="pt-2">
              <div class="text-body-1">{{ exampleText }}</div>
            </v-card-text>
          </v-card>

          <!-- Percentagens das labels -->
          <v-card outlined class="mb-4">
            <v-card-title class="text-h6">
              <v-icon color="primary" left>mdi-chart-pie</v-icon>
              Percentagens de Anotação por Label
            </v-card-title>
            <v-card-text>
              <div v-if="labelPercentages && Object.keys(labelPercentages).length > 0">
                <div 
                  v-for="(percentage, label) in labelPercentages" 
                  :key="label"
                  class="label-percentage-item mb-3"
                >
                  <div class="d-flex align-center justify-space-between mb-2">
                    <span class="label-name font-weight-medium">{{ label }}</span>
                    <v-chip 
                      :color="getPercentageColor(percentage)"
                      text-color="white"
                      small
                    >
                      {{ Math.round(percentage) }}%
                    </v-chip>
                  </div>
                                     <v-progress-linear
                     :value="percentage"
                     :color="getPercentageColor(percentage)"
                     height="12"
                     rounded
                     class="mb-1"
                   >
                     <template #default="{ value: progressValue }">
                       <small class="white--text font-weight-bold">{{ Math.round(progressValue) }}%</small>
                     </template>
                   </v-progress-linear>
                </div>

                          <!-- Estado atual da sinalização -->
          <v-card v-if="currentFlagStatus" outlined class="mb-4">
            <v-card-title class="text-h6">
              <v-icon color="info" left>mdi-flag-outline</v-icon>
              Estado Atual da Sinalização
            </v-card-title>
            <v-card-text>
              <div class="d-flex align-center mb-2">
                <v-chip 
                  :color="currentFlagStatus.isDiscrepant ? 'error' : 'success'"
                  text-color="white"
                  class="mr-2"
                >
                  <v-icon left small>
                    {{ currentFlagStatus.isDiscrepant ? 'mdi-alert-circle' : 'mdi-check-circle' }}
                  </v-icon>
                  {{ currentFlagStatus.isDiscrepant ? 'Discrepante' : 'Consistente' }}
                </v-chip>
                <span class="text-body-2 grey--text">
                  (sinalizado anteriormente)
                </span>
              </div>
              
                             <div v-if="currentFlagStatus.flaggedAt" class="text-body-2 mb-2">
                <strong>Data:</strong> {{ formatDate(currentFlagStatus.flaggedAt) }}
              </div>
              
              <div v-if="currentFlagStatus.observations" class="text-body-2">
                <strong>Observações anteriores:</strong>
                <div class="mt-1 pa-2 grey lighten-4 rounded">
                  <em>{{ currentFlagStatus.observations }}</em>
                </div>
              </div>
            </v-card-text>
          </v-card>

          <!-- Análise automática -->
          <v-alert
            :type="hasAutomaticDiscrepancy ? 'warning' : 'success'"
            outlined
            class="mt-4"
          >
            <div class="d-flex align-center">
              <v-icon 
                :color="hasAutomaticDiscrepancy ? 'warning' : 'success'"
                left
              >
                {{ hasAutomaticDiscrepancy ? 'mdi-alert' : 'mdi-check-circle' }}
              </v-icon>
              <div>
                <strong>Análise Automática:</strong>
                {{ hasAutomaticDiscrepancy 
                  ? `Possível discrepância detectada (concordância máxima: ${maxPercentage}%)` 
                  : `Consenso adequado (concordância máxima: ${maxPercentage}%)` 
                }}
              </div>
            </div>
          </v-alert>
              </div>
              <div v-else class="text-center py-4">
                <v-icon color="grey" size="48">mdi-information</v-icon>
                <div class="text-body-1 grey--text mt-2">
                  Nenhuma anotação encontrada para este exemplo
                </div>
              </div>
            </v-card-text>
          </v-card>

          <!-- Decisão manual -->
          <v-card outlined>
            <v-card-title class="text-h6">
              <v-icon color="primary" left>mdi-account-check</v-icon>
              {{ currentFlagStatus ? 'Alterar Sinalização' : 'Decisão Manual' }}
            </v-card-title>
            <v-card-text>
              <div v-if="currentFlagStatus" class="mb-3">
                <v-alert type="info" outlined dense>
                  <div class="text-body-2">
                    Esta anotação já foi sinalizada anteriormente. 
                    Pode alterar a classificação abaixo se necessário.
                  </div>
                </v-alert>
              </div>
              
              <v-radio-group v-model="manualDecision" class="mt-2">
                <v-radio
                  label="Considerar como discrepante"
                  value="discrepant"
                  color="error"
                >
                  <template #label>
                    <span class="error--text font-weight-medium">
                      <v-icon color="error" small class="mr-1">mdi-alert-circle</v-icon>
                      Considerar como discrepante
                    </span>
                  </template>
                </v-radio>
                <v-radio
                  label="Considerar como consistente"
                  value="consistent"
                  color="success"
                >
                  <template #label>
                    <span class="success--text font-weight-medium">
                      <v-icon color="success" small class="mr-1">mdi-check-circle</v-icon>
                      Considerar como consistente
                    </span>
                  </template>
                </v-radio>
              </v-radio-group>

              <!-- Campo de observações -->
              <v-textarea
                v-model="observations"
                label="Observações (opcional)"
                placeholder="Adicione observações sobre a sua decisão..."
                rows="3"
                outlined
                class="mt-3"
              ></v-textarea>
            </v-card-text>
          </v-card>
        </div>
      </v-card-text>

      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn text @click="dialog = false">
          Cancelar
        </v-btn>
        <v-btn 
          color="primary" 
          :disabled="!manualDecision || loading"
          :loading="saving"
          @click="saveDecision"
        >
          <v-icon left>mdi-content-save</v-icon>
          {{ currentFlagStatus ? 'Atualizar Sinalização' : 'Guardar Decisão' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'
import type { PropType } from 'vue'
import { ExampleDTO } from '~/services/application/example/exampleData'

interface LabelPercentages {
  [label: string]: number
}

interface FlagStatus {
  isDiscrepant: boolean
  flaggedBy?: string
  flaggedAt?: string
  observations?: string
  flaggedManually: boolean
}

export default Vue.extend({
  name: 'PercentageModal',

  props: {
    value: {
      type: Boolean,
      default: false
    },
    example: {
      type: Object as PropType<ExampleDTO>,
      default: null
    }
  },

  data() {
    return {
      loading: false,
      saving: false,
      error: null as string | null,
      exampleText: '',
      labelPercentages: {} as LabelPercentages,
      manualDecision: null as string | null,
      observations: '',
      discrepancyThreshold: 80, // Valor padrão, será obtido do projeto
      currentFlagStatus: null as FlagStatus | null,
      databaseError: false,
      checkInterval: null as NodeJS.Timeout | null
    }
  },

  computed: {
    dialog: {
      get(): boolean {
        return this.value
      },
      set(value: boolean) {
        this.$emit('input', value)
      }
    },

    maxPercentage(): number {
      const percentages = Object.values(this.labelPercentages)
      return percentages.length > 0 ? Math.max(...percentages) : 0
    },

    hasAutomaticDiscrepancy(): boolean {
      return this.maxPercentage < this.discrepancyThreshold && this.maxPercentage > 0
    }
  },

  watch: {
    dialog(newValue) {
      if (newValue && this.example) {
        this.loadExampleData()
        this.startDatabaseCheck()
      } else {
        this.stopDatabaseCheck()
      }
    }
  },

  beforeDestroy() {
    this.stopDatabaseCheck()
  },

  methods: {
    async loadExampleData() {
      this.loading = true
      this.error = null

      try {
        // Carregar o projeto para obter o threshold
        const project = this.$store.getters['projects/project']
        if (!project) {
          throw new Error('Projeto não encontrado')
        }
        
        this.discrepancyThreshold = project.minPercentage || 80

        // Carregar texto do exemplo
        this.exampleText = this.example?.text || 'Texto não disponível'

        // Verificar se temos um exemplo válido
        if (!this.example || !this.example.id) {
          throw new Error('Exemplo inválido')
        }

        // Carregar percentagens das labels para este exemplo específico
        const projectId = this.$route.params.id
        if (!projectId) {
          throw new Error('ID do projeto não encontrado')
        }

        let percentages = {}

        console.log('Carregando percentagens para exemplo:', this.example.id, 'do projeto:', projectId)

        // Tentar carregar baseado no tipo de projeto
        try {
          if (project.canDefineCategory) {
            const allPercentages = await this.$repositories.metrics.fetchCategoryPercentage(projectId)
            percentages = allPercentages[this.example.id] || {}
            console.log('Percentagens de categoria carregadas:', percentages)
          } else if (project.canDefineSpan) {
            const allPercentages = await this.$repositories.metrics.fetchSpanPercentage(projectId)
            percentages = allPercentages[this.example.id] || {}
            console.log('Percentagens de span carregadas:', percentages)
          } else if (project.canDefineRelation) {
            const allPercentages = await this.$repositories.metrics.fetchRelationPercentage(projectId)
            percentages = allPercentages[this.example.id] || {}
            console.log('Percentagens de relação carregadas:', percentages)
          } else {
            console.warn('Tipo de projeto não suportado para percentagens')
          }
        } catch (apiError) {
          console.error('Erro ao carregar percentagens da API:', apiError)
          // Se a API falhar, marcar erro de base de dados e continuar com percentagens vazias
          this.databaseError = true
          percentages = {}
        }

        this.labelPercentages = percentages
        
        // Carregar estado atual de sinalização
        this.loadCurrentFlagStatus()
        
        // Se não há estado anterior, reset da decisão manual
        if (!this.currentFlagStatus) {
          this.manualDecision = null
          this.observations = ''
        }

        console.log('Dados carregados com sucesso:', {
          project: project.name,
          example: this.example.id,
          percentages: Object.keys(percentages).length,
          hasCurrentFlag: !!this.currentFlagStatus
        })

      } catch (error) {
        console.error('Erro ao carregar dados do exemplo:', error)
        this.error = `Não foi possível carregar os dados: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      } finally {
        this.loading = false
      }
    },

    getPercentageColor(percentage: number): string {
      if (percentage < this.discrepancyThreshold) return 'error'
      if (percentage < 90) return 'warning'
      return 'success'
    },

    formatDate(dateString: string): string {
      try {
        const date = new Date(dateString)
        return date.toLocaleString('pt-PT', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        return dateString
      }
    },

    loadCurrentFlagStatus() {
      // Por enquanto, vamos simular dados baseados no localStorage
      // Futuramente isto seria uma chamada à API
      try {
        const storageKey = `flag_status_${this.$route.params.id}_${this.example?.id}`
        const saved = localStorage.getItem(storageKey)
        
        if (saved) {
          this.currentFlagStatus = JSON.parse(saved)
          
          // Pré-preencher a decisão manual com o estado atual
          if (this.currentFlagStatus) {
            this.manualDecision = this.currentFlagStatus.isDiscrepant ? 'discrepant' : 'consistent'
            this.observations = this.currentFlagStatus.observations || ''
          }
        } else {
          this.currentFlagStatus = null
        }
      } catch (error) {
        console.error('Erro ao carregar estado de sinalização:', error)
        this.currentFlagStatus = null
      }
        },

    startDatabaseCheck() {
      // Iniciar verificação periódica da base de dados
      this.checkDatabaseConnection()
      this.checkInterval = setInterval(this.checkDatabaseConnection.bind(this), 5000) // Verificar a cada 5 segundos
    },

    stopDatabaseCheck() {
      // Parar a verificação periódica
      if (this.checkInterval) {
        clearInterval(this.checkInterval)
        this.checkInterval = null
      }
    },

    async checkDatabaseConnection() {
      try {
        // Tentar uma operação simples para verificar a conexão
        const projectId = this.$route.params.id
        const project = this.$store.getters['projects/project']
        
        if (project && projectId) {
          // Teste de conexão baseado no tipo de projeto
          if (project.canDefineCategory) {
            await this.$repositories.metrics.fetchCategoryPercentage(projectId)
          } else if (project.canDefineSpan) {
            await this.$repositories.metrics.fetchSpanPercentage(projectId)
          } else if (project.canDefineRelation) {
            await this.$repositories.metrics.fetchRelationPercentage(projectId)
          }
        }
        
        this.databaseError = false
      } catch (error) {
        console.error('Erro na verificação da conexão com a base de dados:', error)
        this.databaseError = true
      }
    },

    saveDecision() {
      if (!this.manualDecision || !this.example) {
        return
      }

      this.saving = true

      try {
        const isDiscrepant = this.manualDecision === 'discrepant'

        // Não precisamos mais do ID do utilizador

        // Aqui você pode implementar a lógica para salvar a decisão manual
        // Por exemplo, criar uma nova entrada na tabela de discrepâncias
        // ou atualizar um flag no exemplo

        const decisionData = {
          exampleId: this.example.id,
          isDiscrepant,
          observations: this.observations,
          labelPercentages: this.labelPercentages,
          maxPercentage: this.maxPercentage,
          flaggedManually: true,
          flaggedAt: new Date().toISOString()
        }

        console.log('Salvando decisão manual:', decisionData)

        // Salvar no localStorage (futuramente seria uma API)
        try {
          const storageKey = `flag_status_${this.$route.params.id}_${this.example.id}`
          const flagData: FlagStatus = {
            isDiscrepant,
            flaggedAt: decisionData.flaggedAt,
            observations: this.observations,
            flaggedManually: true
          }
          localStorage.setItem(storageKey, JSON.stringify(flagData))
          
          // Atualizar estado atual
          this.currentFlagStatus = flagData
        } catch (storageError) {
          console.warn('Não foi possível salvar no localStorage:', storageError)
        }

        // Emitir evento para o componente pai
        this.$emit('decision-saved', {
          example: this.example,
          decision: decisionData
        })

        // Mostrar mensagem de sucesso de forma segura
        const successMessage = isDiscrepant 
          ? 'Exemplo sinalizado como discrepante' 
          : 'Exemplo marcado como consistente'

        if ((this as any).$toast && typeof (this as any).$toast.success === 'function') {
          ;(this as any).$toast.success(successMessage)
        } else {
          console.log('✅', successMessage)
          // Fallback: usar alert nativo se toast não estiver disponível
          alert(successMessage)
        }

        // Fechar modal
        this.dialog = false

      } catch (error) {
        console.error('Erro ao salvar decisão:', error)
        
        const errorMessage = 'Erro ao salvar a decisão'
        if ((this as any).$toast && typeof (this as any).$toast.error === 'function') {
          ;(this as any).$toast.error(errorMessage)
        } else {
          console.error('❌', errorMessage)
          // Fallback: usar alert nativo se toast não estiver disponível
          alert(errorMessage)
        }
      } finally {
        this.saving = false
      }
    }
  }
})
</script>

<style scoped>
.label-percentage-item {
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #e0e0e0;
}

.label-name {
  font-size: 0.95rem;
  color: #424242;
  max-width: 300px;
}

::v-deep .v-progress-linear {
  border-radius: 6px !important;
}

::v-deep .v-card__title {
  word-break: normal;
}

::v-deep .v-radio .v-label {
  font-size: 0.9rem;
}
</style> 