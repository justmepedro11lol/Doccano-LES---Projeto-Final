<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12" md="6">
    <v-select
      v-model="selectedExample"
      :items="exampleOptions"
          label="Filter by annotation"
      clearable
          outlined
          dense
          prepend-inner-icon="mdi-filter"
    />
      </v-col>
      <v-col cols="12" md="6">
        <v-text-field
          v-model="search"
          :prepend-inner-icon="mdiMagnify"
          label="Search"
          single-line
          hide-details
          outlined
          dense
        />
      </v-col>
    </v-row>

    <v-data-table
      :items="flatItems"
      :headers="headers"
      :loading="isLoading"
      :loading-text="$t('generic.loading')"
      :no-data-text="$t('vuetify.noDataAvailable')"
      :footer-props="{
        showFirstLastPage: true,
        'items-per-page-text': $t('vuetify.itemsPerPageText'),
        'page-text': $t('dataset.pageText')
      }"
      :item-key="itemKey"
      class="elevation-1"
      @input="$emit('input', $event)"
    >
      <template #[`item.exampleName`]="{ item }">
        <v-chip small color="primary" text-color="white">
        {{ item.exampleName }}
        </v-chip>
      </template>

      <template #[`item.labelPercentages`]="{ item }">
        <div class="label-percentages">
          <div 
            v-for="(percentage, label) in item.labelPercentages" 
            :key="label"
            class="label-percentage-item"
          >
            <div class="d-flex align-center justify-space-between mb-1">
              <span class="label-name font-weight-medium text-truncate">{{ label }}</span>
              <span class="percentage-value ml-2">{{ Math.round(percentage) }}%</span>
            </div>
            <v-progress-linear
              :value="percentage"
              :color="getPercentageColor(percentage)"
              height="6"
              rounded
              class="mb-1"
            />
          </div>
        </div>
      </template>

      <template #[`item.maxPercentage`]="{ item }">
        <div class="max-agreement-container">
          <v-progress-linear
            :value="item.maxPercentage"
            :color="getPercentageColor(item.maxPercentage)"
            height="16"
            rounded
          >
            <template #default="{ value }">
              <small class="white--text font-weight-bold">{{ Math.round(value) }}%</small>
            </template>
          </v-progress-linear>
        </div>
      </template>

      <template #[`item.discrepancyBool`]="{ item }">
        <v-chip
          :color="item.discrepancyBool === 'Yes' ? 'error' : 'success'"
          small
          dark
          class="font-weight-bold"
        >
          {{ item.discrepancyBool === 'Yes' ? 'Discrepant' : 'Consistent' }}
        </v-chip>
      </template>

      <template #[`item.actions`]="{ item }">
        <v-btn
          color="primary"
          outlined
          small
          @click="openDiscussion(item)"
        >
          <v-icon left small>mdi-forum</v-icon>
          Discuss
        </v-btn>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import { mdiMagnify, mdiPencil } from '@mdi/js'

