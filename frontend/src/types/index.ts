export interface Project { id: string; name: string; description: string | null; created_at: string }
export type DocStatus = 'processing' | 'completed' | 'failed'
export interface DocumentItem {
  id: string; project_id: string; filename: string; status: DocStatus
  error: string | null; page_count: number | null; created_at: string
}
export interface Conversation { id: string; project_id: string; title: string; created_at: string }
export interface Source { index: number; document_id: string; filename: string; page_number: number; snippet: string }
export interface Message { id: string; role: 'user' | 'assistant'; content: string; sources: Source[]; created_at: string }
export interface ChatResponse { conversation_id: string; message: Message }
