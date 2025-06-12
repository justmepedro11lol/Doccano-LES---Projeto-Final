<template>
  <v-card>
    <v-alert v-if="successMessage" type="success" dismissible @click="successMessage = ''">
      {{ successMessage }}
    </v-alert>
    <v-alert v-if="errorMessage" type="error" dismissible @click="errorMessage = ''">
      {{ errorMessage }}
    </v-alert>
    <template v-if="isAnswered">
      <v-card-title>Perspectiva pessoal já definida</v-card-title>
    </template>
    <template v-else>
      <template v-if="isAdmin">
        <v-card-title>
          <action-menu @create="$router.push('perspectives/add')" />
          <v-btn class="text-capitalize ms-2" outlined @click.stop="dialogDelete = true">
            {{ $t('generic.delete') }}
          </v-btn>
          <v-dialog v-model="dialogDelete">
            <form-delete :selected="selected" @remove="handleDelete" @cancel="dialogDelete = false" />
          </v-dialog>
        </v-card-title>
        <perspective-list v-model="selected" :items="items" :is-loading="isLoading" />
      </template>
      <template v-else>
        <!-- O componente form-answer deverá interpretar as perguntas e renderizar as opções de escolha múltipla -->
        <form-answer
          :questions-list="questionsList"
          :options-list="optionsList"
          :project-id="projectId"
          @submit-answers="submitAnswers"
        />
      </template>
    </template>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'
import ActionMenu from '@/components/perspective/ActionMenu.vue'
import PerspectiveList from '@/components/perspective/PerspectiveList.vue'
import FormAnswer from '~/components/perspective/FormAnswer.vue'
import {
  AnswerItem,
  CreateAnswerCommand,
  MemberItem,
  PerspectiveDTO,
  QuestionItem
} from '~/domain/models/perspective/perspectiveItem'

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
      AlreadyAnswered: false,
      submitted: false,
      successMessage: '',
      errorMessage: ''
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
      }
    } catch (error) {
      console.error('Erro ao buscar o papel ou perguntas:', error)
    }
  },

  methods: {
    async fetchPerspectives() {
      this.isLoading = true
      try {
        const projectId = this.$route.params.id
        const response = await this.$services.perspective.list(projectId)
        this.items = Array.isArray(response) ? response : [response]
      } catch (error) {
        console.error('Erro ao buscar perspectivas:', error)
        alert('Erro ao buscar o papel ou perguntas')
      } finally {
        this.isLoading = false
      }
    },

    async fetchAnswers() {
      this.isLoading = true
      try {
        const response = await this.$services.answer.list()
        console.log('Respostas:', response)
        this.AlreadyAnswered = response.some((answer: AnswerItem) => {
          return this.questionsList.some((question) => question.id === answer.question) &&
                 answer.member === this.myRole?.id;
        });
        console.log('Respondeu?', this.AlreadyAnswered)
      } catch (error) {
        console.error('Erro ao buscar respostas:', error)
      } finally {
        this.isLoading = false
      }
    },

    async fetchQuestions() {
      this.isLoading = true
      try {
        // Obtém a perspectiva (assumindo que há apenas uma)
        const perspectives = await this.$services.perspective.list(this.projectId)
        const perspectiveId = perspectives.id
        const questions = await this.$services.question.list(perspectiveId, this.projectId)
        this.questionsList = questions.filter((question) => question.perspective_id === perspectiveId)
        this.questionsList = questions
        
        console.log('Perguntas:', this.questionsList)
      } catch (error) {
        console.error('Erro ao buscar perguntas:', error)
      } finally {
        this.isLoading = false
      }
    },

    async handleDelete() {
      this.isLoading = true
      try {
        for (const user of this.selected) {
          await this.$services.user.delete(user.id)
        }
        this.items = this.items.filter(
          (user) => !this.selected.some((selectedUser) => selectedUser.id === user.id)
        )
        this.selected = []
        this.dialogDelete = false
      } catch (error) {
        console.error('Erro ao excluir perspectivas:', error)
      } finally {
        this.isLoading = false
      }
    },

    async submitAnswers(formattedAnswers: { questionId: number; answer: string; questionType: number }[], projectId: string) {
      console.log('Respostas submetidas:', formattedAnswers)
      try {
        // Todas as respostas agora são do tipo texto (Text, Numeric, True/False)
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
        console.error('Erro ao submeter respostas:', error)
        if (error.response && error.response.status === 400) {
          const errors = error.response.data
          if (errors.answer_text) {
            this.errorMessage = errors.answer_text[0]
          } else {
            this.errorMessage = JSON.stringify(errors)
          }
        } else if (error.response && error.response.status === 500) {
          this.errorMessage = 'Database is slow or unavailable. Please try again later.'
        } else {
          this.errorMessage = 'Database is slow or unavailable. Please try again later.'
        }
      }
    }
  }
})
</script>

<style scoped>
::v-deep .v-dialog {
  width: 800px;
}
</style>
