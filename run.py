from flask import Flask
import os

app = Flask(__name__)


@app.route("/index/")
def index():
    user = os.environ.get("USER")
    password = os.environ.get("PASS")
    return f"{user}_{password}"


@app.route("/version/")
def version():
    env = os.environ.get("ENV")
    version = os.environ.get("WEBVERSION")
    return f"{env}_{version}"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)