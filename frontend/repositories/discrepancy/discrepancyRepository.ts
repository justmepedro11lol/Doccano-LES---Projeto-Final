// repositories/discrepancy/discrepancyRepositorie.ts

import ApiService from '@/services/api.service'
import type { DiscrepancyMessage } from '~/domain/models/example/discrepancy'

export class APIDiscrepancyRepository {
  constructor(private request = ApiService) {}

  async fetchMessages(projectId: string, exampleId: string): Promise<DiscrepancyMessage[]> {
    console.log('Buscando mensagens para projectId:', projectId, 'exampleId:', exampleId)
    try {
      const response = await this.request.get(`/projects/${projectId}/examples/${exampleId}/discrepancies/messages`)
      console.log('Resposta da API (tipo):', typeof response.data)
      console.log('Resposta da API (valor):', response.data)
      
      // A resposta já é um array de mensagens
      if (Array.isArray(response.data)) {
        console.log('Total de mensagens encontradas:', response.data.length)
        return response.data
      }
      
      // Se não for um array, verifica se tem a propriedade data
      const messages = response.data?.data
      if (Array.isArray(messages)) {
        console.log('Total de mensagens encontradas em data:', messages.length)
        return messages
      }
      
      console.log('Nenhuma mensagem encontrada')
      return []
    } catch (error) {
      console.error('Erro ao buscar mensagens:', error)
      throw error
    }
  }

  postMessage(projectId: string, exampleId: string, text: string) {
    console.log('Enviando mensagem para projectId:', projectId, 'exampleId:', exampleId, 'text:', text)
    return this.request
      .post(`/projects/${projectId}/examples/${exampleId}/discrepancies/messages`, { text })
      .then(res => {
        console.log('Resposta da API (postMessage):', res.data)
        return res.data
      })
  }
}
