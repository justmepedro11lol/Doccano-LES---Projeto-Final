<template>
  <v-container fluid class="pa-8">
    <!-- Database Error Alert -->
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

    <!-- Header principal da página -->
    <div class="mb-8">
      <div class="d-flex align-center justify-space-between">
        <div>
          <h1 class="text-h4 font-weight-bold primary--text mb-2">
            Annotation Rules
          </h1>
          <p class="text-subtitle-1 grey--text text--darken-1">
            Users can vote on the project's annotation rules.
          </p>
        </div>
        <!-- Botão de configuração integrado no header -->
        <v-btn 
          v-if="canConfigureVoting"
          color="primary" 
          large
          elevation="2"
          :disabled="!isDiscussionEnded || hasActiveVoting" 
          @click="showVotingConfig = true"
        >
          <v-icon left>mdi-cog</v-icon>
          Configure New Voting
        </v-btn>
      </div>
    </div>

    <!-- Estados da votação integrados -->
    <div class="mb-6">
      <!-- Estado: Discussão em andamento -->
      <v-alert
        v-if="!isDiscussionEnded"
        type="info"
        prominent
        border="left"
        class="mb-4"
      >
        <div class="d-flex align-center">
          <v-icon left color="info" size="28">mdi-information</v-icon>
          <div>
            <div class="font-weight-bold text-h6">Discussion in Progress</div>
            <div class="text-body-2 mt-1">
              Before configuring a vote, the discussion about discrepancies must be finalized.
              <router-link :to="`/projects/${projectId}/discrepancies`" class="font-weight-medium text-decoration-underline">
                Access the discrepancies page
              </router-link> to participate.
            </div>
          </div>
        </div>
      </v-alert>
      
      <!-- Estado: Sem votação ativa -->
      <v-alert
        v-else-if="!hasActiveVoting"
        type="success"
        prominent
        border="left"
        class="mb-4"
      >
        <div class="d-flex align-center">
          <v-icon left color="success" size="28">mdi-check-circle</v-icon>
          <div>
            <div class="font-weight-bold text-h6">Ready to Vote</div>
            <div class="text-body-2 mt-1">
              The discussion has been finalized. {{ canConfigureVoting ? 'You can configure a new vote.' : 'Wait for the administrator to configure the vote.' }}
            </div>
          </div>
        </div>
      </v-alert>
    </div>

    <!-- Votação Ativa - Seção Principal -->
    <div v-if="activeVoting">
      <!-- Header da Votação Ativa -->
      <v-card elevation="6" class="mb-8 voting-main-card">
        <div class="voting-header-gradient">
          <v-card-title class="white--text py-6">
            <div class="d-flex align-center justify-space-between w-100">
              <div class="d-flex align-center">
                <v-icon left color="white" size="36">mdi-poll</v-icon>
                <div>
                  <h2 class="text-h5 font-weight-bold mb-1">
                    {{ activeVoting.name || 'Annotation Rules Voting' }}
                  </h2>
                  <p class="text-body-1 mb-0 font-weight-light">
                    {{ activeVoting.description || 'Voting in progress for approval of annotation rules.' }}
                  </p>
                </div>
              </div>
            </div>
          </v-card-title>
        </div>
        
        <!-- Informações da votação -->
        <v-card-text class="pa-6">
          <!-- Painel de controle do admin -->
          <div v-if="isProjectAdmin" class="mb-6">
            <v-card elevation="2" color="orange lighten-5" class="admin-control-panel">
              <v-card-text class="pa-4">
                <div class="d-flex align-center justify-space-between">
                  <div class="d-flex align-center">
                    <v-avatar color="orange" size="48" class="mr-4">
                      <v-icon color="white" size="28">mdi-account-tie</v-icon>
                    </v-avatar>
                    <div>
                      <h3 class="text-h6 font-weight-bold mb-1">Administration Panel</h3>
                      <p class="text-body-2 grey--text text--darken-1 mb-1">
                        Manage ongoing voting
                      </p>
                      <v-chip
                        small
                        color="orange"
                        text-color="white"
                        class="mt-1"
                      >
                        <v-icon left small>mdi-information</v-icon>
                        Administrators cannot vote
                      </v-chip>
                    </div>
                  </div>
                  
                  <v-btn 
                    color="error"
                    dark
                    large
                    elevation="4"
                    class="end-voting-btn"
                    @click="confirmEndVoting = true"
                  >
                    <v-icon left>mdi-stop-circle</v-icon>
                    End Voting
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </div>

          <v-row class="mb-4">
            <v-col cols="12" sm="6" md="3">
              <v-card outlined class="text-center pa-4">
                <v-icon color="primary" size="32" class="mb-2">mdi-calendar-start</v-icon>
                <div class="text-caption grey--text">Start Date</div>
                <div class="font-weight-bold">{{ formatDate(activeVoting.startDate) }}</div>
              </v-card>
            </v-col>
            
            <v-col cols="12" sm="6" md="3">
              <v-card outlined class="text-center pa-4">
                <v-icon color="primary" size="32" class="mb-2">mdi-calendar-end</v-icon>
                <div class="text-caption grey--text">End Date</div>
                <div class="font-weight-bold">{{ formatDate(activeVoting.endDate) }}</div>
              </v-card>
            </v-col>
            
            <v-col cols="12" sm="6" md="3">
              <v-card outlined class="text-center pa-4">
                <v-icon color="primary" size="32" class="mb-2">mdi-format-list-bulleted</v-icon>
                <div class="text-caption grey--text">Total Rules</div>
                <div class="font-weight-bold">{{ activeVoting.rules.length }}</div>
              </v-card>
            </v-col>
            
            <v-col cols="12" sm="6" md="3">
              <v-card outlined class="text-center pa-4">
                <v-icon :color="allVotesSubmitted ? 'success' : 'warning'" size="32" class="mb-2">
                  {{ allVotesSubmitted ? 'mdi-check-circle' : 'mdi-clock-outline' }}
                </v-icon>
                <div class="text-caption grey--text">Your Status</div>
                <div class="font-weight-bold">
                  {{ allVotesSubmitted ? 'Completed' : 'Pending' }}
                </div>
              </v-card>
            </v-col>
          </v-row>

          <!-- Filtros melhorados -->
          <v-expansion-panels v-model="showFilters" class="mb-6">
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left color="primary">mdi-filter</v-icon>
                  <span class="font-weight-medium">Advanced Filters</span>
                  <v-spacer></v-spacer>
                  <v-chip v-if="hasActiveFilters" small color="primary" outlined>
                    {{ activeFiltersCount }} active filter{{ activeFiltersCount > 1 ? 's' : '' }}
                  </v-chip>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-row>
                  <v-col cols="12" sm="6" md="3">
                    <v-text-field
                      v-model="filters.keyword"
                      label="Search"
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
                      label="Vote Status"
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
                      label="Current Result"
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
                      label="Sort by"
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
                      Clear Filters
                    </v-btn>
                  </v-col>
                </v-row>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>

          <!-- Lista de regras moderna -->
          <div v-if="filteredRules.length > 0">
            <!-- Contador de regras -->
            <div class="d-flex align-center justify-space-between mb-4">
              <div class="text-subtitle-1 font-weight-medium">
                Rules in Voting
                <v-chip small color="primary" outlined class="ml-2">
                  {{ filteredRules.length }} of {{ activeVoting.rules.length }}
                </v-chip>
              </div>
            </div>

            <!-- Cards das regras - Design minimalista -->
            <v-row>
              <v-col v-for="ruleId in filteredRules" :key="ruleId" cols="12">
                <v-card 
                  flat
                  outlined
                  :class="[
                    'rule-card-minimal',
                    { 
                      'rule-voted': hasVotedForRule(ruleId),
                      'rule-pending': !hasVotedForRule(ruleId) && pendingVotes[ruleId],
                      'rule-not-voted': !hasVotedForRule(ruleId) && !pendingVotes[ruleId]
                    }
                  ]"
                >
                  <v-card-text class="pa-4">
                    <v-row no-gutters align="center">
                      <!-- Informações da regra -->
                      <v-col cols="12" :md="canVote ? 8 : 12">
                        <div class="d-flex align-center">
                          <!-- Status indicator -->
                          <div class="status-indicator mr-3">
                            <v-icon 
                              :color="hasVotedForRule(ruleId) ? 'success' : (pendingVotes[ruleId] ? 'warning' : 'grey lighten-1')"
                              size="20"
                            >
                              {{ hasVotedForRule(ruleId) ? 'mdi-check-circle' : (pendingVotes[ruleId] ? 'mdi-clock-outline' : 'mdi-circle-outline') }}
                            </v-icon>
                          </div>
                          
                          <div class="flex-grow-1">
                            <div class="d-flex align-center mb-1">
                              <h3 class="text-subtitle-1 font-weight-bold mr-2">
                                {{ getRuleName(ruleId) }}
                              </h3>
                              
                              <!-- Category chip (se existir) -->
                              <v-chip
                                v-if="ruleCategory(ruleId)"
                                x-small
                                color="primary"
                                outlined
                                class="ml-2"
                              >
                                {{ ruleCategory(ruleId) }}
                              </v-chip>
                            </div>
                            
                            <p class="text-body-2 grey--text text--darken-1 mb-0">
                              {{ getRuleDescription(ruleId) }}
                            </p>
                            
                            <!-- Estatísticas de votos (só mostra depois de votar ou para admin) -->
                            <div v-if="hasVotedForRule(ruleId) || isProjectAdmin" class="mt-2">
                              <div class="d-flex align-center">
                                <v-chip
                                  x-small
                                  color="success"
                                  text-color="white"
                                  class="mr-2"
                                >
                                  <v-icon left x-small>mdi-thumb-up</v-icon>
                                  {{ ruleVotes(ruleId).aprovar }}
                                </v-chip>
                                
                                <v-chip
                                  x-small
                                  color="error"
                                  text-color="white"
                                  class="mr-2"
                                >
                                  <v-icon left x-small>mdi-thumb-down</v-icon>
                                  {{ ruleVotes(ruleId).rejeitar }}
                                </v-chip>
                                
                                <v-chip
                                  x-small
                                  :color="getVoteResultColor(ruleId)"
                                  text-color="white"
                                >
                                  {{ getVoteResultText(ruleId) }}
                                </v-chip>
                              </div>
                            </div>
                          </div>
                        </div>
                      </v-col>
                      
                      <!-- Área de votação minimalista -->
                      <v-col v-if="canVote" cols="12" md="4">
                        <div class="d-flex justify-end">
                          <!-- Se não votou ainda -->
                          <div v-if="!hasVotedForRule(ruleId)" class="d-flex">
                            <v-btn
                              :color="pendingVotes[ruleId] === 'aprovar' ? 'success' : 'grey lighten-2'"
                              :dark="pendingVotes[ruleId] === 'aprovar'"
                              small
                              class="mr-2 vote-btn"
                              @click="setPendingVote(ruleId, pendingVotes[ruleId] === 'aprovar' ? null : 'aprovar')"
                            >
                              <v-icon small left>mdi-thumb-up</v-icon>
                              Approve
                            </v-btn>
                            
                            <v-btn
                              :color="pendingVotes[ruleId] === 'rejeitar' ? 'error' : 'grey lighten-2'"
                              :dark="pendingVotes[ruleId] === 'rejeitar'"
                              small
                              class="vote-btn"
                              @click="setPendingVote(ruleId, pendingVotes[ruleId] === 'rejeitar' ? null : 'rejeitar')"
                            >
                              <v-icon small left>mdi-thumb-down</v-icon>
                              Reject
                            </v-btn>
                          </div>
                          
                          <!-- Se já votou -->
                          <div v-else>
                            <v-chip
                              :color="getUserVoteForRule(ruleId) === 'aprovar' ? 'success' : 'error'"
                              small
                              dark
                            >
                              <v-icon left small>
                                {{ getUserVoteForRule(ruleId) === 'aprovar' ? 'mdi-thumb-up' : 'mdi-thumb-down' }}
                              </v-icon>
                              {{ getUserVoteForRule(ruleId) === 'aprovar' ? 'Approved' : 'Rejected' }}
                            </v-chip>
                          </div>
                        </div>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            
            <!-- Painel de submissão minimalista -->
            <div v-if="canVote" class="mt-6">
              <v-card 
                flat
                outlined
                :color="allVotesSubmitted ? 'success lighten-5' : 'grey lighten-5'"
                class="submission-panel-minimal"
              >
                <v-card-text class="pa-4">
                  <div v-if="allVotesSubmitted || votesSuccessfullySubmitted">
                    <!-- Estado concluído -->
                    <div class="d-flex align-center">
                      <v-icon color="success" size="24" class="mr-3">mdi-check-circle</v-icon>
                      <div class="flex-grow-1">
                        <div class="text-subtitle-1 font-weight-bold success--text">
                          Voting Submitted Successfully
                        </div>
                        <div class="text-body-2 grey--text">
                          Thank you for your participation!
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div v-else-if="!votesSuccessfullySubmitted">
                    <!-- Estado pendente -->
                    <div class="d-flex align-center justify-space-between">
                      <div class="d-flex align-center flex-grow-1">
                        <v-icon 
                          :color="hasVotedAllRules ? 'primary' : 'grey'" 
                          size="24" 
                          class="mr-3"
                        >
                          {{ hasVotedAllRules ? 'mdi-send' : 'mdi-vote' }}
                        </v-icon>
                        <div class="flex-grow-1">
                          <div class="text-subtitle-1 font-weight-bold">
                            {{ hasVotedAllRules ? 'Ready to Submit' : 'Voting in Progress' }}
                          </div>
                          <div class="text-body-2 grey--text">
                            {{ activeVoting.rules.length - remainingVotesCount }} of {{ activeVoting.rules.length }} rules selected
                          </div>
                        </div>
                      </div>
                      
                      <v-btn
                        color="primary"
                        :disabled="!hasVotedAllRules || isSubmittingVotes"
                        :loading="isSubmittingVotes"
                        @click="submitAllVotes"
                      >
                        <v-icon left small>mdi-send</v-icon>
                        Submit
                      </v-btn>
                    </div>
                    
                    <!-- Barra de progresso minimalista -->
                    <v-progress-linear
                      :value="votingProgress"
                      color="primary"
                      height="4"
                      rounded
                      class="mt-3"
                    ></v-progress-linear>
                  </div>
                </v-card-text>
              </v-card>
            </div>
          </div>
          
          <!-- Estado vazio -->
          <div v-else class="text-center py-12">
            <v-icon size="64" color="grey lighten-1" class="mb-4">mdi-filter-remove</v-icon>
            <h3 class="text-h6 grey--text mb-2">No rules found</h3>
            <p class="grey--text">No rules match the current filters</p>
            <v-btn text color="primary" class="mt-2" @click="resetFilters">
              Clear filters
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </div>

    <!-- Histórico de votações -->
    <div v-if="pastVotings.length > 0">
      <v-card elevation="2" class="mb-6">
        <v-card-title class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-icon left color="primary">mdi-history</v-icon>
            <span class="text-h6">Voting History</span>
          </div>
          <v-btn
            color="info"
            large
            @click="goToHome"
          >
            <v-icon left>mdi-home</v-icon>
            Home Page
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-expansion-panels v-model="openVotingPanels" multiple>
            <v-expansion-panel
              v-for="voting in pastVotings"
              :key="voting.id"
            >
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <div class="flex-grow-1">
                    <div class="font-weight-medium">
                      {{ voting.name || voting.description }}
                    </div>
                    <div v-if="voting.name && voting.description" class="text-caption grey--text mb-1">
                      {{ voting.description }}
                    </div>
                    <div class="text-caption grey--text">
                      {{ formatDate(voting.startDate) }} - {{ formatDate(voting.endDate) }}
                    </div>
                  </div>
                  <v-chip v-if="voting.endedEarly" small color="orange" class="ml-2">
                    Ended early
                  </v-chip>
                </div>
              </v-expansion-panel-header>
              
              <v-expansion-panel-content>
                <div class="mt-4">
                  <h4 class="text-subtitle-1 font-weight-bold mb-4">Final Voting Results</h4>
                  <div class="mb-4">
                    <v-card
                      v-for="ruleId in voting.rules"
                      :key="ruleId"
                      class="mb-3 rule-result-card"
                      outlined
                    >
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center justify-space-between">
                          <div class="d-flex align-center">
                            <v-chip 
                              :color="isRuleApproved(ruleId) ? 'success' : 'error'"
                              class="mr-3 white--text"
                              small
                            >
                              <v-icon left small>
                                {{ isRuleApproved(ruleId) ? 'mdi-check-circle' : 'mdi-close-circle' }}
                              </v-icon>
                              {{ isRuleApproved(ruleId) ? 'Approved' : 'Rejected' }}
                            </v-chip>
                            <span class="text-subtitle-2 font-weight-medium">
                              {{ getRuleName(ruleId) }}
                            </span>
                          </div>
                          
                          <div class="d-flex align-center">
                            <div class="text-center mr-4">
                              <div class="text-caption grey--text">In Favor</div>
                              <v-chip color="success" text-color="white" x-small>
                                <v-icon left x-small>mdi-thumb-up</v-icon>
                                {{ ruleVotes(ruleId).aprovar }}
                              </v-chip>
                            </div>
                            
                            <div class="text-center">
                              <div class="text-caption grey--text">Against</div>
                              <v-chip color="error" text-color="white" x-small>
                                <v-icon left x-small>mdi-thumb-down</v-icon>
                                {{ ruleVotes(ruleId).rejeitar }}
                              </v-chip>
                            </div>
                          </div>
                        </div>
                        
                        <!-- Barra de progresso visual -->
                        <div class="mt-3">
                          <div class="d-flex align-center">
                            <span class="text-caption mr-2">{{ ruleVotes(ruleId).aprovar }}</span>
                            <v-progress-linear
                              :value="getVotePercentage(ruleId, 'aprovar')"
                              color="success"
                              background-color="error"
                              background-opacity="0.3"
                              height="8"
                              rounded
                              class="flex-grow-1"
                            ></v-progress-linear>
                            <span class="text-caption ml-2">{{ ruleVotes(ruleId).rejeitar }}</span>
                          </div>
                          <div class="text-center text-caption grey--text mt-1">
                            {{ Math.round(getVotePercentage(ruleId, 'aprovar')) }}% in favor
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </div>
                  
                  <!-- Botão para fechar a caixa -->
                  <div class="mt-4 text-center">
                    <v-btn
                      color="grey"
                      outlined
                      @click="closeVotingPanel(voting.id)"
                    >
                      <v-icon left>mdi-close</v-icon>
                      Close
                    </v-btn>
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
          Confirm End Voting
        </v-card-title>
        <v-card-text class="pt-4">
          <p class="text-body-1 mb-4">
            Are you sure you want to end the current voting early? This action cannot be undone.
          </p>
          <v-alert type="warning" outlined dense>
            The voting will be finalized immediately and all votes will be counted in their current state.
          </v-alert>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn text large @click="confirmEndVoting = false">
            Cancel
          </v-btn>
          <v-btn color="error" large @click="endVotingEarly">
            <v-icon left>mdi-stop</v-icon>
            End Voting
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
          Close
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
      // Database error state
      databaseError: false,
      databaseCheckInterval: null,
      // Novo: armazenar votos temporários antes do submit
      pendingVotes: {},
      isSubmittingVotes: false,
      votesSuccessfullySubmitted: false,
      filters: {
        keyword: '',
        voteStatus: null,
        voteResult: null,
        category: null,
        sortBy: 'name-asc'
      },
      voteStatusOptions: [
        { text: 'Voted', value: 'voted' },
        { text: 'Not voted', value: 'not-voted' }
      ],
      voteResultOptions: [
        { text: 'Currently approved', value: 'approved' },
        { text: 'Currently rejected', value: 'rejected' },
        { text: 'Tied', value: 'tied' }
      ],
      sortOptions: [
        { text: 'Name (A-Z)', value: 'name-asc' },
        { text: 'Name (Z-A)', value: 'name-desc' },
        { text: 'Most approvals', value: 'approvals-desc' },
        { text: 'Most rejections', value: 'rejections-desc' }
      ],
      openVotingPanels: [] // Para controlar quais painéis de votação estão abertos
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
          filtered = filtered.filter(ruleId => this.hasVotedForRule(ruleId))
        } else if (this.filters.voteStatus === 'not-voted') {
          filtered = filtered.filter(ruleId => !this.hasVotedForRule(ruleId))
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
    },
    
    allVotesSubmitted() {
      if (!this.activeVoting || !this.activeVoting.rules || !this.canVote) {
        return false
      }
      
      // Verificar se o usuário votou em todas as regras (votos já submetidos e confirmados)
      const totalRules = this.activeVoting.rules.length
      const votedRules = this.activeVoting.rules.filter(ruleId => this.hasVotedForRule(ruleId)).length
      
      // Só considera como "tudo submetido" se todos os votos foram confirmados (não pendentes)
      return votedRules === totalRules && Object.keys(this.pendingVotes).length === 0
    }
  },
  
  watch: {
    // Limpar votos pendentes quando mudar a votação ativa
    activeVoting(newVoting, oldVoting) {
      if (newVoting?.id !== oldVoting?.id) {
        this.pendingVotes = {}
        this.votesSuccessfullySubmitted = false
      }
    }
  },
  
  async mounted() {
    const projectId = this.$route.params.id
    this.project = await this.$services.project.findById(projectId)
    
    // Inicializar votos pendentes e estado de submissão
    this.pendingVotes = {}
    this.votesSuccessfullySubmitted = false
    
    // Load discussion state
    this.$store.dispatch('discussion/initDiscussionState')
    
    // Load voting state
    this.$store.dispatch('voting/initVotingState', projectId)
    
    // Check if user is project administrator
    this.checkAdminRole()
    
    // Start database connection check
    this.startDatabaseCheck()
  },

  beforeDestroy() {
    // Limpar o intervalo quando o componente for destruído
    if (this.databaseCheckInterval) {
      clearInterval(this.databaseCheckInterval)
    }
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
        text: 'Voting configured successfully!',
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
            text: 'Voting ended successfully!',
            color: 'success',
            timeout: 3000
          }
          this.confirmEndVoting = false
        } else {
          throw new Error('Error ending voting')
        }
      } catch (error) {
        console.error('Error ending voting:', error)
        this.snackbar = {
          show: true,
          text: 'An error occurred while ending the voting',
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
          
          // Marcar como votos submetidos com sucesso
          this.votesSuccessfullySubmitted = true
          
          // Forçar atualização para mostrar a mensagem imediatamente
          this.$forceUpdate()
          await this.$nextTick()
          
          this.snackbar = {
            show: true,
            text: 'Voting submitted successfully! All your votes have been recorded.',
            color: 'success',
            timeout: 5000
          }
        } else {
          throw new Error('Alguns votos falharam')
        }
        
      } catch (error) {
        console.error('Error submitting votes:', error)
        this.snackbar = {
          show: true,
          text: 'Error submitting voting. Please try again.',
          color: 'error',
          timeout: 5000
        }
      } finally {
        this.isSubmittingVotes = false
      }
    },
    
    getUserVotesSummary() {
      let aprovar = 0;
      let rejeitar = 0;
      
      if (this.activeVoting && this.activeVoting.rules) {
        this.activeVoting.rules.forEach(ruleId => {
          const userVote = this.getUserVoteForRule(ruleId);
          if (userVote === 'aprovar') aprovar++;
          if (userVote === 'rejeitar') rejeitar++;
        });
      }
      
      return { aprovar, rejeitar };
    },
    
    getVoteResultColor(ruleId) {
      const votes = this.ruleVotes(ruleId)
      if (votes.aprovar > votes.rejeitar) {
        return 'success'
      } else if (votes.aprovar < votes.rejeitar) {
        return 'error'
      } else {
        return 'grey'
      }
    },
    
    getVoteResultText(ruleId) {
      const votes = this.ruleVotes(ruleId)
      if (votes.aprovar > votes.rejeitar) {
        return 'Aprovada'
      } else if (votes.aprovar < votes.rejeitar) {
        return 'Rejeitada'
      } else {
        return 'Empate'
      }
    },

    getVotePercentage(ruleId, voteType) {
      const votes = this.ruleVotes(ruleId)
      const total = votes.aprovar + votes.rejeitar
      
      if (total === 0) {
        return 0
      }
      
      if (voteType === 'aprovar') {
        return (votes.aprovar / total) * 100
      } else {
        return (votes.rejeitar / total) * 100
      }
    },

    closeVotingPanel(votingId) {
      // Encontrar o índice do painel da votação e fechá-lo
      const panelIndex = this.pastVotings.findIndex(voting => voting.id === votingId)
      if (panelIndex !== -1) {
        const currentOpenPanels = [...this.openVotingPanels]
        const openPanelIndex = currentOpenPanels.indexOf(panelIndex)
        if (openPanelIndex !== -1) {
          currentOpenPanels.splice(openPanelIndex, 1)
          this.openVotingPanels = currentOpenPanels
        }
      }
    },

    goToHome() {
      this.$router.push(`/projects/${this.projectId}`)
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
        } catch (error) {
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
}
</script>

