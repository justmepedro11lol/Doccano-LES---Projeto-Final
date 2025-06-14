<template>
  <base-card
    :title="$t('Edit User')"
    :agree-text="$t('generic.save')"
    :cancel-text="$t('generic.cancel')"
    @agree="submit"
    @cancel="$emit('cancel')"
  >
    <template #content>
      <v-form ref="form" v-model="valid">
        <!-- Seção de Informações Básicas -->
        <v-card class="form-section mb-4" elevation="2">
          <v-card-title class="section-header">
            <v-icon left color="primary">mdi-account-outline</v-icon>
            <span class="text-h6">Informações Básicas</span>
          </v-card-title>
          <v-card-text class="pa-6">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.username"
                  :counter="100"
                  label="Nome de Utilizador"
                  :rules="[rules.required, rules.counter]"
                  :error-messages="usernameErrors"
                  :loading="checkingUsername"
                  outlined
                  dense
                  required
                  prepend-inner-icon="mdi-account"
                  class="custom-field"
                  @input="onUsernameChange"
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.first_name"
                  label="Primeiro Nome"
                  outlined
                  dense
                  prepend-inner-icon="mdi-account-circle"
                  class="custom-field"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.last_name"
                  label="Último Nome"
                  outlined
                  dense
                  prepend-inner-icon="mdi-account-circle-outline"
                  class="custom-field"
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.email"
                  label="Endereço de Email"
                  :rules="[rules.email, rules.required]"
                  :error-messages="emailErrors"
                  :loading="checkingEmail"
                  outlined
                  dense
                  prepend-inner-icon="mdi-email"
                  class="custom-field"
                  @input="onEmailChange"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Seção de Segurança -->
        <v-card class="form-section mb-4" elevation="2">
          <v-card-title class="section-header">
            <v-icon left color="primary">mdi-shield-key</v-icon>
            <span class="text-h6">Segurança</span>
          </v-card-title>
          <v-card-text class="pa-6">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.password"
                  :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                  :counter="30"
                  persistent-hint
                  hint="Deixe vazio para manter a palavra-passe atual"
                  :rules="passwordEditRules"
                  :type="showPassword ? 'text' : 'password'"
                  label="Nova Palavra-passe"
                  outlined
                  dense
                  prepend-inner-icon="mdi-lock"
                  class="custom-field"
                  @click:append="showPassword = !showPassword"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.passwordConfirmation"
                  :append-icon="showPasswordConfirm ? 'mdi-eye' : 'mdi-eye-off'"
                  :counter="30"
                  persistent-hint
                  hint="Confirme a nova palavra-passe (se alterar)"
                  :rules="passwordConfirmationEditRules"
                  :type="showPasswordConfirm ? 'text' : 'password'"
                  label="Confirmar Nova Palavra-passe"
                  outlined
                  dense
                  prepend-inner-icon="mdi-lock-check"
                  class="custom-field"
                  @click:append="showPasswordConfirm = !showPasswordConfirm"
                />
              </v-col>
            </v-row>

            <!-- Indicador de força da palavra-passe -->
            <v-row v-if="formData.password">
              <v-col cols="12">
                <div class="password-strength">
                  <div class="d-flex align-center mb-2">
                    <span class="text-caption">Força da palavra-passe:</span>
                    <v-chip
                      :color="passwordStrengthColor"
                      small
                      text-color="white"
                      class="ml-2"
                    >
                      {{ passwordStrengthText }}
                    </v-chip>
                  </div>
                  <v-progress-linear
                    :value="passwordStrengthValue"
                    :color="passwordStrengthColor"
                    height="4"
                    rounded
                  ></v-progress-linear>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Seção de Permissões -->
        <v-card class="form-section mb-4" elevation="2">
          <v-card-title class="section-header">
            <v-icon left color="primary">mdi-shield-account</v-icon>
            <span class="text-h6">Permissões</span>
          </v-card-title>
          <v-card-text class="pa-6">
            <v-row>
              <v-col cols="12" md="6">
                <div class="permission-card">
                  <v-checkbox
                    v-model="formData.isStaff"
                    color="primary"
                    class="custom-checkbox"
                  >
                    <template #label>
                      <div>
                        <div class="font-weight-medium">Status de Staff</div>
                        <div class="text-caption grey--text">
                          Permite acesso à área de administração
                        </div>
                      </div>
                    </template>
                  </v-checkbox>
                </div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="permission-card">
                  <v-checkbox
                    v-model="formData.isSuperUser"
                    color="primary"
                    class="custom-checkbox"
                  >
                    <template #label>
                      <div>
                        <div class="font-weight-medium">Status de Superutilizador</div>
                        <div class="text-caption grey--text">
                          Concede todas as permissões automaticamente
                        </div>
                      </div>
                    </template>
                  </v-checkbox>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-form>
    </template>
  </base-card>
