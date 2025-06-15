<template>
  <v-dialog
    :value="value"
    max-width="800px"
    persistent
    @input="$emit('input', $event)"
  >
    <v-card>
      <v-card-title class="headline">
        Configurar Nova Votação
      </v-card-title>

      <v-card-text>
        <v-form ref="form" class="mt-4">
          <!-- Datas de início e fim -->
          <v-row>
            <v-col cols="12" sm="6">
              <v-menu
                v-model="startDateMenu"
                :close-on-content-click="false"
                :nudge-right="40"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template #activator="{ on, attrs }">
                  <v-text-field
                    v-model="startDate"
                    label="Data de Início"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="attrs"
                    :rules="startDateRules"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="startDate"
                  :max="endDate"
                  @input="startDateMenu = false"
                ></v-date-picker>
              </v-menu>
            </v-col>
            <v-col cols="12" sm="6">
              <v-menu
                v-model="endDateMenu"
                :close-on-content-click="false"
                :nudge-right="40"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template #activator="{ on, attrs }">
                  <v-text-field
                    v-model="endDate"
                    label="Data de Fim"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="attrs"
                    :rules="endDateRules"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="endDate"
                  :min="startDate"
                  @input="endDateMenu = false"
                ></v-date-picker>
              </v-menu>
            </v-col>
          </v-row>

          <!-- Nome da votação -->
          <v-text-field
            v-model="votingName"
            label="Nome da Votação"
            placeholder="Digite o nome da votação..."
            required
            :rules="votingNameRules"
            class="mt-4"
          />

          <!-- Descrição da votação -->
          <v-textarea
            v-model="description"
            label="Descrição da Votação"
            rows="4"
            placeholder="Digite a descrição da votação..."
            required
            :rules="descriptionRules"
            class="mt-4"
          />

          <!-- Seleção de regras de anotação -->
          <v-card outlined class="mt-4">
            <v-card-title class="subtitle-1">
              Novas Regras de Anotação
            </v-card-title>
            <v-card-text>
              <v-alert
                v-if="availableRules.length === 0"
                type="info"
                outlined
                class="mb-4"
              >
                <div class="d-flex align-center">
                  <v-icon left color="info">mdi-information</v-icon>
                  <div>
                    <div class="font-weight-bold">Criar Novas Regras</div>
                    <div class="text-body-2 mt-1">
                      Para cada votação, deve criar regras de anotação específicas. 
                      Estas regras serão votadas pelos membros do projeto.
                    </div>
                  </div>
                </div>
              </v-alert>
              
              <v-list v-else>
                <v-list-item
                  v-for="rule in availableRules"
                  :key="rule.id"
                >
                  <v-checkbox
                    v-model="selectedRules"
                    :value="rule.id"
                    hide-details
                    class="mr-2"
                  ></v-checkbox>
                  <div>
                    <div class="font-weight-medium">{{ rule.name }}</div>
                    <div class="text-caption">{{ rule.description }}</div>
                  </div>
                </v-list-item>
              </v-list>
              
              <v-btn
                :color="availableRules.length === 0 ? 'primary' : 'secondary'"
                :outlined="availableRules.length > 0"
                class="mt-4"
                @click="showNewRuleForm = true"
              >
                <v-icon left>mdi-plus</v-icon>
                {{ availableRules.length === 0 ? 'Criar Primeira Regra' : 'Adicionar Outra Regra' }}
              </v-btn>
            </v-card-text>
          </v-card>

          <!-- Formulário para criar nova regra -->
          <NewRuleForm 
            v-if="showNewRuleForm"
            @cancel="showNewRuleForm = false"
            @save="handleNewRule"
          />
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="secondary"
          text
          @click="resetForm(); $emit('input', false)"
        >
          Cancelar
        </v-btn>
        <v-btn
          :loading="saving"
          color="primary"
          :disabled="!isFormValid"
          @click="saveConfig"
        >
          Salvar
        </v-btn>
      </v-card-actions>
    </v-card>
    
    <!-- Dialog para escolher entre regras antigas ou novas -->
    <v-dialog v-model="showOldRulesDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="text-h5 primary--text">
          <v-icon left color="primary">mdi-help-circle</v-icon>
          Regras de Votações Anteriores Encontradas
        </v-card-title>
        
        <v-card-text class="pt-4">
          <p class="text-body-1 mb-4">
            Foram encontradas {{ oldRules.length }} regra{{ oldRules.length > 1 ? 's' : '' }} de votações anteriores. 
            O que deseja fazer?
          </p>
          
          <v-alert type="info" outlined dense class="mb-4">
            <strong>Recomendação:</strong> Para cada nova votação, é recomendado criar regras específicas 
            baseadas nas discussões e discrepâncias atuais do projeto.
          </v-alert>
          
          <div class="mb-4">
            <h4 class="text-subtitle-1 font-weight-bold mb-2">Regras Existentes:</h4>
            <v-list dense>
              <v-list-item v-for="rule in oldRules" :key="rule.id" class="px-0">
                <v-list-item-content>
                  <v-list-item-title class="text-body-2 font-weight-medium">
                    {{ rule.name }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-caption">
                    {{ rule.description }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </div>
        </v-card-text>
        
        <v-card-actions class="pa-4">
          <v-btn
            color="secondary"
            outlined
            large
            @click="useOldRules"
          >
            <v-icon left>mdi-recycle</v-icon>
            Reutilizar Regras Existentes
          </v-btn>
          
          <v-spacer></v-spacer>
          
          <v-btn
            color="primary"
            large
            @click="createNewRules"
          >
            <v-icon left>mdi-plus</v-icon>
            Criar Novas Regras
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { mapGetters } from 'vuex'
import NewRuleForm from './NewRuleForm.vue'

interface AnnotationRule {
  id: number;
  name: string;
  description: string;
}

interface NewRule {
  name: string;
  description: string;
}

export default defineComponent({
  name: 'VotingConfigModal',
  
  components: {
    NewRuleForm
  },
  
  props: {
    value: {
      type: Boolean,
      required: true
    },
    projectId: {
      type: [String, Number],
      default: null
    }
  },
  
  data() {
    return {
      form: null,
      startDate: '',
      endDate: '',
      startDateMenu: false,
      endDateMenu: false,
      description: '',
      votingName: '',
      selectedRules: [] as number[],
      showNewRuleForm: false,
      saving: false,
      oldRules: [] as AnnotationRule[],
      showOldRulesDialog: false,
      
      // Regras de validação
      startDateRules: [
        (v: any) => !!v || 'Data de início é obrigatória'
      ],
      
      endDateRules: [
        (v: any) => !!v || 'Data de fim é obrigatória'
      ],
      
      descriptionRules: [
        (v: any) => !!v || 'Descrição é obrigatória'
      ],

      votingNameRules: [
        (v: any) => !!v || 'Nome da votação é obrigatório'
      ]
    }
  },
  
  computed: {
    ...mapGetters({
      annotationRules: 'voting/annotationRules'
    }),
    
    availableRules(): AnnotationRule[] {
      return this.annotationRules || []
    },
    
    isFormValid(): boolean {
      return Boolean(
        this.startDate && 
        this.endDate && 
        this.votingName &&
        this.description && 
        this.selectedRules.length > 0
      )
    }
  },
  
  watch: {
    async value(newValue) {
      // Quando o modal abre, verificar se existem regras antigas
      if (newValue && this.projectId) {
        const result = await this.$store.dispatch('voting/getOldAnnotationRules', this.projectId)
        
        if (result.success && result.data.length > 0) {
          this.oldRules = result.data
          this.showOldRulesDialog = true
        } else {
          // Se não há regras antigas, limpar e começar do zero
          this.$store.dispatch('voting/clearAnnotationRules', this.projectId)
        }
      }
    }
  },
  
  mounted() {
    if (this.projectId) {
      this.$store.dispatch('voting/initVotingState', this.projectId)
    }
  },
  
  methods: {
    async handleNewRule(newRule: NewRule) {
      // Salvar a regra na store
      const result = await this.$store.dispatch('voting/createAnnotationRule', {
        projectId: this.projectId,
        rule: newRule
      })
      
      if (result.success) {
        // Selecionar automaticamente a nova regra
        this.selectedRules.push(result.data.id)
        this.showNewRuleForm = false
      }
    },
    
    useOldRules() {
      // Manter as regras antigas e permitir selecioná-las
      this.showOldRulesDialog = false
      // As regras antigas já estão carregadas no store
    },
    
    createNewRules() {
      // Limpar regras antigas e começar do zero
      this.$store.dispatch('voting/clearAnnotationRules', this.projectId)
      this.showOldRulesDialog = false
    },
    
    resetForm() {
      // Limpar todos os campos do formulário
      this.startDate = ''
      this.endDate = ''
      this.description = ''
      this.votingName = ''
      this.selectedRules = []
      this.showNewRuleForm = false
      this.oldRules = []
      this.showOldRulesDialog = false
      
      // Reset form validation
      if (this.$refs.form) {
        this.$refs.form.resetValidation()
      }
    },
    
    async saveConfig() {
      // Verificar se o formulário é válido
      if (this.$refs.form && this.isFormValid) {
        this.saving = true
        try {
          // Criar objeto de configuração de votação
          const votingData = {
            name: this.votingName,
            startDate: this.startDate,
            endDate: this.endDate,
            description: this.description,
            rules: this.selectedRules
          }
          
          // Salvar na store
          const result = await this.$store.dispatch('voting/createVoting', {
            projectId: this.projectId,
            votingData
          })
          
          if (result.success) {
            // Notificar componente pai do sucesso
            this.$emit('saved', result.data)
            
            // Limpar formulário e fechar modal
            this.resetForm()
            this.$emit('input', false)
          }
        } catch (error) {
          console.error('Erro ao salvar configuração de votação:', error)
        } finally {
          this.saving = false
        }
      }
    }
  }
})
</script>

<style scoped>
/* Sem necessidade da classe v-datetime-picker */
</style> 