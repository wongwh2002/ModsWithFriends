from flask import Flask, request, jsonify, send_file, send_from_directory, Response
from flask_cors import CORS
import requests
import asyncio
from pyppeteer import launch
import io
from playwright.async_api import async_playwright
import json
import os
import sys

csp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './../csp'))
sys.path.insert(0, csp_path)

from generate import generate_timetable

app = Flask(__name__)
CORS(app)

@app.route('/modInfo', methods=['GET'])
def get_mod_info():
    modCode = request.args.get('modCode')
    if not modCode:
        return jsonify({'error': 'Missing url param'}), 400

    try:
        response = requests.get(f"https://api.nusmods.com/v2/2025-2026/modules/{modCode}.json")
        data = response.json()
        return jsonify({'modInfo' : data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

async def screenshot_json(id, url):
    try:
        image_bytes = await capture_element_screenshot(url)
        #with open(f"{id}.png", "wb") as f:
        #  f.write(image_bytes)
        return image_bytes
    except Exception as e:
        print(e)
        return "Something went wrong while taking screenshot", 500


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


image_cache = {}

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    generate_timetable(data)
    screenshot_functions = []
    try:
      with open("./output.txt", 'r') as f:
          for i, line in enumerate(f):
              if i >= 10:
                  break
              screenshot_functions.append(screenshot_json(i+1, line.strip()))
    except Exception:
      return "No results avaliable", 400
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(asyncio.gather(*screenshot_functions))
    
    for idx, img_bytes in enumerate(results, start=1):
        image_cache[idx] = img_bytes

    image_urls = [f"/image/{i}" for i in range(1, len(results)+1)]

    return {'images_urls': image_urls}, 200

@app.route('/image/<int:index>')
def get_image(index):
    img_bytes = image_cache.get(index)
    if not img_bytes:
        return "Image not found", 404
    #print(img_bytes)
    return Response(img_bytes, mimetype='image/png')
    
@app.route('/Server/<filename>')
def serve_file(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(port=4000)
