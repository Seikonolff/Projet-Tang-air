from flask import Flask, g, render_template, request, redirect, url_for, abort,session
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import sqlite3
import os

UPLOAD_FOLDER = "C:\Projet-Tang-air\static\images\profil"

app = Flask(__name__)
scheduler = BackgroundScheduler()

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

def archive_flights():
    conn = get_db()
    cursor = conn.cursor()
    
    one_day = timedelta(days=1)

    # On récupère la date actuelle
    current_date = datetime.now().date()
    previous_day = current_date - one_day

    query = "UPDATE Vol SET statutVol = 'archived' WHERE dateDuVol < ?"
    cursor.execute(query,(previous_day,))

    conn.commit()

    return

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
        lienImage = "/static/images/profil/" + adresseMail
    
        query = "INSERT INTO User (nom,prenom,dateNaissance,adresseMail,motDePasse,description,idPromo,imageProfile) VALUES (?,?,?,?,?,?,?,?)"
        cursor.execute(query,(nom,prenom,dateNaissance,adresseMail,motDePasse,description,idpromotion,lienImage))

        query = "SELECT idUser FROM User WHERE adresseMail = ?"
        result = cursor.execute(query,(adresseMail,)).fetchone()

        query = "INSERT INTO Pilote (idUser,numeroLicense,nbHeureVolTotal) VALUES (?,?,?)"
        cursor.execute(query,(result[0],numeroLicense,nbHeureVolTotal))

        conn.commit()

        return

    
    imageProfil.save(os.path.join(app.config['UPLOAD_FOLDER'],adresseMail))
    lienImage = '/static/images/profil/'+ adresseMail

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
    session['numeroTelephone'] = result1[10]
    session['flights'] = get_user_flights(idUser, pilot = False)
    session['isPilot'] = False

    query = "SELECT * FROM Pilote WHERE idUser = ?"
    result2 = cursor.execute(query,(idUser,)).fetchone()

    if result2 is not None :
        #Le user qui est en train de se log est pilote, on remplit session en conséquence
        session['isPilot'] = True
        session['numeroLicense'] = result2[1]
        session['nbHeureTotal'] = result2[2]
        session['moyNotePilote'] = calcul_note(idUser, "pilote") #il faut aussi mettre la note dans la db qql part. au moment ou le user se logout ? 
        session['flightsPilot'] = get_user_flights(idUser, pilot = True)
    
    return session


def calcul_note(idUser,statut):
    conn = get_db()
    cursor = conn.cursor()
    print(idUser)

    query = "SELECT note FROM Notation WHERE noté = ? AND statutDuNoté = ?"
    results = cursor.execute(query,(idUser,statut)).fetchall()

    moyenne = None
    
    if results != [] :
        # Extraction des notes individuelles
        notes = [result[0] for result in results]

        # Calcul de la moyenne
        moyenne = sum(notes) / len(notes)

    #On rentre la note dans la base de donnée
    if statut == 'passager':
        query = "UPDATE User SET moyNotePassager = ? WHERE idUser = ?"
    
    else :
        query = "UPDATE Pilote SET moyNotePilote = ? WHERE idUser = ?"

    cursor.execute(query,(moyenne,idUser))
    conn.commit()

    return moyenne

def get_promo():
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM Promo"
    result = cursor.execute(query).fetchall()

    return result

def get_flights(request):
    conn = get_db()
    cursor = conn.cursor()

    inputUser = request.form["inputUser"]
    date = request.form["date"]
    #placesRestantes = request.form["passager"]
    placesRestantes = 0

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
            #mais c'est dur zebi

            return []
                    
    if date :
        flights_query += " AND dateDuVol = ?"
        params.append(date)
    
    else :
        # On prend par défaut la date d'aujourd'hui
        flights_query += " AND dateDuVol >= ?"
        params.append(datetime.now().date())

    if placesRestantes :
        flights_query += " AND placesRestantes >= ?"
        params.append(placesRestantes)

    flights_query += " AND statutVol != 'archived' ORDER BY dateDuVol"
    flights = cursor.execute(flights_query,tuple(params)).fetchall()

    print(flights)
    return flights

def get_flights_frommap(airport):
    conn = get_db()
    cursor = conn.cursor()

    flights_query = "SELECT * FROM User_Pilote_Vol WHERE idAerodromeDepart = ?"
    flights = cursor.execute(flights_query,(airport,)).fetchall()

    return flights

def get_flight_info(idVol):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM User_Pilote_Vol WHERE idVol = ?"
    flight = cursor.execute(query,(idVol,)).fetchone()

    return flight

