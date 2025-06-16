<template>
  <v-container fluid class="pa-0">
    <!-- Loading -->
    <div v-if="isLoading" class="d-flex justify-center align-center" style="height: 50vh">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <!-- Database Error Alert -->
    <v-container v-if="!isLoading" class="pa-0">
      <v-slide-y-transition>
        <v-alert
          v-if="databaseError"
          type="error"
          persistent
          class="ma-4"
        >
          <v-icon left>mdi-database-alert</v-icon>
          Database is currently unavailable. Please try again later.
        </v-alert>
      </v-slide-y-transition>
    </v-container>

    <div v-if="!isLoading">
      <!-- Cabeçalho -->
      <v-row no-gutters class="mb-4">
        <v-col cols="12">
          <v-card class="elevation-2">
            <v-card-title class="primary white--text">
              <v-btn
                @click="goBack"
                class="mr-3"
                icon
                color="white"
              >
                <v-icon>mdi-arrow-left</v-icon>
              </v-btn>
              <v-icon left color="white">mdi-forum</v-icon>
              Discussão de Discrepância - Exemplo {{ exampleId }}
              <v-spacer></v-spacer>
              <v-chip
                :color="exampleData.hasDiscrepancy ? 'error' : 'success'"
                dark
                class="ml-2"
              >
                {{ exampleData.hasDiscrepancy ? 'Discrepante' : 'Consistente' }}
              </v-chip>
              <v-btn
                @click="closeDiscussion"
                class="ml-3"
                icon
                color="white"
                title="Fechar e voltar às Discrepâncias"
              >
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>

      <!-- Informações do Exemplo -->
      <v-row no-gutters class="mb-4">
        <v-col cols="12">
          <v-card class="elevation-1">
            <v-card-title class="text-h6 pb-2">
              <v-icon left color="primary">mdi-text-box</v-icon>
              Texto do Exemplo
            </v-card-title>
            <v-card-text>
              <div class="example-text-container">
                <p class="example-text">{{ exampleData.text || 'Carregando texto...' }}</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Resumo das Diferenças -->
      <v-row no-gutters class="mb-4">
        <v-col cols="12">
          <v-card class="elevation-1">
            <v-card-title class="text-h6 pb-2">
              <v-icon left color="warning">mdi-alert-circle</v-icon>
              Resumo das Diferenças nas Anotações
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="4">
                  <div class="text-body-2 mb-2">
                    <strong>Máxima Concordância:</strong> {{ exampleData.maxPercentage || 0 }}%
                  </div>
                  <div class="text-body-2 mb-2">
                    <strong>Limiar do Projeto:</strong> {{ $store.getters['projects/project'].minPercentage || 80 }}%
                  </div>
                </v-col>
                <v-col cols="12" md="8">
                  <div class="text-body-2 mb-2">
                    <strong>Percentagens por Etiqueta:</strong>
                  </div>
                  <div class="label-percentages-grid">
                    <div 
                      v-for="(percentage, label) in exampleData.labelPercentages" 
                      :key="label"
                      class="label-percentage-item"
                    >
                      <div class="d-flex align-center justify-space-between mb-1">
                        <v-chip
                          small
                          :color="getPercentageColor(percentage)"
                          dark
                          class="mr-2"
                        >
                          {{ label }}
                        </v-chip>
                        <span class="percentage-value">{{ Math.round(percentage) }}%</span>
                      </div>
                      <v-progress-linear
                        :value="percentage"
                        :color="getPercentageColor(percentage)"
                        height="6"
                        rounded
                        class="mb-2"
                      />
                    </div>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Detalhes das Anotações -->
      <v-row no-gutters class="mb-4">
        <v-col cols="12">
          <v-card class="elevation-1">
            <v-card-title class="text-h6 pb-2">
              <v-icon left color="info">mdi-account-group</v-icon>
              Anotações por Utilizador
            </v-card-title>
            <v-card-text>
              <v-row v-if="annotations.length > 0">
                <v-col
                  v-for="(annotation, index) in annotations"
                  :key="index"
                  cols="12"
                  :md="annotations.length > 1 ? 6 : 12"
                  class="mb-3"
                >
                  <v-card
                    :class="[
                      'user-annotation-card',
                      getAnnotationBackgroundClass(index)
                    ]"
                    outlined
                  >
                    <v-card-title class="py-2">
                      <v-avatar
                        :color="getUserColor(annotation.annotator)"
                        size="32"
                        class="mr-2"
                      >
                        <span class="white--text text-caption">
                          {{ getInitials(annotation.annotator) }}
                        </span>
                      </v-avatar>
                      <div>
                        <div class="font-weight-bold">{{ annotation.annotator }}</div>
                        <div class="text-caption text--secondary">
                          {{ formatDate(annotation.createdAt) }}
                        </div>
                      </div>
                    </v-card-title>
                    <v-card-text>
                      <div class="text-subtitle-2 mb-2">Etiquetas:</div>
                      <div v-if="annotation.labels.length === 0" class="text-caption text--secondary">
                        Nenhuma etiqueta atribuída
                      </div>
                      <v-chip
                        v-for="label in annotation.labels"
                        :key="label.id"
                        small
                        :color="getLabelColor(label.name)"
                        class="mr-1 mb-1"
                        dark
                      >
                        {{ label.name }}
                      </v-chip>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
              <div v-else class="text-center py-4">
                <v-icon size="48" color="grey">mdi-clipboard-outline</v-icon>
                <div class="text-subtitle-1 grey--text mt-2">Nenhuma anotação encontrada</div>
                <div class="text-caption grey--text">Este exemplo ainda não foi anotado.</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Chat de Discussão -->
      <v-row no-gutters>
        <v-col cols="12">
          <v-card class="elevation-1">
            <v-card-title class="text-h6 pb-2">
              <v-icon left color="success">mdi-chat</v-icon>
              Discussão
              <v-spacer></v-spacer>
              <v-chip small outlined>
                {{ filteredMessages.length }} mensagens
                <span v-if="selectedUserFilter && selectedUserFilter !== 'all'">
                  ({{ selectedUserFilter }})
                </span>
              </v-chip>
            </v-card-title>
            
            <!-- Filtro por Utilizador -->
            <v-card-text class="pt-0 pb-2">
              <v-row align="center" no-gutters class="px-2">
                <v-col cols="auto" class="mr-3">
                  <v-icon small color="grey" class="mr-1">mdi-account-filter</v-icon>
                  <span class="text-body-2 font-weight-medium text--secondary">
                    Filtrar mensagens:
                  </span>
                </v-col>
                <v-col cols="auto">
                  <v-select
                    v-model="selectedUserFilter"
                    :items="userFilterOptions"
                    item-text="label"
                    item-value="value"
                    dense
                    outlined
                    hide-details
                    class="mt-0"
                    style="min-width: 180px; max-width: 250px;"
                  >
                    <template #selection="{ item }">
                      <v-chip small outlined class="ma-0">
                        <v-icon left x-small>
                          {{ item.value === 'all' ? 'mdi-account-group' : 'mdi-account' }}
                        </v-icon>
                        {{ item.label }}
                      </v-chip>
                    </template>
                    <template #item="{ item }">
                      <v-list-item-icon class="mr-2">
                        <v-icon small>
                          {{ item.value === 'all' ? 'mdi-account-group' : 'mdi-account' }}
                        </v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title>{{ item.label }}</v-list-item-title>
                      </v-list-item-content>
                    </template>
                  </v-select>
                </v-col>
                <v-col v-if="selectedUserFilter !== 'all'" cols="auto" class="ml-2">
                  <v-btn
                    @click="selectedUserFilter = 'all'"
                    icon
                    small
                    color="grey"
                    title="Limpar filtro"
                  >
                    <v-icon small>mdi-close</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>

            <v-card-text class="pa-0">
              <!-- Área de Mensagens -->
              <div ref="messagesContainer" class="messages-container">
                <div
                  v-for="message in filteredMessages"
                  :key="message.id"
                  :class="[
                    'message-item',
                    { 'message-filtered': selectedUserFilter !== 'all' }
                  ]"
                >
                  <div class="d-flex align-start">
                    <v-avatar
                      :color="getUserColor(message.user)"
                      size="36"
                      class="mr-3"
                    >
                      <span class="white--text text-caption">
                        {{ getInitials(message.user) }}
                      </span>
                    </v-avatar>
                    <div class="flex-grow-1">
                      <div class="d-flex align-center mb-1">
                        <span class="font-weight-bold text-body-2">{{ message.user }}</span>
                        <span class="text-caption text--secondary ml-2">
                          {{ formatDate(message.created_at) }}
                        </span>
                      </div>
                      <div class="text-body-2">{{ message.text }}</div>
                    </div>
                  </div>
                </div>

                <div v-if="filteredMessages.length === 0" class="text-center py-8">
                  <v-icon size="64" color="grey">mdi-chat-outline</v-icon>
                  <div class="text-h6 grey--text mt-2">
                    {{ selectedUserFilter && selectedUserFilter !== 'all' 
                        ? `Nenhuma mensagem de ${selectedUserFilter}`
                        : 'Nenhuma mensagem ainda' }}
                  </div>
                  <div class="text-body-2 grey--text">
                    {{ selectedUserFilter && selectedUserFilter !== 'all'
                        ? 'Este utilizador ainda não enviou mensagens'
                        : 'Seja o primeiro a iniciar a discussão sobre esta discrepância' }}
                  </div>
                </div>
              </div>

              <!-- Input de Nova Mensagem -->
              <v-divider></v-divider>
              <div class="pa-4">
                <v-row align="center" no-gutters>
                  <v-col>
                    <v-text-field
                      v-model="newMessage"
                      placeholder="Digite sua mensagem..."
                      outlined
                      dense
                      hide-details
                      @keydown.enter="sendMessage"
                    >
                      <template #prepend-inner>
                        <v-icon color="grey">mdi-message-outline</v-icon>
                      </template>
                    </v-text-field>
                  </v-col>
                  <v-col cols="auto" class="ml-3">
                    <v-btn
                      color="primary"
                      :disabled="!newMessage.trim() || isSendingMessage"
                      :loading="isSendingMessage"
                      @click="sendMessage"
                    >
                      <v-icon left>mdi-send</v-icon>
                      Enviar
                    </v-btn>
                  </v-col>
                </v-row>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapGetters } from 'vuex'
