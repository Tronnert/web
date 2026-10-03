from flask import Flask, Response, request

app = Flask(__name__)

TASK_CODE = "function task(x) {\n    return x * this * this;\n}\n"


@app.after_request
def add_headers(resp):
    if resp.mimetype == "text/plain":
        resp.headers["Content-Type"] = "text/plain; charset=UTF-8"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp


@app.route("/login/")
def login():
    return Response("restarh", mimetype="text/plain")


@app.route("/sample/")
def sample():
    return Response(TASK_CODE, mimetype="text/plain")


@app.route("/")
def index():
    return Response("restarh", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)