</template>

<script lang="ts">
import Vue from 'vue'
import BaseCard from '@/components/utils/BaseCard.vue'
import { UserDTO } from '~/services/application/user/userData'

export default Vue.extend({
  components: {
    BaseCard
  },

  props: {
    user: {
      type: Object as () => UserDTO,
      required: true
    }
  },

  data() {
    return {
      formData: {
        id: this.user.id,
        username: this.user.username,
        first_name: this.user.first_name,
        last_name: this.user.last_name,
        email: this.user.email,
        password: '',
        passwordConfirmation: '',
        isSuperUser: this.user.isSuperUser,
        isStaff: this.user.isStaff
      },
      valid: false,
      
      // Validação em tempo real
      usernameErrors: [] as string[],
      emailErrors: [] as string[],
      checkingUsername: false,
      checkingEmail: false,
      usernameTimeout: null as any,
      emailTimeout: null as any,
      
      // Controle de visibilidade das senhas
      showPassword: false,
      showPasswordConfirm: false,
      
      rules: {
        required: (v: string) => !!v || 'Campo obrigatório',
        counter: (v: string) => (v && v.length <= 100) || 'Máximo 100 caracteres',
        email: (v: string) => /.+@.+\..+/.test(v) || 'Email deve ser válido',
        minLength: (v: string) => (v && v.length >= 8) || 'A palavra-passe deve ter pelo menos 8 caracteres.',
        noCommonWords: (v: string) => {
          const commonWords = ['password', '123456', 'qwerty', 'letmein', 'admin']
          return (
            !commonWords.some((word) => v.toLowerCase().includes(word)) ||
            'Evite usar palavras comuns ou sequências.'
          )
        },
        hasNumberAndSpecialChar: (v: string) => {
          const hasNumber = /\d/.test(v)
          const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(v)
          return (
            (hasNumber && hasSpecialChar) || 'Deve incluir números e caracteres especiais.'
          )
        },
        notSimilarToPersonalInfo: (v: string) => {
          if (!v) return true
          const personalInfo = [this.formData.username]
          for (const info of personalInfo) {
            if (info && v.toLowerCase().includes(info.toLowerCase()))
              return 'A palavra-passe não pode ser muito similar às suas informações pessoais.'
          }
          return true
        }
      }
    }
  },

  computed: {
    passwordEditRules() {
      return [
        // Para edição, a senha não é obrigatória, mas se preenchida deve seguir as regras
        (v: string) => {
          if (!v) return true // Vazio é válido na edição
          return this.rules.counter(v)
        },
        (v: string) => {
          if (!v) return true
          return this.rules.minLength(v)
        },
        (v: string) => {
          if (!v) return true
          return this.rules.noCommonWords(v)
        },
        (v: string) => {
          if (!v) return true
          return this.rules.hasNumberAndSpecialChar(v)
        },
        (v: string) => {
          if (!v) return true
          return this.rules.notSimilarToPersonalInfo(v)
        }
      ]
    },

    passwordConfirmationEditRules() {
      return [
        (v: string) => {
          // Se não há senha, confirmação também deve estar vazia
          if (!this.formData.password && !v) return true
          // Se há senha, deve ter confirmação
          if (this.formData.password && !v) return 'Deve confirmar a palavra-passe'
          // Se há confirmação, deve coincidir
          return this.isPasswordEqual(v) || 'As palavras-passe devem coincidir'
        },
        (v: string) => {
          if (!v) return true
          return this.rules.counter(v)
        }
      ]
    },

    passwordStrengthValue(): number {
      if (!this.formData.password) return 0
      let score = 0
      
      if (this.formData.password.length >= 8) score += 25
      if (/[a-z]/.test(this.formData.password)) score += 15
      if (/[A-Z]/.test(this.formData.password)) score += 15
      if (/\d/.test(this.formData.password)) score += 15
      if (/[!@#$%^&*(),.?":{}|<>]/.test(this.formData.password)) score += 15
      if (this.formData.password.length >= 12) score += 15
      
      return Math.min(score, 100)
    },
    
    passwordStrengthColor(): string {
      if (this.passwordStrengthValue < 30) return 'error'
      if (this.passwordStrengthValue < 60) return 'warning'
      if (this.passwordStrengthValue < 80) return 'primary'
      return 'success'
    },
    
    passwordStrengthText(): string {
      if (this.passwordStrengthValue < 30) return 'Fraca'
      if (this.passwordStrengthValue < 60) return 'Média'
      if (this.passwordStrengthValue < 80) return 'Boa'
      return 'Forte'
    }
  },

  beforeDestroy() {
    // Limpa os timers
    if (this.usernameTimeout) clearTimeout(this.usernameTimeout)
    if (this.emailTimeout) clearTimeout(this.emailTimeout)
  },

  methods: {
    onUsernameChange(value: string) {
      this.formData.username = value
      
      // Limpa timeout anterior
      if (this.usernameTimeout) clearTimeout(this.usernameTimeout)
      
      // Se campo vazio, limpa erros
      if (!value || value.trim() === '') {
        this.usernameErrors = []
        return
      }
      
      // Debounce - espera 500ms após parar de digitar
      this.usernameTimeout = setTimeout(() => {
        this.checkUsernameExists(value)
      }, 500)
    },
    
    onEmailChange(value: string) {
      this.formData.email = value
      
      // Limpa timeout anterior
      if (this.emailTimeout) clearTimeout(this.emailTimeout)
      
      // Se campo vazio, limpa erros
      if (!value || value.trim() === '') {
        this.emailErrors = []
        return
      }
      
      // Verifica se email é válido primeiro
      const emailRegex = /.+@.+\..+/
      if (!emailRegex.test(value)) {
        this.emailErrors = []
        return
      }
      
      // Debounce - espera 500ms após parar de digitar
      this.emailTimeout = setTimeout(() => {
        this.checkEmailExists(value)
      }, 500)
    },
    
    async checkUsernameExists(username: string) {
      if (!username || username.trim() === '') return
      
      this.checkingUsername = true
      this.usernameErrors = []
      
      try {
        const response = await this.$repositories.user.checkUserExists(username, undefined, this.formData.id)
        if (response.username_exists) {
          this.usernameErrors = ['Este nome de utilizador já está em uso']
        }
      } catch (error) {
        console.error('Erro ao verificar username:', error)
      } finally {
        this.checkingUsername = false
      }
    },
    
    async checkEmailExists(email: string) {
      if (!email || email.trim() === '') return
      
      this.checkingEmail = true
      this.emailErrors = []
      
      try {
        const response = await this.$repositories.user.checkUserExists(undefined, email, this.formData.id)
        if (response.email_exists) {
          this.emailErrors = ['Este email já está em uso']
        }
      } catch (error) {
        console.error('Erro ao verificar email:', error)
      } finally {
        this.checkingEmail = false
      }
    },

    isPasswordEqual(v: string): boolean {
      return v === this.formData.password
    },

    submit() {
      const form = this.$refs.form as Vue & { validate: () => boolean }
      if (!form.validate()) return

      const updatedUser: any = {
        id: this.formData.id,
        username: this.formData.username,
        first_name: this.formData.first_name,
        last_name: this.formData.last_name,
        email: this.formData.email,
        isSuperUser: this.formData.isSuperUser,
        isStaff: this.formData.isStaff
      }

      // Só inclui a senha se foi preenchida
      if (this.formData.password && this.formData.passwordConfirmation) {
        updatedUser.password = this.formData.password
        updatedUser.passwordConfirmation = this.formData.passwordConfirmation
      }

      this.$emit('confirmEdit', updatedUser)
    }
  }
})
</script>

<style scoped>
.form-section {
  border-radius: 16px !important;
  transition: all 0.3s ease;
  border-left: 4px solid #1976d2;
}

.form-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
}

.section-header {
  background: linear-gradient(145deg, #f5f5f5 0%, #eeeeee 100%);
  border-radius: 12px 12px 0 0 !important;
  padding: 16px 20px;
  font-weight: 600;
  color: #424242;
}

.custom-field {
  border-radius: 12px !important;
}

.custom-field ::v-deep .v-input__control {
  border-radius: 12px !important;
}

.permission-card {
  background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s ease;
}

.permission-card:hover {
  background: linear-gradient(145deg, #e9ecef 0%, #dee2e6 100%);
}

.custom-checkbox ::v-deep .v-input--selection-controls__input {
  margin-right: 12px;
}

.password-strength {
  background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  padding: 16px;
  margin-top: 8px;
}

/* Animações */
.form-section {
  animation: slideInUp 0.3s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Melhorias nos campos de texto */
.v-text-field ::v-deep .v-input__control {
  border-radius: 12px !important;
}

.v-text-field ::v-deep .v-text-field__details {
  margin-top: 8px;
}

.v-checkbox ::v-deep .v-label {
  line-height: 1.4;
}

/* Chips de força da palavra-passe */
.v-chip {
  border-radius: 16px !important;
  font-weight: 600;
}

/* Progress linear customizado */
.v-progress-linear {
  border-radius: 4px !important;
  overflow: hidden;
}
</style>
