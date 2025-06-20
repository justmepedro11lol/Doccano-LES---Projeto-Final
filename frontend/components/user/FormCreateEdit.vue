<template>
  <div class="form-create-container">
    <!-- Alerta de database com design melhorado -->
    <v-slide-y-transition>
      <v-alert 
        v-if="databaseError" 
        type="warning" 
        dismissible 
        border="left"
        colored-border
        elevation="2"
        class="mb-4"
      >
        <v-icon slot="prepend" color="warning">mdi-database-alert</v-icon>
        Database unavailable. Please try again later.
      </v-alert>
    </v-slide-y-transition>

    <!-- Formulário com design melhorado -->
    <v-form ref="form" v-model="valid" class="user-form">
      <!-- Seção de Informações Básicas -->
      <v-card class="form-section mb-4" elevation="2">
        <v-card-title class="section-header">
          <v-icon left color="primary">mdi-account-outline</v-icon>
          <span class="text-h6">Basic Information</span>
        </v-card-title>
        <v-card-text class="pa-6">
          <v-row>
            <v-col cols="12">
              <v-text-field 
                :value="username" 
                :counter="100" 
                label="Username"
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
                v-model="localFirstName" 
                label="First Name" 
                outlined 
                dense
                prepend-inner-icon="mdi-account-circle"
                class="custom-field"
                @input="$emit('update:firstName', localFirstName)" 
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field 
                v-model="localLastName" 
                label="Last Name" 
                outlined 
                dense
                prepend-inner-icon="mdi-account-circle-outline"
                class="custom-field"
                @input="$emit('update:lastName', localLastName)" 
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="localEmail"
                label="Email Address"
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
          <span class="text-h6">Security</span>
        </v-card-title>
        <v-card-text class="pa-6">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                id="password"
                v-model="localPassword"
                :append-icon="show2 ? mdiEye : mdiEyeOff"
                :counter="30"
                name="password"
                persistent-hint
                :hint="isEditMode ? 'Leave empty to keep current password' : 'Minimum 8 characters, including numbers and symbols'"
                :rules="isEditMode ? passwordEditRules : passwordCreateRules"
                :type="show2 ? 'text' : 'password'"
                label="Password"
                outlined
                dense
                prepend-inner-icon="mdi-lock"
                class="custom-field"
                @click:append="show2 = !show2"
                @input="$emit('update:password', localPassword)"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                id="passwordConfirmation"
                v-model="localPasswordConfirmation"
                :append-icon="show1 ? mdiEye : mdiEyeOff"
                :counter="30"
                name="passwordConfirmation"
                persistent-hint
                :hint="isEditMode ? 'Confirm new password (if changing)' : 'Confirm password'"
                :rules="isEditMode ? passwordConfirmationEditRules : passwordConfirmationCreateRules"
                :type="show1 ? 'text' : 'password'"
                label="Confirm Password"
                outlined
                dense
                prepend-inner-icon="mdi-lock-check"
                class="custom-field"
                @click:append="show1 = !show1"
                @input="$emit('update:passwordConfirmation', localPasswordConfirmation)"
              />
            </v-col>
          </v-row>

          <!-- Indicador de força da palavra-passe -->
          <v-row v-if="localPassword">
            <v-col cols="12">
              <div class="password-strength">
                <div class="d-flex align-center mb-2">
                  <span class="text-caption">Password strength:</span>
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
          <span class="text-h6">Permissions</span>
        </v-card-title>
        <v-card-text class="pa-6">
          <v-row>
            <v-col cols="12" md="6">
              <div class="permission-card">
                <v-checkbox
                  v-model="localIsStaff"
                  color="primary"
                  class="custom-checkbox"
                  @change="$emit('update:isStaff', localIsStaff)"
                >
                  <template #label>
                    <div>
                      <div class="font-weight-medium">Administrator</div>
                      <div class="text-caption grey--text">
                        Full access to all system features
                      </div>
                    </div>
                  </template>
                </v-checkbox>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="permission-card">
                <v-checkbox
                  v-model="localisSuperUser"
                  color="primary"
                  class="custom-checkbox"
                  @change="$emit('update:isSuperUser', localisSuperUser)"
                >
                  <template #label>
                    <div>
                      <div class="font-weight-medium">Staff Member</div>
                      <div class="text-caption grey--text">
                        Access to administrative interface
                      </div>
                    </div>
                  </template>
                </v-checkbox>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Slot para botões -->
      <div class="form-actions">
        <slot :valid="valid" />
      </div>
    </v-form>
  </div>