def get_user_flights(idUser,pilot):
    conn = get_db()
    cursor = conn.cursor()

    if pilot :
        #On récupère les infos des vols du pilote
        query = "SELECT * FROM User_Pilote_Vol WHERE idUser = ? ORDER BY dateDuVol" 
        flights = cursor.execute(query, (idUser,)).fetchall()

        return  flights
        
    else :
        # On récupère les id des vols liés à l'utilisateur dans la table EtrePassager
        query = "SELECT idVol FROM EtrePassager WHERE idUser = ?"
        cursor.execute(query, (idUser,))
        idVols = cursor.fetchall()

        flights = []
        
        # On récupère les infos des vols avec les idVol
        for idVol in idVols:
            query = "SELECT * FROM User_Pilote_Vol WHERE idVol = ?"
            cursor.execute(query, idVol)
            flight = cursor.fetchone()
            flights.append(flight)

        return flights
    
def get_user_fellowpassenger(flights):
    conn = get_db()
    cursor = conn.cursor()
    passagers = []


    for flight in flights :
        query = "SELECT * FROM Passagers WHERE idVol = ? "
        temp = cursor.execute(query,(flight[13],)).fetchall()
        passagers.append(temp)
        #print(passagers)
    
    return passagers
        
def get_airports():
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM Aerodrome"
    airports = cursor.execute(query).fetchall()

    return airports

def get_aircrafts():
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM Avion"
    airports = cursor.execute(query).fetchall()

    return airports

def fill_db_newflight(request) :
    conn = get_db()
    cursor = conn.cursor()

    idAerodromeDepart = request.form["aerodromeDepart"]
    idAerodromeArrive = request.form["aerodromeArrive"]
    idUser = request.form["idUser"]
    typeAvion = request.form['typeaircraft']
    passagerMax = request.form["passagerMax"]
    placesRestantes = passagerMax
    prixTotalIndicatif = request.form["prixTotalIndicatif"]
    prixParPassagers = round(float(prixTotalIndicatif)/(int(passagerMax) + 1),2)
    heureDecollage = request.form['heureDecollage']
    dureeVol = request.form["dureeVol"]
    date = request.form["date"]
    statutVol = "planing"

    query = "INSERT INTO Vol (idUser,idAerodromeDepart,idAerodromeArrive,idAvion,placesRestantes,passagerMax,prixTotalIndicatif,prixParPassagers,dureeVol,dateDuVol,heureDecollage,statutVol) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
    cursor.execute(query,(idUser,idAerodromeDepart,idAerodromeArrive,typeAvion,placesRestantes,passagerMax,prixTotalIndicatif,prixParPassagers,dureeVol,date,heureDecollage,statutVol))

    conn.commit()

    return

def fill_db_reserveflight(request):
    conn = get_db()
    cursor = conn.cursor()

    #on rempli la relation entre User et vol
    query = "INSERT INTO EtrePassager (idUser,idVol,prixPayé, statutReservation) VALUES (?,?,?,?)"
    cursor.execute(query,(request.form['idUser'],request.form['idVol'],request.form['prixPayé'],'pending'))

    #on décrémente les place restantes dans la table Vol
    query = "UPDATE Vol SET placesRestantes =  passagerMax - 1"
    cursor.execute(query)

    conn.commit()

    return

def refresh_user_flights() :
    #On (re)récupère les vols qui sont liés à l'utilisateur.
    session['flights'] = get_user_flights(session['idUser'],pilot=False)
    session['flightsPilot'] = get_user_flights(session['idUser'],pilot=True)

    #A l'aide des infos on récupère les Passagers avec qui on voyage
    session['passengers'] = get_user_fellowpassenger(session['flights'])
    session['passengersPilot'] = get_user_fellowpassenger(session['flightsPilot'])

    return

def user_infos_changes(request):
    conn = get_db()
    cursor = conn.cursor()

    imageProfil = request.files['profilePicture']

    imageProfil.save(os.path.join(app.config['UPLOAD_FOLDER'],str(session['idUser'])))
    lienImage = '/static/images/profil/'+ str(session['idUser'])

    query = "UPDATE User SET nom = ?, prenom = ?, adresseMail = ?, dateNaissance = ?, imageProfile = ?, numerotelephone = ? WHERE idUser = ?"
    cursor.execute(query,(request.form['nom'],request.form['prenom'],request.form['adresseMail'],request.form['dateDeNaissance'],lienImage,request.form['numeroTelephone'],request.form['idUser']))

    conn.commit()

    session['nom'] = request.form['nom']
    session['prenom'] = request.form['prenom']
    session['adresseMail'] = request.form['adresseMail']
    session['dateDeNaissance'] = request.form['dateDeNaissance']
    session['photoDeProfil'] = lienImage
    session['numeroTelephone'] = request.form['numeroTelephone']
    session['flights'] = get_user_flights(session['idUser'], pilot = False)

    return

