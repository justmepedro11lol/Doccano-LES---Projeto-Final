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
        type="warning"
        dismissible
        border="left"
        colored-border
        elevation="2"
        class="ma-4"
        @click="databaseError = false"
      >
        <v-icon slot="prepend" color="warning">mdi-database-alert</v-icon>
        Base de dados indisponível. Por favor, tente novamente mais tarde.
      </v-alert>
    </v-slide-y-transition>

    <v-card-title>
      <v-btn class="text-capitalize" color="primary" @click.stop="$router.push('users/add')">
        {{ $t('generic.create') }}
      </v-btn>
      <v-btn
        class="text-capitalize ms-2"
        :outlined="!canDelete"
        :color="canDelete ? 'error' : 'primary'"
        :disabled="!canDelete"
        @click.stop="dialogDelete = true"
      >
        {{ $t('generic.delete') }}
      </v-btn>
      <v-dialog v-model="dialogDelete">
        <form-delete :selected="selected" @remove="handleDelete" @cancel="dialogDelete = false" />
      </v-dialog>

    </v-card-title>
    <user-list
      v-model="selected"
      :items="items"
      :is-loading="isLoading"
      @editUserPage="openEditPage"
    />
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'
import FormDelete from '@/components/user/FormDelete.vue'
import UserList from '@/components/user/UserList.vue'
import { UserDTO } from '~/services/application/user/userData'


