from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import asyncio
from pyppeteer import launch
import io
from playwright.async_api import async_playwright

app = Flask(__name__)
CORS(app)

@app.route('/expand', methods=['GET'])
def expand_url():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing url param'}), 400

    try:
        response = requests.get(url, allow_redirects=False)
        location = response.headers.get('Location')
        if location:
            return jsonify({'expandedUrl': location})
        else:
            return jsonify({'expandedUrl': url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/screenshot', methods=['GET'])
def screenshot():
    url = request.args.get('url')
    if not url:
        return "Missing url param", 400

    try:
        image_bytes = asyncio.run(capture_element_screenshot(url))
        return send_file(
            io.BytesIO(image_bytes),
            mimetype='image/png',
            as_attachment=False,
            download_name='screenshot.png'
        )
    except Exception as e:
        print(e)
        return "Something went wrong while taking screenshot", 500

'''
async def capture_element_screenshot(url):
    browser = await launch()
    page = await browser.newPage()
    await page.setViewport({'width': 1920, 'height': 1080})
    await page.goto(url, {'waitUntil': 'load'})
    await page.waitForSelector('.timetable')

    element = await page.querySelector('.timetable')
    if not element:
        await browser.close()
        raise Exception("Element with class .timetable not found")

    image_bytes = await element.screenshot({'type': 'png'})
    await browser.close()
    return image_bytes
'''

async def capture_element_screenshot(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_selector('.timetable')
        element = await page.query_selector('.timetable')
        if not element:
            await browser.close()
            raise Exception("Element with class .timetable not found")
        image_bytes = await element.screenshot()
        await browser.close()

        return image_bytes

if __name__ == '__main__':
    app.run(port=4000)
