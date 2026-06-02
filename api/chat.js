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
      'You are an analytics assistant for the public EV charging station (SPKLU) dashboard of ' +
      'PLN UID West Java, data period March 2026. Answer CONCISELY in English, ' +
      'based ONLY on the summarised data below. Where useful, give concrete numbers and one line of insight. ' +
      'If a question is outside the data scope, honestly say the data is not available in the dashboard.\n\n' +
      'SUMMARISED DATA (JSON):\n' + context;

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
