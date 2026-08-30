const https = require('https');

function fetchGoogleTTSChunk(text, lang = 'vi') {
  return new Promise((resolve) => {
    const cleanText = text.trim();
    if (!cleanText) return resolve(Buffer.alloc(0));

    const url = `https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=${encodeURIComponent(lang)}&q=${encodeURIComponent(cleanText)}`;
    const options = {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*'
      }
    };

    https.get(url, options, (res) => {
      if (res.statusCode !== 200) {
        return resolve(Buffer.alloc(0));
      }
      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => resolve(Buffer.concat(chunks)));
    }).on('error', () => {
      resolve(Buffer.alloc(0));
    });
  });
}

function splitTextIntoSmallChunks(text, maxLen = 80) {
  const sentences = text.split(/[\n.;!?:]+/).map(s => s.trim()).filter(Boolean);
  const chunks = [];

  for (const sentence of sentences) {
    if (sentence.length <= maxLen) {
      chunks.push(sentence);
    } else {
      const words = sentence.split(/\s+/);
      let current = "";
      for (const word of words) {
        if ((current + " " + word).trim().length <= maxLen) {
          current = (current + " " + word).trim();
        } else {
          if (current) chunks.push(current);
          current = word;
        }
      }
      if (current) chunks.push(current);
    }
  }
  return chunks.length > 0 ? chunks : [text.substring(0, maxLen)];
}

module.exports = async function handler(req, res) {
  // Support CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.statusCode = 200;
    return res.end();
  }

  let text = '';
  let lang = 'vi';

  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') {
      try {
        body = JSON.parse(body);
      } catch (e) {}
    }
    text = body && body.text ? body.text : '';
    lang = body && body.lang ? body.lang : 'vi';
  } else {
    text = req.query && req.query.text ? req.query.text : '';
    lang = req.query && req.query.lang ? req.query.lang : 'vi';
  }

  if (!text || !text.trim()) {
    res.statusCode = 400;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: 'Missing text parameter' }));
  }

  const cleanText = String(text).trim();
  const targetLang = lang.startsWith('zh') ? 'zh-CN' : (lang.startsWith('vi') ? 'vi' : lang);

  // Split into safe Google TTS chunks (< 80 chars each)
  const chunks = splitTextIntoSmallChunks(cleanText, 80);

  try {
    // Process all chunks in parallel
    const bufferResults = await Promise.all(
      chunks.map(chunk => fetchGoogleTTSChunk(chunk, targetLang))
    );

    const validBuffers = bufferResults.filter(b => b && b.length > 0);
    if (validBuffers.length === 0) {
      res.statusCode = 502;
      res.setHeader('Content-Type', 'application/json');
      return res.end(JSON.stringify({ error: 'Failed to fetch audio from TTS upstream' }));
    }

    const combinedMp3 = Buffer.concat(validBuffers);

    res.statusCode = 200;
    res.setHeader('Content-Type', 'audio/mpeg');
    res.setHeader('Content-Length', combinedMp3.length);
    res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');

    return res.end(combinedMp3);
  } catch (err) {
    console.error('TTS handler error:', err);
    res.statusCode = 500;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: 'Internal Server Error' }));
  }
};