import type { DiscrepancyMessage } from '~/domain/models/example/discrepancy'

interface ExampleData {
  id: string
  text: string
  hasDiscrepancy: boolean
  maxPercentage: number
  labelPercentages: { [label: string]: number }
}

interface Annotation {
  annotator: string
  createdAt: string
  labels: Array<{
    id: string
    name: string
  }>
}

export default Vue.extend({
  name: 'DiscrepancyDiscussionPage',
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      exampleData: {} as ExampleData,
      annotations: [] as Annotation[],
      discussionMessages: [] as DiscrepancyMessage[],
      newMessage: '',
      isSendingMessage: false,
      isLoading: true,
      userColors: [
        '#1976D2', '#388E3C', '#F57C00', '#7B1FA2', '#D32F2F',
        '#0097A7', '#455A64', '#E64A19', '#5D4037', '#689F38',
        '#303F9F', '#C2185B', '#00796B', '#FBC02D', '#795548'
      ],
      selectedUserFilter: 'all',
      // Database error state
      databaseError: false,
      databaseCheckInterval: null as NodeJS.Timeout | null
    }
  },

  async fetch() {
    this.isLoading = true
    try {
      await Promise.all([
        this.loadExampleData(),
        this.loadAnnotations(),
        this.loadMessages()
      ])
    } catch (error) {
      console.error('Erro ao carregar dados:', error)
    } finally {
      this.isLoading = false
    }
  },

  mounted() {
    // Start database connection check
    this.startDatabaseCheck()
  },

  beforeDestroy() {
    // Limpar o intervalo quando o componente for destruído
    if (this.databaseCheckInterval) {
      clearInterval(this.databaseCheckInterval)
    }
  },

  computed: {
    ...mapGetters('projects', ['project']),
    
    projectId(): string {
      return this.$route.params.id
    },

    exampleId(): string {
      return this.$route.params.exampleId
    },

    filteredMessages() {
      if (this.selectedUserFilter === 'all') {
        return this.discussionMessages
      } else {
        return this.discussionMessages.filter(msg => msg.user === this.selectedUserFilter)
      }
    },

    userFilterOptions() {
      const uniqueUsers = [...new Set(this.discussionMessages.map(msg => msg.user))]
        .filter(user => user && user.trim() !== '')
        .sort()
      
      const options = [{ label: 'Todos os utilizadores', value: 'all' }]
      
      uniqueUsers.forEach(user => {
        options.push({
          label: user,
          value: user
        })
      })
      
      return options
    }
  },

  methods: {
    goBack() {
      // Voltar para a página de discrepâncias do projeto
      this.$router.push(`/projects/${this.projectId}/discrepancies`)
    },

    async loadExampleData() {
      try {
        // Carregar dados do exemplo das métricas
        let percentages = {}
        
        const project = (this as any).project
        if (project && project.canDefineCategory) {
          percentages = await this.$repositories.metrics.fetchCategoryPercentage(this.projectId)
        } else if (project && project.canDefineSpan) {
          percentages = await this.$repositories.metrics.fetchSpanPercentage(this.projectId)
        } else if (project && project.canDefineRelation) {
          percentages = await this.$repositories.metrics.fetchRelationPercentage(this.projectId)
        }

        const examplePercentages = (percentages as any)[this.exampleId] || {}
        if (Object.keys(examplePercentages).length > 0) {
          const maxPercentage = Math.max(...Object.values(examplePercentages) as number[])
          
          // Buscar texto do exemplo
          const example = await this.$repositories.example.findById(this.projectId, parseInt(this.exampleId))
          
          this.exampleData = {
            id: this.exampleId,
            text: example.text || `Exemplo ${this.exampleId}`,
            hasDiscrepancy: maxPercentage < (((this as any).project)?.minPercentage || 80),
            maxPercentage: Math.round(maxPercentage),
            labelPercentages: examplePercentages
          }
        }
      } catch (error) {
        console.error('Erro ao carregar dados do exemplo:', error)
      }
    },

    async loadAnnotations() {
      try {
        console.log('Carregando anotações para exemplo:', this.exampleId)
        
        const allAnnotations: any[] = []
        
        // Carregar anotações diretamente da API sem filtros do repositório
        try {
          // Fazer query direta para anotações categóricas
          const categoryResponse = await this.$repositories.category.request.get(
            `/projects/${this.projectId}/examples/${this.exampleId}/categories?show_all=true`
          )
          const categoryTypes = await this.$services.categoryType.list(this.projectId)
          
          console.log('Anotações categóricas encontradas:', categoryResponse.data.length)
          console.log('Dados das anotações categóricas:', categoryResponse.data)
          
          for (const annotation of categoryResponse.data) {
            const labelType = categoryTypes.find((type: any) => type.id === annotation.label)
            allAnnotations.push({
              user: annotation.username || annotation.user?.toString() || 'Unknown',
              created_at: annotation.created_at || new Date().toISOString(),
              labelId: annotation.label,
              labelName: labelType ? (labelType.text || (labelType as any).name || `Label ${annotation.label}`) : `Label ${annotation.label}`,
              type: 'category'
            })
          }
        } catch (error) {
          console.log('Erro ao carregar anotações categóricas:', error)
        }

        // Carregar anotações de span
        try {
          const spanResponse = await this.$repositories.span.request.get(
            `/projects/${this.projectId}/examples/${this.exampleId}/spans?show_all=true`
          )
          const spanTypes = await this.$services.spanType.list(this.projectId)
          
          console.log('Anotações de span encontradas:', spanResponse.data.length)
          console.log('Dados das anotações de span:', spanResponse.data)
          
          for (const annotation of spanResponse.data) {
            const labelType = spanTypes.find(type => type.id === annotation.label)
            allAnnotations.push({
              user: annotation.username || annotation.user?.toString() || 'Unknown',
              created_at: annotation.created_at || new Date().toISOString(),
              labelId: annotation.label,
              labelName: labelType ? (labelType.text || (labelType as any).name || `Label ${annotation.label}`) : `Label ${annotation.label}`,
              type: 'span'
            })
          }
        } catch (error) {
          console.log('Erro ao carregar anotações de span:', error)
        }

        // Carregar anotações de relação
        try {
          const relationResponse = await this.$repositories.relation.request.get(
            `/projects/${this.projectId}/examples/${this.exampleId}/relations?show_all=true`
          )
          const relationTypes = await this.$services.relationType.list(this.projectId)
          
          console.log('Anotações de relação encontradas:', relationResponse.data.length)
          console.log('Dados das anotações de relação:', relationResponse.data)
          
          for (const annotation of relationResponse.data) {
            const labelType = relationTypes.find(type => type.id === annotation.type)
            allAnnotations.push({
              user: annotation.username || annotation.user?.toString() || 'Unknown',
              created_at: annotation.created_at || new Date().toISOString(),
              labelId: annotation.type,
              labelName: labelType ? (labelType.text || (labelType as any).name || `Label ${annotation.type}`) : `Label ${annotation.type}`,
              type: 'relation'
            })
          }
        } catch (error) {
          console.log('Erro ao carregar anotações de relação:', error)
        }

        console.log('Total de anotações encontradas:', allAnnotations.length)
        console.log('Anotações detalhadas:', allAnnotations)

        // Agrupar por utilizador
        const userAnnotations: any = {}
        
        for (const annotation of allAnnotations) {
          const username = annotation.user
          if (!userAnnotations[username]) {
            userAnnotations[username] = {
              annotator: username,
              createdAt: annotation.created_at,
              labels: []
            }
          }
          
          // Verificar se a label já existe para evitar duplicatas
          const existingLabel = userAnnotations[username].labels.find(
            (label: any) => label.id === annotation.labelId.toString() && label.type === annotation.type
          )
          
          if (!existingLabel) {
            userAnnotations[username].labels.push({
              id: annotation.labelId.toString(),
              name: annotation.labelName,
              type: annotation.type
            })
          }
        }

        this.annotations = Object.values(userAnnotations)
        console.log('Anotações agrupadas por utilizador:', this.annotations)
        
        // Se não houver anotações, mostrar mensagem informativa
        if (this.annotations.length === 0) {
          console.log('Nenhuma anotação encontrada para o exemplo', this.exampleId)
        }
      } catch (error) {
        console.error('Erro ao carregar anotações:', error)
        this.annotations = []
      }
    },

    async loadMessages() {
      try {
        console.log('Carregando mensagens...')
        const messages = await this.$repositories.discrepancy.fetchMessages(
          this.projectId,
          this.exampleId
        )
        
        console.log('Resposta da API (tipo):', typeof messages)
        console.log('Resposta da API (valor):', messages)
        
        if (Array.isArray(messages) && messages.length > 0) {
          this.discussionMessages = messages.map((msg) => {
            console.log('Processando mensagem:', msg)
            return {
              id: msg.id || 0,
              user: msg.user || 'Unknown user',
              text: msg.text || '',
              created_at: msg.created_at || new Date().toISOString()
            }
          })
          console.log('Mensagens processadas:', this.discussionMessages)
          console.log('Número de mensagens:', this.discussionMessages.length)
          
          // Resetar filtro se o utilizador selecionado não existe mais
          const uniqueUsers = [...new Set(this.discussionMessages.map(msg => msg.user))]
          if (this.selectedUserFilter !== 'all' && !uniqueUsers.includes(this.selectedUserFilter)) {
            this.selectedUserFilter = 'all'
          }
        } else {
          console.warn('Nenhuma mensagem encontrada ou resposta inválida:', messages)
          this.discussionMessages = []
          this.selectedUserFilter = 'all'
        }
      } catch (error) {
        console.error('Erro ao carregar mensagens:', error)
        this.discussionMessages = []
        this.selectedUserFilter = 'all'
      }
    },

    async sendMessage() {
      if (!this.newMessage || this.isSendingMessage) return
      
      this.isSendingMessage = true
      try {
        const msg = await this.$repositories.discrepancy.sendMessage(
          this.projectId,
          this.exampleId,
          this.newMessage
        )
        
        // Garante que a mensagem tenha todas as propriedades necessárias
        if (msg && typeof msg === 'object') {
          const newMsg = {
            id: msg.id || 0,
            user: msg.user || this.$store.getters['auth/getUsername'],
            text: msg.text || this.newMessage,
            created_at: msg.created_at || new Date().toISOString()
          }
          this.discussionMessages.push(newMsg)
        }
        
        this.newMessage = ''
        this.$nextTick(() => {
          const container = this.$refs.messagesContainer as HTMLElement
          if (container) {
            container.scrollTop = container.scrollHeight
          }
        })
      } catch (error) {
        console.error('Erro ao enviar mensagem:', error)
        alert('Erro ao enviar mensagem. Tente novamente.')
      } finally {
        this.isSendingMessage = false
      }
    },

    getPercentageColor(percentage: number): string {
      const project = this.$store.getters['projects/project']
      if (percentage < (project?.minPercentage || 80)) return 'error'
      if (percentage < 70) return 'warning'
      return 'success'
    },

    getUserColor(username: string): string {
      let hash = 0
      for (let i = 0; i < username.length; i++) {
        hash = username.charCodeAt(i) + ((hash << 5) - hash)
      }
      return this.userColors[Math.abs(hash) % this.userColors.length]
    },

    getInitials(name: string): string {
      return name.split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .substring(0, 2)
    },

    formatDate(dateString: string): string {
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)

      if (diffMins < 1) return 'agora'
      if (diffMins < 60) return `${diffMins}m atrás`
      if (diffHours < 24) return `${diffHours}h atrás`
      if (diffDays < 7) return `${diffDays}d atrás`
      
      return date.toLocaleDateString('pt-PT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    getLabelColor(labelName: string): string {
      const colors = ['primary', 'secondary', 'accent', 'error', 'info', 'success', 'warning']
      const hash = labelName.split('').reduce((a, b) => a + b.charCodeAt(0), 0)
      return colors[hash % colors.length]
    },

    getAnnotationBackgroundClass(index: number): string {
      const classes = ['bg-blue-lighten-5', 'bg-green-lighten-5', 'bg-orange-lighten-5']
      return classes[index % classes.length] || 'bg-grey-lighten-5'
    },

    closeDiscussion() {
      this.goBack()
    },

    // Database connection check methods
    startDatabaseCheck() {
      this.databaseCheckInterval = setInterval(async () => {
        try {
          // Fazer uma chamada simples para verificar se a database está disponível
          await this.$repositories.member.fetchMyRole(this.projectId)
          
          // Se chegou até aqui, a database está funcionando
          if (this.databaseError) {
            this.databaseError = false
          }
        } catch (error: any) {
          console.error('Erro na verificação da database:', error)
          
          // Verificar diferentes tipos de erro que indicam problemas de base de dados
          if (error.response && error.response.status >= 500) {
            this.databaseError = true
          } else if (error.code === 'NETWORK_ERROR' || !error.response) {
            this.databaseError = true
          } else if (error.response && (error.response.status === 503 || error.response.status === 502 || error.response.status === 504)) {
            this.databaseError = true
          }
        }
      }, 2000) // Verificar a cada 2 segundos
    }
  }
})
</script>

