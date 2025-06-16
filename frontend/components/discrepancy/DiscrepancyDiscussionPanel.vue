<template>
  <v-card class="d-flex flex-column" height="100%">
    <v-card-title class="headline primary white--text">
      <v-icon dark class="mr-2">mdi-chat-processing</v-icon>
      Discussão de Discrepância
    </v-card-title>
    
    <v-card-subtitle class="primary white--text pb-2">
      <div class="d-flex align-center">
        <v-icon small class="mr-1">mdi-file-document</v-icon>
        Documento: {{ discrepancyContext.docId }}
        <v-spacer></v-spacer>
        <v-chip x-small outlined color="white">
          {{ participantCount }} participante(s)
        </v-chip>
      </div>
    </v-card-subtitle>

    <v-divider />

    <!-- Resumo da Discrepância -->
    <v-card-text v-if="discrepancyContext.annotation" class="pa-3">
      <div class="text-caption text--secondary mb-1">RESUMO DA DISCREPÂNCIA</div>
      <div class="text-body-2">
        <strong>Tipo:</strong> {{ getDiscrepancyTypeLabel(discrepancyContext.annotation.type) }}
        <br>
        <strong>Anotadores Envolvidos:</strong> 
        <span v-for="(annotator, index) in discrepancyContext.involvedAnnotators" :key="annotator.value">
          {{ annotator.text }}<span v-if="index < discrepancyContext.involvedAnnotators.length - 1">, </span>
        </span>
      </div>
    </v-card-text>

    <v-divider />

    <!-- Seção de Votação -->
    <v-expansion-panels v-if="showVotingSection" flat>
      <v-expansion-panel>
        <v-expansion-panel-header>
          <div class="d-flex align-center">
            <v-icon class="mr-2">mdi-vote</v-icon>
            <span>Consensus Voting</span>
            <v-spacer></v-spacer>
            <v-chip x-small :color="getVotingStatusColor()" outlined>
              {{ getVotingStatusText() }}
            </v-chip>
          </div>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <div v-if="!hasUserVoted" class="mb-3">
            <v-select
              v-model="selectedVote"
              :items="voteOptions"
              label="Select your option"
              outlined
              dense
              hide-details
            />
            <v-btn
              color="primary"
              small
              class="mt-2"
              :disabled="!selectedVote"
              @click="submitVote"
            >
              <v-icon left small>mdi-vote</v-icon>
              Vote
            </v-btn>
          </div>
          
          <div v-if="votingResults.length > 0">
            <div class="text-subtitle-2 mb-2">Voting Results:</div>
            <div v-for="result in votingResults" :key="result.option" class="d-flex align-center mb-1">
              <v-chip x-small :color="result.color" class="mr-2">{{ result.votes }}</v-chip>
              <span class="text-body-2">{{ result.option }}</span>
              <v-progress-linear
                :value="result.percentage"
                :color="result.color"
                class="ml-2"
                height="4"
                style="flex-grow: 1;"
              />
            </div>
          </div>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>

    <!-- Seção de Proposta de Consenso -->
    <v-expansion-panels v-if="showConsensusSection" flat>
      <v-expansion-panel>
        <v-expansion-panel-header>
          <div class="d-flex align-center">
            <v-icon class="mr-2">mdi-handshake</v-icon>
            <span>Consensus Proposal</span>
          </div>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-select
            v-model="selectedConsensusLabel"
            :items="consensusLabelOptions"
            label="Proposed Consensus Label"
            outlined
            dense
            hide-details
            class="mb-2"
          />
          <v-textarea
            v-model="consensusJustification"
            label="Justification (optional)"
            outlined
            dense
            rows="2"
            hide-details
            class="mb-2"
          />
          <v-btn
            color="success"
            small
            :disabled="!selectedConsensusLabel"
            @click="proposeConsensus"
          >
            <v-icon left small>mdi-handshake</v-icon>
            Propose Consensus
          </v-btn>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>

    <v-divider />

    <!-- Mensagens de Discussão -->
    <v-card-text class="flex-grow-1 overflow-y-auto pa-3" style="max-height: 300px;">
      <div v-if="isLoading" class="text-center pa-4">
        <v-progress-circular indeterminate color="primary" size="24"></v-progress-circular>
        <div class="text-caption mt-2">Loading messages...</div>
      </div>
      <div v-else-if="messages.length === 0" class="text-center pa-4">
        <v-icon color="grey lighten-1">mdi-chat-outline</v-icon>
        <div class="text-body-2 mt-2">No messages yet.</div>
        <div class="text-caption text--secondary">Start the discussion below!</div>
      </div>
      <div v-else>
        <div v-for="msg in messages" :key="msg.id" class="message-item mb-3">
          <div class="d-flex align-start">
            <v-avatar size="32" :color="getUserColor(msg.user)" class="mr-2">
              <span class="white--text text-caption font-weight-bold">
                {{ msg.user[0].toUpperCase() }}
              </span>
            </v-avatar>
            <div class="flex-grow-1">
              <div class="d-flex align-center">
                <span class="text-subtitle-2 font-weight-bold">{{ msg.user }}</span>
                <v-spacer></v-spacer>
                <span class="text-caption text--secondary">{{ formatDate(msg.created_at) }}</span>
              </div>
                             <!-- eslint-disable-next-line vue/no-v-html -->
               <div class="text-body-2 mt-1" v-html="formatMessage(msg.text)"></div>
              <div v-if="msg.type === 'vote'" class="mt-1">
                <v-chip x-small color="primary" outlined>
                  <v-icon left x-small>mdi-vote</v-icon>
                  Vote: {{ msg.voteOption }}
                </v-chip>
              </div>
              <div v-if="msg.type === 'consensus'" class="mt-1">
                <v-chip x-small color="success" outlined>
                  <v-icon left x-small>mdi-handshake</v-icon>
                  Consensus Proposal
                </v-chip>
              </div>
            </div>
          </div>
        </div>
      </div>
    </v-card-text>

    <v-divider />

    <!-- Entrada de Nova Mensagem -->
    <v-card-actions class="pa-3">
      <v-textarea
        v-model="newMessage"
        label="Write your message..."
        rows="2"
        outlined
        dense
        hide-details
        class="mr-2"
        @keydown.ctrl.enter="sendMessage"
        @keydown.meta.enter="sendMessage"
      />
      <div class="d-flex flex-column">
        <v-btn
          fab
          x-small
          color="primary"
          :loading="isSending"
          :disabled="!newMessage.trim()"
          @click="sendMessage"
          class="mb-1"
        >
          <v-icon small>mdi-send</v-icon>
        </v-btn>
                 <v-tooltip bottom>
           <template #activator="{ on, attrs }">
            <v-btn
              fab
              x-small
              color="grey lighten-1"
              v-bind="attrs"
              v-on="on"
              @click="showEmojiPicker = !showEmojiPicker"
            >
              <v-icon small>mdi-emoticon</v-icon>
            </v-btn>
          </template>
          <span>Add emoji</span>
        </v-tooltip>
      </div>
    </v-card-actions>

    <!-- Picker de Emoji -->
    <v-card v-if="showEmojiPicker" class="emoji-picker pa-2">
      <div class="d-flex flex-wrap">
        <v-btn
          v-for="emoji in commonEmojis"
          :key="emoji"
          text
          x-small
          class="ma-1"
          @click="addEmoji(emoji)"
        >
          {{ emoji }}
        </v-btn>
      </div>
    </v-card>

    <!-- Ações Finais -->
    <v-divider />
    <v-card-actions class="justify-space-between pa-3">
      <div>
        <v-btn
          text
          small
          color="grey"
          :loading="isRefreshing"
          @click="refreshMessages"
        >
          <v-icon left small>mdi-refresh</v-icon>
          Atualizar
        </v-btn>
      </div>
      <div>
        <v-btn
          color="success"
          :disabled="!canResolve"
          @click="confirmResolution"
        >
          <v-icon left>mdi-check-circle</v-icon>
          Marcar como Resolvido
        </v-btn>
      </div>
    </v-card-actions>

    <!-- Diálogo de Confirmação -->
    <v-dialog v-model="showResolutionDialog" max-width="400">
      <v-card>
        <v-card-title>
          <v-icon class="mr-2" color="success">mdi-check-circle</v-icon>
          Confirmar Resolução
        </v-card-title>
        <v-card-text>
          Tem certeza que deseja marcar esta discrepância como resolvida?
          <br><br>
          <strong>Esta ação não pode ser desfeita.</strong>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showResolutionDialog = false">Cancelar</v-btn>
          <v-btn color="success" @click="markAsResolved">Confirmar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import type { PropType } from 'vue'
