<template>
  <div class="perspective-list-container">
    <!-- Alerta de erro de base de dados -->
    <v-slide-y-transition>
      <v-alert
        v-if="databaseError"
        type="error"
        dismissible
        border="left"
        colored-border
        elevation="2"
        class="mb-4"
        @click="$emit('database-error', '')"
      >
        <v-icon slot="prepend" color="error">mdi-database-alert</v-icon>
        {{ databaseError }}
      </v-alert>
    </v-slide-y-transition>

    <!-- Card de filtros com design melhorado -->
    <v-card class="filters-card mb-4" elevation="2">
      <v-card-title class="pb-2">
        <v-icon left color="primary">mdi-filter-variant</v-icon>
        <span class="text-h6">Filters</span>
        <v-spacer></v-spacer>
        <v-btn 
          :disabled="!hasActiveFilters"
          color="secondary" 
          text
          small 
          class="clear-filters-btn"
          @click="clearAllFilters"
        >
          <v-icon left small>mdi-filter-remove</v-icon>
          Clear Filters
        </v-btn>
      </v-card-title>
      
      <v-card-text class="pt-0">
        <v-row>
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedQuestion"
              :items="availableQuestions"
              label="Select question"
              clearable
              outlined
              dense
              prepend-icon="mdi-help-circle-outline"
              class="filter-select"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedUser"
              :items="availableUsers"
              label="Select user"
              clearable
              outlined
              dense
              prepend-icon="mdi-account-outline"
              class="filter-select"
            />
          </v-col>
          <!-- Só mostra o filtro de projeto se não estivermos numa página específica de projeto -->
          <v-col v-if="!isProjectSpecificPage" cols="12" md="3">
            <v-select
              v-model="selectedProject"
              :items="availableProjects"
              label="Select project"
              clearable
              outlined
              dense
              prepend-icon="mdi-folder-outline"
              class="filter-select"
            />
          </v-col>
          <v-col cols="12" :md="isProjectSpecificPage ? 6 : 3">
            <v-select
              v-model="selectedAnswer"
              :items="availableAnswers"
              label="Select answer"
              clearable
              outlined
              dense
              prepend-icon="mdi-comment-text-outline"
              class="filter-select"
            />
          </v-col>
        </v-row>
        
        <!-- Campo de busca por texto melhorado -->
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="search"
              :prepend-inner-icon="mdiMagnify"
              label="Search in all columns (question, answer, user...)"
              single-line
              hide-details
              outlined
              dense
              clearable
              class="search-field"
              background-color="grey lighten-5"
              placeholder="Type to search..."
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Card da tabela com design melhorado -->
    <v-card class="data-table-card" elevation="2">
      <v-card-title class="pb-2">
        <v-icon left color="primary">mdi-table</v-icon>
        <span class="text-h6">Perspective Responses</span>
        <v-spacer></v-spacer>
        <v-chip 
          v-if="processedItems.length > 0" 
          color="primary" 
          text-color="white" 
          small
        >
          {{ processedItems.length }} {{ processedItems.length === 1 ? 'result' : 'results' }}
        </v-chip>
      </v-card-title>

      <v-card-text class="pt-0">
        <!-- Tabela de dados melhorada -->
        <v-data-table
          :items="processedItems"
          :headers="headers"
          :loading="isLoading || loadingNames"
          :loading-text="loadingNames ? 'Loading names...' : $t('generic.loading')"
          :no-data-text="databaseError ? 'Database unavailable' : $t('vuetify.noDataAvailable')"
          :footer-props="{
            showFirstLastPage: true,
            'items-per-page-text': $t('vuetify.itemsPerPageText'),
            'page-text': $t('dataset.pageText')
          }"
          item-key="id"
          class="elevation-1 data-table"
          @input="$emit('input', $event)"
        >
          <template #[`item.memberName`]="{ item }">
            <div class="d-flex align-center">
              <v-avatar size="32" color="primary" class="mr-3">
                <v-icon color="white" size="16">mdi-account</v-icon>
              </v-avatar>
              <span class="font-weight-medium">{{ item.memberName }}</span>
            </div>
          </template>
          
          <template #[`item.projectName`]="{ item }">
            <div class="d-flex align-center">
              <v-avatar size="32" color="info" class="mr-3">
                <v-icon color="white" size="16">mdi-folder</v-icon>
              </v-avatar>
              <span class="font-weight-medium">{{ item.projectName }}</span>
            </div>
          </template>
          
          <template #[`item.question`]="{ item }">
            <div class="question-cell">
              <v-tooltip bottom>
                <template #activator="{ on, attrs }">
                  <span 
                    v-bind="attrs"
                    class="question-text"
                    v-on="on"
                  >
                    {{ item.question }}
                  </span>
                </template>
                <span>{{ item.question }}</span>
              </v-tooltip>
            </div>
          </template>
          
          <template #[`item.answer`]="{ item }">
            <v-chip
              :color="getAnswerChipColor(item.answer)"
              text-color="white"
              small
              class="font-weight-medium"
            >
              {{ item.answer }}
            </v-chip>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiMagnify } from '@mdi/js'
