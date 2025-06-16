// repositories/discrepancy/discrepancyRepository.ts

import ApiService from '@/services/api.service'
import type { DiscrepancyMessage } from '~/domain/models/example/discrepancy'

export interface DiscrepancyParams {
  status?: 'pending' | 'reviewing' | 'resolved' | 'ignored'
  discrepancy_type?: string
  priority?: number
  example?: number
  search?: string
  ordering?: string
  limit?: number
  offset?: number
}

export interface DetectDiscrepanciesResponse {
  message: string
  discrepancies: any[]
}

export interface DiscrepancyResolutionSuggestion {
  suggested_action: string
  confidence: number
  reasoning: string
  recommended_label?: any
}

export class APIDiscrepancyRepository {
  constructor(private request = ApiService) {}

  async list(projectId: string, params: DiscrepancyParams = {}): Promise<any[]> {
    console.log('🔍 Buscando discrepâncias para projeto:', projectId, 'com parâmetros:', params)
    try {
      const response = await this.request.get(`/projects/${projectId}/discrepancies/`, { params })
      console.log('✅ Discrepâncias encontradas:', response.data)
      
      // A API pode retornar um array direto ou um objeto com results
      if (Array.isArray(response.data)) {
        return response.data
      }
      
      if (response.data?.results && Array.isArray(response.data.results)) {
        return response.data.results
      }
      
      return []
    } catch (error) {
      console.error('❌ Erro ao buscar discrepâncias:', error)
      throw error
    }
  }

  async findById(projectId: string, discrepancyId: number): Promise<any> {
    console.log('🔍 Buscando discrepância por ID:', discrepancyId)
    try {
      const response = await this.request.get(`/projects/${projectId}/discrepancies/${discrepancyId}/`)
      return response.data
    } catch (error) {
      console.error('❌ Erro ao buscar discrepância por ID:', error)
      throw error
    }
  }

  async create(projectId: string, discrepancyData: any): Promise<any> {
    console.log('📝 Criando nova discrepância:', discrepancyData)
    try {
      const response = await this.request.post(`/projects/${projectId}/discrepancies/`, discrepancyData)
      return response.data
    } catch (error) {
      console.error('❌ Erro ao criar discrepância:', error)
      throw error
    }
  }

  async update(projectId: string, discrepancyId: number, discrepancyData: any): Promise<any> {
    console.log('✏️ Atualizando discrepância:', discrepancyId, discrepancyData)
    try {
      const response = await this.request.put(`/projects/${projectId}/discrepancies/${discrepancyId}/`, discrepancyData)
      return response.data
    } catch (error) {
      console.error('❌ Erro ao atualizar discrepância:', error)
      throw error
    }
  }

  async delete(projectId: string, discrepancyId: number): Promise<void> {
    console.log('🗑️ Deletando discrepância:', discrepancyId)
    try {
      await this.request.delete(`/projects/${projectId}/discrepancies/${discrepancyId}/`)
    } catch (error) {
      console.error('❌ Erro ao deletar discrepância:', error)
      throw error
    }
  }

  async detectDiscrepancies(projectId: string): Promise<DetectDiscrepanciesResponse> {
    console.log('🤖 Detectando discrepâncias automaticamente para projeto:', projectId)
    try {
      const response = await this.request.post(`/projects/${projectId}/discrepancies/detect/`)
      console.log('✅ Resultado da detecção automática:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Erro ao detectar discrepâncias:', error)
      throw error
    }
  }

  async resolve(projectId: string, discrepancyId: number, resolutionNotes: string = ''): Promise<any> {
    console.log('✅ Resolvendo discrepância:', discrepancyId, 'com notas:', resolutionNotes)
    try {
      const response = await this.request.post(`/projects/${projectId}/discrepancies/${discrepancyId}/resolve/`, {
        resolution_notes: resolutionNotes
      })
      return response.data
    } catch (error) {
      console.error('❌ Erro ao resolver discrepância:', error)
      throw error
    }
  }

  async suggestResolution(projectId: string, discrepancyId: number): Promise<DiscrepancyResolutionSuggestion> {
    console.log('💡 Buscando sugestão de resolução para discrepância:', discrepancyId)
    try {
      const response = await this.request.get(`/projects/${projectId}/discrepancies/${discrepancyId}/suggest-resolution/`)
      return response.data
    } catch (error) {
      console.error('❌ Erro ao buscar sugestão de resolução:', error)
      throw error
    }
  }

  async addComment(projectId: string, discrepancyId: number, comment: string): Promise<any> {
    console.log('💬 Adicionando comentário à discrepância:', discrepancyId, comment)
    try {
      const response = await this.request.post(`/projects/${projectId}/discrepancies/${discrepancyId}/comments/`, {
        comment
      })
      return response.data
    } catch (error) {
      console.error('❌ Erro ao adicionar comentário:', error)
      throw error
    }
  }

  async getStatistics(projectId: string): Promise<any> {
    console.log('📊 Buscando estatísticas de discrepâncias para projeto:', projectId)
    try {
      const response = await this.request.get(`/projects/${projectId}/discrepancies/statistics/`)
      return response.data
    } catch (error) {
      console.error('❌ Erro ao buscar estatísticas:', error)
      throw error
    }
  }

  // Métodos legados para compatibilidade com chat
  async fetchMessages(projectId: string): Promise<DiscrepancyMessage[]> {
    console.log('📨 Buscando mensagens do chat para projectId:', projectId)
    try {
      const response = await this.request.get(`/projects/${projectId}/discrepancies/messages`)
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
      console.error('❌ Erro ao buscar mensagens:', error)
      throw error
    }
  }

  postMessage(projectId: string, text: string) {
    console.log('📤 Enviando mensagem para o chat do projectId:', projectId, 'text:', text)
    return this.request
      .post(`/projects/${projectId}/discrepancies/messages`, { text })
      .then(res => {
        console.log('✅ Resposta da API (postMessage):', res.data)
        return res.data
      })
  }
}
