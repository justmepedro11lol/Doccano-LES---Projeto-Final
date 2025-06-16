export interface ConsensusData {
  label_id: number
  label_text: string
  justification?: string
}

export interface AnnotatorInfo {
  value: number
  text: string
  username: string
  role?: string
}

export interface AnnotationData {
  id: number
  label: number
  start_offset?: number
  end_offset?: number
  user: number
  type: 'span' | 'category' | 'relation'
}

export interface DiscrepancyType {
  type: 'etiqueta-diferente' | 'span-diferente' | 'etiqueta-ausente' | 'none'
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
}

export interface DiscrepancyMessage {
  id: number
  user: string
  text: string
  created_at: string
  type?: 'message' | 'vote' | 'consensus' | 'system'
  vote_option?: string
  consensus_data?: ConsensusData
}

export interface DiscrepancyContext {
  docId: number
  annotation?: AnnotationData
  text?: string
  involvedAnnotators?: AnnotatorInfo[]
  discrepancyType?: DiscrepancyType
}

export interface VotingResult {
  option: string
  votes: number
  percentage: number
  color: string
  users: string[]
}

export interface DiscrepancyStats {
  total: number
  resolved: number
  pending: number
  byType: Record<string, number>
  byAnnotator: Record<string, number>
}

export interface DiscrepancyFilter {
  dataset?: string
  annotators: number[]
  disagreementStatus: 'pending' | 'resolved' | 'all'
  categories: number[]
  recordRange?: string
}

export interface DiscrepancyDocument {
  docId: number
  text: string
  annotations: Record<number, AnnotationData[]>
  isResolved: boolean
  discrepancyTypes: DiscrepancyType[]
  metadata?: Record<string, any>
}

export interface DiscrepancyResolution {
  docId: number
  resolvedBy: number
  resolvedAt: string
  resolutionType: 'consensus' | 'override' | 'vote'
  finalAnnotation?: AnnotationData
  notes?: string
}

export interface UserPermissions {
  canVote: boolean
  canProposeConsensus: boolean
  canResolve: boolean
  canViewAll: boolean
  canModerate: boolean
}

export interface DiscrepancyNotification {
  id: number
  type: 'new_discrepancy' | 'vote_cast' | 'consensus_proposed' | 'resolved'
  message: string
  timestamp: string
  read: boolean
  docId: number
}

export type DiscrepancyEvent = {
  type: 'message_added' | 'vote_submitted' | 'consensus_proposed' | 'resolved'
  data: any
  timestamp: string
  userId: number
}
  