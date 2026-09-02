-- Skema penyimpanan bersama untuk Perpustakaan naskah (Supabase / Postgres).
-- Jalankan sekali pada proyek Supabase yang dipilih (SQL Editor, atau apply_migration).
--
-- Dua tabel + satu bucket:
--   papers          naskah yang diunggah lewat tab Perpustakaan (isi HTML sudah diparse di klien)
--   paper_comments  komentar pembimbing, tertambat ke blok naskah (data-b)
--   bucket "papers" berkas asli (.docx/.md/.pdf) supaya bisa diunduh
--
-- Kebijakan akses:
--   anon  : baca semua naskah & komentar; tulis/ubah/hapus komentar (dashboard privat pembimbing)
--   upload: HANYA lewat api/papers.js dengan kunci layanan + kata sandi PAPERS_UPLOAD_KEY

create table if not exists public.papers (
  id          text primary key,                 -- slug, mis. "paper5-feeder-level"
  n           int,                              -- nomor urut di perpustakaan
  title       text not null,
  short       text,
  kind        text default 'Journal article',
  venue       text,
  alt         text,
  status      text default 'draft',             -- draft | review | submitted | plan
  stage       text,
  pct         int  default 0,
  target      text,
  lead        text,
  data        jsonb default '[]'::jsonb,
  method      jsonb default '[]'::jsonb,
  todo        jsonb default '[]'::jsonb,
  tabs        jsonb default '[]'::jsonb,
  category    text,                             -- akses | jaringan | emisi | bisnis
  abstract    text,                             -- abstrak apa adanya
  goal        text,                             -- tujuan riset (brief)
  finding     text,                             -- temuan kunci (brief)
  html        text not null,                    -- isi naskah, blok bernomor data-b
  words       int  default 0,
  file_name   text,
  file_path   text,                             -- path di bucket "papers"
  file_size   int,
  uploaded_by text,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

create table if not exists public.paper_comments (
  id          text primary key,
  paper_id    text not null,
  b           int  not null,                    -- indeks blok (data-b)
  quote       text,
  text        text not null,
  tag         text default 'tanya',             -- mayor | minor | tanya | setuju
  who         text,
  resolved    boolean default false,
  ts          bigint,                           -- epoch ms dari klien
  created_at  timestamptz default now()
);
create index if not exists paper_comments_paper_idx on public.paper_comments (paper_id, b);

alter table public.papers          enable row level security;
alter table public.paper_comments  enable row level security;

drop policy if exists papers_read      on public.papers;
drop policy if exists comments_read    on public.paper_comments;
drop policy if exists comments_write   on public.paper_comments;
drop policy if exists comments_update  on public.paper_comments;
drop policy if exists comments_delete  on public.paper_comments;

create policy papers_read     on public.papers          for select to anon, authenticated using (true);
create policy comments_read   on public.paper_comments  for select to anon, authenticated using (true);
create policy comments_write  on public.paper_comments  for insert to anon, authenticated with check (true);
create policy comments_update on public.paper_comments  for update to anon, authenticated using (true) with check (true);
create policy comments_delete on public.paper_comments  for delete to anon, authenticated using (true);
-- Tidak ada kebijakan insert/update/delete untuk papers: hanya kunci layanan (api/papers.js) yang boleh.

insert into storage.buckets (id, name, public)
  values ('papers', 'papers', true)
  on conflict (id) do update set public = true;

drop policy if exists papers_bucket_read on storage.objects;
create policy papers_bucket_read on storage.objects
  for select to anon, authenticated using (bucket_id = 'papers');
-- Unggah ke bucket hanya lewat kunci layanan.
