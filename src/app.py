from flask import Flask, render_template, request, flash
from flask_uploads import UploadSet, configure_uploads

app = Flask(__name__)
app.secret_key = "super secret key"

midis = UploadSet("MIDIS", "mid")
app.config["UPLOADED_MIDIS_DEST"] = "uploads"
configure_uploads(app, midis)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and "midi" in request.files:
        if request.files['midi'].filename == '':
            flash("No file selected", "red lighten-3")
            return render_template("index.html")
        filename = midis.save(request.files["midi"])
        flash(str(filename) + " uploaded", "green lighten-3")
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