<style scoped>
.example-text-container {
  background-color: #f8f9fa;
  border-left: 4px solid #2196f3;
  border-radius: 4px;
  padding: 16px;
}

.example-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #333;
  margin: 0;
  font-style: italic;
}

.label-percentages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.label-percentage-item {
  background-color: #fafafa;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #e0e0e0;
}

.percentage-value {
  font-weight: bold;
  font-size: 0.9rem;
}

.user-annotation-card {
  transition: transform 0.2s ease-in-out;
}

.user-annotation-card:hover {
  transform: translateY(-2px);
}

.bg-blue-lighten-5 {
  background-color: #e3f2fd;
}

.bg-green-lighten-5 {
  background-color: #e8f5e8;
}

.bg-orange-lighten-5 {
  background-color: #fff3e0;
}

.messages-container {
  max-height: 400px;
  overflow-y: auto;
  padding: 16px;
  background-color: #fafafa;
}

.message-item {
  background-color: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  animation: fadeInUp 0.3s ease-out;
  transition: all 0.2s ease;
}

.message-item:last-child {
  margin-bottom: 0;
}

.message-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  transform: translateY(-1px);
}

/* Destaque para mensagens filtradas */
.message-filtered {
  border-left: 4px solid #2196f3;
  background-color: #f8fafe;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scrollbar personalizada */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 