def user_editflight(request):
    conn = get_db()
    cursor = conn.cursor()

    idAerodromeDepart = request.form['aerodromeDepart']
    idAerodromeArrive = request.form['aerodromeArrive']
    idAvion = request.form['typeaircraft']
    passagerMax = request.form['passagerMax']
    dateDuVol = request.form['date']
    heureDecollage = request.form['heureDecollage']
    dureeVol = request.form['dureeVol']
    prixTotalIndicatif = request.form['prixTotalIndicatif']
    prixParPassagers = round(float(prixTotalIndicatif)/(int(passagerMax) + 1),2)
    placesRestantesBefore = request.form['placesRestantesBefore']
    passagerMaxBefore = request.form['passagermaxBefore']
    placesRestantes = int(placesRestantesBefore) + (int(passagerMax) - int(passagerMaxBefore))
    if(placesRestantes < 0) :
        placesRestantes = 0
    idVol = request.form['idVol']

    query = "UPDATE Vol SET idAerodromeDepart = ?, idAerodromeArrive = ?, idAvion = ?, passagerMax = ?, dateDuVol = ?, heureDecollage = ?, dureeVol = ?, prixTotalindicatif = ?, prixParPassagers = ?, placesRestantes = ? WHERE idVol = ?"
    cursor.execute(query,(idAerodromeDepart,idAerodromeArrive,idAvion,passagerMax,dateDuVol,heureDecollage,dureeVol,prixTotalIndicatif,prixParPassagers,placesRestantes,idVol))

    conn.commit()

    return

def user_cancelflight(idUser,idVol) :
    conn = get_db()
    cursor = conn.cursor()
    if session['isPilot'] and not user_notflying(idUser,idVol):
        #le pilote suprime son vol
        query = "DELETE FROM Vol Where idUser = ? AND idVol = ?"
        cursor.execute(query,(idUser,idVol))

        #on supprime les passagers du vol
        query = "DELETE FROM EtrePassager Where idVol = ?"
        cursor.execute(query,(idVol,))

    else :
        query = "DELETE FROM EtrePassager WHERE idUser = ? AND idVol = ?"
        cursor.execute(query,(idUser,idVol))

    conn.commit()

    return

def user_not_listed(idUser,idVol) :
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM EtrePassager WHERE idUser = ? AND idVol = ?"
    flight = cursor.execute(query,(idUser,idVol)).fetchall()

    if not flight :
        #L'utilisateur n'est pas listé sur le vol
        return True
    else :
        return False
    
def user_notflying(idUser,idVol) :
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM User_Pilote_Vol WHERE idUser = ? AND idVol = ?"
    flight = cursor.execute(query,(idUser,idVol)).fetchall()

    if not flight :
        #l'utilisateur n'est pas le pilote c'est ok
        return True
    else :
        #l'utilisateur est le pilote du vol qu'il tente de réserver. Bizarre non ? 
        return False
    
def note_alreadyexists(request) :
    conn = get_db()
    cursor = conn.cursor()

    noteur = session['idUser']
    noté = request.form['noté']
    idVol = request.form['idVol']

    query = "SELECT * FROM Notation WHERE noteur = ? AND noté = ? AND idVol = ?"
    result = cursor.execute(query,(noteur,noté,idVol)).fetchall()

    if not result :
        return False
    else :
        return True

    
def confirm_passenger(idVol,idPassager) :
    conn = get_db()
    cursor = conn.cursor()

    query ="UPDATE EtrePassager SET statutReservation = 'confirmed' WHERE idVol = ? and idUser = ?"
    cursor.execute(query,(idVol,idPassager))

    conn.commit()

    return

def cancel_passenger(idVol,idPassager) :
    conn = get_db()
    cursor = conn.cursor()

    query ="DELETE FROM EtrePassager WHERE idVol = ? and idUser = ?"
    cursor.execute(query,(idVol,idPassager))

    conn.commit()

    return

def fill_db_newnote(request) :
    conn = get_db()
    cursor = conn.cursor()

    noteur = session['idUser']
    noté = request.form['noté']
    note = request.form['note']
    commentaire = request.form['commentaire']
    idVol = request.form['idVol']

    if( user_notflying(noté,idVol) ) :
        statutDuNoté = 'passager'
    else :
        statutDuNoté = 'pilote'

    query = "INSERT INTO Notation (noteur,noté,idVol,note,commentaire,statutDuNoté) VALUES (?,?,?,?,?,?)"
    cursor.execute(query,(noteur,noté,idVol,note,commentaire,statutDuNoté))

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
        return render_template("LandingPage.html", session=session, airports = get_airports())
    else :
        return render_template("LandingPage.html", airports = get_airports())

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
        aircrafts = get_aircrafts()
        return render_template("ViewFlights.html", flights = flights, airports = airports, aircrafts = aircrafts)
    else :

        return render_template("LandingPage.html")
    
