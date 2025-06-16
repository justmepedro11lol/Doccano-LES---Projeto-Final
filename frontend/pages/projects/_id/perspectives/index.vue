<template>
  <div class="perspectives-container">
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
        persistent
        class="ma-4"
      >
        <v-icon left>mdi-database-alert</v-icon>
        Database is currently unavailable. Please try again later.
      </v-alert>
    </v-slide-y-transition>

    <!-- Card principal com design melhorado -->
    <v-card class="main-card" elevation="3">
      <template v-if="isAnswered">
        <v-card-title class="primary white--text d-flex align-center">
          <v-icon left color="white" size="28">mdi-check-circle-outline</v-icon>
          <span class="text-h5">Personal Perspective Already Defined</span>
        </v-card-title>
        <v-card-text class="pa-6 text-center">
          <v-icon size="80" color="success" class="mb-4">mdi-account-check</v-icon>
          <p class="text-h6 mb-0">Your personal perspective has already been submitted for this project.</p>
        </v-card-text>
      </template>

      <template v-else>
        <template v-if="isAdmin">
          <!-- Seção de Administração -->
          <v-card-title class="primary white--text d-flex align-center">
            <v-icon left color="white" size="28">mdi-cog</v-icon>
            <span class="text-h5">Perspective Management</span>
          </v-card-title>
          
          <v-card-text class="pa-0">
            <!-- Barra de ações com design melhorado -->
            <v-toolbar flat color="grey lighten-4" class="px-4">
              <action-menu 
                :disabled="hasPerspectives" 
                @create="$router.push('perspectives/add')"
              />
              <v-spacer></v-spacer>
              <v-btn 
                :disabled="selected.length === 0"
                class="text-capitalize" 
                outlined 
                color="error"
                @click.stop="dialogDelete = true"
              >
                <v-icon left>mdi-delete</v-icon>
                {{ $t('generic.delete') }}
              </v-btn>
            </v-toolbar>

            <!-- Lista de perspectivas -->
            <div class="pa-4">
              <perspective-list 
                v-model="selected" 
                :items="items" 
                :is-loading="isLoading"
                :database-error="databaseError"
                @database-error="handleDatabaseError"
              />
            </div>
          </v-card-text>

          <!-- Dialog de confirmação de exclusão -->
          <v-dialog v-model="dialogDelete" max-width="500px">
            <v-card>
              <v-card-title class="error white--text">
                <v-icon left color="white">mdi-delete-alert</v-icon>
                Confirm Deletion
              </v-card-title>
              <v-card-text class="pa-4">
                <p class="mb-0">Are you sure you want to delete the selected items?</p>
              </v-card-text>
              <v-card-actions class="pa-4">
                <v-spacer></v-spacer>
                <v-btn text @click="dialogDelete = false">Cancel</v-btn>
                <v-btn color="error" @click="handleDelete">Delete</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </template>

        <template v-else>
          <!-- Seção do Utilizador -->
          <v-card-title class="primary white--text d-flex align-center">
            <v-icon left color="white" size="28">mdi-account-question</v-icon>
            <span class="text-h5">Define Personal Perspective</span>
          </v-card-title>
          
          <v-card-text class="pa-6">
            <form-answer
              :questions-list="questionsList"
              :options-list="optionsList"
              :project-id="projectId"
              :database-error="databaseError"
              @submit-answers="submitAnswers"
              @database-error="handleDatabaseError"
            />
          </v-card-text>
        </template>
      </template>
    </v-card>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'
import ActionMenu from '@/components/perspective/ActionMenu.vue'
import PerspectiveList from '@/components/perspective/PerspectiveList.vue'
import FormAnswer from '~/components/perspective/FormAnswer.vue'
import { AnswerItem } from '~/domain/models/perspective/answer/answer'
import { QuestionItem , OptionsQuestionItem } from '~/domain/models/perspective/question/question'
import { PerspectiveDTO } from '~/services/application/perspective/perspectiveData'
import { CreateAnswerCommand } from '~/services/application/perspective/answer/answerCommand'
import { MemberItem } from '~/domain/models/member/member'


