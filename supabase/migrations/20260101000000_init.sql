-- Industrial Document AI: initial schema
create extension if not exists vector;

-- profiles (linked to Supabase Auth)
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text,
  created_at timestamptz not null default now()
);

create function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email) values (new.id, new.email);
  return new;
end $$;

create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

create table public.projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  description text,
  created_at timestamptz not null default now()
);
create index on public.projects (user_id);

create table public.documents (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  filename text not null,
  storage_path text not null,
  status text not null default 'processing' check (status in ('processing','completed','failed')),
  error text,
  page_count int,
  created_at timestamptz not null default now()
);
create index on public.documents (project_id);

create table public.document_chunks (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  document_id uuid not null references public.documents(id) on delete cascade,
  chunk_index int not null,
  filename text not null,
  page_number int not null,
  content text not null,
  embedding vector(384) not null,  -- intfloat/multilingual-e5-small
  fts tsvector generated always as (to_tsvector('simple', content)) stored
);
create index on public.document_chunks (project_id);
create index on public.document_chunks (document_id);
create index document_chunks_embedding_idx on public.document_chunks using hnsw (embedding vector_cosine_ops);
create index document_chunks_fts_idx on public.document_chunks using gin (fts);

create table public.conversations (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  created_at timestamptz not null default now()
);
create index on public.conversations (project_id, user_id);

create table public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  role text not null check (role in ('user','assistant')),
  content text not null,
  sources jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);
create index on public.messages (conversation_id, created_at);

-- Row Level Security (defense in depth: FastAPI connects with a privileged role and also checks ownership)
alter table public.profiles enable row level security;
alter table public.projects enable row level security;
alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;

create policy "own profile" on public.profiles for all using (id = auth.uid()) with check (id = auth.uid());
create policy "own projects" on public.projects for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "own documents" on public.documents for all
  using (exists (select 1 from public.projects p where p.id = project_id and p.user_id = auth.uid()));
create policy "own chunks" on public.document_chunks for select
  using (exists (select 1 from public.projects p where p.id = project_id and p.user_id = auth.uid()));
create policy "own conversations" on public.conversations for all
  using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "own messages" on public.messages for all
  using (exists (select 1 from public.conversations c where c.id = conversation_id and c.user_id = auth.uid()));

-- Private storage bucket for original PDFs (accessed only via the backend service-role key)
insert into storage.buckets (id, name, public) values ('documents', 'documents', false)
on conflict (id) do nothing;
