from flask import Flask

app = Flask(__name__)


@app.get("/")
def home():
    return "<h1>Hello, Flask!</h1>"


if __name__ == "__main__":
    app.run()
