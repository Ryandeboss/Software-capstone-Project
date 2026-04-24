create table if not exists public.celebrity_embeddings (
  id uuid primary key default gen_random_uuid(),
  celebrity_name text not null,
  source_image text not null,
  embedding jsonb not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (celebrity_name, source_image)
);