import { mapGetters } from 'vuex'

interface DiscrepancyContext {
  docId: number
  annotation?: any
  text?: string
  involvedAnnotators?: any[]
}

interface DiscrepancyMessage {
  id: number
  user: string
  text: string
  created_at: string
  type?: 'message' | 'vote' | 'consensus'
  voteOption?: string
  consensusData?: any
}

interface VotingResult {
  option: string
  votes: number
  percentage: number
  color: string
}

export default Vue.extend({
  name: 'DiscrepancyDiscussionPanel',

  props: {
    discrepancyContext: {
      type: Object as PropType<DiscrepancyContext>,
      required: true
    },
    projectMembers: {
      type: Array,
      default: () => []
    }
  },

  data() {
    return {
      messages: [] as DiscrepancyMessage[],
      newMessage: '',
      isLoading: false,
      isSending: false,
      isRefreshing: false,
      polling: null as any,
      canResolve: false,
      
      // Votação
      showVotingSection: true,
      selectedVote: null,
      voteOptions: [
        { text: 'Manter anotação do Anotador 1', value: 'annotator_1' },
        { text: 'Manter anotação do Anotador 2', value: 'annotator_2' },
        { text: 'Criar nova anotação consensual', value: 'consensus' },
        { text: 'Remover anotação completamente', value: 'remove' }
      ],
      votes: {},
      hasUserVoted: false,
      
      // Consenso
      showConsensusSection: true,
      selectedConsensusLabel: null,
      consensusJustification: '',
      consensusLabelOptions: [],
      
      // UI
      showEmojiPicker: false,
      showResolutionDialog: false,
      commonEmojis: ['👍', '👎', '❤️', '😄', '😮', '😢', '😡', '🤔', '✅', '❌', '⚠️', '💡'],
      
      // Cores dos usuários
      userColors: ['blue', 'green', 'purple', 'orange', 'red', 'teal', 'pink', 'indigo']
    }
  },

  computed: {
    ...mapGetters('projects', ['project']),
    
    projectId(): string {
      return this.project.id
    },
    
    participantCount(): number {
      const uniqueUsers = new Set(this.messages.map(m => m.user))
      return uniqueUsers.size
    },
    
    votingResults(): VotingResult[] {
      if (!this.votes || Object.keys(this.votes).length === 0) return []
      
      const totalVotes = Object.values(this.votes).reduce((sum: number, count: any) => sum + count, 0)
      const colors = ['primary', 'success', 'warning', 'error']
      
      return Object.entries(this.votes)
        .map(([option, votes], index) => ({
          option: this.getVoteOptionLabel(option),
          votes: votes as number,
          percentage: totalVotes > 0 ? ((votes as number) / totalVotes) * 100 : 0,
          color: colors[index % colors.length]
        }))
        .sort((a, b) => b.votes - a.votes)
    }
  },

  watch: {
    discrepancyContext: {
      handler: 'initialize',
      immediate: true,
      deep: true
    }
  },

  async created() {
    await this.checkPermissions()
    await this.loadConsensusOptions()
  },

  mounted() {
    this.setupPolling()
  },

  beforeDestroy() {
    this.cleanupPolling()
  },

  methods: {
    async initialize() {
      if (!this.discrepancyContext) return
      
      await this.fetchMessages()
      this.fetchVotingData()
      this.updateVoteOptions()
    },

    async fetchMessages() {
      if (!this.discrepancyContext) return
      
      this.isLoading = true
      try {
        const allMessages = await this.$repositories.discrepancy.fetchMessages(this.projectId)
        
        // Filter messages for the current context
        const contextPrefix = `[Doc: ${this.discrepancyContext.docId}]`
        this.messages = allMessages
          .filter((msg: DiscrepancyMessage) => msg.text.startsWith(contextPrefix))
          .map((msg: DiscrepancyMessage) => ({
            ...msg,
            text: msg.text.substring(contextPrefix.length).trim(),
            type: this.detectMessageType(msg.text)
          }))
          .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())

      } catch (error) {
        console.error('Erro ao buscar mensagens:', error)
      } finally {
        this.isLoading = false
      }
    },

    fetchVotingData() {
      // Simular dados de votação - em implementação real, buscar do backend
      this.votes = {
        'annotator_1': 2,
        'annotator_2': 1,
        'consensus': 3,
        'remove': 0
      }
      
      // Verificar se usuário atual já votou
      const currentUser = 'current_user' // Pegar do contexto/auth
      this.hasUserVoted = this.messages.some(m => m.user === currentUser && m.type === 'vote')
    },

    async sendMessage() {
      if (!this.newMessage.trim() || !this.discrepancyContext) return
      
      this.isSending = true
      const contextPrefix = `[Doc: ${this.discrepancyContext.docId}]`
      const messageText = `${contextPrefix} ${this.newMessage}`

      try {
        await this.$repositories.discrepancy.postMessage(this.projectId, messageText)
        this.newMessage = ''
        this.showEmojiPicker = false
        await this.fetchMessages()
      } catch (error) {
        console.error('Error sending message:', error)
      } finally {
        this.isSending = false
      }
    },

    async submitVote() {
      if (!this.selectedVote || !this.discrepancyContext) return
      
      try {
        const voteMessage = `[Doc: ${this.discrepancyContext.docId}] [VOTE:${this.selectedVote}] Votou em: ${this.getVoteOptionLabel(this.selectedVote)}`
        await this.$repositories.discrepancy.postMessage(this.projectId, voteMessage)
        
        this.hasUserVoted = true
        this.selectedVote = null
        await this.fetchMessages()
        this.fetchVotingData()
        
        this.$emit('vote-submitted', {
          docId: this.discrepancyContext.docId,
          vote: this.selectedVote
        })
      } catch (error) {
        console.error('Erro ao submeter voto:', error)
      }
    },

    async proposeConsensus() {
      if (!this.selectedConsensusLabel || !this.discrepancyContext) return
      
      try {
        let consensusText = `[Doc: ${this.discrepancyContext.docId}] [CONSENSUS:${this.selectedConsensusLabel}] Proposta de consenso: ${this.selectedConsensusLabel}`
        if (this.consensusJustification) {
          consensusText += ` - Justificação: ${this.consensusJustification}`
        }
        
        await this.$repositories.discrepancy.postMessage(this.projectId, consensusText)
        
        this.selectedConsensusLabel = null
        this.consensusJustification = ''
        await this.fetchMessages()
        
        this.$emit('consensus-proposed', {
          docId: this.discrepancyContext.docId,
          label: this.selectedConsensusLabel,
          justification: this.consensusJustification
        })
      } catch (error) {
        console.error('Erro ao propor consenso:', error)
      }
    },

    confirmResolution() {
      this.showResolutionDialog = true
    },

    async markAsResolved() {
      if (!this.discrepancyContext) return
      
      try {
        await this.$repositories.example.confirm(this.projectId, this.discrepancyContext.docId)
        
        // Post system message
        const systemMessage = `[Doc: ${this.discrepancyContext.docId}] [SYSTEM] Marcado como resolvido.`
        await this.$repositories.discrepancy.postMessage(this.projectId, systemMessage)
        
        this.showResolutionDialog = false
        this.$emit('resolved', this.discrepancyContext)
      } catch (error) {
        console.error('Erro ao marcar como resolvido:', error)
      }
    },

    async refreshMessages() {
      this.isRefreshing = true
      await this.fetchMessages()
      this.fetchVotingData()
      this.isRefreshing = false
    },

    async checkPermissions() {
      try {
        const role = await this.$repositories.member.fetchMyRole(this.projectId)
        this.canResolve = role.isProjectAdmin || role.isProjectManager
      } catch (error) {
        console.error('Erro ao verificar permissões:', error)
        this.canResolve = false
      }
    },

    async loadConsensusOptions() {
      try {
        const categories = await this.$repositories.categoryType.list(this.projectId)
        this.consensusLabelOptions = categories.map((cat: any) => ({
          text: cat.text,
          value: cat.id
        }))
      } catch (error) {
        console.error('Erro ao carregar opções de consenso:', error)
      }
    },

    updateVoteOptions() {
      if (this.discrepancyContext.involvedAnnotators && this.discrepancyContext.involvedAnnotators.length >= 2) {
        this.voteOptions = this.discrepancyContext.involvedAnnotators.map((annotator, index) => ({
          text: `Manter anotação de ${annotator.text}`,
          value: `annotator_${index + 1}`
        })).concat([
          { text: 'Criar nova anotação consensual', value: 'consensus' },
          { text: 'Remover anotação completamente', value: 'remove' }
        ])
      }
    },

    detectMessageType(text: string): 'message' | 'vote' | 'consensus' {
      if (text.includes('[VOTE:')) return 'vote'
      if (text.includes('[CONSENSUS:')) return 'consensus'
      return 'message'
    },

    getDiscrepancyTypeLabel(type: string): string {
      const labels = {
        'etiqueta-diferente': 'Etiqueta Diferente',
        'span-diferente': 'Span Diferente',
        'etiqueta-ausente': 'Etiqueta Ausente',
        'none': 'Sem Discrepância'
      }
      return labels[type] || type || 'Desconhecido'
    },

    getVoteOptionLabel(value: string): string {
      const option = this.voteOptions.find(opt => opt.value === value)
      return option ? option.text : value
    },

    getVotingStatusColor(): string {
      const total = Object.values(this.votes).reduce((sum: number, count: any) => sum + count, 0)
      if (total === 0) return 'grey'
      if (total < 3) return 'warning'
      return 'success'
    },

    getVotingStatusText(): string {
      const total = Object.values(this.votes).reduce((sum: number, count: any) => sum + count, 0)
      if (total === 0) return 'Sem votos'
      return `${total} voto${total > 1 ? 's' : ''}`
    },

    getUserColor(username: string): string {
      const hash = username.split('').reduce((a, b) => {
        a = ((a << 5) - a) + b.charCodeAt(0)
        return a & a
      }, 0)
      return this.userColors[Math.abs(hash) % this.userColors.length]
    },

    addEmoji(emoji: string) {
      this.newMessage += emoji
      this.showEmojiPicker = false
    },

    formatMessage(text: string): string {
      // Remove prefixos de sistema
      let formatted = text.replace(/\[VOTE:.*?\]/g, '').replace(/\[CONSENSUS:.*?\]/g, '').replace(/\[SYSTEM\]/g, '')
      
      // Destaca menções (@usuario)
      formatted = formatted.replace(/@(\w+)/g, '<strong class="primary--text">@$1</strong>')
      
      // Adiciona quebras de linha
      formatted = formatted.replace(/\n/g, '<br>')
      
      return formatted.trim()
    },

    formatDate(dateString: string): string {
      if (!dateString) return ''
      const date = new Date(dateString)
      const now = new Date()
      const diff = now.getTime() - date.getTime()
      
      if (diff < 60000) return 'agora'
      if (diff < 3600000) return `${Math.floor(diff / 60000)}min`
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`
      
      return date.toLocaleDateString('pt-PT', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    setupPolling() {
      this.polling = setInterval(() => {
        this.refreshMessages()
      }, 10000) // Atualizar a cada 10 segundos
    },

    cleanupPolling() {
      if (this.polling) {
        clearInterval(this.polling)
      }
    }
  }
})
</script>

<style scoped>
.overflow-y-auto {
  overflow-y: auto;
}

.message-item {
  transition: background-color 0.2s ease;
}

.message-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
  padding: 4px;
  margin: -4px;
}

.emoji-picker {
  position: absolute;
  bottom: 120px;
  right: 8px;
  z-index: 1000;
  max-width: 200px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 12px 16px;
}

.v-expansion-panel >>> .v-expansion-panel-header {
  min-height: 40px;
  padding: 8px 16px;
}

/* Animações suaves */
.v-expansion-panel {
  transition: all 0.3s ease;
}

.v-chip {
  transition: all 0.2s ease;
}

.v-btn {
  transition: all 0.2s ease;
}

/* Scrollbar personalizada */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style> 