from flask import Flask, Response, request
from datetime import datetime
import json

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


@app.route("/login/")
def login():
    return Response("restarh", mimetype="text/plain")


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


@app.route("/<regex('[0-9]{6}'):ddmmyy>/")
def date_route(ddmmyy):
    today = datetime.now().strftime("%d-%m-%Y")
    payload = {"date": today, "login": LOGIN}
    return Response(
        json.dumps(payload, ensure_ascii=False),
        mimetype="application/json",
    )


@app.route("/api/rv/<string:abc>")
def reverse_route(abc):
    if not abc or not all("a" <= c <= "z" for c in abc):
        return Response("not found", status=404, mimetype="text/plain")
    return Response(abc[::-1], mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