@app.route('/searchmap/<airport>', methods=["GET"])
def searchmap(airport):
        airports = get_airports()
        flights = get_flights_frommap(airport)
        aircrafts = get_aircrafts()
        return render_template("ViewFlights.html", flights = flights, airports = airports, aircrafts = aircrafts)
    
@app.route('/profile', methods = ["GET"])
def profile():
    #On (re)récupère les vols qui sont liés à l'utilisateur.
    refresh_user_flights()

    return render_template("ViewProfilePage.html", session = session, airports = get_airports(), aircrafts = get_aircrafts())
    
@app.route('/edit_profile', methods=["POST"])
def edit_profile():
    user_infos_changes(request)
    return redirect(url_for("profile"))
    
@app.route('/chat')
def chat() :
    # C'est possible ?

    return

@app.route('/addflight', methods = ["GET", "POST"])
def addflight():
    if request.method == "POST" :
        #le pilote propose un vol, on récupère les données du formulaire
        fill_db_newflight(request)
        refresh_user_flights()
        return render_template("ViewProfilePage.html", flightHasBeenAdded = True)
    else :
        #le pilote a cliqué sur le btn, on retourne l'html
        airports = get_airports()
        aircrafts = get_aircrafts()
        return render_template("AddFlightPage.html", session = session, airports = airports, aircrafts=aircrafts)
    
@app.route('/reserveflight/<idVol>', methods = ["GET", "POST"])
def reserveflight(idVol):
    if request.method == "POST" :
        if user_not_listed(session['idUser'],idVol) :
            #l'utilisateur n'est pas déjà listé sur le vol

            if user_notflying(session['idUser'],idVol) :
                #l'utilisateur n'est pas le pilote non plus
                fill_db_reserveflight(request)
                refresh_user_flights()

                return render_template("ViewProfilePage.html", vol_ajoute = True)
            else :
                #l'utilisateur tente de réserver son vol
                refresh_user_flights()
                return render_template("ViewProfilePage.html", pilotTriesToBeisOwnFriend = True, airports = get_airports(), aircrafts = get_aircrafts())
        else :
            #l'utilisateur est déjà listé sur le vol
            refresh_user_flights()
            return render_template("ViewProfilePage.html", userListedAlready = True)

    else :
        return render_template("ReserveFlightPage.html", session = session, flight = get_flight_info(idVol), airports = get_airports() )
    
@app.route('/resaconfirm/<idVol>/<idPassager>', methods = ["GET"])
def resaconfirm(idVol,idPassager):
    confirm_passenger(idVol,idPassager)
    refresh_user_flights()

    return render_template("ViewProfilePage.html",resaIsConfirmed = True, airports = get_airports(), aircrafts = get_aircrafts())

@app.route('/cancelresa/<idVol>/<idPassager>', methods = ["GET"])
def resacancel(idVol,idPassager):
    cancel_passenger(idVol,idPassager)
    refresh_user_flights()
    return render_template("ViewProfilePage.html",resaIsCanceled = True, airports = get_airports(), aircrafts = get_aircrafts())

@app.route('/editflight', methods = ["POST"])
def editflight():
    user_editflight(request)
    refresh_user_flights()
    return render_template("ViewProfilePage.html",flightHasBeenEdited = True, airports = get_airports(), aircrafts = get_aircrafts())

@app.route('/cancelflight/<idVol>/<idUser>')
def cancelflight(idVol,idUser):
    user_cancelflight(idUser,idVol)
    refresh_user_flights()

    return render_template("ViewProfilePage.html",flightHasBeenCanceled = True, airports = get_airports(), aircrafts = get_aircrafts())

@app.route('/archiveflight')
def archive() :
    archive_flights()

    return render_template('LandingPage.html')

@app.route('/note', methods = ['POST'])
def note() :
    if note_alreadyexists(request) :
        #La note a déjà été atribuée

        return render_template("ViewProfilePage.html", note_alreadyexists = True, airports = get_airports(), aircrafts = get_aircrafts())
    fill_db_newnote(request)

    return redirect(url_for('profile'))

@app.route('/clafete')
def clafete() :

    return render_template('clafete.html')

@app.route('/forgotpassword')
def forgotpassword() :

    return render_template('forgotpassword.html')

'''
Fin de la gestion des routes
'''

if __name__ == '__main__':
    '''scheduler.add_job(archive_flights, 'interval', minutes=1)  # Exécution toutes les 30 minutes
    with app.app_context():
        get_db()
        scheduler.start()'''
    
    app.run(debug=True)

app.teardown_appcontext(close_db)