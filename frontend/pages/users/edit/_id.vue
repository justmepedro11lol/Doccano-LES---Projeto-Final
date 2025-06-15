<template>
  <div class="user-edit-container">
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
      >
        <v-icon slot="prepend" color="warning">mdi-database-alert</v-icon>
        Base de dados indisponível. Por favor, tente novamente mais tarde.
      </v-alert>
    </v-slide-y-transition>

    <!-- Card principal com design melhorado -->
    <v-card class="main-card" elevation="3">
      <v-card-title class="primary white--text d-flex align-center">
        <v-icon left color="white" size="28">mdi-account-edit</v-icon>
        <span class="text-h5">Editar Utilizador</span>
      </v-card-title>

      <v-card-text class="pa-6">
        <form-create 
          v-if="editedItem && !isLoading"
          v-bind.sync="editedItem" 
          :id="userId"
          :items="items"
          :is-edit-mode="true"
        >
          <template #default="{ valid }">
            <!-- Botões de ação com design melhorado -->
            <div class="actions-container mt-6">
              <div class="d-flex flex-wrap gap-3 justify-center">
                <v-btn
                  color="error"
                  outlined
                  large
                  class="action-btn"
                  @click="$router.push('/users')"
                >
                  <v-icon left>mdi-close</v-icon>
                  Cancelar
                </v-btn>

                <v-btn
                  :disabled="!valid || databaseError"
                  color="primary"
                  large
                  elevated
                  class="action-btn primary-btn"
                  @click="save"
                >
                  <v-icon left>mdi-content-save</v-icon>
                  Guardar Alterações
                </v-btn>
              </div>
            </div>
          </template>
        </form-create>
      </v-card-text>
    </v-card>

    <!-- Loading overlay -->
    <v-overlay v-if="isLoading" absolute>
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
      ></v-progress-circular>
    </v-overlay>
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

  data() {
    return {
      editedItem: null as UserDTO | null,
      originalUser: null as UserDTO | null,
      items: [] as UserDTO[],
      errorMessage: '',
      successMessage: '',
      isLoading: false,
      databaseError: false
    }
  },

  computed: {
    userId(): number {
      return parseInt(this.$route.params.id)
    },

    isFormValid(): boolean {
      // This computed property is no longer directly used for button disabling.
      // The 'valid' state from the FormCreate component is now used directly.
      return true; // Or remove if not used elsewhere.
    },

    service(): any {
      return this.$services.user
    }
  },

  async created() {
    this.isLoading = true
    try {
      // Carrega lista de usuários para validação e busca o usuário específico
      this.items = await this.service.list()
      
      // Busca o usuário específico na lista
      this.originalUser = this.items.find(user => user.id === this.userId) || null
      
      if (!this.originalUser) {
        this.errorMessage = 'Utilizador não encontrado.'
        setTimeout(() => {
          this.$router.push('/users')
        }, 2000)
        return
      }
      
      // Cria uma cópia do usuário para edição
      this.editedItem = {
        id: this.originalUser.id,
        username: this.originalUser.username,
        firstName: this.originalUser.firstName,
        lastName: this.originalUser.lastName,
        email: this.originalUser.email,
        isSuperUser: this.originalUser.isSuperUser,
        isStaff: this.originalUser.isStaff,
        password: '', // Senha sempre vazia na edição
        passwordConfirmation: ''
      }

      console.log('=== UTILIZADOR CARREGADO ===')
      console.log('Dados originais:', this.originalUser)
      console.log('Dados para edição:', this.editedItem)
      
    } catch (error) {
      console.error('Error loading user:', error)
      this.errorMessage = `Erro ao carregar utilizador: ${error.message || 'Erro desconhecido'}`
    } finally {
      this.isLoading = false
    }
    
    // Não inicia health check para melhorar performance
    // this.startHealthCheck()
  },
  
  beforeDestroy() {
    // Não há mais health check para limpar
  },

  methods: {
    async save() {
      if (!this.editedItem) return
      
      this.isLoading = true
      this.errorMessage = ''
      this.successMessage = ''
      
      try {
        // Prepara payload para envio
        const userPayload: any = {
          username: this.editedItem.username,
          first_name: this.editedItem.firstName,
          last_name: this.editedItem.lastName,
          email: this.editedItem.email,
          isSuperUser: this.editedItem.isSuperUser,
          isStaff: this.editedItem.isStaff
        }
        
        // Debug: Log para verificar os valores
        console.log('=== GUARDAR UTILIZADOR ===')
        console.log('isSuperUser:', this.editedItem.isSuperUser)
        console.log('isStaff:', this.editedItem.isStaff)
        console.log('Payload:', userPayload)
        
        // Só inclui senha se foi preenchida
        if (this.editedItem.password && this.editedItem.passwordConfirmation) {
          userPayload.password = this.editedItem.password
          userPayload.passwordConfirmation = this.editedItem.passwordConfirmation
        }
        
        await this.service.update(this.userId, userPayload)
        
        // Sucesso - redireciona imediatamente
        this.$router.push('/users')
        
      } catch (error: any) {
        console.error('Erro ao guardar:', error)
        this.errorMessage = 'Erro ao guardar utilizador. Tente novamente.'
      } finally {
        this.isLoading = false
      }
    },

    handleError(error: any) {
      if (error.response) {
        if (error.response.status === 503) {
          this.databaseError = true
          this.errorMessage = 'Base de dados indisponível. Por favor, tente novamente mais tarde.'
        } else if (error.response.status === 400) {
          const errors = error.response.data
          if (errors.username) {
            this.errorMessage = 'Nome de utilizador já existe.'
          } else if (errors.email) {
            this.errorMessage = 'Email já existe.'
          } else {
            this.errorMessage = 'Erro de validação desconhecido.'
          }
        } else {
          this.errorMessage = `Erro: ${error.message || 'Erro desconhecido'}`
        }
      }
    }
  }
})
</script>

<style scoped>
.user-edit-container {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  padding: 20px;
}

.main-card {
  max-width: 900px;
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

.actions-container {
  padding: 20px;
  background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px;
  margin-top: 20px;
}

.action-btn {
  border-radius: 24px !important;
  text-transform: none !important;
  font-weight: 600;
  padding: 0 24px;
  min-width: 140px;
  margin: 4px;
}

.primary-btn {
  background: linear-gradient(145deg, #1976d2 0%, #1565c0 100%) !important;
}

.gap-3 {
  gap: 12px;
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

/* Efeitos de hover nos botões */
.v-btn:hover:not(.v-btn--disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

/* Animações */
.main-card {
  animation: slideInUp 0.4s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>