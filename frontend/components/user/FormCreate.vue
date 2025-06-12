<template>
  <v-card>
    <v-alert v-if="databaseError" type="error" dismissible class="mb-4">
      <v-icon left>mdi-database-alert</v-icon>
      Base de dados indisponível. Por favor, tente novamente mais tarde.
    </v-alert>
    
    <v-card-title>Create a User</v-card-title>
    <v-card-text>
      <v-form ref="form" v-model="valid">
        <v-row>
          <v-col cols="12" sm="12">
            <v-text-field 
              :value="username" 
              :counter="100" 
              :label="'Username'"
              :rules="[rules.required, rules.counter]" 
              :error-messages="usernameErrors"
              :loading="checkingUsername"
              outlined 
              required
              @input="onUsernameChange" 
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field v-model="localFirstName" label="First name" outlined 
              @input="$emit('update:firstName', localFirstName)" />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field v-model="localLastName" label="Last name" outlined 
            @input="$emit('update:lastName', localLastName)" />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" sm="12">
            <v-text-field
              v-model="localEmail"
              label="Email address"
              :rules="[rules.email, rules.required]"
              :error-messages="emailErrors"
              :loading="checkingEmail"
              outlined
              @input="onEmailChange"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6" sm="6">
            <v-text-field
              id="password"
              v-model="localPassword"
              :append-icon="show2 ? mdiEye : mdiEyeOff"
              :counter="30"
              name="password"
              persistent-hint
              :rules="[
                rules.required,
                rules.counter,
                rules.minLength,
                rules.noCommonWords,
                rules.hasNumberAndSpecialChar,
                rules.notSimilarToPersonalInfo
              ]"
              :type="show2 ? 'text' : 'password'"
              :label="$t('user.password')"
              outlined
              @click:append="show2 = !show2"
              @input="$emit('update:password', localPassword)"
            />
          </v-col>
          <v-col cols="6" sm="6">
            <v-text-field
              id="passwordConfirmation"
              v-model="localPasswordConfirmation"
              :append-icon="show1 ? mdiEye : mdiEyeOff"
              :counter="30"
              name="passwordConfirmation"
              persistent-hint
              :rules="[rules.required, rules.counter, rules.passwordsMatch]"
              :type="show1 ? 'text' : 'password'"
              :label="$t('user.passwordConfirmation')"
              outlined
              @click:append="show1 = !show1"
              @input="$emit('update:passwordConfirmation', localPasswordConfirmation)"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" sm="6">
            <v-checkbox
              v-model="localIsStaff"
              label="Staff Status"
              hint="Designates whether the user can log into this admin site."
              persistent-hint
              @change="$emit('update:isStaff', localIsStaff)"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-checkbox
              v-model="localisSuperUser"
              label="Superuser Status"
              hint="Designates that this user has all permissions without explicitly assigning them."
              persistent-hint
              @change="$emit('update:isSuperUser', localisSuperUser)"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" sm="12">
            <slot :valid="valid" />
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
  </v-card>
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
      required: true
    },
    passwordConfirmation: {
      type: String,
      required: true
    },
    isSuperUser: {
      type: Boolean,
      default: false
    },
    isStaff: {
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
      
      rules: {
        passwordsMatch: (
          v: string // @ts-ignore
        ) => this.isEqual(v) || 'Passwords must match',
        required: (v: string) => !!v || 'Required',
        counter: (
          v: string // @ts-ignore
        ) => (v && v.length <= 100) || this.$t('rules.userNameRules').userNameLessThan30Chars,
        minLength: (v: string) =>
          (v && v.length >= 8) || 'Your password must contain at least 8 characters.',
        noCommonWords: (v: string) => {
          const commonWords = ['password', '123456', 'qwerty', 'letmein', 'admin']
          return (
            !commonWords.some((word) => v.toLowerCase().includes(word)) ||
            'Avoid using common words or sequences.'
          )
        },
        email: (v: string) => /.+@.+\..+/.test(v) || 'E-mail must be valid',
        hasNumberAndSpecialChar: (v: string) => {
          const hasNumber = /\d/.test(v)
          const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(v)
          return (
            (hasNumber && hasSpecialChar) || 'It should include numbers and special characters.'
          )
        },
        notSimilarToPersonalInfo: (v: string) => {
          if (!v) return true // If empty, let 'required' rule handle it
          const personalInfo = [this.username] // Add more fields if needed
          for (const info of personalInfo) {
            if (info && v.toLowerCase().includes(info.toLowerCase()))
              return 'Your password cannot be too similar to your other personal information.'
          }
          return true
        }
      },
      mdiReload,
      show2: false,
      mdiEye,
      mdiEyeOff,
      show1: false
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
          this.usernameErrors = ['Este nome de utilizador já está em uso']
        }
      } catch (error) {
        console.error('Erro ao verificar username:', error)
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
          this.emailErrors = ['Este email já está em uso']
        }
      } catch (error) {
        console.error('Erro ao verificar email:', error)
        if (error.response && error.response.status === 503) {
          this.databaseError = true
        }
      } finally {
        this.checkingEmail = false
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
