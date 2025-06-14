<template>
  <v-container fluid class="pa-8">
    <!-- Header elegante -->
    <div class="mb-8">
      <h1 class="text-h4 font-weight-bold primary--text mb-2">
        Regras de Anotação
      </h1>
      <p class="text-subtitle-1 grey--text text--darken-1">
        Os utilizadores podem votar nas regras de anotação do projeto.
      </p>
    </div>

    <!-- Estado da discussão -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-alert
          v-if="!isDiscussionEnded"
          type="info"
          text
          prominent
          border="left"
          class="mb-4"
        >
          <div class="d-flex align-center">
            <v-icon left color="info">mdi-information</v-icon>
            <div>
              <div class="font-weight-medium">Discussão em Andamento</div>
              <div class="text-caption mt-1">
                Antes de configurar uma votação, é necessário que a discussão sobre discrepâncias seja finalizada.
                Acesse a página de <router-link :to="`/projects/${projectId}/discrepancies`" class="font-weight-medium">discrepâncias</router-link> para participar.
              </div>
            </div>
          </div>
        </v-alert>
        
        <v-alert
          v-else-if="hasActiveVoting"
          type="warning"
          text
          prominent
          border="left"
          class="mb-4"
        >
          <div class="d-flex align-center">
            <v-icon left color="warning">mdi-vote</v-icon>
            <div>
              <div class="font-weight-medium">Votação em Andamento</div>
              <div class="text-caption mt-1">
                Já existe uma votação em curso. Aguarde o término da votação atual antes de configurar uma nova.
              </div>
            </div>
          </div>
        </v-alert>
        
        <v-alert
          v-else
          type="success"
          text
          prominent
          border="left"
          class="mb-4"
        >
          <div class="d-flex align-center">
            <v-icon left color="success">mdi-check-circle</v-icon>
            <div>
              <div class="font-weight-medium">Pronto para Votar</div>
              <div class="text-caption mt-1">
                A discussão foi finalizada. Pode configurar uma nova votação.
              </div>
            </div>
          </div>
        </v-alert>
      </v-col>
    </v-row>

    <!-- Botão de configuração (apenas para administradores) -->
    <v-row v-if="canConfigureVoting" class="mb-6">
      <v-col cols="12" class="text-right">
        <v-btn 
          color="primary" 
          large
          elevation="2"
          :disabled="!isDiscussionEnded || hasActiveVoting" 
          @click="showVotingConfig = true"
        >
          <v-icon left>mdi-cog</v-icon>
          Configurar Nova Votação
        </v-btn>
      </v-col>
    </v-row>

    <!-- Votação ativa -->
    <div v-if="activeVoting">
      <v-card elevation="4" class="mb-8">
        <v-card-title class="primary white--text d-flex align-center">
          <v-icon left color="white">mdi-poll</v-icon>
          <span class="text-h6">Votação em Andamento</span>
          <v-spacer></v-spacer>
          <v-btn 
            v-if="canConfigureVoting" 
            color="error" 
            outlined
            dark
            @click="confirmEndVoting = true"
          >
            <v-icon left small>mdi-stop</v-icon>
            Terminar Votação
          </v-btn>
        </v-card-title>
        
        <v-card-text class="pa-6">
          <!-- Informações da votação -->
          <v-row class="mb-4">
            <v-col cols="12" md="6">
              <div class="d-flex align-center mb-3">
                <v-icon color="primary" class="mr-3">mdi-calendar-start</v-icon>
                <div>
                  <div class="text-caption grey--text">Data de Início</div>
                  <div class="font-weight-medium">{{ formatDate(activeVoting.startDate) }}</div>
                </div>
              </div>
            </v-col>
            
            <v-col cols="12" md="6">
              <div class="d-flex align-center mb-3">
                <v-icon color="primary" class="mr-3">mdi-calendar-end</v-icon>
                <div>
                  <div class="text-caption grey--text">Data de Término</div>
                  <div class="font-weight-medium">{{ formatDate(activeVoting.endDate) }}</div>
                </div>
              </div>
            </v-col>
          </v-row>
          
          <div class="mb-6">
            <div class="text-caption grey--text mb-2">Descrição</div>
            <div class="text-body-1">{{ activeVoting.description }}</div>
          </div>

          <!-- Filtros melhorados -->
          <v-expansion-panels v-model="showFilters" class="mb-6">
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left color="primary">mdi-filter</v-icon>
                  <span class="font-weight-medium">Filtros Avançados</span>
                  <v-spacer></v-spacer>
                  <v-chip v-if="hasActiveFilters" small color="primary" outlined>
                    {{ activeFiltersCount }} filtro{{ activeFiltersCount > 1 ? 's' : '' }} ativo{{ activeFiltersCount > 1 ? 's' : '' }}
                  </v-chip>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-row>
                  <v-col cols="12" sm="6" md="3">
                    <v-text-field
                      v-model="filters.keyword"
                      label="Pesquisar"
                      dense
                      outlined
                      clearable
                      prepend-inner-icon="mdi-magnify"
                      hide-details
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-select
                      v-model="filters.voteStatus"
                      :items="voteStatusOptions"
                      label="Estado do Voto"
                      dense
                      outlined
                      clearable
                      hide-details
                    ></v-select>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-select
                      v-model="filters.voteResult"
                      :items="voteResultOptions"
                      label="Resultado Atual"
                      dense
                      outlined
                      clearable
                      hide-details
                    ></v-select>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-select
                      v-model="filters.sortBy"
                      :items="sortOptions"
                      label="Ordenar por"
                      dense
                      outlined
                      hide-details
                    ></v-select>
                  </v-col>
                </v-row>
                <v-row class="mt-3">
                  <v-col cols="12" class="text-right">
                    <v-btn
                      text
                      color="primary"
                      @click="resetFilters"
                    >
                      <v-icon left>mdi-refresh</v-icon>
                      Limpar Filtros
                    </v-btn>
                  </v-col>
                </v-row>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>

          <!-- Mensagem para administradores de projeto -->
          <v-alert
            v-if="isProjectAdmin"
            type="info"
            text
            prominent
            border="left"
            class="mb-6"
          >
            <div class="d-flex align-center">
              <v-icon left color="info">mdi-account-tie</v-icon>
              <div>
                <div class="font-weight-medium">Administrador do Projeto</div>
                <div class="text-caption mt-1">
                  Como administrador do projeto, não pode votar nas regras de anotação. Pode apenas configurar e gerir as votações.
                </div>
              </div>
            </div>
          </v-alert>

          <!-- Lista de regras moderna -->
          <div v-if="filteredRules.length > 0">
            <!-- Contador de regras -->
            <div class="d-flex align-center justify-space-between mb-4">
              <div class="text-subtitle-1 font-weight-medium">
                Regras em Votação
                <v-chip small color="primary" outlined class="ml-2">
                  {{ filteredRules.length }} de {{ activeVoting.rules.length }}
                </v-chip>
              </div>
            </div>

            <!-- Cards das regras -->
            <v-row>
              <v-col v-for="ruleId in filteredRules" :key="ruleId" cols="12">
                <v-card 
                  elevation="2" 
                  :class="[
                    'mb-4 transition-all',
                    { 'rule-voted': hasVotedForRule(ruleId) || pendingVotes[ruleId] }
                  ]"
                >
                  <v-card-text class="pa-6">
                    <v-row align="center">
                      <!-- Informações da regra -->
                      <v-col cols="12" md="8">
                        <div class="d-flex align-start mb-3">
                          <div class="flex-grow-1">
                            <h3 class="text-h6 font-weight-bold mb-2">
                              {{ getRuleName(ruleId) }}
                            </h3>
                            <p class="text-body-2 grey--text text--darken-1 mb-3">
                              {{ getRuleDescription(ruleId) }}
                            </p>
                            
                            <!-- Status chips -->
                            <div class="d-flex flex-wrap gap-2">
                              <v-chip
                                small
                                :color="hasVotedForRule(ruleId) || pendingVotes[ruleId] ? 'success' : 'grey'"
                                :outlined="!hasVotedForRule(ruleId) && !pendingVotes[ruleId]"
                              >
                                <v-icon left x-small>
                                  {{ hasVotedForRule(ruleId) || pendingVotes[ruleId] ? 'mdi-check' : 'mdi-circle-outline' }}
                                </v-icon>
                                {{ hasVotedForRule(ruleId) || pendingVotes[ruleId] ? 'Votado' : 'Pendente' }}
                              </v-chip>
                              
                              <v-chip
                                v-if="ruleCategory(ruleId)"
                                small
                                color="purple"
                                outlined
                              >
                                {{ ruleCategory(ruleId) }}
                              </v-chip>
                            </div>
                          </div>
                        </div>
                        
                        <!-- Estatísticas de votos -->
                        <div class="d-flex gap-4">
                          <div class="d-flex align-center">
                            <v-icon color="success" class="mr-2">mdi-thumb-up</v-icon>
                            <span class="font-weight-medium">{{ ruleVotes(ruleId).aprovar }} Aprovações</span>
                          </div>
                          <div class="d-flex align-center">
                            <v-icon color="error" class="mr-2">mdi-thumb-down</v-icon>
                            <span class="font-weight-medium">{{ ruleVotes(ruleId).rejeitar }} Rejeições</span>
                          </div>
                        </div>
                      </v-col>
                      
                      <!-- Área de votação -->
                      <v-col cols="12" md="4">
                        <div class="text-center">
                          <!-- Se pode votar e não votou ainda -->
                          <div v-if="canVote && !hasVotedForRule(ruleId)" class="voting-area">
                            <div class="mb-3">
                              <div class="text-caption grey--text mb-2">Seu Voto:</div>
                              <v-btn-toggle
                                :value="pendingVotes[ruleId] || null"
                                @change="setPendingVote(ruleId, $event)"
                                mandatory
                                borderless
                                color="primary"
                              >
                                <v-btn
                                  value="aprovar"
                                  :color="pendingVotes[ruleId] === 'aprovar' ? 'success' : ''"
                                  :outlined="pendingVotes[ruleId] !== 'aprovar'"
                                  class="mr-2"
                                >
                                  <v-icon left>mdi-thumb-up</v-icon>
                                  Aprovar
                                </v-btn>
                                <v-btn
                                  value="rejeitar"
                                  :color="pendingVotes[ruleId] === 'rejeitar' ? 'error' : ''"
                                  :outlined="pendingVotes[ruleId] !== 'rejeitar'"
                                >
                                  <v-icon left>mdi-thumb-down</v-icon>
                                  Rejeitar
                                </v-btn>
                              </v-btn-toggle>
                            </div>
                          </div>
                          
                          <!-- Se pode votar e já votou -->
                          <div v-else-if="canVote && hasVotedForRule(ruleId)" class="text-center">
                            <v-chip 
                              :color="getUserVoteForRule(ruleId) === 'aprovar' ? 'success' : 'error'"
                              large
                              class="white--text font-weight-bold"
                            >
                              <v-icon left>
                                {{ getUserVoteForRule(ruleId) === 'aprovar' ? 'mdi-thumb-up' : 'mdi-thumb-down' }}
                              </v-icon>
                              {{ getUserVoteForRule(ruleId) === 'aprovar' ? 'Aprovado' : 'Rejeitado' }}
                            </v-chip>
                          </div>
                          
                          <!-- Se é admin do projeto -->
                          <div v-else-if="isProjectAdmin" class="text-center">
                            <div class="pa-4">
                              <v-chip color="orange" outlined large class="mb-2">
                                <v-icon left>mdi-account-tie</v-icon>
                                Admin do Projeto
                              </v-chip>
                              <div class="text-caption grey--text">
                                Não pode votar
                              </div>
                            </div>
                          </div>
                          
                          <!-- Estado loading ou indefinido -->
                          <div v-else class="text-center">
                            <v-progress-circular indeterminate size="24"></v-progress-circular>
                            <div class="text-caption grey--text mt-2">Carregando...</div>
                          </div>
                        </div>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            
            <!-- Painel de submissão (apenas para anotadores) -->
            <div v-if="canVote" class="mt-8">
              <v-card color="grey lighten-5" elevation="0" class="pa-6">
                <v-row align="center">
                  <v-col cols="12" md="8">
                    <div class="d-flex align-center">
                      <v-icon 
                        :color="hasVotedAllRules ? 'success' : 'warning'" 
                        size="32" 
                        class="mr-4"
                      >
                        {{ hasVotedAllRules ? 'mdi-check-circle' : 'mdi-alert-circle' }}
                      </v-icon>
                      <div>
                        <div class="text-h6 font-weight-bold">
                          {{ hasVotedAllRules ? 'Votação Completa' : 'Votação Pendente' }}
                        </div>
                        <div class="text-body-2 grey--text">
                          <span v-if="remainingVotesCount > 0">
                            Faltam {{ remainingVotesCount }} {{ remainingVotesCount === 1 ? 'regra' : 'regras' }} para votar
                          </span>
                          <span v-else>
                            Todas as regras foram selecionadas. Pode submeter a votação.
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Barra de progresso -->
                    <v-progress-linear
                      :value="votingProgress"
                      color="primary"
                      height="12"
                      rounded
                      class="mt-4"
                    ></v-progress-linear>
                    
                    <div class="text-center text-caption mt-2 grey--text">
                      {{ activeVoting.rules.length - remainingVotesCount }} de {{ activeVoting.rules.length }} regras votadas
                    </div>
                  </v-col>
                  
                  <v-col cols="12" md="4" class="text-center">
                    <v-btn
                      color="primary"
                      x-large
                      :disabled="!hasVotedAllRules || isSubmittingVotes"
                      :loading="isSubmittingVotes"
                      @click="submitAllVotes"
                      elevation="4"
                    >
                      <v-icon left>mdi-send</v-icon>
                      Submeter Votação
                    </v-btn>
                  </v-col>
                </v-row>
              </v-card>
            </div>
          </div>
          
          <!-- Estado vazio -->
          <div v-else class="text-center py-12">
            <v-icon size="64" color="grey lighten-1" class="mb-4">mdi-filter-remove</v-icon>
            <h3 class="text-h6 grey--text mb-2">Nenhuma regra encontrada</h3>
            <p class="grey--text">Nenhuma regra corresponde aos filtros atuais</p>
            <v-btn text color="primary" class="mt-2" @click="resetFilters">
              Limpar filtros
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </div>

    <!-- Histórico de votações -->
    <div v-if="pastVotings.length > 0">
      <v-card elevation="2" class="mb-6">
        <v-card-title class="d-flex align-center">
          <v-icon left color="primary">mdi-history</v-icon>
          <span class="text-h6">Histórico de Votações</span>
        </v-card-title>
        <v-card-text>
          <v-expansion-panels multiple>
            <v-expansion-panel
              v-for="voting in pastVotings"
              :key="voting.id"
            >
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <div class="flex-grow-1">
                    <div class="font-weight-medium">{{ voting.description }}</div>
                    <div class="text-caption grey--text">
                      {{ formatDate(voting.startDate) }} - {{ formatDate(voting.endDate) }}
                    </div>
                  </div>
                  <v-chip v-if="voting.endedEarly" small color="orange" class="ml-2">
                    Terminada antecipadamente
                  </v-chip>
                </div>
              </v-expansion-panel-header>
              
              <v-expansion-panel-content>
                <div class="mt-4">
                  <h4 class="text-subtitle-1 font-weight-bold mb-4">Resultados da Votação</h4>
                  <div class="mb-4">
                    <v-chip 
                      v-for="ruleId in voting.rules"
                      :key="ruleId"
                      :color="isRuleApproved(ruleId) ? 'success' : 'error'"
                      class="mr-2 mb-2 white--text"
                    >
                      {{ getRuleName(ruleId) }}: {{ isRuleApproved(ruleId) ? 'Aprovada' : 'Rejeitada' }}
                    </v-chip>
                  </div>
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card-text>
      </v-card>
    </div>

    <!-- Modal de configuração de votação -->
    <VotingConfigModal
      v-model="showVotingConfig"
      :project-id="projectId"
      @saved="handleVotingSaved"
    />
    
    <!-- Dialog de confirmação para terminar votação -->
    <v-dialog v-model="confirmEndVoting" max-width="600">
      <v-card>
        <v-card-title class="text-h5 error--text">
          <v-icon left color="error">mdi-alert</v-icon>
          Confirmar Término da Votação
        </v-card-title>
        <v-card-text class="pt-4">
          <p class="text-body-1 mb-4">
            Tem a certeza que deseja terminar a votação atual antecipadamente? Esta ação não pode ser desfeita.
          </p>
          <v-alert type="warning" outlined dense>
            A votação será finalizada imediatamente e todos os votos serão contabilizados no estado atual.
          </v-alert>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn text large @click="confirmEndVoting = false">
            Cancelar
          </v-btn>
          <v-btn color="error" large @click="endVotingEarly">
            <v-icon left>mdi-stop</v-icon>
            Terminar Votação
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar para notificações -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      top
      right
    >
      {{ snackbar.text }}
      <template #action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="snackbar.show = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script>