export default {
  name: 'DiscrepancyList',

  props: {
    isLoading: { type: Boolean, default: false, required: true },
    items: { type: Object, required: true },
    discrepancyThreshold: { type: Number, default: 0, required: true }
  },

  data() {
    return {
      search: '',
      mdiMagnify,
      mdiPencil,
      selectedExample: null,
      exampleNameMap: {}
    }
  },

  computed: {
    headers () {
      return [
        { text: 'Example', value: 'exampleName', sortable: true },
        { text: 'Status', value: 'discrepancyBool', sortable: true },
        { text: 'Label Voting Percentages', value: 'labelPercentages', sortable: false },
        { text: 'Max Agreement', value: 'maxPercentage', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false }
      ]
    },

    flatItems () {
      const rows = []
      const source = this.filteredItems

      for (const [id, labels] of Object.entries(source)) {
        // Aguarda o nome ser carregado
        if (!this.exampleNameMap[id]) {
          continue
        }
        
        // Validar se o id é válido antes de processar
        if (!id || id === 'undefined' || id === 'null') {
          console.warn('Invalid exampleId found:', id)
          continue
        }

        const entries = Object.entries(labels)
        if (!entries.length) {
          console.warn('No labels found for example:', id)
          continue
        }

        // Encontrar a percentagem máxima para determinar se há discrepância
        const maxPercentage = Math.max(...entries.map(([, perc]) => perc))
        const hasDiscrepancy = maxPercentage < this.discrepancyThreshold
        const displayName = this.exampleNameMap[id]

        rows.push({
          exampleId: id.toString(),
          exampleName: displayName,
          labelPercentages: labels,
          discrepancyBool: hasDiscrepancy ? 'Yes' : 'No',
          maxPercentage
        })
      }

      return rows.filter(item =>
        item.exampleName.toLowerCase().includes(this.search.toLowerCase()) ||
        Object.keys(item.labelPercentages).some(label => 
          label.toLowerCase().includes(this.search.toLowerCase())
        )
      )
    },

    exampleOptions () {
      return [
        { text: 'All annotations', value: 'All annotations' },
        ...Object.entries(this.exampleNameMap).map(([id, name]) => ({
          text: name, value: id
        }))
      ]
    },

    filteredItems () {
      if (!this.selectedExample || this.selectedExample === 'All annotations') {
        return this.items
      }
      const sel = this.items[this.selectedExample]
      return sel ? { [this.selectedExample]: sel } : {}
    },

    itemKey () {
      return 'exampleId'
    }
  },

  watch: {
    items: {
      immediate: true,
      async handler(newItems) {
        if (newItems) {
          for (const id of Object.keys(newItems)) {
            await this.resolveExampleName(id)
          }
        }
      }
    }
  },

  methods: {
    async resolveExampleName(id) {
      if (this.exampleNameMap[id]) {
        return this.exampleNameMap[id]
      }

      try {
        const projectId = this.$route.params.id
        const example = await this.$repositories.example.findById(projectId, parseInt(id))
        const name = example.text || `Example ${id}`
        
        this.$set(this.exampleNameMap, id, name)
        return name
      } catch (error) {
        console.error(`Erro ao buscar exemplo ${id}:`, error)
        const fallbackName = `Example ${id}`
        this.$set(this.exampleNameMap, id, fallbackName)
        return fallbackName
      }
    },

    getPercentageColor(percentage) {
      if (percentage < this.discrepancyThreshold) return 'error'
      if (percentage < 70) return 'warning'
      return 'success'
    },

    openDiscussion(item) {
      // Redirecionar para página dedicada de discussão
      const projectId = this.$route.params.id
      this.$router.push(`/projects/${projectId}/discrepancies/${item.exampleId}/discuss`)
    }
  }
}
</script>

<style scoped>
.label-percentages {
  min-width: 200px;
}

.label-percentage-item {
  margin-bottom: 8px;
}

.label-percentage-item:last-child {
  margin-bottom: 0;
}

.label-name {
  max-width: 120px;
  font-size: 0.875rem;
}

.percentage-value {
  font-weight: bold;
  font-size: 0.875rem;
}

.max-agreement-container {
  min-width: 120px;
}
</style>

<style scoped>
.container {
  padding-left: 20px;
  padding-right: 20px;
  margin-top: 10px;
}

.label-percentages {
  min-width: 280px;
  max-width: 350px;
}

.label-percentage-item {
  margin-bottom: 6px;
  padding: 4px 6px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 2px solid #e0e0e0;
}

.label-name {
  font-size: 0.8rem;
  color: #424242;
  max-width: 160px;
}

.percentage-value {
  font-size: 0.75rem;
  font-weight: bold;
  color: #1976d2;
  min-width: 35px;
  text-align: right;
}

::v-deep .v-progress-linear {
  border-radius: 3px !important;
}

::v-deep .v-data-table td {
  vertical-align: top !important;
  padding-top: 12px !important;
  padding-bottom: 12px !important;
}

.max-agreement-container {
  width: 100%;
  min-width: 120px;
}
</style>
