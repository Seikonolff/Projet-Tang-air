from flask import Flask, g, render_template, request, redirect, url_for, abort,session
import sqlite3
import os

UPLOAD_FOLDER = "C:\Projet-Tang-air\static\images\profil"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

'''
Début définition des fonctions 
'''

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("./tanair.db")
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def check_user_exists(eMail):
    conn = get_db()
    cursor = conn.cursor()
    
    # Exécute une requête pour vérifier si l'utilisateur existe dans la base de données
    query = "SELECT * FROM User WHERE adresseMail = ?"
    cursor.execute(query, (eMail,))
    result = cursor.fetchone()
    
    # Retourne True si l'utilisateur existe, False sinon
    return result is not None

def check_credentials(username, password):
    conn = get_db()
    cursor = conn.cursor()
    
    # Exécute une requête pour récupérer les informations de l'utilisateur
    query = "SELECT motDePasse FROM User WHERE adresseMail = ?"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    
    # Vérifie si l'utilisateur existe et si le mot de passe correspond
    if result is not None and result[0] == password:
        return True
    
    return False

def fill_db_signup(request):
    conn = get_db()
    cursor = conn.cursor()

    nom = request.form["nom"]
    prenom = request.form["prenom"]
    dateNaissance = request.form["dateNaissance"]
    adresseMail = request.form["adresseMail"]
    motDePasse = request.form["motdepasse"]
    description = request.form ["description"]
    imageProfil = request.files['profilePicture']
    idpromotion = request.form["promo"] 

    if 'isPilot' in request.form :
        #L'user se déclare comme étant pilote
        numeroLicense = request.form["numeroLicense"]
        nbHeureVolTotal = request.form["nbHeureVolTotal"]

        imageProfil.save(os.path.join(app.config['UPLOAD_FOLDER'],adresseMail))
        lienImage = './static/images/profil/'+ adresseMail
    
        query = "INSERT INTO User (nom,prenom,dateNaissance,adresseMail,motDePasse,description,idPromo,imageProfile) VALUES (?,?,?,?,?,?,?,?)"
        cursor.execute(query,(nom,prenom,dateNaissance,adresseMail,motDePasse,description,idpromotion,lienImage))

        query = "SELECT idUser FROM User WHERE adresseMail = ?"
        result = cursor.execute(query,(adresseMail,)).fetchone()

        query = "INSERT INTO Pilote (idUser,numeroLicense,nbHeureVolTotal) VALUES (?,?,?)"
        cursor.execute(query,(result[0],numeroLicense,nbHeureVolTotal))

        conn.commit()

        return

    
    imageProfil.save(os.path.join(app.config['UPLOAD_FOLDER'],adresseMail))
    lienImage = './static/images/profil/'+ adresseMail

    query = "INSERT INTO User (nom,prenom,dateNaissance,adresseMail,motDePasse,description,idPromo,imageProfile) VALUES (?,?,?,?,?,?,?,?)"
    cursor.execute(query,(nom,prenom,dateNaissance,adresseMail,motDePasse,description,idpromotion,lienImage))

    conn.commit()

    return

def open_session(eMail):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM User WHERE adresseMail = ?"
    result1 = cursor.execute(query,(eMail,)).fetchone()

    idUser = result1[0]
    session['idUser'] = idUser
    session['nom'] = result1[1]
    session['prenom'] = result1[2]
    session['dateDeNaissance'] = result1[3]
    session['adresseMail'] = result1[4]
    session['description'] = result1[6]
    session['promo'] =result1[7]
    session['moyenneNotePassager'] = calcul_note(idUser, "passager")
    session['photoDeProfil'] = result1[9]

    query = "SELECT * FROM Pilote WHERE idUser = ?"
    result2 = cursor.execute(query,(idUser,)).fetchone()

    if result2 is not None :
        #Le user qui est en train de se log est pilote, on remplit session en conséquence
        session['isPilot'] = True
        session['numeroLicense'] = result2[1]
        session['nbHeureTotal'] = result2[2]
        session['moyNotePilote'] = calcul_note(idUser, "pilote")
    
    return session


def calcul_note(idUser,statut):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT note FROM Notation WHERE noté = ? AND statutDuNoté = ?"
    results = cursor.execute(query,(idUser,statut)).fetchall()
    
    if results != [] :
        # Extraction des notes individuelles
        notes = [result[0] for result in results]

        # Calcul de la moyenne
        moyenne = sum(notes) / len(notes)
        return moyenne
    
    return

def get_promo():
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM Promo"
    result = cursor.execute(query).fetchall()

    return result

