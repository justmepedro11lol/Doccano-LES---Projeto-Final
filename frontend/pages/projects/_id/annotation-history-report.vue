<template>
  <v-container fluid class="pa-0">
    <!-- Header Section -->
    <div class="hero-section">
      <v-container>
        <v-row align="center" class="py-8">
          <v-col cols="12" class="text-center">
            <v-icon size="64" color="white" class="mb-4">mdi-history</v-icon>
            <h1 class="display-1 font-weight-bold white--text mb-2">
              Annotation History Report
            </h1>
            <p class="subtitle-1 white--text">
              Detailed analysis of project annotation history and evolution
            </p>
          </v-col>
        </v-row>
      </v-container>
    </div>

    <!-- Main Content -->
    <v-container class="py-8">
      <!-- Summary Cards -->
      <v-row v-if="!isLoading && historyData.length > 0">
        <v-col cols="12" md="3">
          <v-card class="text-center pa-4" elevation="2">
            <v-icon size="48" color="primary" class="mb-3">mdi-file-document-multiple</v-icon>
            <h3 class="headline font-weight-bold">{{ summaryStats.totalAnnotations }}</h3>
            <p class="body-2 grey--text">Total of Annotations</p>
          </v-card>
        </v-col>
        <v-col cols="12" md="3">
          <v-card class="text-center pa-4" elevation="2">
            <v-icon size="48" color="success" class="mb-3">mdi-account-multiple</v-icon>
            <h3 class="headline font-weight-bold">{{ summaryStats.uniqueAnnotators }}</h3>
            <p class="body-2 grey--text">Active Annotators</p>
          </v-card>
        </v-col>
        <v-col cols="12" md="3">
          <v-card class="text-center pa-4" elevation="2">
            <v-icon size="48" color="warning" class="mb-3">mdi-pencil-plus</v-icon>
            <h3 class="headline font-weight-bold">{{ summaryStats.totalCreated }}</h3>
            <p class="body-2 grey--text">Annotations Created</p>
          </v-card>
        </v-col>
        <v-col cols="12" md="3">
          <v-card class="text-center pa-4" elevation="2">
            <v-icon size="48" color="error" class="mb-3">mdi-pencil-remove</v-icon>
            <h3 class="headline font-weight-bold">{{ summaryStats.totalDeleted }}</h3>
            <p class="body-2 grey--text">Annotations Deleted</p>
          </v-card>
        </v-col>
      </v-row>

      <!-- Loading State -->
      <v-row v-if="isLoading">
        <v-col cols="12">
          <v-card class="text-center pa-8" elevation="2">
            <v-progress-circular indeterminate color="primary" size="64" class="mb-4"></v-progress-circular>
            <h3 class="headline">Loading annotation history...</h3>
            <p class="body-2 grey--text">Please wait while we fetch the data</p>
          </v-card>
        </v-col>
      </v-row>

      <!-- No Data State -->
      <v-row v-if="!isLoading && historyData.length === 0">
        <v-col cols="12">
          <v-card class="text-center pa-8" elevation="2">
            <v-icon size="64" color="grey lighten-2" class="mb-4">mdi-history</v-icon>
            <h3 class="headline">No annotation history found</h3>
            <p class="body-2 grey--text">This project doesn't have any annotations yet, or they couldn't be loaded.</p>
          </v-card>
        </v-col>
      </v-row>

      <v-row v-if="!isLoading && historyData.length > 0" class="mt-6">
        <!-- Filters Panel -->
        <v-col cols="12" lg="3">
          <v-card elevation="2">
            <v-card-title class="primary white--text">
              <v-icon left color="white">mdi-filter</v-icon>
              Filters
            </v-card-title>
            <v-card-text class="pa-4">
              <v-form @submit.prevent="applyFilters">
                <!-- Anotators -->
                <v-select
                  v-model="filters.annotator_ids"
                  :items="availableAnnotators"
                  item-text="username"
                  item-value="id"
                  label="Annotators"
                  multiple
                  chips
                  small-chips
                  deletable-chips
                  class="mb-3"
                ></v-select>

                <!-- Action Type -->
                <v-select
                  v-model="filters.action_type"
                  :items="actionTypes"
                  label="Action Type"
                  multiple
                  chips
                  small-chips
                  deletable-chips
                  class="mb-3"
                ></v-select>

                <!-- Period -->
                <v-text-field
                  v-model="filters.start_date"
                  label="Start Date"
                  type="date"
                  class="mb-3"
                ></v-text-field>

                <v-text-field
                  v-model="filters.end_date"
                  label="End Date"
                  type="date"
                  class="mb-3"
                ></v-text-field>

                <!-- Label Categories -->
                <v-select
                  v-model="filters.label_categories"
                  :items="availableLabels"
                  label="Label Categories"
                  multiple
                  chips
                  small-chips
                  deletable-chips
                  class="mb-3"
                ></v-select>

                <!-- Annotation Status -->
                <v-select
                  v-model="filters.annotation_status"
                  :items="statusOptions"
                  label="Annotation Status"
                  multiple
                  chips
                  small-chips
                  deletable-chips
                  class="mb-3"
                ></v-select>

                <!-- Sorting -->
                <v-select
                  v-model="filters.sort_by"
                  :items="sortOptions"
                  item-text="label"
                  item-value="value"
                  label="Sort By"
                  class="mb-3"
                ></v-select>

                <v-select
                  v-model="filters.order"
                  :items="[
                    { text: 'Most Recent', value: 'desc' },
                    { text: 'Most Old', value: 'asc' }
                  ]"
                  label="Order"
                  class="mb-4"
                ></v-select>

                <v-btn color="primary" type="submit" block class="mb-2" :loading="isLoading">
                  <v-icon left>mdi-magnify</v-icon>
                  Apply Filters
                </v-btn>

                <v-btn color="grey" block @click="clearFilters">
                  <v-icon left>mdi-filter-off</v-icon>
                  Clear Filters
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- Export Panel -->
          <v-card elevation="2" class="mt-4">
            <v-card-title class="success white--text">
              <v-icon left color="white">mdi-download</v-icon>
              Export
            </v-card-title>
            <v-card-text class="pa-4">
              <v-btn color="success" block class="mb-2" :loading="isExporting" @click="exportReport('csv')">
                <v-icon left>mdi-file-delimited</v-icon>
                Export CSV
              </v-btn>
              <v-btn color="red" block :loading="isExporting" @click="exportReport('pdf')">
                <v-icon left>mdi-file-pdf-box</v-icon>
                Export PDF
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Results Section -->
        <v-col cols="12" lg="9">
          <!-- Timeline View Toggle -->
          <v-card elevation="2" class="mb-4">
            <v-card-text class="pa-4">
              <v-row align="center">
                <v-col cols="auto">
                  <v-btn-toggle v-model="viewMode" mandatory>
                    <v-btn value="table">
                      <v-icon left>mdi-table</v-icon>
                      Table
                    </v-btn>
                    <v-btn value="timeline">
                      <v-icon left>mdi-timeline</v-icon>
                      Timeline
                    </v-btn>
                  </v-btn-toggle>
                </v-col>
                <v-spacer></v-spacer>
                <v-col cols="auto">
                  <v-chip color="info" text-color="white">
                    {{ filteredData.length }} records found
                  </v-chip>
                </v-col>
                <v-col cols="auto">
                  <v-btn
                    color="primary"
                    @click="refreshData"
                    :loading="isLoading"
                    small
                  >
                    <v-icon left>mdi-refresh</v-icon>
                    Refresh
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Table View -->
          <v-card v-if="viewMode === 'table'" elevation="2">
            <v-card-title class="info white--text">
              <v-icon left color="white">mdi-table</v-icon>
              Annotation History
            </v-card-title>
            
            <v-card-text class="pa-0">
              <v-skeleton-loader
                v-if="isLoading"
                type="table"
                class="ma-4"
              ></v-skeleton-loader>
              
              <v-data-table
                v-else
                :headers="tableHeaders"
                :items="filteredData"
                :loading="isLoading"
                :items-per-page="15"
                class="elevation-0"
              >
                <template #[`item.action_description`]="{ item }">
                  <div>
                    <div class="font-weight-medium">{{ item.action }} in {{ getShortText(item.text) }}</div>
                    <div class="caption grey--text">{{ formatDate(item.timestamp) }} {{ formatTime(item.timestamp) }}</div>
                  </div>
                </template>

                <template #[`item.annotation_info`]="{ item }">
                  <div>
                    <div class="font-weight-medium">Annotated {{ item.label || 'Unknown' }}</div>
                    <div class="caption grey--text d-flex align-center">
                      <v-avatar size="16" color="primary" class="mr-1">
                        <v-icon color="white" size="10">mdi-account</v-icon>
                      </v-avatar>
                      {{ item.annotator }}
                    </div>
                  </div>
                </template>

                <template #[`item.details`]="{ item }">
                  <v-btn
                    icon
                    small
                    @click="showDetails(item)"
                  >
                    <v-icon>mdi-eye</v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>

          <!-- Timeline View -->
          <v-card v-else-if="viewMode === 'timeline'" elevation="2">
            <v-card-title class="info white--text">
              <v-icon left color="white">mdi-timeline</v-icon>
              Annotation Timeline
            </v-card-title>
            
            <v-card-text class="pa-4">
              <v-timeline v-if="!isLoading && timelineData.length > 0" align-top>
                <v-timeline-item
                  v-for="(item, index) in timelineData"
                  :key="index"
                  :color="getActionColor(item.action)"
                  small
                >
                  <template #opposite>
                    <span class="caption grey--text">{{ formatTime(item.timestamp) }}</span>
                  </template>
                  
                  <v-card class="elevation-2">
                    <v-card-text class="pa-3">
                      <div class="d-flex align-center mb-2">
                        <v-avatar size="24" :color="getActionColor(item.action)" class="mr-2">
                          <v-icon color="white" size="12">{{ getActionIcon(item.action) }}</v-icon>
                        </v-avatar>
                        <span class="font-weight-medium">{{ item.annotator }}</span>
                        <v-spacer></v-spacer>
                        <span class="caption">{{ formatDate(item.timestamp) }}</span>
                      </div>
                      
                      <div class="mb-2">
                        <strong>{{ item.action }} in {{ getShortText(item.text) }}</strong>
                      </div>
                      
                      <div class="caption grey--text">
                        Annotated {{ item.label || 'Unknown' }}
                      </div>
                    </v-card-text>
                  </v-card>
                </v-timeline-item>
              </v-timeline>
              
              <div v-else-if="!isLoading" class="text-center py-8">
                <v-icon size="64" color="grey lighten-2">mdi-timeline-outline</v-icon>
                <div class="headline mt-4 grey--text">No history found</div>
                <div class="caption grey--text">Adjust filters to see more results</div>
              </div>
              
              <v-skeleton-loader
                v-else
                type="card@3"
              ></v-skeleton-loader>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="600px">
      <v-card v-if="selectedItem">
        <v-card-title class="primary white--text">
          <v-icon left color="white">mdi-information</v-icon>
          Annotation Details
        </v-card-title>
        
        <v-card-text class="pa-4">
          <v-row>
            <v-col cols="6">
              <strong>Annotator:</strong><br>
              {{ selectedItem.annotator }}
            </v-col>
            <v-col cols="6">
              <strong>Action:</strong><br>
              <v-chip :color="getActionColor(selectedItem.action)" text-color="white" small>
                {{ selectedItem.action }}
              </v-chip>
            </v-col>
          </v-row>
          
          <v-row class="mt-3">
            <v-col cols="6">
              <strong>Date/Time:</strong><br>
              {{ formatDateTime(selectedItem.timestamp) }}
            </v-col>
            <v-col cols="6">
              <strong>Label:</strong><br>
              <v-chip v-if="selectedItem.label" color="primary" outlined small>
                {{ selectedItem.label }}
              </v-chip>
              <span v-else class="grey--text">N/A</span>
            </v-col>
          </v-row>
          
          <v-row v-if="selectedItem.text" class="mt-3">
            <v-col cols="12">
              <strong>Annotated Text:</strong><br>
              <div class="mt-2 pa-3 grey lighten-4 rounded">
                {{ selectedItem.text }}
              </div>
            </v-col>
          </v-row>
          
          <v-row v-if="selectedItem.confidence" class="mt-3">
            <v-col cols="12">
              <strong>Confidence:</strong><br>
              <v-progress-linear
                :value="selectedItem.confidence * 100"
                color="primary"
                height="20"
                class="mt-2"
              >
                <template #default="{ value }">
                  <strong>{{ Math.ceil(value) }}%</strong>
                </template>
              </v-progress-linear>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="detailsDialog = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'

