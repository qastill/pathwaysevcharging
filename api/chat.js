// Vercel serverless function — proxy ke DeepSeek API.
// Kunci API disimpan server-side via environment variable DEEPSEEK_API_KEY
// (atur di Vercel: Project -> Settings -> Environment Variables), jadi tidak
// pernah terekspos di sisi browser.
module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  const key = process.env.DEEPSEEK_API_KEY;
  if (!key) {
    res.status(500).json({ error: 'DEEPSEEK_API_KEY belum diatur di Environment Variables Vercel.' });
    return;
  }
  try {
    const body = req.body || {};
    const messages = Array.isArray(body.messages) ? body.messages : [];
    const context = typeof body.context === 'string' ? body.context : '';
    const system =
      'Kamu adalah asisten analitik untuk dashboard SPKLU (Stasiun Pengisian Kendaraan Listrik Umum) ' +
      'PLN UID Jawa Barat, periode data Maret 2026. Jawab SINGKAT, padat, dan dalam Bahasa Indonesia, ' +
      'berbasis HANYA pada data ringkas di bawah. Bila perlu beri angka konkret dan satu kalimat insight. ' +
      'Jika pertanyaan di luar cakupan data, katakan dengan jujur bahwa datanya tidak tersedia di dashboard.\n\n' +
      'DATA RINGKAS (JSON):\n' + context;

    const r = await fetch('https://api.deepseek.com/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + key },
      body: JSON.stringify({
        model: 'deepseek-chat',
        temperature: 0.3,
        max_tokens: 700,
        messages: [{ role: 'system', content: system }].concat(messages)
      })
    });
    const data = await r.json();
    if (!r.ok) {
      res.status(r.status).json({ error: (data.error && data.error.message) || 'DeepSeek API error' });
      return;
    }
    const reply =
      data.choices && data.choices[0] && data.choices[0].message
        ? data.choices[0].message.content
        : '(tidak ada jawaban)';
    res.status(200).json({ reply });
  } catch (e) {
    res.status(500).json({ error: String(e && e.message ? e.message : e) });
  }
};
