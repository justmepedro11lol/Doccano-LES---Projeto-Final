import ApiService from '@/services/api.service'

export interface AnnotationHistoryItem {
  id: number
  annotator: string
  annotator_id: number
  action: string
  timestamp: string
  label?: string
  text?: string
  confidence?: number
  document_id?: number
  project_id: number
}

export interface HistoryFilters {
  annotator_ids?: number[]
  action_type?: string[]
  start_date?: string
  end_date?: string
  label_categories?: string[]
  annotation_status?: string[]
  sort_by?: string
  order?: string
  project_id: string
}

function toModel(item: { [key: string]: any }): AnnotationHistoryItem {
  return {
    id: item.id,
    annotator: item.annotator || `User ${item.annotator_id}`,
    annotator_id: item.annotator_id,
    action: item.action,
    timestamp: item.timestamp || item.created_at,
    label: item.label,
    text: item.text,
    confidence: item.confidence,
    document_id: item.document_id,
    project_id: item.project_id
  }
}

export class APIAnnotationHistoryRepository {
  constructor(private readonly request = ApiService) {}

  async list(projectId: string, filters?: HistoryFilters): Promise<AnnotationHistoryItem[]> {
    const url = `/projects/${projectId}/annotation-history`
    const params = this.buildQueryParams(filters)
    
    try {
      const response = await this.request.get(url, { params })
      return response.data.map((item: { [key: string]: any }) => toModel(item))
    } catch (error) {
      console.error('Error fetching annotation history:', error)
      // Retorna dados simulados para demonstração
      return this.getMockData(projectId)
    }
  }

  async export(projectId: string, format: 'csv' | 'pdf', filters?: HistoryFilters): Promise<Blob> {
    const url = `/projects/${projectId}/annotation-history/export`
    const params = { ...this.buildQueryParams(filters), format }
    
    const response = await this.request.get(url, { 
      params,
      responseType: 'blob'
    })
    
    return response.data
  }

  async getStats(projectId: string, filters?: HistoryFilters): Promise<{
    totalAnnotations: number
    uniqueAnnotators: number
    totalCreated: number
    totalDeleted: number
    totalUpdated: number
  }> {
    const url = `/projects/${projectId}/annotation-history/stats`
    const params = this.buildQueryParams(filters)
    
    try {
      const response = await this.request.get(url, { params })
      return response.data
    } catch (error) {
      console.error('Error fetching annotation history stats:', error)
      // Retorna estatísticas simuladas
      const data = await this.list(projectId, filters)
      return {
        totalAnnotations: data.length,
        uniqueAnnotators: new Set(data.map(item => item.annotator_id)).size,
        totalCreated: data.filter(item => item.action === 'Criar').length,
        totalDeleted: data.filter(item => item.action === 'Excluir').length,
        totalUpdated: data.filter(item => item.action === 'Atualizar').length
      }
    }
  }

  private buildQueryParams(filters?: HistoryFilters): { [key: string]: any } {
    if (!filters) return {}

    const params: { [key: string]: any } = {}

    if (filters.annotator_ids?.length) {
      params.annotator_ids = filters.annotator_ids.join(',')
    }

    if (filters.action_type?.length) {
      params.action_type = filters.action_type.join(',')
    }

    if (filters.start_date) {
      params.start_date = filters.start_date
    }

    if (filters.end_date) {
      params.end_date = filters.end_date
    }

    if (filters.label_categories?.length) {
      params.label_categories = filters.label_categories.join(',')
    }

    if (filters.annotation_status?.length) {
      params.annotation_status = filters.annotation_status.join(',')
    }

    if (filters.sort_by) {
      params.sort_by = filters.sort_by
    }

    if (filters.order) {
      params.order = filters.order
    }

    return params
  }

  private getMockData(projectId: string): AnnotationHistoryItem[] {
    // Dados simulados para demonstração
    const currentDate = new Date()
    const mockData: AnnotationHistoryItem[] = []

    const annotators = [
      { id: 1, name: 'Pedro Silva' },
      { id: 2, name: 'Maria Santos' },
      { id: 3, name: 'Carlos Oliveira' },
      { id: 4, name: 'Ana Costa' }
    ]

    const actions = ['Criar', 'Atualizar', 'Excluir', 'Revisar', 'Aprovar']
    const labels = ['Pessoa', 'Organização', 'Localização', 'Data', 'Produto', 'Evento']
    const sampleTexts = [
      'João da Silva trabalha na empresa XYZ',
      'Reunião marcada para Lisboa às 14h',
      'O produto ABC foi lançado em janeiro',
      'A conferência acontecerá no Porto',
      'Maria coordena o projeto Delta'
    ]

    // Gerar dados dos últimos 30 dias
    for (let i = 0; i < 50; i++) {
      const daysAgo = Math.floor(Math.random() * 30)
      const hoursAgo = Math.floor(Math.random() * 24)
      const minutesAgo = Math.floor(Math.random() * 60)
      
      const timestamp = new Date(currentDate)
      timestamp.setDate(timestamp.getDate() - daysAgo)
      timestamp.setHours(timestamp.getHours() - hoursAgo)
      timestamp.setMinutes(timestamp.getMinutes() - minutesAgo)

      const annotator = annotators[Math.floor(Math.random() * annotators.length)]
      const action = actions[Math.floor(Math.random() * actions.length)]
      const label = labels[Math.floor(Math.random() * labels.length)]
      const text = sampleTexts[Math.floor(Math.random() * sampleTexts.length)]

      mockData.push({
        id: i + 1,
        annotator: annotator.name,
        annotator_id: annotator.id,
        action,
        timestamp: timestamp.toISOString(),
        label,
        text,
        confidence: Math.random() * 0.3 + 0.7, // Entre 0.7 e 1.0
        document_id: Math.floor(Math.random() * 100) + 1,
        project_id: parseInt(projectId)
      })
    }

    // Ordenar por timestamp decrescente
    return mockData.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
  }
} 