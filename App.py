from flask import Flask, g, render_template, request, redirect, session
import sqlite3

DATABASE = 'database.db'

app = Flask(__name__)
app.secret_key = "your_secret_key_here"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def home():
    print("SESSION BUILD:", session.get("build"))

    parts = query_db("SELECT * FROM Parts")

    build_ids = session.get("build", [])
    build_ids = [pid for pid in build_ids if pid]

    build_parts = []
    total = 0

    if build_ids:
        placeholders = ",".join(["?"] * len(build_ids))

        rows = query_db(
            f"SELECT * FROM Parts WHERE PartID IN ({placeholders})",
            build_ids
        )

        parts_map = {row["PartID"]: row for row in rows}
        build_parts = [parts_map[pid] for pid in build_ids if pid in parts_map]

        total = sum(p["Price"] for p in build_parts)

    return render_template(
        "Home.html",
        parts=parts,
        BuildParts=build_parts,
        total=total 
        )

@app.route('/add/<int:part_id>')
def add_part(part_id):
    print("ADDING PART:", part_id) 

    build = session.get("build", [])
    build.append(part_id)

    session["build"] = build
    session.modified = True

    return redirect('/')


@app.route('/clear')
def clear_build():
    session["build"] = []
    session.modified = True
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=5001)


