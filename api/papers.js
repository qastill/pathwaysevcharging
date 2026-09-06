// Vercel serverless function — pintu unggah naskah & konfigurasi klien Perpustakaan.
//
// Env var yang dibutuhkan (Vercel: Project -> Settings -> Environment Variables):
//   SUPABASE_URL          https://<ref>.supabase.co
//   SUPABASE_ANON_KEY     kunci publik (anon / sb_publishable_...) — dikirim ke klien untuk baca & komentar
//   SUPABASE_SERVICE_KEY  kunci layanan (service_role) — HANYA dipakai di sini untuk unggah
//   PAPERS_UPLOAD_KEY     kata sandi unggah yang diketik pengunggah di form
//
// GET  /api/papers            -> {url, anonKey}  (klien memakai ini; bila env kosong -> {configured:false})
// POST /api/papers            -> unggah: {key, paper:{...}, file:{name,type,base64}}
//
// Bila env belum diatur, tab Perpustakaan otomatis jatuh ke mode lokal (localStorage).
module.exports = async (req, res) => {
  const url = process.env.SUPABASE_URL;
  const anon = process.env.SUPABASE_ANON_KEY;
  const service = process.env.SUPABASE_SERVICE_KEY;
  const uploadKey = process.env.PAPERS_UPLOAD_KEY;

  if (req.method === 'GET') {
    if (!url || !anon) { res.status(200).json({ configured: false }); return; }
    res.status(200).json({ configured: true, url, anonKey: anon, upload: !!(service && uploadKey) });
    return;
  }
  if (req.method !== 'POST') { res.status(405).json({ error: 'Method not allowed' }); return; }
  if (!url || !service || !uploadKey) {
    res.status(500).json({ error: 'SUPABASE_URL / SUPABASE_SERVICE_KEY / PAPERS_UPLOAD_KEY belum diatur di Vercel.' });
    return;
  }

  try {
    const body = req.body || {};
    if (!body.key || body.key !== uploadKey) { res.status(401).json({ error: 'Kata sandi unggah salah.' }); return; }
    const p = body.paper || {};
    const f = body.file || null;
    if (!p.id || !/^[a-z0-9][a-z0-9-]{1,60}$/.test(p.id)) { res.status(400).json({ error: 'id naskah tidak valid (huruf kecil, angka, tanda hubung).' }); return; }
    if (!p.title || !p.html) { res.status(400).json({ error: 'judul dan isi naskah wajib ada.' }); return; }

    const H = { apikey: service, Authorization: 'Bearer ' + service };
    let filePath = null, fileSize = null;
    if (f && f.base64 && f.name) {
      const buf = Buffer.from(f.base64, 'base64');
      if (buf.length > 20 * 1024 * 1024) { res.status(413).json({ error: 'Berkas > 20 MB.' }); return; }
      const safe = String(f.name).replace(/[^A-Za-z0-9._-]+/g, '_').slice(-120);
      filePath = p.id + '/' + safe;
      fileSize = buf.length;
      const up = await fetch(url + '/storage/v1/object/papers/' + filePath, {
        method: 'POST',
        headers: Object.assign({ 'Content-Type': f.type || 'application/octet-stream', 'x-upsert': 'true' }, H),
        body: buf
      });
      if (!up.ok) { const t = await up.text(); res.status(502).json({ error: 'Gagal simpan berkas: ' + t.slice(0, 300) }); return; }
    }

    const row = {
      id: p.id, n: p.n || null, title: p.title, short: p.short || null, kind: p.kind || 'Journal article',
      venue: p.venue || null, alt: p.alt || null, status: p.status || 'draft', stage: p.stage || null,
      pct: Number(p.pct) || 0, target: p.target || null, lead: p.lead || null,
      data: Array.isArray(p.data) ? p.data : [], method: Array.isArray(p.method) ? p.method : [],
      todo: Array.isArray(p.todo) ? p.todo : [], tabs: Array.isArray(p.tabs) ? p.tabs : [],
      category: p.category || null, abstract: p.abstract ? String(p.abstract).slice(0, 8000) : null,
      goal: p.goal ? String(p.goal).slice(0, 2000) : null, finding: p.finding ? String(p.finding).slice(0, 4000) : null,
      html: String(p.html).slice(0, 4 * 1024 * 1024), words: Number(p.words) || 0,
      file_name: f && f.name ? f.name : null, file_path: filePath, file_size: fileSize,
      uploaded_by: p.uploaded_by || null, updated_at: new Date().toISOString()
    };
    const ins = await fetch(url + '/rest/v1/papers?on_conflict=id', {
      method: 'POST',
      headers: Object.assign({ 'Content-Type': 'application/json', Prefer: 'resolution=merge-duplicates,return=representation' }, H),
      body: JSON.stringify(row)
    });
    if (!ins.ok) { const t = await ins.text(); res.status(502).json({ error: 'Gagal simpan naskah: ' + t.slice(0, 300) }); return; }
    const saved = await ins.json();
    res.status(200).json({ ok: true, paper: saved[0] || row,
      fileUrl: filePath ? url + '/storage/v1/object/public/papers/' + filePath : null });
  } catch (e) {
    res.status(500).json({ error: String(e && e.message ? e.message : e) });
  }
};
module.exports.config = { api: { bodyParser: { sizeLimit: '25mb' } } };