import type { PropType } from 'vue'
import { PerspectiveDTO } from '~/services/application/perspective/perspectiveData'

export default Vue.extend({
  name: 'PerspectiveList',
  props: {
    isLoading: {
      type: Boolean,
      default: false,
      required: true
    },
    // Os itens (perspectivas) devem já vir filtrados ou possuir um atributo project_id
    items: {
      type: Array as PropType<PerspectiveDTO[]>,
      default: () => [],
      required: true
    },
    value: {
      type: Array as PropType<PerspectiveDTO[]>,
      default: () => [],
      required: true
    },
    disableEdit: {
      type: Boolean,
      default: false
    },
    members: {
      type: Array as PropType<any[]>,
      default: () => []
    },
    databaseError: {
      type: String,
      default: ''
    }
  },

  data() {
    return {
      search: '',
      mdiMagnify,
      // Selecção dos filtros: pergunta, utilizador, projeto e resposta
      selectedQuestion: null as string | null,
      selectedUser: null as string | null,
      selectedProject: null as string | null,
      selectedAnswer: null as string | null,
      // Armazena os nomes carregados para os IDs de 0 a 100
      memberNames: {} as { [key: number]: string },
      // Armazena os nomes dos projetos
      projectNames: {} as { [key: number]: string },
      // Indica se os nomes estão sendo carregados
      loadingNames: false
    }
  },

  computed: {
    // Header com quatro colunas: Criador, Projeto, Pergunta e Resposta
    headers() {
      const baseHeaders = [
        { text: this.$t('Created by'), value: 'memberName', sortable: true, width: '200px' },
        { text: this.$t('Question'), value: 'question', sortable: true, width: '35%' },
        { text: this.$t('Answer'), value: 'answer', sortable: true, width: '200px' }
      ]
      
      // Só adiciona a coluna de projeto se não estivermos numa página específica de projeto
      if (!this.isProjectSpecificPage) {
        baseHeaders.splice(1, 0, { text: 'Project', value: 'projectName', sortable: true, width: '200px' })
      }
      
      return baseHeaders
    },
    projectId(): string {
      return this.$route.params.id
    },
    // Verifica se estamos numa página específica de projeto
    isProjectSpecificPage(): boolean {
      return !!this.projectId && this.$route.path.includes('/projects/')
    },
    // Extrai as perguntas disponíveis e adiciona a opção "Todas as perguntas"
    availableQuestions() {
      const questionsSet = new Set<string>()
      const itemsToProcess = this.projectId ? 
        this.items.filter(item => Number(item.project_id) === Number(this.projectId)) :
        this.items;

      itemsToProcess.forEach(item => {
        if (Array.isArray(item.questions)) {
          item.questions.forEach(q => {
            if (q.question) {
              questionsSet.add(q.question)
            }
          })
        }
      })
      return Array.from(questionsSet)
    },
    // Extrai os utilizadores disponíveis a partir das respostas e adiciona "Todos os utilizadores"
    availableUsers() {
      const usersSet = new Set<string>()
      const itemsToProcess = this.projectId ? 
        this.items.filter(item => Number(item.project_id) === Number(this.projectId)) :
        this.items;

      itemsToProcess.forEach(item => {
        if (Array.isArray(item.questions)) {
          item.questions.forEach(q => {
            if (Array.isArray(q.answers)) {
              q.answers.forEach((a: any) => {
                let memberName = ''
                if (a.member) {
                  if (typeof a.member === 'object' && a.member.name) {
                    memberName = a.member.name
                  } else if (typeof a.member === 'number') {
                    memberName = this.memberNames[a.member] || a.member.toString()
                  }
                  if (memberName) {
                    usersSet.add(memberName)
                  }
                }
              })
            }
          })
        }
      })
      return Array.from(usersSet)
    },
    // Extrai as respostas disponíveis e adiciona "Todas as respostas"
    availableAnswers() {
      const answersSet = new Set<string>()
      const itemsToProcess = this.projectId ? 
        this.items.filter(item => Number(item.project_id) === Number(this.projectId)) :
        this.items;

      itemsToProcess.forEach(item => {
        if (Array.isArray(item.questions)) {
          item.questions.forEach(q => {
            if (Array.isArray(q.answers)) {
              q.answers.forEach((a: any) => {
                const answerText = a.answer_text || a.answer_option || ''
                if (answerText) {
                  answersSet.add(answerText)
                }
              })
            }
          })
        }
      })
      return Array.from(answersSet)
    },
    // Extrai os projetos disponíveis
    availableProjects() {
      const projectsSet = new Set<string>()
      const itemsToProcess = this.projectId ? 
        this.items.filter(item => Number(item.project_id) === Number(this.projectId)) :
        this.items;

      itemsToProcess.forEach(item => {
        const projectName = this.projectNames[item.project_id] || `Project ${item.project_id}`
        projectsSet.add(projectName)
      })
      return Array.from(projectsSet)
    },
    // Processa os itens gerando uma linha para cada resposta e aplicando os filtros selecionados
    processedItems() {
      const result: Array<{ id: number; memberName: string; projectName: string; question: string; answer: string }> = []
      const itemsToProcess = this.projectId ? 
        this.items.filter(item => Number(item.project_id) === Number(this.projectId)) :
        this.items;

      let counter = 0
      itemsToProcess.forEach(item => {
        if (Array.isArray(item.questions)) {
          item.questions.forEach(q => {
            // Filtra pela pergunta, se selecionada
            if (this.selectedQuestion && 
                q.question && q.question.toLowerCase() !== this.selectedQuestion.toLowerCase()) {
              return
            }
            if (Array.isArray(q.answers)) {
              q.answers.forEach((a: any) => {
                let memberId: number 
                let memberName = ''
                if (a.member) {
                  if (typeof a.member === 'object' && a.member.id != null) {
                    memberId = a.member.id
                    memberName = a.member.name || memberId.toString()
                  } else if (typeof a.member === 'number') {
                    memberId = a.member
                    memberName = this.memberNames[memberId] || memberId.toString()
                  }
                }
                const answerText = a.answer_text || a.answer_option || ''
                const projectName = this.projectNames[item.project_id] || `Project ${item.project_id}`
                // Cria um registro para cada resposta
                const row = {
                  id: counter++,
                  memberName,
                  projectName,
                  question: q.question,
                  answer: answerText
                }
                // Filtro de busca (buscando em todas as colunas com melhor normalização)
                if (this.search) {
                  const searchLower = this.search.toLowerCase().trim()
                  const combinedText = `${row.memberName} ${row.projectName} ${row.question} ${row.answer}`.toLowerCase()
                  
                  // Busca mais flexível - permite busca por palavras parciais
                  const searchWords = searchLower.split(' ').filter(word => word.length > 0)
                  const matchesSearch = searchWords.every(word => combinedText.includes(word))
                  
                  if (!matchesSearch) {
                    return
                  }
                }
                // Filtro por utilizador, se selecionado
                if (this.selectedUser &&
                    row.memberName.toLowerCase() !== this.selectedUser.toLowerCase()) {
                  return
                }
                // Filtro por projeto, se selecionado
                if (this.selectedProject &&
                    row.projectName.toLowerCase() !== this.selectedProject.toLowerCase()) {
                  return
                }
                // Filtro por resposta, se selecionada
                if (this.selectedAnswer &&
                    row.answer.toLowerCase() !== this.selectedAnswer.toLowerCase()) {
                  return
                }
                result.push(row)
              })
            }
          })
        }
      })
      return result
    },
    hasActiveFilters() {
      return this.selectedQuestion !== null || this.selectedUser !== null || this.selectedProject !== null || this.selectedAnswer !== null || this.search !== ''
    }
  },

  watch: {
    selectedQuestion(newVal) {
      console.log('selectedQuestion changed:', newVal)
    },
    selectedUser(newVal) {
      console.log('selectedUser changed:', newVal)
    },
    selectedProject(newVal) {
      console.log('selectedProject changed:', newVal)
    },
    selectedAnswer(newVal) {
      console.log('selectedAnswer changed:', newVal)
    },
    // Quando os itens mudam, recarrega os nomes dos membros e projetos
    items: {
      async handler() {
        if (this.items.length > 0) {
          await this.$nextTick()
          await this.loadMemberNames()
          await this.loadProjectNames()
        }
      },
      deep: true,
      immediate: true
    }
  },

  async mounted() {
    if (this.items.length > 0) {
      await this.$nextTick()
      await this.loadMemberNames()
      await this.loadProjectNames()
    }
  },

  methods: {
    // Método para carregar os nomes dos membros de forma eficiente
    async loadMemberNames() {
      if (this.loadingNames) return
      this.loadingNames = true
      
      try {
        // Primeiro, obtém os IDs únicos dos membros a partir dos itens
        const memberIds = new Set<number>()
        
        this.items.forEach(item => {
          if (Array.isArray(item.questions)) {
            item.questions.forEach(q => {
              if (Array.isArray(q.answers)) {
                q.answers.forEach((a: any) => {
                  if (a.member) {
                    if (typeof a.member === 'object' && a.member.id != null) {
                      memberIds.add(a.member.id)
                    } else if (typeof a.member === 'number') {
                      memberIds.add(a.member)
                    }
                  }
                })
              }
            })
          }
        })

        // Se há membros para carregar, obtém a lista de membros do projeto
        if (memberIds.size > 0) {
          // Tenta buscar todos os membros de todos os projetos únicos
          const projectIds = [...new Set(this.items.map(item => item.project_id))]
          
          for (const projectId of projectIds) {
            try {
              const members = await this.$repositories.member.list(projectId.toString())
              members.forEach(member => {
                if (memberIds.has(member.id)) {
                  this.$set(this.memberNames, member.id, member.username)
                  console.log(`Fetched member ${member.id}:`, member.username)
                }
              })
            } catch (error: any) {
              console.log(`Error fetching members for project ${projectId}:`, error)
              
              // Emit database error if it's a server error
              if (error.response && error.response.status >= 500) {
                this.$emit('database-error', 'Database is currently unavailable while loading member names.')
              } else if (error.code === 'NETWORK_ERROR' || !error.response) {
                this.$emit('database-error', 'Database connection error while loading member names.')
              }
            }
          }
          
          // Para membros que não foram encontrados, define um nome padrão
          Array.from(memberIds).forEach(memberId => {
            if (!this.memberNames[memberId]) {
              this.$set(this.memberNames, memberId, `User ${memberId}`)
            }
          })
        }
      } finally {
        this.loadingNames = false
      }
    },
    
    // Método para carregar os nomes dos projetos de forma eficiente
    async loadProjectNames() {
      // Obtém os IDs únicos dos projetos a partir dos itens
      const projectIds = [...new Set(this.items.map(item => item.project_id))]
      
      const loadPromises = projectIds.map(async (projectId) => {
        try {
          const project = await this.$services.project.findById(projectId.toString())
          this.$set(this.projectNames, projectId, project.name)
          console.log(`Fetched project ${projectId}:`, project.name)
        } catch (error: any) {
          console.log(`Project not found for ID ${projectId}:`, error)
          this.$set(this.projectNames, projectId, `Project ${projectId}`)
          
          // Emit database error if it's a server error
          if (error.response && error.response.status >= 500) {
            this.$emit('database-error', 'Database is currently unavailable while loading project names.')
          } else if (error.code === 'NETWORK_ERROR' || !error.response) {
            this.$emit('database-error', 'Database connection error while loading project names.')
          }
        }
      })

      await Promise.all(loadPromises)
    },
    clearAllFilters() {
      this.selectedQuestion = null
      this.selectedUser = null
      this.selectedProject = null
      this.selectedAnswer = null
      this.search = ''
    },
    getAnswerChipColor(answer: string) {
      // Retorna cores diferentes baseadas no tipo de resposta
      if (!answer) return 'grey'
      
      // Para respostas True/False
      if (answer.toLowerCase() === 'true' || answer.toLowerCase() === 'sim') return 'success'
      if (answer.toLowerCase() === 'false' || answer.toLowerCase() === 'não') return 'error'
      
      // Para respostas numéricas
      if (!isNaN(Number(answer))) {
        const num = Number(answer)
        if (num > 7) return 'success'
        if (num > 4) return 'warning'
        return 'error'
      }
      
      // Para outras respostas
      return 'primary'
    }
  }
})
</script>

<style scoped>
.perspective-list-container {
  padding: 0;
}

.filters-card {
  border-radius: 12px !important;
  background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
}

.data-table-card {
  border-radius: 12px !important;
  background: #ffffff;
}

.filter-select {
  border-radius: 8px;
}

.clear-filters-btn {
  border-radius: 20px !important;
  text-transform: none !important;
  font-weight: 600;
}

.search-field {
  border-radius: 12px !important;
}

.data-table {
  border-radius: 8px !important;
}

.question-cell {
  max-width: 300px;
}

.question-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
  cursor: help;
}

.v-chip {
  border-radius: 16px !important;
}

.v-card-title {
  font-weight: 600;
  color: #424242;
}

.v-data-table ::v-deep .v-data-table__wrapper {
  border-radius: 8px;
}

.v-data-table ::v-deep th {
  background-color: #f5f5f5 !important;
  font-weight: 600 !important;
  color: #424242 !important;
}

.v-data-table ::v-deep tbody tr:hover {
  background-color: rgba(25, 118, 210, 0.04) !important;
}

/* Animações suaves */
.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
}

.v-chip {
  transition: all 0.2s ease;
}

.v-chip:hover {
  transform: scale(1.05);
}
</style>