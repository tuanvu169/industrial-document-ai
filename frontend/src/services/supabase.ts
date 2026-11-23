import { createClient } from '@supabase/supabase-js'

// Only the public anon key lives in the frontend. Service-role and Gemini keys stay in the backend.
export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL ?? 'http://localhost',
  import.meta.env.VITE_SUPABASE_ANON_KEY ?? 'missing-anon-key',
)
