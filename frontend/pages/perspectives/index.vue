<template>
  <v-card>
    <!-- Alertas com design melhorado -->
    <v-slide-y-transition>
      <v-alert
        v-if="successMessage"
        type="success"
        dismissible
        border="left"
        colored-border
        elevation="2"
        class="ma-4"
        @click="successMessage = ''"
      >
        <v-icon slot="prepend" color="success">mdi-check-circle</v-icon>
        {{ successMessage }}
      </v-alert>
    </v-slide-y-transition>

    <v-slide-y-transition>
      <v-alert
        v-if="errorMessage"
        type="error"
        dismissible
        border="left"
        colored-border
        elevation="2"
        class="ma-4"
        @click="errorMessage = ''"
      >
        <v-icon slot="prepend" color="error">mdi-alert-circle</v-icon>
        {{ errorMessage }}
      </v-alert>
    </v-slide-y-transition>

    <v-slide-y-transition>
      <v-alert
        v-if="databaseError"
        type="error"
        dismissible
        border="left"
        colored-border
        elevation="2"
        class="ma-4"
        @click="databaseError = false"
      >
        <v-icon slot="prepend" color="error">mdi-database-alert</v-icon>
        Base de dados indisponível. Por favor, tente novamente mais tarde.
      </v-alert>
    </v-slide-y-transition>

    <v-card-title>
      <h1>Perspectives</h1>
      <v-spacer></v-spacer>
      
    </v-card-title>
    <v-card-text>
      <perspective-list
        v-model="selected"
        :items="items"
        :is-loading="isLoading"
        :members="members"
      />

      <!-- Seção de Cards Resumo por Projeto -->
      <v-divider class="my-6"></v-divider>
      
      <div class="project-summary-section">
        <h2 class="text-h5 mb-4 d-flex align-center">
          <v-icon left color="primary">mdi-chart-box-outline</v-icon>
          Resumo por Projeto
        </h2>
        
        <v-row v-if="!isLoading && projectSummaries.length > 0">
          <v-col
            v-for="summary in projectSummaries"
            :key="summary.projectId"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <v-card
              class="project-summary-card"
              elevation="3"
              hover
            >
              <v-card-title class="pb-2">
                <v-avatar color="primary" size="40" class="mr-3">
                  <v-icon color="white">mdi-folder</v-icon>
                </v-avatar>
                <div>
                  <div class="text-h6 font-weight-bold">{{ summary.projectName }}</div>
                  <div class="text-caption text--secondary">Projeto #{{ summary.projectId }}</div>
                </div>
              </v-card-title>
              
              <v-card-text>
                <div class="mb-3">
                  <div class="d-flex align-center mb-2">
                    <v-icon small color="info" class="mr-2">mdi-help-circle</v-icon>
                    <span class="text-subtitle2 font-weight-medium">Questões:</span>
                  </div>
                  <div class="questions-list">
                    <v-chip
                      v-for="(question, index) in summary.questions.slice(0, 2)"
                      :key="index"
                      small
                      color="info"
                      text-color="white"
                      class="ma-1"
                      :title="question"
                    >
                      {{ question.length > 25 ? question.substring(0, 25) + '...' : question }}
                    </v-chip>
                    <v-chip
                      v-if="summary.questions.length > 2"
                      small
                      color="grey"
                      text-color="white"
                      class="ma-1"
                    >
                      +{{ summary.questions.length - 2 }} mais
                    </v-chip>
                  </div>
                </div>
                
                <v-divider class="my-3"></v-divider>
                
                <div class="stats-section">
                  <div class="d-flex justify-space-between align-center mb-2">
                    <span class="text-body-2 text--secondary">Total de Respostas:</span>
                    <v-chip color="success" text-color="white" small>
                      {{ summary.totalAnswers }}
                    </v-chip>
                  </div>
                  <div class="d-flex justify-space-between align-center">
                    <span class="text-body-2 text--secondary">Participantes:</span>
                    <v-chip color="primary" text-color="white" small>
                      {{ summary.uniqueMembers }}
                    </v-chip>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        
        <v-row v-else-if="isLoading">
          <v-col
            v-for="n in 4"
            :key="n"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <v-skeleton-loader
              type="card"
              class="project-summary-card"
            ></v-skeleton-loader>
          </v-col>
        </v-row>
        
        <v-alert
          v-else
          type="info"
          text
          class="mt-4"
        >
          <v-icon slot="prepend">mdi-information</v-icon>
          Nenhum projeto encontrado para exibir resumo.
        </v-alert>
      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { mapGetters } from 'vuex'
import PerspectiveList from '@/components/perspective/PerspectiveList.vue'
import { PerspectiveDTO } from '~/services/application/perspective/perspectiveData'

