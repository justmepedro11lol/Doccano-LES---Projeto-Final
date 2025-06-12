import ApiService from '@/services/api.service'
import { PerspectiveItem } from '~/domain/models/perspective/perspective'

function toModel(item: { [key: string]: any }): PerspectiveItem {
  return new PerspectiveItem(item.id, item.project_id, item.questions, item.members)
}

function toPayload(item: PerspectiveItem): { [key: string]: any } {
  return {
    id: item.id,
    project_id: item.project_id,
    questions: item.questions,
    members: item.members
  }
}

export class APIPerspectiveRepository {
  constructor(private readonly baseUrl = 'perspective', private readonly request = ApiService) {}

  async list(projectId: string): Promise<PerspectiveItem> {
    const url = `/projects/${projectId}/${this.baseUrl}s`;
    const response = await this.request.get(url);
    if (response.data.length === 0) {
      throw new Error('Nenhuma perspectiva encontrada.');
    }
    return toModel(response.data[0]); // Retorna apenas o primeiro item
  }

  async create(projectId: string, item: PerspectiveItem): Promise<PerspectiveItem> {
    const url = `/projects/${projectId}/${this.baseUrl}s/create`
    const payload = toPayload(item)
    const response = await this.request.post(url, payload)
    return toModel(response.data)
  }
}
