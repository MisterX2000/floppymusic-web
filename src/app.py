from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_uploads import UploadSet, configure_uploads, UploadNotAllowed
import subprocess
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "super secret key"

DATABASE = "database.sqlite"
db = sqlite3.connect(DATABASE)
c = db.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS songs(id INTEGER PRIMARY KEY, name TEXT, dropfac REAL)""")
db.commit()
db.close()

midis = UploadSet("MIDIS", "mid")
app.config["UPLOADED_MIDIS_DEST"] = "uploads/"
configure_uploads(app, midis)

playing = None
proc = None


def get_db():
    # Opens a new database connection if there is none yet for the current application context.
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = sqlite3.connect(DATABASE)
    return g.sqlite_db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_db(error):
    # Closes the database again at the end of the request."""
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route("/")
def index():
    return render_template("index.html", playing=playing, songs=query_db("""SELECT * FROM songs"""))


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST" and "midi" in request.files:
        try:
            if request.files['midi'].filename == '':
                flash("No file selected", "alert-warning")
                return render_template("add.html")
            filename = midis.save(request.files["midi"])
        except UploadNotAllowed:
            flash("Upload not allowed (MIDI Files only)", "alert-danger")
            return render_template("add.html")
        dropfactor = request.form["drop-factor"]
        get_db().execute("""INSERT INTO songs (name, dropfac) VALUES(?, ?)""", [str(filename), float(dropfactor)])
        get_db().commit()
        flash(str(filename) + " uploaded", "alert-success")
    return render_template("add.html")


@app.route("/stop")
def stop():
    global playing
    global proc
    playing = None

    # TODO: add function to stop music
    if proc is None:
        flash("Process not started", "alert-danger")
    else:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
            flash("Process stopped", "alert-success")
        else:
            flash("Process already stopped", "alert-success")

    return redirect(url_for("index"))


@app.route("/play/<song_id>")
def play(song_id):
    global playing
    global proc
    if os.path.isfile(app.config["UPLOADED_MIDIS_DEST"] + query_db("""SELECT name FROM songs WHERE id=?""", song_id)[0][0]):
        playing = query_db("""SELECT * FROM songs WHERE id=?""", song_id)[0]
    else:
        flash("File not found", "alert-danger")
        return redirect(url_for("index"))

    # TODO: add function to play music
    try:
        proc = subprocess.run(["../floppymusic", ["-D " + str(playing[2]), "floppymusic-web/" + app.config["UPLOADED_MIDIS_DEST"] + str(playing[1])]])
    except FileNotFoundError:
        flash(flash("Floppymusic file not found", "alert-danger"))
        return redirect(url_for("index"))

    return redirect(url_for("index"))


@app.route("/edit/<song_id>", methods=["GET", "POST"])
def edit(song_id):
    if request.method == "POST":
        name = request.form["file-name"]
        dropfac = request.form["drop-factor"]
        try:
            os.rename(app.config["UPLOADED_MIDIS_DEST"] + query_db("""SELECT name FROM songs WHERE id=?""", song_id)[0][0],
                      app.config["UPLOADED_MIDIS_DEST"] + name + ".mid")
        except FileNotFoundError:
            flash("File not found", "alert-danger")
            return redirect(url_for('index'))
        get_db().execute("""UPDATE songs SET name=?,dropfac=? WHERE id=?""", [str(name) + ".mid", float(dropfac), int(song_id)])
        get_db().commit()
        flash("Edited {}. {}.mid ({})".format(song_id, name, dropfac), "alert-success")
        return redirect(url_for('index'))

    return render_template('edit.html', song=query_db("""SELECT * FROM songs WHERE id=?""", song_id))


@app.route("/delete/<song_id>")
def delete(song_id):
    try:
        os.remove("uploads/" + query_db("""SELECT name FROM songs WHERE id=?""", song_id)[0][0])
    except FileNotFoundError:
        flash("File not found", "alert-danger")
    get_db().execute("""DELETE FROM songs WHERE id=? """, song_id)
    get_db().commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    #app.run(host="0.0.0.0", debug=True)
    app.run(debug=True)
