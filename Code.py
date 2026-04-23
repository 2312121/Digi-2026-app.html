from flask import Flask, g, render_template
import sqlite3

DATABASE = 'Database.db'


#initialise
app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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
    #home page
    sql = """SELECT Players.PlayerID,Countries.name,Players.PlayerName,Players.ImageURL
                FROM Players
                JOIN Countries ON Countries.CountryID=Players.CountryID"""
    results = query_db(sql)
    return render_template("Home.html", results=results)

@app.route('/Players/<int:id>')
def Player(id):
    #just one Player based on id
    sql = """SELECT * FROM Players 
            JOIN Countries ON Countries.CountryID=Players.CountryID
            WHERE Players.PlayerID = ?;"""
    result = query_db(sql,(id,),True)
    return render_template("Player.html", Player=result)
    

if __name__ == "__main__":
    app.run(debug=True)