export default Vue.extend({
  components: {
    ActionMenu,
    PerspectiveList,
    FormAnswer
  },

  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      dialogDelete: false,
      items: [] as PerspectiveDTO[],
      selected: [] as PerspectiveDTO[],
      isLoading: false,
      tab: 0,
      drawerLeft: null,
      myRole: null as MemberItem | null,
      questionsList: [] as QuestionItem[],
      answersList: [] as AnswerItem[],
      optionsList: [] as OptionsQuestionItem[],
      AlreadyAnswered: false,
      submitted: false,
      successMessage: '',
      errorMessage: '',
      databaseError: '',
      databaseCheckInterval: null as NodeJS.Timeout | null
    }
  },

  computed: {
    ...mapGetters('auth', ['isStaff', 'isSuperUser']),
    projectId(): string {
      return this.$route.params.id
    },
    isAdmin(): boolean {
      return this.myRole?.isProjectAdmin ?? false
    },
    isSubmitted(): boolean {
      return this.submitted
    },
    isAnswered(): boolean {
      return this.AlreadyAnswered
    },
    hasPerspectives(): boolean {
      return this.items.length > 0
    }
  },

  async mounted() {
    try {
      const memberRepository = this.$repositories.member
      this.myRole = await memberRepository.fetchMyRole(this.projectId)
      if (this.isAdmin) {
        await this.fetchPerspectives()
      } else {
        await this.fetchQuestions()
        await this.fetchAnswers()
        await this.fetchOptions()
      }
      
      // Iniciar verificação da database de 1 em 1 segundo
      this.startDatabaseCheck()
    } catch (error) {
      console.error('Erro ao buscar o papel ou perguntas:', error)
    }
  },

  beforeDestroy() {
    // Limpar o intervalo quando o componente for destruído
    if (this.databaseCheckInterval) {
      clearInterval(this.databaseCheckInterval)
    }
  },

  methods: {
    startDatabaseCheck() {
      this.databaseCheckInterval = setInterval(async () => {
        try {
          // Fazer uma chamada simples para verificar se a database está disponível
          await this.$services.perspective.list(this.projectId)
          // Se chegou até aqui, a database está funcionando
          if (this.databaseError) {
            this.databaseError = ''
          }
        } catch (error: any) {
          console.error('Erro na verificação da database:', error)
          if (error.response && error.response.status >= 500) {
            this.databaseError = 'Database is currently unavailable. Trying to reconnect...'
          } else if (error.code === 'NETWORK_ERROR' || !error.response) {
            this.databaseError = 'Database connection error. Checking connectivity...'
          }
        }
      }, 1000) // 1 segundo
    },

    async fetchPerspectives() {
      this.isLoading = true
      this.databaseError = ''
      try {
        const projectId = this.$route.params.id
        const response = await this.$services.perspective.list(projectId)
        this.items = response
      } catch (error: any) {
        console.error('Error fetching perspectives:', error)
        this.items = []
        
        // Handle database errors
        if (error.response && error.response.status >= 500) {
          this.databaseError = 'Database is currently unavailable. Please try again later.'
        } else if (error.code === 'NETWORK_ERROR' || !error.response) {
          this.databaseError = 'Database connection error. Please check your internet connection.'
        } else {
          this.errorMessage = 'Error loading perspectives. Please try again.'
        }
      } finally {
        this.isLoading = false
      }
    },

    async fetchAnswers() {
      this.isLoading = true
      try {
        const response = await this.$services.answer.list()
        console.log('Answers:', response)
        this.AlreadyAnswered = response.some((answer: AnswerItem) => {
          return this.questionsList.some((question) => question.id === answer.question) &&
                 answer.member === this.myRole?.id;
        });
        console.log('Already answered?', this.AlreadyAnswered)
      } catch (error: any) {
        console.error('Error fetching answers:', error)
        
        // Handle database errors
        if (error.response && error.response.status >= 500) {
          this.databaseError = 'Database is currently unavailable. Please try again later.'
        } else if (error.code === 'NETWORK_ERROR' || !error.response) {
          this.databaseError = 'Database connection error. Please check your internet connection.'
        }
      } finally {
        this.isLoading = false
      }
    },

    async fetchQuestions() {
      this.isLoading = true
      try {
        console.log('🔍 Starting fetchQuestions for project:', this.projectId)
        
        // Get project perspectives
        const perspectives = await this.$services.perspective.list(this.projectId)
        console.log('📋 Perspectives found:', perspectives)
        
        if (perspectives.length > 0) {
          const perspectiveId = perspectives[0].id
          console.log('🎯 Using perspective ID:', perspectiveId)
          
          const questions = await this.$services.question.list(perspectiveId, this.projectId)
          console.log('Questions obtained from API:', questions)
          
          // Detailed filter debug
          console.log('Perspective ID for filter:', perspectiveId)
          questions.forEach((question, index) => {
            console.log(`Question ${index}:`, {
              id: question.id,
              question: question.question,
              perspective_id: question.perspective_id,
              type: question.type
            })
          })
          
          this.questionsList = questions.filter((question) => question.perspective_id === perspectiveId)
          console.log('Filtered questions:', this.questionsList)
          console.log('Total questions:', this.questionsList.length)
        } else {
          console.log('⚠️ No perspectives found for the project')
          this.questionsList = []
        }
      } catch (error: any) {
        console.error('❌ Error fetching questions:', error)
        console.error('📄 Error details:', error.response?.data)
        console.error('🔢 Error status:', error.response?.status)
        this.questionsList = []
        
        // Handle database errors
        if (error.response && error.response.status >= 500) {
          this.databaseError = 'Database is currently unavailable. Please try again later.'
        } else if (error.code === 'NETWORK_ERROR' || !error.response) {
          this.databaseError = 'Database connection error. Please check your internet connection.'
        } else {
          this.errorMessage = 'Error loading questions. Please try again.'
        }
      } finally {
        this.isLoading = false
      }
    },

    async fetchOptions() {
      this.isLoading = true
      try {
        const response = await this.$services.optionsQuestion.list(this.projectId)
        this.optionsList = response
        console.log('Options:', this.optionsList)
      } catch (error: any) {
        console.error('Error fetching options:', error)
        
        // Handle database errors
        if (error.response && error.response.status >= 500) {
          this.databaseError = 'Database is currently unavailable. Please try again later.'
        } else if (error.code === 'NETWORK_ERROR' || !error.response) {
          this.databaseError = 'Database connection error. Please check your internet connection.'
        } else {
          this.errorMessage = 'Error loading options. Please try again.'
        }
      } finally {
        this.isLoading = false
      }
    },

    async handleDelete() {
      this.isLoading = true
      try {
        for (const perspective of this.selected) {
          await this.$services.perspective.delete(perspective.id)
        }
        this.items = this.items.filter(
          (perspective) => !this.selected.some((selectedPerspective) => selectedPerspective.id === perspective.id)
        )
        this.selected = []
        this.dialogDelete = false
        this.successMessage = 'Perspectives deleted successfully!'
      } catch (error: any) {
        console.error('Error deleting perspectives:', error)
        
        // Handle database errors
        if (error.response && error.response.status >= 500) {
          this.databaseError = 'Database is currently unavailable. Please try again later.'
        } else if (error.code === 'NETWORK_ERROR' || !error.response) {
          this.databaseError = 'Database connection error. Please check your internet connection.'
        } else {
          this.errorMessage = 'Error deleting perspectives. Please try again.'
        }
      } finally {
        this.isLoading = false
      }
    },

    async submitAnswers(formattedAnswers: { questionId: number; answer: string; questionType: number }[], projectId: string) {
      console.log('Submitted answers:', formattedAnswers)
      try {
        // All answers are now text type (Text, Numeric, True/False)
        const answersToSubmit: CreateAnswerCommand[] = formattedAnswers.map((formattedAnswer) => {
          return {
            member: this.myRole?.id || 0,
            question: formattedAnswer.questionId,
            answer_text: formattedAnswer.answer
          }
        })

        for (const answer of answersToSubmit) {
          await this.$services.answer.create(projectId, answer)
        }
        this.successMessage = 'Answers successfully submitted!'
        setTimeout(() => {
          this.successMessage = ''
          this.submitted = true
          this.$router.push(`/projects/${this.projectId}/perspectives`)
        }, 7000)
        window.location.reload();
      } catch (error: any) {
        console.error('Error submitting answers:', error)
        if (error.response && error.response.status === 400) {
          const errors = error.response.data
          if (errors.answer_text) {
            this.errorMessage = errors.answer_text[0]
          } else {
            this.errorMessage = JSON.stringify(errors)
          }
        } else if (error.response && error.response.status >= 500) {
          this.databaseError = 'Database is currently unavailable. Please try again later.'
        } else if (error.code === 'NETWORK_ERROR' || !error.response) {
          this.databaseError = 'Database connection error. Please check your internet connection.'
        } else {
          this.errorMessage = 'Error submitting answers. Please try again later.'
        }
      }
    },

    handleDatabaseError(message: string) {
      this.databaseError = message
    }
  }
})
</script>

<style scoped>
.perspectives-container {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  padding: 20px;
}

.main-card {
  max-width: 1200px;
  margin: 0 auto;
  border-radius: 16px !important;
  overflow: hidden;
}

.v-card-title {
  border-radius: 0 !important;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.v-alert {
  border-radius: 12px !important;
  font-weight: 500;
}

.v-toolbar {
  border-radius: 0 !important;
}

.v-btn {
  border-radius: 8px !important;
  font-weight: 600;
  text-transform: none !important;
}

.v-dialog .v-card {
  border-radius: 16px !important;
}

/* Transições suaves */
.v-slide-y-transition-enter-active,
.v-slide-y-transition-leave-active {
  transition: all 0.3s ease;
}

.v-slide-y-transition-enter,
.v-slide-y-transition-leave-to {
  transform: translateY(-15px);
  opacity: 0;
}
</style>
