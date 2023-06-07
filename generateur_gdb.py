import sqlite3

# Création de la base de données
conn = sqlite3.connect('tangair.db')
cursor = conn.cursor()

# Création de la table "User"
cursor.execute('''
    CREATE TABLE User (
        idUser INTEGER PRIMARY KEY,
        nom TEXT,
        prenom TEXT,
        dateNaissance DATE,
        adresse TEXT,
        identification TEXT,
        motDePasse TEXT,
        idPromo TEXT,
        moyNotePassager REAL,
        imageProfile TEXT,
        idCampus INTEGER,
        FOREIGN KEY (idCampus) REFERENCES Campus(idCampus)
    )
''')

# Création de la table "Pilote"
cursor.execute('''
    CREATE TABLE Pilote (
        idUser INTEGER PRIMARY KEY,
        numeroLicense INTEGER,
        description TEXT,
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
        prixHeureVol REAL,
        idAerodrome INTEGER,
        FOREIGN KEY (idAerodrome) REFERENCES Aerodrome(idAerodrome)
        
    )
''')

# Création de la table "Aerodrome"
cursor.execute('''
    CREATE TABLE Aerodrome (
        idAerodrome INTEGER PRIMARY KEY,
        nbPiste INTEGER,
        latitude INTEGER,
        longitude INTEGER
    )
''')

# Création de la table "Vol"
cursor.execute('''
    CREATE TABLE Vol (
        idVol INTEGER PRIMARY KEY,
        aerodromeDepart TEXT,
        aerodromeArrive TEXT,
        nombreReservations INTEGER,
        passagerMax INTEGER,
        piloteMax INTEGER,
        prixTotalIndicatif REAL,
        prixParPassagers REAL,
        prixTotalFinal REAL,
        dureeVol REAL,
        dateDuVol DATE
    )
''')

# Création de la table "Campus"
cursor.execute('''
    CREATE TABLE Campus (
        idCampus INTEGER PRIMARY KEY,
        nomCampus TEXT,
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
        FOREIGN KEY (idUser) REFERENCES User(idUser),
        FOREIGN KEY (idVol) REFERENCES Vol(idVol)
    )
''')

# Création de la relation entre Vol et Pilote
cursor.execute('''
    CREATE TABLE Fly (
        idUser INTEGER,
        idVol INTEGER,
        FOREIGN KEY (idUser) REFERENCES Pilote(idUser),
        FOREIGN KEY (idVol) REFERENCES Vol(idVol)
    )
''')

# Création de la relation entre Avion et Vol
cursor.execute('''
    CREATE TABLE OpererAvec (
        idAvion INTEGER,
        idVol INTEGER,
        FOREIGN KEY (idAvion) REFERENCES Avion(idAvion),
        FOREIGN KEY (idVol) REFERENCES Vol(idVol)
    )
''')

# Enregistrement des modifications et fermeture de la connexion
conn.commit()
conn.close()

print("Base de données créée avec succès !")