</template>

<script lang="ts">
import { mdiReload, mdiEye, mdiEyeOff } from '@mdi/js'
import type { PropType } from 'vue'
import Vue from 'vue'
import { UserDTO } from '~/services/application/user/userData'

export default Vue.extend({
  props: {
    items: {
      type: Array as PropType<UserDTO[]>,
      default: () => [],
      required: true
    },
    id: {
      type: Number as () => number | undefined,
      default: undefined
    },
    username: {
      type: String,
      required: true
    },
    firstName: {
      type: String,
      required: false,
      default: ''
    },
    lastName: {
      type: String,
      required: false,
      default: ''
    },
    email: {
      type: String,
      required: false,
      default: ''
    },
    password: {
      type: String,
      required: false,
      default: ''
    },
    passwordConfirmation: {
      type: String,
      required: false,
      default: ''
    },
    isSuperUser: {
      type: Boolean,
      default: false
    },
    isStaff: {
      type: Boolean,
      default: false
    },
    isEditMode: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      localPassword: this.password,
      localPasswordConfirmation: this.passwordConfirmation,
      localIsStaff: this.isStaff,
      localisSuperUser: this.isSuperUser,
      localFirstName: this.firstName,
      localLastName: this.lastName,
      localEmail: this.email,
      valid: false,
      
      // Validação em tempo real
      usernameErrors: [] as string[],
      emailErrors: [] as string[],
      checkingUsername: false,
      checkingEmail: false,
      usernameTimeout: null as any,
      emailTimeout: null as any,
      
      // Health check
      databaseError: false,
      healthCheckInterval: null as any,
      
      mdiReload,
      show2: false,
      mdiEye,
      mdiEyeOff,
      show1: false
    }
  },

  computed: {
    rules() {
      return {
        required: (v: string) => !!v || 'Required field',
        counter: (
          v: string // @ts-ignore
        ) => (v && v.length <= 100) || 'Maximum 100 characters',
        minLength: (v: string) =>
          (v && v.length >= 8) || 'Password must be at least 8 characters long.',
        noCommonWords: (v: string) => {
          const commonWords = ['password', '123456', 'qwerty', 'letmein', 'admin']
          return (
            !commonWords.some((word) => v.toLowerCase().includes(word)) ||
            'Avoid using common words or sequences.'
          )
        },
        email: (v: string) => /.+@.+\..+/.test(v) || 'Email must be valid',
        hasNumberAndSpecialChar: (v: string) => {
          const hasNumber = /\d/.test(v)
          const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(v)
          return (
            (hasNumber && hasSpecialChar) || 'Must include numbers and special characters.'
          )
        },
        notSimilarToPersonalInfo: (v: string) => {
          if (!v) return true // If empty, let 'required' rule handle it
          const personalInfo = [this.username] // Add more fields if needed
          for (const info of personalInfo) {
            if (info && v.toLowerCase().includes(info.toLowerCase()))
              return 'Password cannot be too similar to your personal information.'
          }
          return true
        }
      }
    },

    passwordCreateRules() {
      return [
        this.rules.required,
        this.rules.counter,
        this.rules.minLength,
        this.rules.noCommonWords,
        this.rules.hasNumberAndSpecialChar,
        this.rules.notSimilarToPersonalInfo
      ]
    },

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

    passwordConfirmationCreateRules() {
      return [
        this.rules.required,
        this.rules.counter,
        (v: string) => this.isEqual(v) || 'Passwords must match'
      ]
    },

    passwordConfirmationEditRules() {
      return [
        (v: string) => {
          // Se não há senha, confirmação também deve estar vazia
          if (!this.localPassword && !v) return true
          // Se há senha, deve ter confirmação
          if (this.localPassword && !v) return 'Must confirm password'
          // Se há confirmação, deve coincidir
          return this.isEqual(v) || 'Passwords must match'
        },
        (v: string) => {
          if (!v) return true
          return this.rules.counter(v)
        }
      ]
    },

    passwordStrengthValue(): number {
      if (!this.localPassword) return 0
      let score = 0
      
      if (this.localPassword.length >= 8) score += 25
      if (/[a-z]/.test(this.localPassword)) score += 15
      if (/[A-Z]/.test(this.localPassword)) score += 15
      if (/\d/.test(this.localPassword)) score += 15
      if (/[!@#$%^&*(),.?":{}|<>]/.test(this.localPassword)) score += 15
      if (this.localPassword.length >= 12) score += 15
      
      return Math.min(score, 100)
    },
    
    passwordStrengthColor(): string {
      if (this.passwordStrengthValue < 30) return 'error'
      if (this.passwordStrengthValue < 60) return 'warning'
      if (this.passwordStrengthValue < 80) return 'primary'
      return 'success'
    },
    
    passwordStrengthText(): string {
      if (this.passwordStrengthValue < 30) return 'Weak'
      if (this.passwordStrengthValue < 60) return 'Medium'
      if (this.passwordStrengthValue < 80) return 'Good'
      return 'Strong'
    }
  },
  
  watch: {
    password(newVal) {
      this.localPassword = newVal
    },
    passwordConfirmation(newVal) {
      this.localPasswordConfirmation = newVal
    },
    firstName(newVal) {
      this.localFirstName = newVal
    },
    lastName(newVal) {
      this.localLastName = newVal
    },
    email(newVal) {
      this.localEmail = newVal
    },
    isStaff(newVal) {
      this.localIsStaff = newVal
    },
    isSuperUser(newVal) {
      this.localisSuperUser = newVal
    }
  },
  
  mounted() {
    // Inicia verificação de saúde da base de dados
    this.startHealthCheck()
  },
  
  beforeDestroy() {
    // Limpa os timers
    if (this.usernameTimeout) clearTimeout(this.usernameTimeout)
    if (this.emailTimeout) clearTimeout(this.emailTimeout)
    if (this.healthCheckInterval) clearInterval(this.healthCheckInterval)
  },
  
  methods: {
    onUsernameChange(value: string) {
      this.$emit('update:username', value)
      
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
      this.$emit('update:email', value)
      this.localEmail = value
      
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
        const response = await this.$repositories.user.checkUserExists(username, undefined, this.id)
        if (response.username_exists) {
          this.usernameErrors = ['This username is already in use']
        }
      } catch (error) {
        console.error('Error checking username:', error)
        if (error.response && error.response.status === 503) {
          this.databaseError = true
        }
      } finally {
        this.checkingUsername = false
      }
    },
    
    async checkEmailExists(email: string) {
      if (!email || email.trim() === '') return
      
      this.checkingEmail = true
      this.emailErrors = []
      
      try {
        const response = await this.$repositories.user.checkUserExists(undefined, email, this.id)
        if (response.email_exists) {
          this.emailErrors = ['This email is already in use']
        }
      } catch (error) {
        console.error('Error checking email:', error)
        if (error.response && error.response.status === 503) {
          this.databaseError = true
        }
      } finally {
        this.checkingEmail = false
      }
    },
    
    startHealthCheck() {
      // Verifica a saúde da base de dados a cada 2 segundos
      this.healthCheckInterval = setInterval(async () => {
        try {
          await this.$repositories.user.checkHealth()
          this.databaseError = false
        } catch (error) {
          console.error('Database health check failed:', error)
          this.databaseError = true
        }
      }, 2000)
    },
    
    isUsedName(username: string): boolean {
      return (
        this.items.filter((item) => item.id !== this.id && item.username === username).length > 0
      )
    },
    isUsedEmail(email: string): boolean {
      return (
        this.items.filter((item) => item.id !== this.id && item.email === email).length > 0
      )
    },
    isEqual(v: string): boolean {
      return v === this.localPassword
    }
  }
})
</script>

<style scoped>
.form-create-container {
  max-width: 100%;
}

.user-form {
  width: 100%;
}

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

.form-actions {
  margin-top: 20px;
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

.v-slide-y-transition-enter-active,
.v-slide-y-transition-leave-active {
  transition: all 0.3s ease;
}

.v-slide-y-transition-enter,
.v-slide-y-transition-leave-to {
  transform: translateY(-15px);
  opacity: 0;
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