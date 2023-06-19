import sqlite3

# Création de la base de données
conn = sqlite3.connect('tanair.db')
cursor = conn.cursor()

# Création de la table "User"
cursor.execute('''
    CREATE TABLE User (
        idUser INTEGER PRIMARY KEY,
        nom TEXT,
        prenom TEXT,
        dateNaissance DATE,
        adresseMail TEXT,
        motDePasse TEXT,
        description TEXT,
        idPromo INTEGER,
        moyNotePassager REAL,
        imageProfile TEXT,
        numeroTelephone TEXT,
        FOREIGN KEY (idPromo) REFERENCES Promo(idPromo)
    )
''')

# Création de la table "Pilote"
cursor.execute('''
    CREATE TABLE Pilote (
        idUser INTEGER PRIMARY KEY,
        numeroLicense INTEGER,
        nbHeureVolTotal REAL,
        moyNotePilote REAL,
        FOREIGN KEY (idUser) REFERENCES User(idUser)
    )
''')

# Création de la table "Avion"
cursor.execute('''
    CREATE TABLE Avion (
        idAvion INTEGER PRIMARY KEY,
        typeAvion TEXT,
        constructeur TEXT,
        imageAvion TEXT,
        idAeroclub INTEGER,
        FOREIGN KEY (idAeroclub) REFERENCES Aeroclub(idAeroclub)

    )
''')

# Création de la table "Aeroclub"
cursor.execute('''
    CREATE TABLE Aeroclub (
        idAeroclub INTEGER PRIMARY KEY,
        nomAeroclub TEXT,
        prixHeureVol REAL,
        idAerodrome INTEGER,
        FOREIGN KEY (idAerodrome) REFERENCES Aerodrome(idAerodrome)
        
    )
''')

# Création de la table "Aerodrome"
cursor.execute('''
    CREATE TABLE Aerodrome (
        idAerodrome INTEGER PRIMARY KEY,
        nom TEXT,
        nbPiste INTEGER,
        latitude INTEGER,
        longitude INTEGER
    )
''')

# Création de la table "Vol"
cursor.execute('''
    CREATE TABLE Vol (
        idVol INTEGER PRIMARY KEY,
        idUser INTEGER,
        idAerodromeDepart INTEGER,
        idAerodromeArrive INTEGER,
        idAvion INTEGER,
        placesRestantes INTEGER,
        passagerMax INTEGER,
        prixTotalIndicatif REAL,
        prixTotalReel REAL,
        prixParPassagers REAL,
        prixTotalFinal REAL,
        dureeVol REAL,
        dateDuVol DATE,
        heureDecollage REAL,
        statutVol TEXT,
        FOREIGN KEY (idUser) REFERENCES Pilote(idUser),
        FOREIGN KEY (idAerodromeDepart) REFERENCES Aerodrome(idAerodrome),
        FOREIGN KEY (idAerodromeArrive) REFERENCES Aerodrome(idAerodrome),
        FOREIGN KEY (idAvion) REFERENCES Avion(idAvion)
    )
''')

# Création de la table "Notation"
cursor.execute('''
    CREATE TABLE Notation (
        noteur INTEGER,
        noté INTEGER,
        idVol INTEGER,
        note REAL,
        commentaire TEXT,
        statutDuNoté TEXT,
        FOREIGN KEY (noteur) REFERENCES User(idUser),
        FOREIGN KEY (noté) REFERENCES User(idUser),
        FOREIGN KEY (idVol) REFERENCES Vol(idVol)
    )
''')

# Création de la table "Message"
cursor.execute('''
    CREATE TABLE Message (
        envoyeur INTEGER,
        destinataire INTEGER,
        corpsMessage TEXT,
        FOREIGN KEY (envoyeur) REFERENCES User(idUser),
        FOREIGN KEY (destinataire) REFERENCES User(idUser)
    )
''')

# Création de la table "Promo"
cursor.execute('''
    CREATE TABLE Promo (
        idPromo INTEGER PRIMARY KEY,
        nomPromo TEXT,
        nomCampus Text,
        latitude INTEGER,
        longitude INTEGER
    )
''')

# Création de la relation "vole sur" entre Pilote et Avion
cursor.execute('''
    CREATE TABLE VoleSur (
        idUser INTEGER,
        idAvion INTEGER,
        nbHeureDeVol REAL,
        FOREIGN KEY (idUser) REFERENCES Pilote(idUser),
        FOREIGN KEY (idAvion) REFERENCES Avion(idAvion)
    )
''')

# Création de la relation "être passager" entre Vol et User
cursor.execute('''
    CREATE TABLE EtrePassager (
        idUser INTEGER,
        idVol INTEGER,
        prixPayé REAL,
        statutReservation TEXT,
        FOREIGN KEY (idUser) REFERENCES User(idUser),
        FOREIGN KEY (idVol) REFERENCES Vol(idVol)
    )
''')

# Création de la vue "User_Pilote_vol" entre Vol et User et Pilote
cursor.execute('''
    CREATE VIEW User_Pilote_Vol AS
    SELECT User.nom, User.prenom, User.imageProfile, Pilote.moyNotePilote, Vol.idAerodromeDepart, Vol.idAerodromeArrive, Vol.idAvion, Vol.PlacesRestantes, Vol.passagerMax, Vol.prixTotalIndicatif, Vol.prixParPassagers, Vol.dureeVol, Vol.dateDuVol, Vol.idVol, User.idUser, vol.statutVol, vol.heureDecollage
    FROM User
    JOIN Pilote ON User.idUser = Pilote.idUser
    JOIN Vol ON User.idUser = Vol.idUser
    ''')

# Création de la vue "Passagers" entre User et Vol grâce à la table EtrePassager
cursor.execute('''
    CREATE VIEW Passagers AS
    SELECT User.idUser, User.nom, User.prenom, User.imageProfile, Vol.idVol, EtrePassager.prixPayé, EtrePassager.statutReservation
    FROM EtrePassager
    JOIN User ON User.idUser = EtrePassager.idUser
    JOIN Vol ON EtrePassager.idVol = Vol.idVol
    ''')

# Enregistrement des modifications et fermeture de la connexion
conn.commit()
conn.close()

print("Base de données créée avec succès !")