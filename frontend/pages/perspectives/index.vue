<template>
  <v-card>
    <v-card-title>
      <h1>Perspectives</h1>
      <v-spacer></v-spacer>
      
    </v-card-title>
    <v-card-text>
      <perspective-list
        v-model="selected"
        :items="items"
        :is-loading="isLoading"
        :members="members"
      />
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { mapGetters } from 'vuex'
import PerspectiveList from '@/components/perspective/PerspectiveList.vue'
import { PerspectiveDTO } from '~/services/application/perspective/perspectiveData'

export default {
  components: {
    PerspectiveList
  },

  layout: 'projects',
  middleware: ['check-auth', 'auth', 'isSuperUser'],

  data() {
    return {
      items: [] as PerspectiveDTO[],
      selected: [] as PerspectiveDTO[],
      isLoading: false,
      members: []
    }
  },

  async fetch() {
    await this.fetchPerspectives()
    this.fetchMembers()
  },

  computed: {
    ...mapGetters('auth', ['isStaff', 'isSuperUser'])
  },

  methods: {
    async fetchPerspectives() {
      this.isLoading = true
      try {
        const response = await this.$services.perspective.list()
        console.log('Fetched perspectives for general view:', response)
        this.items = response
      } catch (error) {
        console.error('Error fetching perspectives:', error)
        this.items = []
      } finally {
        this.isLoading = false
      }
    },

    fetchMembers() {
      // Como não há um projeto específico aqui, não precisamos buscar membros
      // Os membros serão carregados pelo componente PerspectiveList conforme necessário
      this.members = []
    }
  }
}
</script>

<style scoped>
.v-card {
  margin: 16px;
}
</style> 