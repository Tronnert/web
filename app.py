from flask import Flask, Response, request

app = Flask(__name__)


@app.after_request
def add_custom_headers(resp):
    resp.headers["X-Author"] = "restarh"
    resp.headers["Access-Control-Allow-Methods"] = "*"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp


@app.route("/", methods=["GET", "OPTIONS"])
def index():
    if request.method == "OPTIONS":
        return Response(status=204)
    return Response("restarh", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
