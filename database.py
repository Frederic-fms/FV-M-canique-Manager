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
        type_client TEXT,
        nom TEXT NOT NULL,
        prenom TEXT,
        siret TEXT,
        telephone TEXT,
        telephone2 TEXT,
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
        mise_en_circulation TEXT,
        controle_technique TEXT,
        observations TEXT,
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
     travaux TEXT,
     statut TEXT DEFAULT 'En attente'
     )
     """)

    cur.execute("""
     CREATE TABLE IF NOT EXISTS factures(
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     numero TEXT,
     date TEXT,
     client TEXT,
     immatriculation TEXT,
     montant_ht REAL,
     tva REAL,
     montant_ttc REAL,
     acompte REAL DEFAULT 0,
     reste_a_payer REAL DEFAULT 0,
     mode_paiement TEXT,
     statut TEXT DEFAULT 'En attente',
     travaux TEXT
     )
     """)

    cur.execute("""
     CREATE TABLE IF NOT EXISTS reparations(
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     numero TEXT,
     date TEXT,
     client TEXT,
     immatriculation TEXT,
     kilometrage INTEGER,
     travaux_prevus TEXT,
     travaux_effectues TEXT,
     temps_main_oeuvre REAL,
     observations TEXT,
     statut TEXT DEFAULT 'En attente',
     devis_id INTEGER,
     facture_id INTEGER
     )
     """)

    # ==============================
    # TABLE PRESTATIONS
    # ==============================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS devis_lignes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        devis_id INTEGER,
        reference TEXT,
        designation TEXT,
        qte REAL,
        pu_ht REAL,
        tva REAL,
        total REAL,
        FOREIGN KEY(devis_id) REFERENCES devis(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ordres_reparation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT,
        date TEXT,
        client TEXT,
        immatriculation TEXT,
        kilometrage INTEGER,
        travaux_prevus TEXT,
        travaux_effectues TEXT,
        temps_mo REAL,
        observations TEXT,
        statut TEXT
         )
         """)

    # ==========================================
    # TABLE PRESTATIONS
    # ==========================================
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prestations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference TEXT UNIQUE,
        designation TEXT NOT NULL,
        categorie TEXT,
        type_tarification TEXT,
        unite TEXT,
        quantite REAL,
        prix_ht REAL,
        tva REAL,
        prix_ttc REAL
    )
    """)

    cur.execute("PRAGMA table_info(prestations)")
    print("Colonnes prestations :",cur.fetchall())


    conn.commit()
    conn.close()


creer_base()

def supprimer_prestation(reference):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM prestations WHERE reference=?",
        (reference,)
    )

    conn.commit()
    conn.close()


def modifier_prestation(reference,
                        designation,
                        categorie,
                        type_tarification,
                        unite,
                        quantite,
                        prix_ht,
                        tva,
                        prix_ttc):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        UPDATE prestations
        SET
            designation=?,
            categorie=?,
            type_tarification=?,
            unite=?,
            quantite=?,
            prix_ht=?,
            tva=?,
            prix_ttc=?
        WHERE reference=?
    """, (
        designation,
        categorie,
        type_tarification,
        unite,
        quantite,
        prix_ht,
        tva,
        prix_ttc,
        reference
    ))

    conn.commit()
    conn.close()


def recuperer_prestation(reference):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT reference,
               designation,
               categorie,
               type_tarification,
               unite,
               quantite,
               prix_ht,
               tva,
               prix_ttc
        FROM prestations
        WHERE reference=?
    """, (reference,))

    prestation = cur.fetchone()

    conn.close()

    return prestation


def ajouter_prestation(reference, designation, categorie, type_tarification,
                       unite, quantite, prix_ht,
                       tva, prix_ttc):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO prestations
        (reference, designation, categorie, type_tarification,
         unite, quantite, prix_ht,
         tva, prix_ttc)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reference,
        designation,
        categorie,
        type_tarification,
        unite,
        quantite,
        prix_ht,
        tva,
        prix_ttc
    ))

    conn.commit()
    conn.close()