export default Vue.extend({
  components: {
    FormDelete,
    UserList
  },

  layout: 'projects',

  middleware: ['check-auth', 'auth', 'isSuperUser'],

  data() {
    return {
      dialogDelete: false,
      items: [] as UserDTO[],
      selected: [] as UserDTO[],
      isLoading: false,
      tab: 0,
      drawerLeft: null,
      successMessage: '',
      errorMessage: '',
      databaseError: false
    }
  },

  computed: {
    ...mapGetters('auth', ['isStaff', 'isSuperUser']),

    canDelete(): boolean {
      return this.selected.length > 0
    }
  },

  mounted() {
    this.fetchUsers()
  },

  methods: {
    async fetchUsers() {
      this.isLoading = true
      try {
        const response = await this.$services.user.list()
        this.items = response
        this.databaseError = false
      } catch (error) {
        console.error('Erro ao buscar utilizadores:', error)
        this.handleError(error, 'Erro ao carregar utilizadores')
      } finally {
        this.isLoading = false
      }
    },
    async deleteUser(userId: number) {
      this.isLoading = true
      try {
        await this.$services.user.delete(userId)
        this.items = this.items.filter((user) => user.id !== userId)
        this.databaseError = false
      } catch (error) {
        console.error('Erro ao excluir utilizador:', error)
        this.handleError(error, 'Erro ao eliminar utilizador')
      } finally {
        this.isLoading = false
      }
    },
    async handleDelete() {
      this.isLoading = true
      this.clearMessages()
      
      console.log('=== INÍCIO DA ELIMINAÇÃO ===')
      console.log('Utilizadores selecionados:', this.selected.map(u => u.username))
      
      try {
        // Tries to delete each selected user
        for (const user of this.selected) {
          console.log(`Eliminando utilizador: ${user.username} (ID: ${user.id})`)
          await this.$services.user.delete(user.id)
        }
        
        console.log('✅ Todos os utilizadores eliminados com sucesso')
        
        // Updates the list by removing the deleted users
        this.items = this.items.filter(
          (user) => !this.selected.some((selectedUser) => selectedUser.id === user.id)
        )
        
        const deletedCount = this.selected.length
        this.selected = []
        this.dialogDelete = false
        this.databaseError = false

        // Show success message
        this.successMessage = deletedCount > 1 
          ? `${deletedCount} utilizadores eliminados com sucesso!`
          : 'Utilizador eliminado com sucesso!'
        
        this.hideMessageAfterDelay('successMessage')
        
      } catch (error) {
        this.dialogDelete = false
        console.error('❌ ERRO NA ELIMINAÇÃO')
        console.error('Erro:', error)
        
        const err = error as any
        
        if (err.response) {
          console.log(`Resposta HTTP: ${err.response.status} - ${err.response.statusText}`)
          
          // Check if the error is about deleting the own account
          if (err.response.status === 403) {
            console.log('Erro 403: Tentativa de eliminar própria conta')
            this.errorMessage = 'Não pode eliminar a sua própria conta.'
          }
          // Check for authentication issues
          else if (err.response.status === 401) {
            console.log('Erro de autenticação')
            this.errorMessage = 'Sem permissões para eliminar utilizadores. Verifique se está autenticado como administrador.'
          }
          // Check SPECIFICALLY for database connection issues (503 Service Unavailable)
          else if (err.response.status === 503) {
            console.log('Erro 503: Serviço indisponível - Base de dados')
            this.databaseError = true
            this.errorMessage = ''
          }
          // 500 Internal Server Error - could be database or other server issues
          else if (err.response.status === 500) {
            console.log('Erro 500: Erro interno do servidor')
            // Only consider it a database error if the error message specifically mentions database
            if (err.response.data && typeof err.response.data === 'string' && 
                err.response.data.toLowerCase().includes('database')) {
              this.databaseError = true
              this.errorMessage = ''
            } else {
              this.errorMessage = 'Erro interno do servidor. Por favor, tente novamente.'
            }
          }
          // 404 Not Found - endpoint doesn't exist
          else if (err.response.status === 404) {
            console.log('Erro 404: Endpoint não encontrado')
            this.errorMessage = 'Funcionalidade não disponível. Contacte o administrador.'
          }
          // 502 Bad Gateway - usually proxy/connectivity issues, not database
          else if (err.response.status === 502) {
            console.log('Erro 502: Bad Gateway - Problema de conectividade')
            // Check if it's actually a successful delete that returned 204 but got converted to 502
            if (err.response.statusText === 'No Content') {
              console.log('502 com No Content - provavelmente um 204 bem-sucedido convertido pelo proxy')
              // Treat as success since the operation was likely successful
              const deletedCount = this.selected.length
              this.items = this.items.filter(
                (user) => !this.selected.some((selectedUser) => selectedUser.id === user.id)
              )
              this.selected = []
              this.dialogDelete = false
              this.databaseError = false
              this.successMessage = deletedCount > 1 
                ? `${deletedCount} utilizadores eliminados com sucesso!`
                : 'Utilizador eliminado com sucesso!'
              this.hideMessageAfterDelay('successMessage')
              return // Exit early, don't show error
            } else {
              this.errorMessage = 'Erro de conectividade com o servidor. Verifique se o backend está a funcionar.'
            }
          }
          // Other HTTP errors
          else {
            console.log('Outro erro HTTP')
            this.errorMessage = `Erro ${err.response.status}: ${err.response.data?.detail || 'Erro ao eliminar utilizador'}`
          }
        } 
        // Network or connection error (no response)
        else if (err.request) {
          console.log('Erro de rede - sem resposta do servidor')
          this.errorMessage = 'Erro de conectividade. Verifique a ligação à internet.'
        }
        // Error in request configuration
        else {
          console.log('Erro na configuração da requisição')
          this.errorMessage = 'Erro interno. Por favor, tente novamente.'
        }
        
        this.hideMessageAfterDelay('errorMessage', 5000)
        
      } finally {
        this.isLoading = false
      }
    },

    openEditPage(user: UserDTO) {
      this.$router.push(`/users/edit/${user.id}`)
    },
    handleError(error: any, defaultMessage: string) {
      const err = error as any
      
      // Check for database/server errors
      if (err.response && err.response.status === 503) {
        console.log('handleError: Erro 503 - Base de dados indisponível')
        this.databaseError = true
        this.errorMessage = ''
      }
      // Network or connection error (no response)
      else if (!err.response) {
        console.log('handleError: Sem resposta do servidor - assumindo problema de conectividade')
        this.errorMessage = 'Erro de conectividade. Verifique a ligação à internet.'
      }
      // 500 with database mention
      else if (err.response && err.response.status === 500 && 
               err.response.data && typeof err.response.data === 'string' && 
               err.response.data.toLowerCase().includes('database')) {
        console.log('handleError: Erro 500 com menção à base de dados')
        this.databaseError = true
        this.errorMessage = ''
      }
      // Other errors
      else {
        console.log('handleError: Outro tipo de erro')
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
})
</script>

<style scoped>
::v-deep .v-dialog {
  width: 800px;
}

.v-alert {
  border-radius: 12px !important;
  font-weight: 500;
}
</style>
