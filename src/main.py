from flask import Flask, redirect, render_template, request
from werkzeug.utils import secure_filename
import uuid
import os

UPLOAD_FOLDER = "uploads/"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)
    if file:
        filename = secure_filename(f"{file.filename}-{uuid.uuid4()}")
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return {"genre": "foo", "tempo": 120, "filename": filename}
    return redirect(request.url)


@app.route("/collide", methods=["POST"])
def collide():
    data = request.get_json()

    file_data = []
    for file in data:
        if file.get("filename"):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.get("filename"))
            if os.path.exists(file_path) and file_path.startswith(
                app.config["UPLOAD_FOLDER"]
            ):  # TODO: probably fails with relative paths
                with open(file_path, "rb") as f:
                    data = f.read()
                    file_data.append(data)

    # do some fancy processing with file_data, then return some data back
    return file_data[0]


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000)
