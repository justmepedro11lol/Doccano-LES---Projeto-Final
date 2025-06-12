<template>
  <div>
    <v-alert v-if="sucessMessage" type="success" dismissible>{{ sucessMessage }}</v-alert>
    <v-alert v-if="errorMessage" type="error" dismissible>{{ errorMessage }}</v-alert>
    <form-create
      v-slot="slotProps"
      v-bind.sync="editedItem"
      :perspective-id="null"
      :items="items"
      @update-questions="updateQuestions"
    >
      <v-btn color="error" class="text-capitalize" @click="$router.back()"> Cancel </v-btn>
      <v-btn :disabled="!slotProps.valid" color="primary" class="text-capitalize" @click="save">
        Save
      </v-btn>
    </form-create>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import FormCreate from '~/components/perspective/FormCreate.vue'
import { CreatePerspectiveCommand } from '~/services/application/perspective/perspectiveCommand'
import { PerspectiveDTO } from '~/services/application/perspective/perspectiveData'
import {
  QuestionDTO,
  QuestionTypeDTO
} from '~/services/application/perspective/question/questionData'

export default Vue.extend({
  components: {
    FormCreate
  },

  layout: 'projects',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      editedItem: {
        id: null,
        project_id: 0,
        questions: [],
        members: []
      } as CreatePerspectiveCommand,

      questionTypeItem: [
        {
          id: 1,
          question_type: 'Text'
        },
        {
          id: 2,
          question_type: 'Numeric'
        },
        {
          id: 3,
          question_type: 'True/False'
        }
      ] as QuestionTypeDTO[],

      defaultItem: {
        id: null,
        project_id: 0,
        questions: [],
        members: []
      } as CreatePerspectiveCommand,

      errorMessage: '',
      sucessMessage: '',
      items: [] as PerspectiveDTO[]
    }
  },

  computed: {
    projectId(): string {
      return this.$route.params.id
    },

    service(): any {
      return this.$services.perspective
    }
  },

  methods: {
    updateQuestions(questions: QuestionDTO[]) {
      this.editedItem.questions = questions
    },

    async save() {
      try {
        this.editedItem.project_id = Number(this.projectId)
        this.editedItem.members = await this.getAnnotatorIds();
        
        // Garantir que os tipos de pergunta existem
        const questionTypeText = await this.$services.questionType.findById(
          this.projectId,
          this.questionTypeItem[0].id
        )
        const questionTypeNumeric = await this.$services.questionType.findById(
          this.projectId,
          this.questionTypeItem[1].id
        )
        const questionTypeTrueFalse = await this.$services.questionType.findById(
          this.projectId,
          this.questionTypeItem[2].id
        )
        
        if (!questionTypeText || !questionTypeText.id)
          await this.$services.questionType.create(this.projectId, {
            id: this.questionTypeItem[0].id,
            question_type: this.questionTypeItem[0].question_type
          })
        if (!questionTypeNumeric || !questionTypeNumeric.id)
          await this.$services.questionType.create(this.projectId, {
            id: this.questionTypeItem[1].id,
            question_type: this.questionTypeItem[1].question_type
          })
        if (!questionTypeTrueFalse || !questionTypeTrueFalse.id)
          await this.$services.questionType.create(this.projectId, {
            id: this.questionTypeItem[2].id,
            question_type: this.questionTypeItem[2].question_type
          })
        
        await this.service.create(this.projectId, this.editedItem)
        this.sucessMessage = 'A perspective has been successfully added to this project and an email has been sent to all annotators of the project'
        setTimeout(() => {
          this.$router.push(`/projects/${this.projectId}/perspectives`)
        }, 1000)
      } catch (error) {
        this.handleError(error)
      }
    },
    async getAnnotatorIds(): Promise<number[]> {
      const members = await this.$repositories.member.list(this.projectId)
      return members.filter((member) => member.rolename === 'annotator').map((member) => member.id)
    },
    handleError(error: any) {
      this.editedItem = Object.assign({}, this.defaultItem)
      if (error.response && error.response.status === 400) {
        this.errorMessage = 'Already has a perspective with that name.'
      } else {
        this.errorMessage = 'Database is slow or unavailable. Please try again later.'
      }
    }
  }
})
</script>
