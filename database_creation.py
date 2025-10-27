import sqlite3
db = sqlite3.connect("AdoptionCenter.db")

db.execute("create table if not exists Adopteurs(code_ad integer PRIMARY KEY, nom_ad text, prenom_ad text, numero texte, adresse text)")
db.execute("create table if not exists Animaux(code_an integer PRIMARY KEY, nom_an text, race text, status text)")
db.execute("""
CREATE TABLE IF NOT EXISTS Adoptions(
    code_an INTEGER,
    code_ad INTEGER,
    date TEXT,
    FOREIGN KEY (code_an) REFERENCES Animaux(code_an),
    FOREIGN KEY (code_ad) REFERENCES Adopteurs(code_ad)
)
""")

db.commit()

#data des adopteurs deja inscrits
adopteurs_data = [
    (1, "El Amrani", "Sofia", "0612345678", "Casablanca"),
    (2, "Benkirane", "Youssef", "0623456789", "Rabat"),
    (3, "Mansouri", "Salma", "0634567890", "Marrakech"),
    (4, "Fassi", "Adam", "0645678901", "Fes"),
    (5, "Cherkaoui", "Lina", "0656789012", "Tangier"),
    (6, "Bouazizi", "Rachid", "0667890123", "Agadir"),
    (7, "Ziani", "Aya", "0678901234", "Tetouan"),
    (8, "Haddad", "Karim", "0689012345", "Oujda"),
    (9, "Rahimi", "Imane", "0690123456", "Kenitra"),
    (10, "Ouazzani", "Samir", "0601234567", "El Jadida")
]

for adopter in adopteurs_data:
    db.execute("insert into Adopteurs(code_ad, nom_ad, prenom_ad, numero, adresse) VALUES (?, ?, ?, ?, ?)", adopter)

db.commit()

# data des animaux
animaux_data = [
    (1, 'Bella', 'Chien', 'Non Adopté'),
    (2, 'Max', 'Chat', 'Non Adopté'),
    (3, 'Luna', 'Chien', 'Adopté'),
    (4, 'Oliver', 'Chat', 'Non Adopté'),
    (5, 'Charlie', 'Lapin', 'Non Adopté'),
    (6, 'Daisy', 'Chien', 'Non Adopté'),
    (7, 'Milo', 'Chat', 'Adopté'),
    (8, 'Coco', 'Perroquet', 'Adopté'),
    (9, 'Rocky', 'Chien', 'Adopté'),
    (10, 'Lucy', 'Chat', 'Adopté'),
    (11, 'Simba', 'Hamster','Adopté'),
    (12, 'Mimi', 'Chien', 'Adopté'),
    (13, 'Lala', 'Chat', 'Adopté'),
    (14, 'Sunny', 'Perroquet','Adopté'),
    (15, 'Oreo', 'Lapin', 'Adopté')

]

for animal in animaux_data:
    db.execute("insert into Animaux(code_an, nom_an, race, status) VALUES (?, ?, ?, ?)", animal)

db.commit()

# data des adoptions deja executées
adoption_data=[
    (3,1,"21 Juillet 2025"),
    (7,2,"23 Mai 2025"),
    (8,3,"17 Mars 2025"),
    (9,4,"11 Juin 2025"),
    (10,5,"22 Janvier 2025"),
    (11,6,"25 Fevrier 2025"),
    (12,7,"1 Mai 2025"),
    (13,8,"10 Novembre 2025"),
    (14,9,"4 Juin 2025"),
    (15,10,"20 Octobre 2025")

]

for adoption in adoption_data :
    db.execute("insert into Adoptions(code_an ,code_ad,date)VALUES(?,?,?)",adoption)

db.commit()

db.close()