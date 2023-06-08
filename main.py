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

@app.route('/test')
def Test():
    return render_template("TEST.html",isLogged=False)

@app.route('/test/Gueric')
def TestGuegs():
    return render_template("Add_flight_page.html")

@app.route('/test/Baptiste/sign in')
def TestBaptiste1():
    return render_template("sign in.html")

@app.route('/test/Baptiste/login')
def TestBaptiste2():
    return render_template("log in.html")



if __name__ == '__main__':
    app.run(debug=True)