interface HistoryItem {
  id: number
  annotator: string
  annotator_id: number
  action: string
  timestamp: string
  label?: string
  text?: string
  confidence?: number
  document_id?: number
}

export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth', 'auth'],

  data() {
    return {
      viewMode: 'table' as 'table' | 'timeline',
      isLoading: false,
      isExporting: false,
      historyData: [] as HistoryItem[],
      availableAnnotators: [] as Array<{id: number, username: string}>,
      availableLabels: [] as string[],
      detailsDialog: false,
      selectedItem: null as HistoryItem | null,
      
      filters: {
        annotator_ids: [] as number[],
        action_type: [] as string[],
        start_date: '',
        end_date: '',
        label_categories: [] as string[],
        annotation_status: [] as string[],
        sort_by: 'timestamp',
        order: 'desc'
      },

      actionTypes: [
        'Create',
        'Update', 
        'Delete',
        'Review',
        'Approve',
        'Reject'
      ],

      statusOptions: [
        'Active',
        'Inactive',
        'Pending',
        'Approved',
        'Rejected'
      ],

      sortOptions: [
        { label: 'Date/Time', value: 'timestamp' },
        { label: 'Annotator', value: 'annotator' },
        { label: 'Action', value: 'action' },
        { label: 'Label', value: 'label' }
      ],

      tableHeaders: [
        { text: 'Action', value: 'action_description', sortable: true },
        { text: 'Annotation', value: 'annotation_info', sortable: true },
        { text: 'Details', value: 'details', sortable: false }
      ]
    }
  },

  computed: {
    projectId(): string {
      return this.$route.params.id
    },

    filteredData(): HistoryItem[] {
      let data = [...this.historyData]

      // Apply filters
      if (this.filters.annotator_ids.length > 0) {
        data = data.filter(item => this.filters.annotator_ids.includes(item.annotator_id))
      }

      if (this.filters.action_type.length > 0) {
        data = data.filter(item => this.filters.action_type.includes(item.action))
      }

      if (this.filters.start_date) {
        data = data.filter(item => item.timestamp >= this.filters.start_date)
      }

      if (this.filters.end_date) {
        data = data.filter(item => item.timestamp <= this.filters.end_date)
      }

      if (this.filters.label_categories.length > 0) {
        data = data.filter(item => item.label && this.filters.label_categories.includes(item.label))
      }

      // Sort
      data.sort((a, b) => {
        const aVal = a[this.filters.sort_by as keyof HistoryItem] || ''
        const bVal = b[this.filters.sort_by as keyof HistoryItem] || ''
        
        if (this.filters.order === 'desc') {
          return bVal > aVal ? 1 : -1
        } else {
          return aVal > bVal ? 1 : -1
        }
      })

      return data
    },

    timelineData(): HistoryItem[] {
      return this.filteredData.slice(0, 50) // Limit timeline for performance
    },

    summaryStats() {
      const data = this.filteredData
      return {
        totalAnnotations: data.length,
        uniqueAnnotators: new Set(data.map(item => item.annotator_id)).size,
        totalCreated: data.filter(item => item.action === 'Create').length,
        totalDeleted: data.filter(item => item.action === 'Delete').length
      }
    }
  },

  async mounted() {
    await this.loadData()
  },

  methods: {
    async loadData() {
      this.isLoading = true
      try {
        console.log('🔄 Loading annotation history data...')
        console.log('📋 Project ID:', this.projectId)
        console.log('👤 Current user:', this.$auth?.user?.username || 'Unknown')
        
        await Promise.all([
          this.loadHistoryData(),
          this.loadAnnotators(),
          this.loadLabels()
        ])
      } catch (error) {
        console.error('Error loading data:', error)
      } finally {
        this.isLoading = false
      }
    },

    async loadHistoryData() {
      try {
        const filters = {
          ...this.filters,
          project_id: this.projectId
        }
        // Adicionar timestamp para evitar cache
        const timestamp = new Date().getTime()
        console.log(`🔄 Loading history data at ${timestamp}`)
        this.historyData = await this.$repositories.annotationHistory.list(this.projectId, filters)
        console.log(`✅ Loaded ${this.historyData.length} history items`)
      } catch (error) {
        console.error('Error loading history:', error)
        this.historyData = []
      }
    },

    async loadAnnotators() {
      try {
        const members = await this.$repositories.member.list(this.projectId)
        this.availableAnnotators = members.map(member => ({
          id: member.user,
          username: member.username
        }))
      } catch (error) {
        console.error('Error loading annotators:', error)
      }
    },

    async loadLabels() {
      try {
        // Carregar tipos de label do projeto
        const [categoryTypes, spanTypes, relationTypes] = await Promise.all([
          this.$repositories.categoryType.list(this.projectId).catch(() => []),
          this.$repositories.spanType.list(this.projectId).catch(() => []),
          this.$repositories.relationType.list(this.projectId).catch(() => [])
        ])

        // Combinar todos os tipos de label
        const allLabels = [
          ...categoryTypes.map((type: any) => type.text),
          ...spanTypes.map((type: any) => type.text),
          ...relationTypes.map((type: any) => type.text)
        ]

        // Remover duplicatas e ordenar
        this.availableLabels = [...new Set(allLabels)].sort()
        
        // Se não houver labels, usar fallback
        if (this.availableLabels.length === 0) {
          this.availableLabels = [
            'Person',
            'Organization', 
            'Location',
            'Date',
            'Product',
            'Event'
          ]
        }
      } catch (error) {
        console.error('Error loading labels:', error)
        // Fallback para labels padrão
        this.availableLabels = [
          'Person',
          'Organization', 
          'Location',
          'Date',
          'Product',
          'Event'
        ]
      }
    },

    applyFilters() {
      // Filters are applied automatically via computed property
      console.log('Filters applied:', this.filters)
    },

    clearFilters() {
      this.filters = {
        annotator_ids: [],
        action_type: [],
        start_date: '',
        end_date: '',
        label_categories: [],
        annotation_status: [],
        sort_by: 'timestamp',
        order: 'desc'
      }
    },

    async exportReport(format: 'csv' | 'pdf') {
      this.isExporting = true
      try {
        const filters = {
          ...this.filters,
          project_id: this.projectId
        }
        const blob = await this.$repositories.annotationHistory.export(this.projectId, format, filters)
        
        // Create file download
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `annotation-history-${this.projectId}.${format}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        console.log(`Report exported in ${format} format`)
      } catch (error) {
        console.error('Error exporting:', error)
      } finally {
        this.isExporting = false
      }
    },

    showDetails(item: HistoryItem) {
      this.selectedItem = item
      this.detailsDialog = true
    },

    getActionColor(action: string): string {
      const colors: {[key: string]: string} = {
        'Create': 'success',
        'Update': 'primary',
        'Delete': 'error',
        'Review': 'warning',
        'Approve': 'success',
        'Reject': 'error'
      }
      return colors[action] || 'grey'
    },

    getActionIcon(action: string): string {
      const icons: {[key: string]: string} = {
        'Create': 'mdi-plus',
        'Update': 'mdi-pencil',
        'Delete': 'mdi-delete',
        'Review': 'mdi-eye',
        'Approve': 'mdi-check',
        'Reject': 'mdi-close'
      }
      return icons[action] || 'mdi-help'
    },

    formatDate(timestamp: string): string {
      return new Date(timestamp).toLocaleDateString('en-US')
    },

    formatTime(timestamp: string): string {
      return new Date(timestamp).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },

    formatDateTime(timestamp: string): string {
      return new Date(timestamp).toLocaleString('en-US')
    },

    getShortText(text: string): string {
      if (!text) return 'Unknown Text'
      return text.length > 30 ? text.substring(0, 30) + '...' : text
    },

    async refreshData() {
      await this.loadData()
    }
  }
})
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.v-card {
  border-radius: 12px !important;
}

.v-chip {
  border-radius: 16px !important;
}

.v-btn {
  border-radius: 8px !important;
}

.v-timeline-item {
  margin-bottom: 16px;
}

.elevation-0 {
  box-shadow: none !important;
}
</style> 