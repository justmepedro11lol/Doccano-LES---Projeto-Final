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
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { mapGetters } from 'vuex'
import PerspectiveList from '@/components/perspective/PerspectiveList.vue'
import { PerspectiveDTO } from '~/services/application/perspective/perspectiveData'

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
      databaseError: false
    }
  },

  async fetch() {
    await this.fetchPerspectives()
    this.fetchMembers()
  },

  computed: {
    ...mapGetters('auth', ['isStaff', 'isSuperUser'])
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

    fetchMembers() {
      // Como não há um projeto específico aqui, não precisamos buscar membros
      // Os membros serão carregados pelo componente PerspectiveList conforme necessário
      this.members = []
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
</style> 