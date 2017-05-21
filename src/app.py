from flask import Flask, render_template, request, flash, g
from flask_uploads import UploadSet, configure_uploads
import sqlite3

app = Flask(__name__)
app.secret_key = "super secret key"

DATABASE = "database.sqlite"
db = sqlite3.connect(DATABASE)
c = db.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS songs(id INTEGER PRIMARY KEY, name TEXT, dropfac INTEGER)""")
db.commit()
db.close()

midis = UploadSet("MIDIS", "mid")
app.config["UPLOADED_MIDIS_DEST"] = "uploads"
configure_uploads(app, midis)


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context."""
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = sqlite3.connect(DATABASE)
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route("/")
def index():
    return render_template("index.html", playing="Nothing", songs=None)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST" and "midi" in request.files:
        if request.files['midi'].filename == '':
            flash("No file selected", "alert-warning")
            return render_template("add.html")
        filename = midis.save(request.files["midi"])
        dropfactor = request.form["drop-factor"]
        c.execute("""INSERT INTO songs (name, dropfac) VALUES(?, ?)""", filename, dropfactor)
        flash(str(filename) + " uploaded", "alert-success")
    return render_template("add.html")


if __name__ == "__main__":
    #app.run(host="0.0.0.0")
    app.run(debug=True)
