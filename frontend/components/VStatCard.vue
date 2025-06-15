<template>
  <v-card class="text-center" :color="color" dark>
    <v-card-text class="py-4">
      <v-icon size="48" class="mb-2">{{ icon }}</v-icon>
      <div class="text-h3 font-weight-bold mb-1">{{ formattedValue }}</div>
      <div class="text-subtitle-1">{{ title }}</div>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'VStatCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    icon: {
      type: String,
      default: 'mdi-information'
    },
    color: {
      type: String,
      default: 'primary'
    }
  },
  computed: {
    formattedValue() {
      if (typeof this.value === 'number') {
        return this.value.toLocaleString('pt-BR')
      }
      return this.value
    }
  }
}
</script> 