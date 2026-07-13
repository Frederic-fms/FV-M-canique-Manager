import sqlite3

DB_NAME = "fms_manager.db"


def creer_base():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # ==========================
    # TABLE CLIENTS
    # ==========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT,
        telephone TEXT,
        email TEXT,
        adresse TEXT,
        code_postal TEXT,
        ville TEXT,
        observations TEXT
    )
    """)

    # ==========================
    # TABLE VEHICULES
    # ==========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS vehicules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        immatriculation TEXT UNIQUE,
        marque TEXT,
        modele TEXT,
        version TEXT,
        motorisation TEXT,
        carburant TEXT,
        boite TEXT,
        annee TEXT,
        kilometrage INTEGER,
        vin TEXT,
        couleur TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
    """)
    cur.execute("""
     CREATE TABLE IF NOT EXISTS devis(
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     numero TEXT,
     date TEXT,
     client TEXT,
     immatriculation TEXT,
     montant_ht REAL,
     tva REAL,
     montant_ttc REAL,
     travaux TEXT
     )
     """)

    # ==============================
    # TABLE PRESTATIONS
    # ==============================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS prestations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        devis_id INTEGER,
        designation TEXT,
        qte REAL,
        prix REAL,
        total REAL,
        FOREIGN KEY(devis_id) REFERENCES devis(id)
    )
    """)

    conn.commit()
    conn.close()


creer_base()
