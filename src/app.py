from flask import Flask, render_template, request, flash
from flask_uploads import UploadSet, configure_uploads
import sqlite3

app = Flask(__name__)
app.secret_key = "super secret key"

db = sqlite3.connect('database.sqlite')
curs = db.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS songs(id INTEGER PRIMARY KEY, name TEXT, dropfac INTEGER)""")

midis = UploadSet("MIDIS", "mid")
app.config["UPLOADED_MIDIS_DEST"] = "uploads"
configure_uploads(app, midis)


@app.route("/")
def index():
    return render_template("index.html", playing="Nothing")


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST" and "midi" in request.files:
        if request.files['midi'].filename == '':
            flash("No file selected", "alert-warning")
            return render_template("add.html")
        filename = midis.save(request.files["midi"])
        flash(str(filename) + " uploaded", "alert-success")
    return render_template("add.html")


if __name__ == "__main__":
    #app.run(host="0.0.0.0")
    app.run(debug=True)
