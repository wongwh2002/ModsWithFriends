const express = require('express');
const app = express();
const cors = require('cors');
const PORT = 4000;
const puppeteer = require('puppeteer');

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

app.get('/screenshot', async (req, res) => {
  const {url} = req.query;
  try {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    await page.setViewport({ width: 1920, height: 1080 });
    await page.goto(url, { waitUntil: 'load' });
    await page.waitForSelector('.timetable');
    const element = await page.$('.timetable');

    //setTimeout(() => {},1000);

    if (!element) {
      return res.status(404).send('Element with class .timetable not found');
    }

    const imageBuffer = await element.screenshot({ type: 'png' });

    res.set('Content-Type', 'image/png');
    res.send(imageBuffer);
  } catch (err) {
    console.error(err);
    res.status(500).send('Something went wrong while taking screenshot');
  } finally {
    if (browser) await browser.close();
  }
})

app.listen(PORT, () => {
  console.log(`Proxy server running at http://localhost:${PORT}`);
});