<style scoped>
/* Cards das regras minimalistas */
.rule-card-minimal {
  border-radius: 8px !important;
  margin-bottom: 12px;
  transition: all 0.2s ease;
  border: 1px solid #e0e0e0 !important;
}

.rule-card-minimal:hover {
  border-color: #1976d2 !important;
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.1) !important;
}

.rule-voted {
  border-left: 3px solid #4CAF50 !important;
  background-color: #f8fff8 !important;
}

.rule-pending {
  border-left: 3px solid #FF9800 !important;
  background-color: #fffbf0 !important;
}

.rule-not-voted {
  border-left: 3px solid #e0e0e0 !important;
}

/* Botões de votação */
.vote-btn {
  border-radius: 6px !important;
  transition: all 0.2s ease !important;
  text-transform: none !important;
}

.vote-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}

/* Status indicator */
.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Painel de submissão minimalista */
.submission-panel-minimal {
  border-radius: 8px !important;
  transition: all 0.2s ease;
}

.submission-panel-minimal:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}

/* Responsividade */
@media (max-width: 768px) {
  .vote-btn {
    margin-bottom: 8px !important;
  }
}

/* Header da votação principal */
.voting-header-gradient {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  box-shadow: 0 8px 32px rgba(25, 118, 210, 0.3);
}

.voting-main-card {
  border-radius: 16px !important;
  overflow: hidden;
}

/* Cards de resultado das votações */
.rule-result-card {
  border-radius: 8px !important;
  transition: all 0.2s ease;
  border: 1px solid #e0e0e0 !important;
}

.rule-result-card:hover {
  border-color: #1976d2 !important;
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.1) !important;
}

/* Customização das barras de progresso */
::v-deep .v-progress-linear {
  border-radius: 4px !important;
}

/* Responsividade para resultados das votações */
@media (max-width: 768px) {
  .rule-result-card .d-flex.justify-space-between {
    flex-direction: column !important;
    align-items: flex-start !important;
  }
  
  .rule-result-card .d-flex.align-center:last-child {
    margin-top: 12px !important;
    width: 100% !important;
    justify-content: space-around !important;
  }
}

/* Painel de administração melhorado */
.admin-control-panel {
  border-left: 4px solid #FF9800;
  border-radius: 12px !important;
}

.end-voting-btn {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  transition: all 0.3s ease !important;
}

.end-voting-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(244, 67, 54, 0.4) !important;
}

.end-voting-btn:active {
  transform: translateY(0);
}
</style> 