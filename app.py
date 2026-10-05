from flask import Flask, Response, request, send_file
from PIL import Image
import io
import requests
import gzip
from datetime import datetime
import json
from pymongo import MongoClient


app = Flask(__name__)

LOGIN = "restarh"

TASK_CODE = (
    "function task(x) {\n"
    "    return new Promise((resolve, reject) => {\n"
    "        if (x < 18) resolve('yes');\n"
    "        else reject('no');\n"
    "    });\n"
    "}\n"
)

FETCH_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>fetch</title>
</head>
<body>
<input id="inp">
<button id="bt">go</button>
<script>
document.getElementById('bt').addEventListener('click', async () => {
    const inp = document.getElementById('inp');
    try {
        const r = await fetch(inp.value);
        inp.value = await r.text();
    } catch (e) {
        inp.value = String(e);
    }
});
</script>
</body>
</html>
"""


@app.after_request
def add_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = (
        "x-test,ngrok-skip-browser-warning,Content-Type,Accept,Access-Control-Allow-Headers"
    )
    if resp.mimetype == "text/plain":
        resp.headers["Content-Type"] = "text/plain; charset=UTF-8"
    elif resp.mimetype == "text/html":
        resp.headers["Content-Type"] = "text/html; charset=UTF-8"
    elif resp.mimetype == "application/json":
        resp.headers["Content-Type"] = "application/json"
    return resp


@app.route("/")
def index():
    return Response("restarh", mimetype="text/plain")


@app.route("/login")
def login():
    return Response(LOGIN, mimetype="text/plain")


@app.route("/promise/")
def promise():
    return Response(TASK_CODE, mimetype="text/plain")


@app.route("/fetch/")
def fetch():
    return Response(FETCH_HTML, mimetype="text/html")


@app.route("/result4/", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def result4():
    if request.method == "OPTIONS":
        return Response(status=204)

    x_test = request.headers.get("x-test", "")
    try:
        x_body = request.get_data(as_text=True)
    except Exception:
        x_body = request.get_data().decode("latin-1", errors="replace")

    payload = {
        "message": "restarh",
        "x-result": x_test,
        "x-body": x_body,
    }
    return Response(
        json.dumps(payload, ensure_ascii=False),
        mimetype="application/json",
    )


@app.route("/<string:ddmmyy>/")
def date_route(ddmmyy):
    if not (len(ddmmyy) == 6 and ddmmyy.isdigit()):
        return Response("not found", status=404, mimetype="text/plain")
    return Response(LOGIN, mimetype="text/plain")


@app.route("/add/<string:x1>/<string:x2>")
def add_route(x1, x2):
    try:
        s = float(x1) + float(x2)
    except ValueError:
        return Response("not found", status=404, mimetype="text/plain")
    if s.is_integer():
        s = int(s)
    return Response(str(s), mimetype="text/plain")


@app.route("/mpy/<string:y1>/<string:y2>")
def mpy_route(y1, y2):
    try:
        p = float(y1) * float(y2)
    except ValueError:
        return Response("not found", status=404, mimetype="text/plain")
    if p.is_integer():
        p = int(p)
    return Response(str(p), mimetype="text/plain")


@app.route("/size2json/", methods=["POST", "OPTIONS"])
def size2json():
    if request.method == "OPTIONS":
        return Response(status=204)

    file = request.files.get("image")
    if file is None:
        return Response(
            json.dumps({"error": "no image field"}),
            status=400,
            mimetype="application/json",
        )

    try:
        data = file.read()
        img = Image.open(io.BytesIO(data))
        width, height = img.size
    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=400,
            mimetype="application/json",
        )

    payload = {"width": width, "height": height}
    return Response(
        json.dumps(payload, ensure_ascii=False),
        mimetype="application/json",
    )


@app.route("/api/rv/<string:abc>")
def reverse_route(abc):
    if not abc or not all("a" <= c <= "z" for c in abc):
        return Response("not found", status=404, mimetype="text/plain")
    return Response(abc[::-1], mimetype="text/plain")


@app.route("/insert/", methods=["POST", "OPTIONS"])
def insert():
    if request.method == "OPTIONS":
        return Response(status=204)
    data = {}
    if request.form:
        data.update(request.form.to_dict())
    if request.is_json:
        try:
            data.update(request.get_json(force=True) or {})
        except Exception:
            pass
    lowered = {k.lower(): v for k, v in data.items()}
    login_v = lowered.get("login")
    password_v = lowered.get("password")
    url_v = lowered.get("url")
    print(f"[insert] login={login_v!r} password_len={len(password_v or '')} "
          f"url={url_v!r}", flush=True)
    if not login_v or not password_v or not url_v:
        return Response(
            json.dumps({"error": "login, password and URL are required"}),
            status=400, mimetype="application/json",
        )
    client = None
    try:
        client = MongoClient(url_v, serverSelectionTimeoutMS=5000)
        db = client.get_default_database()
        if db is None:
            db = client.get_database("readusers")
        users = db["users"]
        doc = {"login": str(login_v), "password": str(password_v)}
        result = users.insert_one(doc)
        payload = {
            "ok": True,
            "inserted_id": str(result.inserted_id),
            "login": doc["login"],
            "password": doc["password"],
        }
    except Exception as e:
        print(f"[insert] ERROR: {e}", flush=True)
        return Response(
            json.dumps({"error": str(e)}, ensure_ascii=False),
            status=500, mimetype="application/json",
        )
    finally:
        if client is not None:
            client.close()
    return Response(
        json.dumps(payload, ensure_ascii=False),
        mimetype="application/json",
    )


@app.route("/id/<string:N>")
def id_route(N):
    url = f"https://nd.kodaktor.ru/users/{N}"
    headers = {"Content-Type": None, "Accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}, ensure_ascii=False),
            status=502, mimetype="application/json",
        )
    login_value = data.get("login")
    if login_value is None:
        return Response(
            json.dumps({"error": "login not found in response", "raw": data},
                       ensure_ascii=False),
            status=502, mimetype="application/json",
        )

    return Response(str(login_value), mimetype="text/plain")


@app.route("/zipper", methods=["POST"])
def zipper():
    if 'file' not in request.files:
        return Response("No file part", status=400)
    
    file = request.files['file']
    if file.filename == '':
        return Response("No selected file", status=400)
    file_data = file.read()
    compressed_data = gzip.compress(file_data)
    return send_file(
        io.BytesIO(compressed_data),
        mimetype='application/gzip',
        as_attachment=True,
        download_name=f"{file.filename}.gz"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
