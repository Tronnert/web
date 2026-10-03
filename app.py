from flask import Flask, Response

app = Flask(__name__)

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
    resp.headers["Access-Control-Allow-Methods"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"

    if resp.mimetype == "text/plain":
        resp.headers["Content-Type"] = "text/plain; charset=UTF-8"
    elif resp.mimetype == "text/html":
        resp.headers["Content-Type"] = "text/html; charset=UTF-8"
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
