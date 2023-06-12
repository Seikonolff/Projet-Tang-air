from flask import Flask, g, render_template, request, redirect, url_for, abort,session
import sqlite3

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("./tangair.db")
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def check_user_exists(eMail):
    conn = get_db()
    cursor = conn.cursor()
    
    # Exécute une requête pour vérifier si l'utilisateur existe dans la base de données
    query = "SELECT * FROM User WHERE identification = ?"
    cursor.execute(query, (eMail,))
    result = cursor.fetchone()
    
    # Retourne True si l'utilisateur existe, False sinon
    return result is not None

def check_credentials(username, password):
    conn = get_db()
    cursor = conn.cursor()
    
    # Exécute une requête pour récupérer les informations de l'utilisateur
    query = "SELECT motDePasse FROM User WHERE identification = ?"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    
    # Vérifie si l'utilisateur existe et si le mot de passe correspond
    if result is not None and result[0] == password:
        return True
    
    return False

def fill_db_signIn(eMail,mdp):
    conn = get_db()
    cursor = conn.cursor()

    query = "INSERT INTO User (identification,motDePasse) VALUES (?,?)"
    cursor.execute(query,(eMail,mdp))
    conn.commit()

    return

@app.route('/')
def LandingPage():
    print('identifiant' in session)
    if 'identifiant' in session :
        return render_template("LandingPage.html", session=session)
    else :
        return render_template("LandingPage.html")

@app.route('/signin', methods=['GET','POST'])
def Signin():
    if request.method == 'POST' :
        eMail = request.form["id"]
        motDePasse = request.form["password"]

        if check_user_exists(eMail):
            #L'email rentré existe déjà dans la base de donée
            return render_template("Signin.html",userExists = True)
        else :
            #on rempli la base de donnée avec les infos données par l'utilisateur
            fill_db_signIn(eMail,motDePasse)
            
        return redirect(url_for("LandingPage"))
    else :
        return render_template("Signin.html")


@app.route('/login', methods=["GET","POST"])
def Login():
    if(request.method == "POST") :
        eMail = request.form["email"] # à modifier en fonction de l'attribut name du formulaire
        mdp = request.form["password"]    #idem
        if check_credentials(eMail,mdp) :
            session['identifiant'] = eMail
            #faire d'autres truc pour remplir la variable session (nom,prénom,nombre d'étoiles, tableau avec les id des vols prévus et effectués, nombre de notifications,nombre de message...)

            return render_template("LandingPage.html",name=session['identifiant']) #name n'est pas l'identifiant, à changer
        else :
            return render_template("Login.html",wrongcredentials = True)
    else :
        return render_template("Login.html")

@app.route('/logout')
def logout():
    #remove the username from the session if it's there
    session.clear()
    return redirect(url_for('LandingPage'))

@app.route('/test')
def Test():
    return render_template("TEST.html",isLogged=False)

@app.route('/test/Gueric')
def TestGuegs():
    return render_template("AddFlightPage.html")

@app.route('/test/Baptiste/Signin')
def TestBaptiste1():
    return render_template("Signin.html")

@app.route('/test/Baptiste/login')
def TestBaptiste2():
    return render_template("Login.html")

if __name__ == '__main__':
    app.run(debug=True)

app.teardown_appcontext(close_db)