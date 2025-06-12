<template>
  <div>
    <v-alert v-if="sucessMessage" type="success" dismissible>{{ sucessMessage }}</v-alert>
    <v-alert v-if="errorMessage" type="error" dismissible>{{ errorMessage }}</v-alert>
    <v-alert v-if="databaseError" type="error" dismissible class="mb-4">
      <v-icon left>mdi-database-alert</v-icon>
      Base de dados indisponível. Por favor, tente novamente mais tarde.
    </v-alert>
    
    <form-create v-bind.sync="editedItem" :items="items">
      <v-btn color="error" style="text-transform: none" @click="$router.push('/users')">
        Cancel
      </v-btn>
      <v-btn :disabled="!isFormValid || databaseError" color="primary" class="text-capitalize" @click="save">
        Save
      </v-btn>
      <v-btn :disabled="!isFormValid || databaseError" color="primary" style="text-transform: none" outlined @click="saveAndAnother">
        Save and add another
      </v-btn>
    </form-create>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import FormCreate from '~/components/user/FormCreate.vue'
import { UserDTO } from '~/services/application/user/userData'

export default Vue.extend({
  components: {
    FormCreate
  },

  layout: 'projects',

  middleware: ['check-auth', 'auth'],

  async created() {
    try {
      this.items = await this.service.list()
    } catch (error) {
      console.error('Error loading users:', error)
      if (error.response && error.response.status === 503) {
        this.databaseError = true
      }
    }
    
    // Inicia verificação de saúde da base de dados
    this.startHealthCheck()
  },
  
  beforeDestroy() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval)
    }
  },

  data() {
    return {
      editedItem: {
        username: '',
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        passwordConfirmation: '',
        isSuperUser: false,
        isStaff: false
      } as any,
      defaultItem: {
        username: '',
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        passwordConfirmation: '',
        isSuperUser: false,
        isStaff: false
      } as any,
      items: [] as UserDTO[],
      errorMessage: '',
      sucessMessage: '',
      databaseError: false,
      healthCheckInterval: null as any
    }
  },

  computed: {
    projectId(): string {
      return this.$route.params.id
    },

    isFormValid(): boolean {
      return !!this.editedItem.username && !!this.editedItem.password && !!this.editedItem.passwordConfirmation && !!this.editedItem.email;
    },

    service(): any {
      return this.$services.user
    }
  },

  methods: {
    async save() {
      try {
        // Converte para o formato esperado pelo backend
        const userPayload = {
          ...this.editedItem,
          first_name: this.editedItem.firstName,
          last_name: this.editedItem.lastName
        }
        
        await this.service.create(userPayload)
        this.sucessMessage = 'O utilizador foi criado com sucesso!'
        this.databaseError = false
        setTimeout(() => {
          this.$router.push(`/users`)
        }, 1000)
      } catch (error: any) {
        this.handleError(error)
      }
    },

    async saveAndAnother() {
      try {
        // Converte para o formato esperado pelo backend
        const userPayload = {
          ...this.editedItem,
          first_name: this.editedItem.firstName,
          last_name: this.editedItem.lastName
        }
        
        await this.service.create(userPayload)
        this.sucessMessage = 'O utilizador foi criado com sucesso!'
        this.databaseError = false
        this.editedItem = Object.assign({}, this.defaultItem)
        this.items = await this.service.list()
      } catch (error) {
        this.handleError(error)
      }
    },

    handleError(error: any) {
      this.editedItem = Object.assign({}, this.defaultItem)
      if (error.response) {
        if (error.response.status === 503) {
          this.databaseError = true
          this.errorMessage = 'Base de dados indisponível. Por favor, tente novamente mais tarde.'
        } else if (error.response.status === 400) {
          const errors = error.response.data
          if (errors.username) {
            this.errorMessage = errors.username[0]
          } else if (errors.email) {
            this.errorMessage = errors.email[0]
          } else {
            this.errorMessage = JSON.stringify(errors)
          }
        } else {
          this.errorMessage = 'Erro ao criar utilizador. Por favor, tente novamente.'
        }
      } else {
        this.databaseError = true
        this.errorMessage = 'Base de dados indisponível. Por favor, tente novamente mais tarde.'
      }
    },
    
    startHealthCheck() {
      // Verifica a saúde da base de dados a cada 1 segundo
      this.healthCheckInterval = setInterval(async () => {
        try {
          await this.$repositories.user.checkHealth()
          this.databaseError = false
        } catch (error) {
          console.error('Database health check failed:', error)
          this.databaseError = true
        }
      }, 1000)
    }
  }
})
</script>
