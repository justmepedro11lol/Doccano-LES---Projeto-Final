import ApiService from '@/services/api.service'

export interface AnnotatorReportFilters {
  dataset_id?: string[]
  annotator_id?: string[]
  data_inicial?: string
  data_final?: string
  categoria_label?: string[]
  perspectiva_id?: string[]
  estado_desacordo?: 'todos' | 'em_desacordo' | 'resolvido'
  sort_by?: string
  order?: 'asc' | 'desc'
  page?: number
  page_size?: number
}

export interface AnnotatorDetail {
  annotator_id: string
  nome_anotador: string
  username: string
  total_anotacoes: number
  datasets_distintos: number
  tempo_total_min: number
  tempo_medio_por_anotacao_seg: number
  taxa_desacordo_percent: number
  desacordos_resolvidos: number
  score_concordancia_medio: number
  perspectivas_usadas: string[]
  categorias_mais_frequentes: string[]
  primeira_anotacao: string
  ultima_anotacao: string
}

export interface AnnotatorReport {
  filtros_aplicados: Record<string, any>
  resumo_global: {
    total_anotadores: number
    total_anotacoes: number
    taxa_desacordo_global_percent: number
    score_concordancia_global?: number
  }
  detalhe_anotadores: AnnotatorDetail[]
  pagination?: {
    total: number
    page: number
    pages: number
    per_page: number
  }
}

export interface AnnotatorReportMetadata {
  annotators: Array<{
    id: string
    name: string
    username: string
  }>
  categories: string[]
  perspectives: Array<{
    id: string
    name: string
  }>
  datasets: Array<{
    id: string
    name: string
  }>
  sort_options: Array<{
    value: string
    label: string
  }>
  disagreement_states: Array<{
    value: string
    label: string
  }>
}

export class APIAnnotatorReportRepository {
  constructor(private readonly request = ApiService) {}

  async getAnnotatorReport(projectId: string, filters: AnnotatorReportFilters): Promise<AnnotatorReport> {
    const url = `/projects/${projectId}/reports/annotators`
    const response = await this.request.get(url, { params: filters })
    return response.data
  }

  async getMetadata(projectId: string): Promise<AnnotatorReportMetadata> {
    const url = `/projects/${projectId}/reports/annotators/metadata`
    const response = await this.request.get(url)
    return response.data
  }

  async exportAnnotatorReport(projectId: string, filters: AnnotatorReportFilters & { format: 'csv' | 'pdf' }): Promise<Blob> {
    const url = `/projects/${projectId}/reports/annotators/export`
    const response = await this.request.get(url, { 
      params: filters,
      responseType: 'blob'
    })
    return response.data
  }
} 