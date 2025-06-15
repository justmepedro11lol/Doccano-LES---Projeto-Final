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

  async fetch() {
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

  methods: {

    async handleDelete() {
      this.isLoading = true
      this.clearMessages()
      
      try {
        // Elimina cada utilizador selecionado
        for (const user of this.selected) {
          await this.$services.user.delete(user.id)
        }
        
        // Atualiza a lista removendo os utilizadores eliminados
        this.items = this.items.filter(
          (user) => !this.selected.some((selectedUser) => selectedUser.id === user.id)
        )
        
        const deletedCount = this.selected.length
        this.selected = []
        this.dialogDelete = false

        // Mostra mensagem de sucesso
        this.successMessage = deletedCount > 1 
          ? `${deletedCount} utilizadores eliminados com sucesso!`
          : 'User deleted successfully!'
        
        this.hideMessageAfterDelay('successMessage')
        
      } catch (error: any) {
        this.dialogDelete = false
        console.error('Erro ao eliminar utilizador:', error)
        
        // Tratar mensagens de erro específicas
        if (error.response && error.response.status === 403) {
          const errorDetail = error.response.data?.detail || ''
          if (errorDetail.includes('cannot delete your own user')) {
            this.errorMessage = 'You cannot delete your own user.'
          } else if (errorDetail.includes('cannot delete an admin user')) {
            this.errorMessage = 'You cannot delete an admin.'
          } else {
            this.errorMessage = 'Sem permissões para eliminar este utilizador.'
          }
        } else {
          this.errorMessage = 'Erro ao eliminar utilizador. Tente novamente.'
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
      console.error('Erro:', error)
      this.errorMessage = defaultMessage
      this.hideMessageAfterDelay('errorMessage', 5000)
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
