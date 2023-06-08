from flask import Flask, g, render_template, request, redirect, url_for, abort
import sqlite3

app = Flask(__name__)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("./tangair.db")
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

app.teardown_appcontext(close_db)

@app.route('/')
def LandingPage():
    return render_template("LandingPage.html",isLogged=True)

@app.route('/logIn', methods=["GET","POST"])
def logIn():
    conn = get_db()
    cursor = conn.cursor()

    if(request.method == "POST") :
        eMail = request.form["email"] # à modifier en fonction de l'attribut name du formulaire
        mdp = request.form["motDePasse"]    #idem
        

    return render_template()

@app.route('/test')
def Test():
    return render_template("TEST.html",isLogged=False)

@app.route('/test/Gueric')
def TestGuegs():
    return render_template("Add_flight_page.html")

@app.route('/test/Baptiste')
def TestBaptiste():
    return render_template("TEST.html")



if __name__ == '__main__':
    app.run(debug=True)