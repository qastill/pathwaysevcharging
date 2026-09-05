-- Ngecas — optional shared backend (Supabase). The app runs fully on-device without this.
-- Run in the SQL editor, then set VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY at build time.
create extension if not exists pgcrypto;

create table if not exists public.hosts (
  id text primary key,
  owner uuid references auth.users(id) on delete cascade,
  name text not null, host text not null, address text, area text, city text, province text default 'Jawa Barat',
  lat double precision not null, lng double precision not null,
  kw numeric not null default 7, plug text not null default 'Type 2', price_kwh integer not null,
  days text not null default 'daily', "from" text not null default '18:00', "to" text not null default '06:00',
  amenities text[] default '{}', note text, active boolean default true,
  created_at timestamptz default now()
);
create table if not exists public.bookings (
  id text primary key,
  user_id uuid references auth.users(id) on delete cascade,
  code text not null, kind text not null check (kind in ('station','host')), target_id text not null,
  plug text, kw numeric, date date not null, start_time text not null, end_time text,
  start_soc int, target_soc int, est_kwh numeric, est_cost integer, price_kwh integer, payment text,
  status text not null default 'upcoming' check (status in ('upcoming','active','completed','cancelled')),
  session jsonb, created_at timestamptz default now()
);
create table if not exists public.reviews (
  id text primary key,
  user_id uuid references auth.users(id) on delete set null,
  target_id text not null, rating int not null check (rating between 1 and 5), text text, tags text[] default '{}', author text,
  created_at timestamptz default now()
);
create index if not exists reviews_target on public.reviews(target_id);
create index if not exists bookings_user on public.bookings(user_id);
create index if not exists hosts_active on public.hosts(active);

alter table public.hosts enable row level security;
alter table public.bookings enable row level security;
alter table public.reviews enable row level security;
create policy "hosts are public" on public.hosts for select using (active);
create policy "owners manage hosts" on public.hosts for all using (auth.uid() = owner) with check (auth.uid() = owner);
create policy "own bookings" on public.bookings for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "reviews are public" on public.reviews for select using (true);
create policy "signed-in users write reviews" on public.reviews for insert with check (auth.uid() = user_id);
