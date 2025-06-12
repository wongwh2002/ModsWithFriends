const express = require('express');
const app = express();
const cors = require('cors');
const PORT = 4000;

app.use(cors());

app.get('/expand', async (req, res) => {
  const { url } = req.query;

  if (!url) return res.status(400).json({ error: 'Missing url param' });

  try {
    const response = await fetch(url, { redirect: 'manual' });
    const location = response.headers.get('location');
    if (location) {
      res.json({ expandedUrl: location });
    } else {
      res.json({expandedUrl : url});
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`Proxy server running at http://localhost:${PORT}`);
});
