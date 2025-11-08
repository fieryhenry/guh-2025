from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    filename = request.form.get("filename")
    print(filename)
    return {"genre": "foo", "tempo": 120}


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000)
