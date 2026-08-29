const https = require('https');

module.exports = async function handler(req, res) {
  const { text, lang = 'zh-CN' } = req.query;

  if (!text) {
    return res.status(400).json({ error: 'Missing text parameter' });
  }

  const cleanText = String(text).trim().substring(0, 500);
  const targetLang = lang.startsWith('zh') ? 'zh-CN' : (lang.startsWith('vi') ? 'vi' : lang);

  const googleUrl = `https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=${encodeURIComponent(targetLang)}&q=${encodeURIComponent(cleanText)}`;

  const options = {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': '*/*'
    }
  };

  try {
    https.get(googleUrl, options, (googleRes) => {
      if (googleRes.statusCode !== 200) {
        return res.status(googleRes.statusCode).json({ error: `TTS upstream error: ${googleRes.statusCode}` });
      }

      res.setHeader('Content-Type', 'audio/mpeg');
      res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
      res.setHeader('Access-Control-Allow-Origin', '*');

      googleRes.pipe(res);
    }).on('error', (err) => {
      console.error('TTS proxy error:', err);
      res.status(500).json({ error: 'Failed to proxy audio' });
    });
  } catch (err) {
    console.error('Handler error:', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
};