interface ProjectSummary {
  projectId: number
  projectName: string
  questions: string[]
  totalAnswers: number
  uniqueMembers: number
}

export default {
  components: {
    PerspectiveList
  },

  layout: 'projects',
  middleware: ['check-auth', 'auth', 'isSuperUser'],

  data() {
    return {
      items: [] as PerspectiveDTO[],
      selected: [] as PerspectiveDTO[],
      isLoading: false,
      members: [],
      successMessage: '',
      errorMessage: '',
      databaseError: false,
      projectNames: {} as Record<number, string>,
      memberNames: {} as Record<number, string>
    }
  },

  async fetch() {
    await this.fetchPerspectives()
    if (this.items.length > 0) {
      await this.loadProjectNames()
      await this.loadMemberNames()
    }
  },

  computed: {
    ...mapGetters('auth', ['isStaff', 'isSuperUser']),
    
    projectSummaries(): ProjectSummary[] {
      if (!this.items || this.items.length === 0) return []
      
      // Forçar reatividade nos nomes dos projetos
      const projectNamesRef = this.projectNames

      const summaryMap = new Map<number, any>()
      
      this.items.forEach(perspective => {
        const projectId = perspective.project_id
        
        if (!summaryMap.has(projectId)) {
          summaryMap.set(projectId, {
            projectId,
            projectName: projectNamesRef[projectId] || `Projeto ${projectId}`,
            questions: new Set<string>(),
            totalAnswers: 0,
            uniqueMembers: new Set<number>()
          })
        }
        
        const summary = summaryMap.get(projectId)
        
        // Processar questões e respostas reais (igual ao PerspectiveList)
        if (perspective.questions && Array.isArray(perspective.questions)) {
          perspective.questions.forEach(question => {
            // Adicionar questão única
            if (question && question.question) {
              summary.questions.add(question.question)
            }
            
            // Contar respostas reais e membros únicos
            if (question.answers && Array.isArray(question.answers)) {
              question.answers.forEach((answer: any) => {
                // Contar cada resposta
                summary.totalAnswers++
                
                // Adicionar membro único
                if (answer.member) {
                  let memberId: number
                  if (typeof answer.member === 'object' && answer.member.id != null) {
                    memberId = answer.member.id
                  } else if (typeof answer.member === 'number') {
                    memberId = answer.member
                  }
                  if (memberId) {
                    summary.uniqueMembers.add(memberId)
                  }
                }
              })
            }
          })
        }
      })
      
      // Converter Sets para arrays/números
      const result = Array.from(summaryMap.values()).map(summary => ({
        projectId: summary.projectId,
        projectName: summary.projectName,
        questions: Array.from(summary.questions),
        totalAnswers: summary.totalAnswers,
        uniqueMembers: summary.uniqueMembers.size
      }))
      
      return result
    }
  },

  methods: {
    async fetchPerspectives() {
      this.isLoading = true
      try {
        const response = await this.$services.perspective.list()
        console.log('Fetched perspectives for general view:', response)
        this.items = response
        this.databaseError = false
      } catch (error) {
        console.error('Error fetching perspectives:', error)
        this.handleError(error, 'Erro ao carregar perspectivas')
        this.items = []
      } finally {
        this.isLoading = false
      }
    },

    async loadProjectNames() {
      // Obtém os IDs únicos dos projetos a partir dos itens (igual ao PerspectiveList)
      const projectIds = [...new Set(this.items.map(item => item.project_id))]
      console.log('Carregando nomes para projetos:', projectIds)
      
      const loadPromises = projectIds.map(async (projectId) => {
        try {
          const project = await this.$services.project.findById(projectId.toString())
          this.$set(this.projectNames, projectId, project.name)
          console.log(`Fetched project ${projectId}:`, project.name)
        } catch (error) {
          console.log(`Project not found for ID ${projectId}:`, error)
          this.$set(this.projectNames, projectId, `Projeto ${projectId}`)
        }
      })

      await Promise.all(loadPromises)
      console.log('Todos os nomes dos projetos carregados:', this.projectNames)
    },

    async loadMemberNames() {
      try {
        // Coletar todos os IDs de membros únicos das respostas
        const memberIds = new Set<number>()
        
        this.items.forEach(perspective => {
          if (perspective.questions && Array.isArray(perspective.questions)) {
            perspective.questions.forEach(question => {
              if (question.answers && Array.isArray(question.answers)) {
                question.answers.forEach((answer: any) => {
                  if (answer.member) {
                    let memberId: number
                    if (typeof answer.member === 'object' && answer.member.id != null) {
                      memberId = answer.member.id
                    } else if (typeof answer.member === 'number') {
                      memberId = answer.member
                    }
                    if (memberId) {
                      memberIds.add(memberId)
                    }
                  }
                })
              }
            })
          }
        })
        
        console.log('Carregando nomes para membros:', Array.from(memberIds))
        
        // Carregar nomes dos membros (assumindo que há um método para isso)
        for (const memberId of memberIds) {
          try {
            // Tentar carregar o nome do membro - pode precisar de ajuste dependendo da API
            const user = await this.$services.user.findById(memberId.toString())
            this.memberNames[memberId] = user.username || user.name || `Utilizador ${memberId}`
          } catch (error) {
            console.warn(`Erro ao carregar nome do membro ${memberId}:`, error)
            this.memberNames[memberId] = `Utilizador ${memberId}`
          }
        }
        
        console.log('Nomes dos membros carregados:', this.memberNames)
      } catch (error) {
        console.error('Erro ao carregar nomes dos membros:', error)
      }
    },

    handleError(error: any, defaultMessage: string) {
      const err = error as any
      
      console.log('=== ANÁLISE DO ERRO ===')
      console.log('Erro completo:', err)
      console.log('Response:', err.response)
      console.log('Status:', err.response?.status)
      console.log('Data:', err.response?.data)
      console.log('Message:', err.message)
      
      // Check for database/server errors
      if (err.response && err.response.status === 503) {
        console.log('handleError: Erro 503 - Base de dados indisponível')
        this.databaseError = true
        this.errorMessage = defaultMessage
        this.hideMessageAfterDelay('errorMessage', 5000)
      }
      // Network or connection error (no response) - likely database issue
      else if (!err.response) {
        console.log('handleError: Sem resposta do servidor - assumindo problema de base de dados')
        this.databaseError = true
        this.errorMessage = defaultMessage
        this.hideMessageAfterDelay('errorMessage', 5000)
      }
      // 500 Internal Server Error - often database related
      else if (err.response && err.response.status === 500) {
        console.log('handleError: Erro 500 - assumindo problema de base de dados')
        // Only consider it a database error if the error message specifically mentions database
        if (err.response.data && typeof err.response.data === 'string' && 
            err.response.data.toLowerCase().includes('database')) {
          console.log('handleError: Erro 500 com menção específica à base de dados')
          this.databaseError = true
          this.errorMessage = defaultMessage
        } else {
          console.log('handleError: Erro 500 genérico')
          this.errorMessage = defaultMessage
        }
        this.hideMessageAfterDelay('errorMessage', 5000)
      }
      // 502 Bad Gateway - server connectivity issues
      else if (err.response && err.response.status === 502) {
        console.log('handleError: Erro 502 - problema de conectividade do servidor')
        this.databaseError = true
        this.errorMessage = defaultMessage
        this.hideMessageAfterDelay('errorMessage', 5000)
      }
      // 504 Gateway Timeout - server timeout, likely database
      else if (err.response && err.response.status === 504) {
        console.log('handleError: Erro 504 - timeout do servidor')
        this.databaseError = true
        this.errorMessage = defaultMessage
        this.hideMessageAfterDelay('errorMessage', 5000)
      }
      // Network timeout errors
      else if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        console.log('handleError: Timeout de rede')
        this.databaseError = true
        this.errorMessage = defaultMessage
        this.hideMessageAfterDelay('errorMessage', 5000)
      }
      // Connection refused errors
      else if (err.code === 'ECONNREFUSED' || err.message?.includes('ECONNREFUSED')) {
        console.log('handleError: Conexão recusada')
        this.databaseError = true
        this.errorMessage = defaultMessage
        this.hideMessageAfterDelay('errorMessage', 5000)
      }
      // Other connection errors
      else if (err.code && (err.code.startsWith('ECONN') || err.code.startsWith('ENET'))) {
        console.log('handleError: Erro de conexão de rede')
        this.databaseError = true
        this.errorMessage = defaultMessage
        this.hideMessageAfterDelay('errorMessage', 5000)
      }
      // Other errors
      else {
        console.log('handleError: Outro tipo de erro - mostrando apenas mensagem específica')
        this.errorMessage = defaultMessage
        this.hideMessageAfterDelay('errorMessage', 5000)
      }
    },

    clearMessages() {
      this.successMessage = ''
      this.errorMessage = ''
      this.databaseError = false
    },

    hideMessageAfterDelay(messageProperty: string, delay: number = 3000) {
      setTimeout(() => {
        ;(this as any)[messageProperty] = ''
      }, delay)
    }
  }
}
</script>

<style scoped>
.v-card {
  margin: 16px;
}

.v-alert {
  border-radius: 12px !important;
  font-weight: 500;
}

.project-summary-section {
  margin-top: 24px;
}

.project-summary-card {
  height: 100%;
  border-radius: 12px !important;
  transition: all 0.3s ease;
}

.project-summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}

.questions-list {
  min-height: 60px;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
}

.stats-section {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
}
</style> 