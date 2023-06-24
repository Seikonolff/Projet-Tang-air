import pandas as pd
from geopy.geocoders import Nominatim
import sqlite3

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("./tanair.db")
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Liste des codes OACI des aérodromes en France
codes_oaci = [
    "LFRU",  # Paris Charles de Gaulle Airport
    "LFPO",  # Paris Orly Airport
    "LFMN",  # Nice Côte d'Azur Airport
    "LFLL",  # Lyon-Saint-Exupéry Airport
    "LFNG", "LFHO", "LFTW", "LFME", "LFNU", "LFTN", "LFHF", "LFLQ", "LFMT", "LFMS", "LFHD", "LFMN", "LFNV", "LFNH", "LFMV", "LFNT", 
    "LFNZ", "LFNE", "LFNR", "LFML", "LFMA", "LFMQ", "LFNF", "LFMU", "LFMP", "LFMZ", "LFCM", "LFNX", "LFIF", "LFNB", "LFHL",
    "LFCL", "LFBO", "LFBF", "LFBR", "LFBD", "LFCS", "LFDI", "LFDR", "LFDM", "LFDF", "LFBS", "LFCH", "LFCD", "LFIV", "LFDK", "LFCY", 
    "LFDC", "LFCZ", "LFBZ", "LFBP", "LFBT", "LFDT", "LFRB", "LFRQ", "LFES", "LFRO", "LFRT", "LFED", "LFEC", "LFRV", "LFEQ", "LFEA",
    "LFEB", "LFRD", "LFRU", "LFDY", "NTAA", "NTTM", "FMEE",
    
    # Ajoutez d'autres codes OACI ici...
]

# Chargement des correspondances entre les codes OACI et les noms des aérodromes à partir d'un fichier CSV
correspondances = pd.read_csv("correspondances_oaci.csv", delimiter=";")

# Fonction pour obtenir le nom de l'aérodrome à partir de son code OACI
def get_aerodrome_name(oaci_code):
    row = correspondances[correspondances["co OACI"] == oaci_code]
    if not row.empty:
        return row["Nom"].values[0]
    else:
        return None

def get_coordinates(oaci_code):
    geolocator = Nominatim(user_agent="aerodrome_locator")
    location = geolocator.geocode(oaci_code + ", France")
    if location:
        return location.latitude, location.longitude
    else:
        return None

# Créer un DataFrame pour stocker les données des aérodromes
df = pd.DataFrame(columns=["code OACI", "Nom", "Latitude", "Longitude"])

'''
# Remplir le DataFrame avec les coordonnées et les noms des aérodromes
for oaci_code in codes_oaci:
    coordinates = get_coordinates(oaci_code)
    aerodrome_name = get_aerodrome_name(oaci_code)
    if coordinates and aerodrome_name:
        df = pd.concat([df, pd.DataFrame({
    "code OACI": [oaci_code],
    "Nom": [aerodrome_name],
    "Latitude": [coordinates[0]],
    "Longitude": [coordinates[1]]
})], ignore_index=True)
'''

conn = sqlite3.connect('tanair.db')
cursor = conn.cursor()
query = "INSERT INTO Aerodrome (nom,latitude,longitude,codeOACI) VALUES (?,?,?,?)"

for oaci_code in codes_oaci :
    coordinates = get_coordinates(oaci_code)
    aerodrome_name = get_aerodrome_name(oaci_code)
    cursor.execute(query,(aerodrome_name,coordinates[0],coordinates[1],oaci_code))
    print(oaci_code + "a été ajouté avec succès")
    conn.commit()

close_db()

'''
# Afficher le DataFrame
print(df)
'''