def get_flights(request):
    conn = get_db()
    cursor = conn.cursor()

    inputUser = request.form["inputUser"] # à mettre dans des if pour voir si c'est un pilote ou un aéroport
    date = request.form["date"]
    placesRestantes = request.form["passager"]

    airport_query = "SELECT idAerodrome,nom FROM Aerodrome WHERE nom = ?" #On regarde dans la table ce qui a été rentré
    airport = cursor.execute(airport_query,(inputUser,)).fetchone()

    flights_query = "SELECT * FROM User_Pilote_Vol WHERE"
    params = []

    if inputUser :
        #Il faut déterminer si un aéroport à été rentré, un nom ou prénom de pilote
        airport_query = "SELECT idAerodrome,nom FROM Aerodrome WHERE nom = ?" #On regarde dans la table ce qui a été rentré
        airport = cursor.execute(airport_query,(inputUser,)).fetchone()

        if airport :
            flights_query += " idAerodromeDepart = ?"
            params.append(airport[0])
        else :
            #Il faut déterminer si un prénom ou un nom de pilote a été rentré
            oui = "oui" #reqUETE SQL ICI

    if date :
        flights_query += " AND dateDuVol = ?"
        params.append(date)

    if placesRestantes :
        flights_query += " AND placesRestantes >= ?"
        params.append(placesRestantes)

    flights = cursor.execute(flights_query,tuple(params)).fetchall()

    print(flights)

    return flights

def get_airports():
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT idAerodrome, nom FROM Aerodrome"
    airports = cursor.execute(query).fetchall()

    return airports

def fill_db_newflight(request) :
    conn = get_db()
    cursor = conn.cursor()

    idAerodromeDepart = request.form["aerodromeDepart"]
    idAerodromeArrive = request.form["aerodromeArrive"]
    idUser = request.form["idUser"]
    passagerMax = request.form["passagerMax"]
    placesRestantes = passagerMax
    prixTotalIndicatif = request.form["prixTotalIndicatif"]
    prixParPassagers = round(float(prixTotalIndicatif)/(int(passagerMax) + 1),2)
    dureeVol = request.form["dureeVol"]
    date = request.form["date"]

    query = "INSERT INTO Vol (idUser,idAerodromeDepart,idAerodromeArrive,placesRestantes,passagerMax,prixTotalIndicatif,prixParPassagers,dureeVol,dateDuVol) VALUES (?,?,?,?,?,?,?,?,?)"
    cursor.execute(query,(idUser,idAerodromeDepart,idAerodromeArrive,placesRestantes,passagerMax,prixTotalIndicatif,prixParPassagers,dureeVol,date))

    conn.commit()

    return 


'''
Fin définition des fonctions 
'''

'''
Début de la gestion des routes
'''

@app.route('/')
def LandingPage():
    if 'identifiant' in session :
        return render_template("LandingPage.html", session=session)
    else :
        return render_template("LandingPage.html")

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST' :    
        if check_user_exists(request.form["adresseMail"]):
            #L'email rentré existe déjà dans la base de donée
            return render_template("signup.html",userAlreadyExists = True)
        else :
            #on rempli la base de donnée avec les infos données par l'utilisateur
            fill_db_signup(request) #peut-être passer juste request en paramètre ?
            return redirect(url_for("Login"))
    else :
        promos = get_promo()
        return render_template("signup.html", promos=promos)

@app.route('/login', methods=["GET","POST"])
def Login():
    if(request.method == "POST") :
        eMail = request.form["email"] # à modifier en fonction de l'attribut name du formulaire
        password = request.form["password"]    #idem

        if check_credentials(eMail,password) :
            session = open_session(eMail)
            return render_template("LandingPage.html",session=session) #name n'est pas l'identifiant, à changer
        
        else :
            return render_template("Login.html",wrongcredentials = True)
        
    else :
        return render_template("Login.html")

@app.route('/logout')
def logout():
    #remove the username from the session if it's there
    session.clear()
    return redirect(url_for('LandingPage'))

@app.route('/search', methods=["GET", "POST"])
def search():
    if request.method == "POST" :
        airports = get_airports()
        flights = get_flights(request)
        return render_template("ViewFlights.html", flights = flights, airports = airports)
    else :
        return redirect(url_for("LandingPage"))
    
@app.route('/profile', methods = ["GET", "POST"])
def profile():
    if request.method == "POST" :
        #le user tente de modifier son profil
        return
    else :
        return render_template("ViewProfilePage.html", session=session)
    
@app.route('/edit_profile', methods=["GET"])
def edit_profile():
    return render_template("EditProfil.html")
    
@app.route('/chat')
def chat() :
    # C'est possible ?

    return

@app.route('/addflight', methods = ["GET", "POST"])
def addflight():
    if request.method == "POST" :
        #le pilote propose un vol, on récupère les données du formulaire
        fill_db_newflight(request)

        return redirect(url_for("LandingPage"))
    else :
        #le pilote a cliqué sur le btn, on retourne l'html
        airports = get_airports()
        return render_template("AddFlightPage.html", session = session, airports = airports)
    
@app.route('/reserveflight', methods = ["GET", "POST"])
def reserveflight():
    if request.method == "POST" :
        #le pilote propose un vol, on récupère les données du formulaire
        return
    else :
        #le pilote a cliqué sur le btn, on retourne l'html
        return render_template("ReserveFlightPage.html", session = session)
    
'''
Fin de la gestion des routes
'''

if __name__ == '__main__':
    app.run(debug=True)

app.teardown_appcontext(close_db)