import { mapGetters } from 'vuex'
import { mdiPoll } from '@mdi/js'
import VotingConfigModal from '~/components/voting/VotingConfigModal.vue'

export default {
  name: 'AnnotationRulesPage',
  
  components: {
    VotingConfigModal
  },

  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  validate({ params }) {
    return /^\d+$/.test(params.id)
  },

  data() {
    return {
      mdiPoll,
      project: {},
      showVotingConfig: false,
      confirmEndVoting: false,
      showFilters: null,
      snackbar: {
        show: false,
        text: '',
        color: 'success',
        timeout: 3000
      },
      isProjectAdmin: false,
      // Novo: armazenar votos temporários antes do submit
      pendingVotes: {},
      isSubmittingVotes: false,
      filters: {
        keyword: '',
        voteStatus: null,
        voteResult: null,
        category: null,
        sortBy: 'name-asc'
      },
      voteStatusOptions: [
        { text: 'Votado', value: 'voted' },
        { text: 'Não votado', value: 'not-voted' }
      ],
      voteResultOptions: [
        { text: 'Atualmente aprovado', value: 'approved' },
        { text: 'Atualmente rejeitado', value: 'rejected' },
        { text: 'Empatado', value: 'tied' }
      ],
      sortOptions: [
        { text: 'Nome (A-Z)', value: 'name-asc' },
        { text: 'Nome (Z-A)', value: 'name-desc' },
        { text: 'Mais aprovações', value: 'approvals-desc' },
        { text: 'Mais rejeições', value: 'rejections-desc' }
      ]
    }
  },
  
  computed: {
    isDiscussionEnded() {
      return this.$store.getters['discussion/isDiscussionEnded'](this.projectId)
    },
    ...mapGetters('voting', [
      'activeVoting', 
      'annotationRules', 
      'hasActiveVoting', 
      'ruleVotes',
      'hasUserVotedForRule',
      'getUserVoteForRule'
    ]),
    ...mapGetters('auth', ['isStaff', 'isSuperUser']),
    
    projectId() {
      return this.$route.params.id
    },
    
    // Corrigido: apenas administradores de projeto podem configurar votações
    canConfigureVoting() {
      return this.isProjectAdmin
    },
    
    // Novo: verificar se pode votar (todos exceto admin do projeto)
    canVote() {
      return !this.isProjectAdmin
    },
    
    pastVotings() {
      return this.$store.getters['voting/pastVotings'](this.projectId)
    },
    
    hasActiveFilters() {
      return !!(this.filters.keyword || this.filters.voteStatus || this.filters.voteResult || this.filters.category)
    },
    
    activeFiltersCount() {
      let count = 0
      if (this.filters.keyword) count++
      if (this.filters.voteStatus) count++
      if (this.filters.voteResult) count++
      if (this.filters.category) count++
      return count
    },
    
    filteredRules() {
      if (!this.activeVoting || !this.activeVoting.rules) {
        return []
      }
      
      // Start with all rules
      let filtered = [...this.activeVoting.rules]
      
      // Apply keyword filter
      if (this.filters.keyword) {
        const keyword = this.filters.keyword.toLowerCase()
        filtered = filtered.filter(ruleId => {
          const name = this.getRuleName(ruleId).toLowerCase()
          const description = this.getRuleDescription(ruleId).toLowerCase()
          return name.includes(keyword) || description.includes(keyword)
        })
      }
      
      // Apply vote status filter
      if (this.filters.voteStatus) {
        if (this.filters.voteStatus === 'voted') {
          filtered = filtered.filter(ruleId => this.hasVotedForRule(ruleId) || this.pendingVotes[ruleId])
        } else if (this.filters.voteStatus === 'not-voted') {
          filtered = filtered.filter(ruleId => !this.hasVotedForRule(ruleId) && !this.pendingVotes[ruleId])
        }
      }
      
      // Apply vote result filter
      if (this.filters.voteResult) {
        filtered = filtered.filter(ruleId => {
          const votes = this.ruleVotes(ruleId)
          if (this.filters.voteResult === 'approved') {
            return votes.aprovar > votes.rejeitar
          } else if (this.filters.voteResult === 'rejected') {
            return votes.aprovar < votes.rejeitar
          } else if (this.filters.voteResult === 'tied') {
            return votes.aprovar === votes.rejeitar
          }
          return true
        })
      }
      
      // Apply category filter
      if (this.filters.category) {
        filtered = filtered.filter(ruleId => 
          this.ruleCategory(ruleId) === this.filters.category
        )
      }
      
      // Apply sorting
      if (this.filters.sortBy) {
        const sortBy = this.filters.sortBy
        
        filtered.sort((a, b) => {
          if (sortBy === 'name-asc') {
            return this.getRuleName(a).localeCompare(this.getRuleName(b))
          } else if (sortBy === 'name-desc') {
            return this.getRuleName(b).localeCompare(this.getRuleName(a))
          } else if (sortBy === 'approvals-desc') {
            return this.ruleVotes(b).aprovar - this.ruleVotes(a).aprovar
          } else if (sortBy === 'rejections-desc') {
            return this.ruleVotes(b).rejeitar - this.ruleVotes(a).rejeitar
          }
          
          return 0
        })
      }
      
      return filtered
    },
    
    getCategoryOptions() {
      if (!this.activeVoting || !this.activeVoting.rules) {
        return []
      }
      
      // Get unique categories from all rules
      const categories = new Set()
      
      this.activeVoting.rules.forEach(ruleId => {
        const category = this.ruleCategory(ruleId)
        if (category) {
          categories.add(category)
        }
      })
      
      return Array.from(categories).map(category => ({
        text: category,
        value: category
      }))
    },
    
    hasVotedAllRules() {
      if (!this.activeVoting || !this.activeVoting.rules || !this.canVote) {
        return false
      }
      
      return this.activeVoting.rules.every(ruleId => {
        // Verificar se já existe voto confirmado ou voto pendente
        return this.hasVotedForRule(ruleId) || this.pendingVotes[ruleId]
      })
    },
    
    remainingVotesCount() {
      if (!this.activeVoting || !this.activeVoting.rules || !this.canVote) {
        return 0
      }
      
      return this.activeVoting.rules.filter(ruleId => {
        return !this.hasVotedForRule(ruleId) && !this.pendingVotes[ruleId]
      }).length
    },
    
    // Novo: computed para calcular o progresso da votação
    votingProgress() {
      if (!this.activeVoting || !this.activeVoting.rules || !this.canVote) {
        return 0
      }
      
      const totalRules = this.activeVoting.rules.length
      const votedRules = totalRules - this.remainingVotesCount
      
      return (votedRules / totalRules) * 100
    }
  },
  
  watch: {
    // Limpar votos pendentes quando mudar a votação ativa
    activeVoting(newVoting, oldVoting) {
      if (newVoting?.id !== oldVoting?.id) {
        this.pendingVotes = {}
      }
    }
  },
  
  async mounted() {
    const projectId = this.$route.params.id
    this.project = await this.$services.project.findById(projectId)
    
    // Inicializar votos pendentes
    this.pendingVotes = {}
    
    // Load discussion state
    this.$store.dispatch('discussion/initDiscussionState')
    
    // Load voting state
    this.$store.dispatch('voting/initVotingState', projectId)
    
    // Check if user is project administrator
    this.checkAdminRole()
  },
  
  methods: {
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('pt-BR')
    },
    
    getRuleName(ruleId) {
      const rule = this.annotationRules.find(r => r.id === ruleId)
      return rule ? rule.name : 'Regra não encontrada'
    },
    
    getRuleDescription(ruleId) {
      const rule = this.annotationRules.find(r => r.id === ruleId)
      return rule ? rule.description : ''
    },
    
    ruleCategory(ruleId) {
      const rule = this.annotationRules.find(r => r.id === ruleId)
      return rule && rule.category ? rule.category : null
    },
    
    hasVotedForRule(ruleId) {
      // Use store getter to check if user has already voted
      return this.hasUserVotedForRule(ruleId)
    },
    
    handleVotingSaved(votingData) {
      // Display success notification
      this.snackbar = {
        show: true,
        text: 'Votação configurada com sucesso!',
        color: 'success',
        timeout: 3000
      }
      
      // Ensure voting state is updated
      this.$store.commit('voting/SET_ACTIVE_VOTING', {
        projectId: this.projectId,
        voting: votingData
      })
    },
    
    async checkAdminRole() {
      try {
        const member = await this.$repositories.member.fetchMyRole(this.projectId)
        this.isProjectAdmin = member.isProjectAdmin
        
        // Debug logs temporários
        console.log('=== DEBUG VOTING PERMISSIONS ===')
        console.log('isProjectAdmin:', this.isProjectAdmin, '(pode configurar/terminar votações, NÃO pode votar)')
        console.log('isStaff:', this.isStaff, '(pode votar)')
        console.log('isSuperUser:', this.isSuperUser, '(pode votar)')
        console.log('canConfigureVoting:', this.canConfigureVoting)
        console.log('canVote:', this.canVote)
        console.log('member:', member)
        console.log('================================')
        
      } catch (error) {
        console.error('Erro ao verificar papel de administrador:', error)
        // Em caso de erro, assumir que não é admin
        this.isProjectAdmin = false
      }
    },
    
    async endVotingEarly() {
      try {
        // Call action to end voting early
        const result = await this.$store.dispatch('voting/endVotingEarly', {
          projectId: this.projectId
        })
        
        if (result.success) {
          this.snackbar = {
            show: true,
            text: 'Votação terminada com sucesso!',
            color: 'success',
            timeout: 3000
          }
          this.confirmEndVoting = false
        } else {
          throw new Error('Erro ao terminar votação')
        }
      } catch (error) {
        console.error('Erro ao terminar votação:', error)
        this.snackbar = {
          show: true,
          text: 'Ocorreu um erro ao terminar a votação',
          color: 'error',
          timeout: 3000
        }
      }
    },
    
    isRuleApproved(ruleId) {
      const votes = this.ruleVotes(ruleId)
      return votes.aprovar > votes.rejeitar
    },
    
    resetFilters() {
      this.filters = {
        keyword: '',
        voteStatus: null,
        voteResult: null,
        category: null,
        sortBy: 'name-asc'
      }
    },
    
    // Novo: método para definir voto pendente
    setPendingVote(ruleId, vote) {
      if (this.hasVotedForRule(ruleId)) {
        return // Se já votou, não permite alterar
      }
      
      this.$set(this.pendingVotes, ruleId, vote)
    },
    
    // Novo: método para submeter todos os votos
    async submitAllVotes() {
      if (!this.canVote || !this.hasVotedAllRules || this.isSubmittingVotes) {
        return
      }
      
      this.isSubmittingVotes = true
      
      try {
        // Submeter todos os votos pendentes
        const promises = Object.entries(this.pendingVotes).map(([ruleId, vote]) => {
          if (!this.hasVotedForRule(parseInt(ruleId))) {
            return this.$store.dispatch('voting/voteForRule', { 
              ruleId: parseInt(ruleId), 
              vote 
            })
          }
          return Promise.resolve({ success: true })
        })
        
        const results = await Promise.all(promises)
        
        // Verificar se todos os votos foram bem-sucedidos
        const allSuccessful = results.every(result => result.success !== false)
        
        if (allSuccessful) {
          // Limpar votos pendentes
          this.pendingVotes = {}
          
          this.snackbar = {
            show: true,
            text: 'Votação submetida com sucesso! Todos os seus votos foram registrados.',
            color: 'success',
            timeout: 5000
          }
        } else {
          throw new Error('Alguns votos falharam')
        }
        
      } catch (error) {
        console.error('Erro ao submeter votos:', error)
        this.snackbar = {
          show: true,
          text: 'Erro ao submeter votação. Tente novamente.',
          color: 'error',
          timeout: 5000
        }
      } finally {
        this.isSubmittingVotes = false
      }
    }
  }
}
</script>

<style scoped>
.rule-voted {
  border-left: 4px solid #4CAF50 !important;
}

.voting-area {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.gap-2 > * {
  margin-right: 8px;
  margin-bottom: 8px;
}

.transition-all {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}
</style> 