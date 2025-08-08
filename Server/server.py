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
from mod_db import mods_database

csp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./../csp"))
sys.path.insert(0, csp_path)

#from generate import generate_timetable
from permutate_shared_mods import get_solutions

app = Flask(__name__)
CORS(app)

db = mods_database()


@app.route("/", methods=["GET"])
def index():
    return "ModsWithFriends backend is running.", 200


@app.route("/modInfo", methods=["GET"])
def get_mod_info():
    modCode = request.args.get("modCode")
    if not modCode:
        return jsonify({"error": "Missing url param"}), 400

    try:
        response = requests.get(
            f"https://api.nusmods.com/v2/2024-2025/modules/{modCode}.json"
        )
        data = response.json()
        return jsonify({"modInfo": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/expand", methods=["GET"])
def expand_url():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url param"}), 400

    try:
        response = requests.get(url, allow_redirects=False)
        location = response.headers.get("Location")
        if location:
            return jsonify({"expandedUrl": location})
        else:
            return jsonify({"expandedUrl": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/screenshot", methods=["GET"])
def screenshot():
    url = request.args.get("url")
    if not url:
        return "Missing url param", 400

    try:
        image_bytes = asyncio.run(capture_element_screenshot(url))
        return send_file(
            io.BytesIO(image_bytes),
            mimetype="image/png",
            as_attachment=False,
            download_name="screenshot.png",
        )
    except Exception as e:
        print(e)
        return "Something went wrong while taking screenshot", 500


"""
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
"""


async def screenshot_json(id, url):
    try:
        image_bytes = await capture_element_screenshot(url)
        # with open(f"{id}.png", "wb") as f:
        #  f.write(image_bytes)
        return image_bytes
    except Exception as e:
        print(e)
        return "Something went wrong while taking screenshot", 500


async def capture_element_screenshot(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_selector(".timetable")
        element = await page.query_selector(".timetable")
        if not element:
            await browser.close()
            raise Exception("Element with class .timetable not found")
        image_bytes = await element.screenshot()
        await browser.close()

        return image_bytes


image_cache = {}


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    solutions = get_solutions(data["config"])
    user_solutions = solutions[data["user"]]
    screenshot_functions = []
    try:
        with open("./output.txt", "r") as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                screenshot_functions.append(screenshot_json(i + 1, line.strip()))
    except Exception:
        return "No results avaliable", 400
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(asyncio.gather(*screenshot_functions))

    for idx, img_bytes in enumerate(results, start=1):
        image_cache[idx] = img_bytes

    image_urls = [f"/image/{i}" for i in range(1, len(results) + 1)]

    return {"images_urls": image_urls}, 200


@app.route("/image/<int:index>")
def get_image(index):
    img_bytes = image_cache.get(index)
    if not img_bytes:
        return "Image not found", 404
    # print(img_bytes)
    return Response(img_bytes, mimetype="image/png")


@app.route("/new_session", methods=["POST"])
def new_session_login():
    print("[Login]")
    name, password, session_id = get_login_info()
    success = db.add_student(name, password)
    db.add_new_session(session_id)
    db.add_student_sessions(name, session_id, json.dumps({}))
    if success:
        return jsonify({"status": "success", "message": "Student added"}), 200
    else:
        return jsonify({"status": "exists", "message": "Student already exists"}), 400


def get_login_info():
    data = request.get_json()
    name, password = data["name"], data["password"]
    session_id = data["session_id"]
    return name, password, session_id


@app.route("/save_preferences", methods=["POST"])
def save_preference():
    session_id, name, preferences = get_preferences_data()
    db.add_student_sessions(name, session_id, json.dumps(preferences))
    return "updated student preference", 200


def get_preferences_data():
    data = request.get_json()
    session_id, name, preferences = (
        data["session_id"],
        data["name"],
        data["preferences"],
    )
    return session_id, name, preferences


@app.route("/get_preferences", methods=["POST"])
def get_preference():
    data = request.get_json()
    session_id, name = (data["session_id"], data["name"])
    preferences = db.get_preference_from_student_sessions(name, session_id)
    return jsonify({"preferences": preferences}), 200


@app.route("/get_new_session", methods=["GET"])
def get_new_session_id():
    new_id = db.generate_session_id()
    if new_id:
        return jsonify({"new_id": new_id}), 200
    return jsonify({"error": "unable to generate unique session id"}), 400


@app.route("/join_session", methods=["POST"])
def join_session():
    name, password, session_id = get_login_info()
    if not db.is_session_exists(session_id):
        return "session does not exist", 400
    success = db.join_session(name, password, session_id)
    if success:
        return "joined session", 200
    return "wrong password", 401


@app.route("/sem1_data", methods=["GET"])
def get_sem1_data():
    print("[GETTING SEM1 DATA]")
    sem1_data = db.get_sem1_data()
    return jsonify({"sem_data": sem1_data}), 200


@app.route("/sem2_data", methods=["GET"])
def get_sem2_data():
    print("[GETTING SEM2 DATA]")
    sem2_data = db.get_sem2_data()
    return jsonify({"sem_data": sem2_data}), 200


@app.route("/Server/<filename>")
def serve_file(filename):
    return send_from_directory(".", filename)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 4000))
    app.run(host="0.0.0.0", port=port)
