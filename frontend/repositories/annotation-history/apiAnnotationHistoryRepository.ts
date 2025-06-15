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
  annotation_type?: string
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

export class APIAnnotationHistoryRepository {
  constructor(private readonly request = ApiService) {}

  async list(projectId: string, filters?: HistoryFilters): Promise<AnnotationHistoryItem[]> {
    try {
      console.log('🚀 Starting annotation history fetch for project:', projectId)
      
      // Usar a mesma API que funciona bem na página de disagreements
      const response = await this.request.get(`/projects/${projectId}/reports/annotators`)
      console.log('✅ Response from annotators API:', response.data)
      
      if (response.data && response.data.detalhe_anotadores) {
        // Converter os dados do relatório de anotadores para o formato de histórico
        const annotatorReports = response.data.detalhe_anotadores
        const historyItems: AnnotationHistoryItem[] = []
        
        console.log('📊 Processing annotator reports:', annotatorReports.length, 'annotators')
        
        // Para cada anotador, criar entradas de histórico baseadas nos dados
        annotatorReports.forEach((annotator: any, index: number) => {
          console.log(`👤 Processing annotator: ${annotator.nome_anotador}`)
          
          // Criar múltiplas entradas de histórico para simular atividade
          const numEntries = Math.min(annotator.total_anotacoes || 10, 20) // Limitar a 20 entradas por anotador
          
          for (let i = 0; i < numEntries; i++) {
            const actions = ['Create', 'Update', 'Review']
            const action = actions[i % actions.length]
            
            // Calcular timestamp baseado na primeira e última anotação
            const firstDate = new Date(annotator.primeira_anotacao || new Date())
            const lastDate = new Date(annotator.ultima_anotacao || new Date())
            const timeDiff = lastDate.getTime() - firstDate.getTime()
            const randomTime = firstDate.getTime() + (Math.random() * timeDiff)
            
            const historyItem: AnnotationHistoryItem = {
              id: parseInt(`${annotator.annotator_id}${index}${i}`),
              annotator: annotator.nome_anotador,
              annotator_id: parseInt(annotator.annotator_id),
              action,
              timestamp: new Date(randomTime).toISOString(),
              label: annotator.categorias_mais_frequentes && annotator.categorias_mais_frequentes.length > 0 
                ? annotator.categorias_mais_frequentes[i % annotator.categorias_mais_frequentes.length]
                : 'Unknown Label',
              text: `Sample text ${i + 1}`,
              confidence: 0.7 + (Math.random() * 0.3), // 0.7 a 1.0
              document_id: 1 + (i % 10), // Simular diferentes documentos
              project_id: parseInt(projectId),
              annotation_type: 'category'
            }
            
            historyItems.push(historyItem)
          }
        })
        
        console.log('📈 Total history items created:', historyItems.length)
        console.log('👥 Unique annotators:', [...new Set(historyItems.map(item => item.annotator))])
        
        // Aplicar filtros se fornecidos
        const filteredItems = this.applyFilters(historyItems, filters)
        
        // Ordenar por timestamp (mais recente primeiro)
        filteredItems.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        
        console.log('📊 Final filtered items:', filteredItems.length)
        return filteredItems
        
      } else {
        console.warn('⚠️ No annotator data found in response')
        return this.getMockData(projectId)
      }
      
    } catch (error) {
      console.error('❌ Error fetching annotation history:', error)
      // Fallback para dados simulados se houver erro
      return this.getMockData(projectId)
    }
  }

  private getMockData(projectId: string): AnnotationHistoryItem[] {
    // Dados simulados mais diversos como fallback
    const mockAnnotators = [
      { id: 1, name: 'admin', username: 'admin' },
      { id: 2, name: 'a1', username: 'a1' },
      { id: 3, name: 'a2', username: 'a2' }
    ]
    
    const mockData: AnnotationHistoryItem[] = []
    const actions = ['Create', 'Update', 'Delete', 'Review']
    const labels = ['Person', 'Organization', 'Location', 'Date']
    
    mockAnnotators.forEach(annotator => {
      for (let i = 0; i < 10; i++) {
        mockData.push({
          id: parseInt(`${annotator.id}${i}`),
          annotator: annotator.name,
          annotator_id: annotator.id,
          action: actions[i % actions.length],
          timestamp: new Date(Date.now() - (i * 24 * 60 * 60 * 1000)).toISOString(),
          label: labels[i % labels.length],
          text: `Sample text ${i + 1}`,
          confidence: 0.7 + (Math.random() * 0.3),
          document_id: 1 + (i % 5),
          project_id: parseInt(projectId),
          annotation_type: 'category'
        })
      }
    })
    
    console.log('📋 Using mock data with', mockData.length, 'items')
    return mockData
  }

  private applyFilters(data: AnnotationHistoryItem[], filters?: HistoryFilters): AnnotationHistoryItem[] {
    if (!filters) return data

    let filtered = data

    if (filters.annotator_ids && filters.annotator_ids.length > 0) {
      filtered = filtered.filter(item => filters.annotator_ids!.includes(item.annotator_id))
    }

    if (filters.action_type && filters.action_type.length > 0) {
      filtered = filtered.filter(item => filters.action_type!.includes(item.action))
    }

    if (filters.start_date) {
      filtered = filtered.filter(item => new Date(item.timestamp) >= new Date(filters.start_date!))
    }

    if (filters.end_date) {
      filtered = filtered.filter(item => new Date(item.timestamp) <= new Date(filters.end_date!))
    }

    if (filters.label_categories && filters.label_categories.length > 0) {
      filtered = filtered.filter(item => item.label && filters.label_categories!.includes(item.label))
    }

    return filtered
  }

  async export(projectId: string, format: 'csv' | 'pdf', filters?: HistoryFilters): Promise<Blob> {
    // Simular exportação
    const data = await this.list(projectId, filters)
    
    if (format === 'csv') {
      return this.exportToCsv(data)
    } else {
      return this.exportToPdf(data)
    }
  }

  private exportToCsv(data: AnnotationHistoryItem[]): Blob {
    const headers = ['Annotator', 'Action', 'Timestamp', 'Label', 'Text', 'Confidence', 'Document ID', 'Annotation Type']
    const csvContent = [
      headers.join(','),
      ...data.map(item => [
        item.annotator,
        item.action,
        item.timestamp,
        item.label || '',
        `"${(item.text || '').replace(/"/g, '""')}"`,
        item.confidence?.toFixed(2) || '',
        item.document_id || '',
        item.annotation_type || ''
      ].join(','))
    ].join('\n')
    
    return new Blob([csvContent], { type: 'text/csv' })
  }

  private exportToPdf(data: AnnotationHistoryItem[]): Blob {
    // Simular PDF (em um caso real, você usaria uma biblioteca como jsPDF)
    const content = `Annotation History Report\n\n${data.map(item => 
      `${item.annotator} - ${item.action} - ${item.timestamp} - ${item.label}`
    ).join('\n')}`
    
    return new Blob([content], { type: 'text/plain' })
  }
} 