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
        numero TEXT UNIQUE,
        date TEXT,
        client TEXT,
        client_id INTEGER,
        immatriculation TEXT,
        statut TEXT,
        echeance TEXT,
        observations TEXT,
        remise REAL DEFAULT 0,
        deja_verse REAL DEFAULT 0,
        total_ht REAL DEFAULT 0,
        tva REAL DEFAULT 0,
        total_ttc REAL DEFAULT 0
    )
    """)
    try:
        cur.execute("ALTER TABLE devis ADD COLUMN client_id INTEGER")
    except:
        pass

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
    CREATE TABLE IF NOT EXISTS lignes_devis(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        devis_id INTEGER,
        reference TEXT,
        designation TEXT,
        quantite REAL,
        prix_ht REAL,
        tva REAL,
        total REAL,
        FOREIGN KEY(devis_id) REFERENCES devis(id)
    )
    """)
    try:
        cur.execute("ALTER TABLE lignes_devis ADD COLUMN heures INTEGER DEFAULT 0")
    except:
        pass
    try:
        cur.execute("ALTER TABLE lignes_devis ADD COLUMN minutes INTEGER DEFAULT 0")
    except:
        pass
    try:
        cur.execute("""ALTER TABLE lignes_devis ADD COLUMN temps_heures_unitaire INTEGER DEFAULT 0""")
    except:
        pass
    try:
        cur.execute("""ALTER TABLE lignes_devis ADD COLUMN temps_minutes_unitaire INTEGER DEFAULT 0""")
    except:
        pass
    cur.execute("PRAGMA table_info(lignes_devis)")
    print("Colonnes lignes_devis :")
    print(cur.fetchall())
    conn.commit()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ordres_reparation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT,
        date TEXT,
        client TEXT,
        client_id INTEGER,
        devis_id INTEGER,
        facture INTEGER,
        immatriculation TEXT,
        kilometrage INTEGER,
        travaux_prevus TEXT,
        travaux_effectues TEXT,
        temps_prevu TEXT,
        temps_reel TEXT,
        observations TEXT,
        statut TEXT
         )
         """)
    try:
        cur.execute("ALTER TABLE ordres_reparation ADD COLUMN client_id INTEGER")
    except:
        pass
    try:
        cur.execute("ALTER TABLE ordres_reparation ADD COLUMN devis_id INTEGER")
    except:
        pass
    try:
        cur.execute("ALTER TABLE ordres_reparation ADD COLUMN facture_id INTEGER")
    except:
        pass
    try:
        cur.execute("ALTER TABLE ordres_reparation ADD COLUMN temps_prevu TEXT")
    except:
        pass
    try:
        cur.execute("ALTER TABLE ordres_reparation ADD COLUMN temps_reel TEXT")
    except:
        pass
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lignes_or(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        or_id INTEGER,
        designation TEXT,
        quantite REAL,
        temps TEXT,
        prix_ht REAL,
        total REAL,
        FOREIGN KEY(or_id) REFERENCES ordres_reparation(id)
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
        temps_heures INTEGER DEFAULT 0,
        temps_minutes INTEGER DEFAULT 0,
        prix_ttc REAL
    )
    """)
    try:
        cur.execute("ALTER TABLE prestations ADD COLUMN temps_heures INTEGER DEFAULT 0")
    except:
        pass
    try:
        cur.execute("ALTER TABLE prestations ADD COLUMN temps_minutes INTEGER DEFAULT 0")
    except:
        pass
    try:
        cur.execute("ALTER TABLE prestations ADD COLUMN favori INTEGER DEFAULT 0")
    except:
        pass
    try:
        cur.execute("ALTER TABLE prestations ADD COLUMN actif INTEGER DEFAULT 1")
    except:
        pass
    try:
        cur.execute("ALTER TABLE prestations ADD COLUMN forfait INTEGER DEFAULT 0")
    except:
        pass
    cur.execute("PRAGMA table_info(prestations)")
    colonnes= cur.fetchall()
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
                        temps_heures,
                        temps_minutes,
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
            temps_heures=?,
            temps_minutes=?,
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
        temps_heures,
        temps_minutes,
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
               temps_heures,
               temps_minutes,
               prix_ttc
        FROM prestations
        WHERE reference=?
    """, (reference,))

    prestation = cur.fetchone()

    conn.close()

    return prestation

def recuperer_toutes_prestations():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            reference,
            designation,
            categorie,
            type_tarification,
            temps_heures,
            temps_minutes,
            prix_ht
        FROM prestations
        WHERE actif=1
        ORDER BY categorie, designation
    """)

    resultat = cur.fetchall()

    conn.close()

    return resultat


def ajouter_prestation(reference, designation, categorie, type_tarification,
                       unite, quantite, prix_ht,
                       tva, temps_heures, temps_minutes, prix_ttc):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO prestations
        (reference, designation, categorie, type_tarification,
         unite, quantite, prix_ht,
         tva, temps_heures, temps_minutes, prix_ttc)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reference,
        designation,
        categorie,
        type_tarification,
        unite,
        quantite,
        prix_ht,
        tva,
        temps_heures,
        temps_minutes,
        prix_ttc
    ))

    conn.commit()
    conn.close()

def creer_or_depuis_devis(numero,
                          date,
                          client,
                          client_id,
                          immatriculation,
                          observations):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
   
    annee = date.split("/")[-1]

    cur.execute("""
        SELECT numero
        FROM ordres_reparation
        WHERE numero LIKE ?
        ORDER BY id DESC
        LIMIT 1
    """, (f"OR-{annee}-%",))

    resultat = cur.fetchone()

    if resultat:
        dernier = int(resultat[0].split("-")[-1]) + 1
    else:
        dernier = 1

    numero_or = f"OR-{annee}-{dernier:04d}"

    cur.execute("""
        INSERT INTO ordres_reparation
        (
            numero,
            date,
            client,
            client_id,
            immatriculation,
            observations,
            statut
        )
        VALUES (?,?,?,?,?,?,?)
    """, (
        numero_or,
        date,
        client,
        client_id,
        immatriculation,
        observations,
        "En attente"
    ))
    # ID du nouvel OR
    or_id = cur.lastrowid

    # Récupérer l'id du devis
    cur.execute("SELECT id FROM devis WHERE numero=?", (numero,))
    resultat = cur.fetchone()

    if resultat:
        devis_id = resultat[0]

        # Copier les prestations du devis
        cur.execute("""
            SELECT
                designation,
                quantite,
                heures,
                minutes,
                prix_ht,
                total
            FROM lignes_devis
            WHERE devis_id=?
        """, (devis_id,))

        for ligne in cur.fetchall():
            cur.execute("""
                INSERT INTO lignes_or
                (
                    or_id,
                    designation,
                    quantite,
                    temps,
                    prix_ht,
                    total
                )
                VALUES (?,?,?,?,?,?)
            """, (
                or_id,
                ligne[0],
                ligne[1],
                f"{ligne[2]}h {ligne[3]:02d}",
                ligne[4],
                ligne[5]
            ))

    cur.execute(
        "SELECT temps_prevu FROM ordres_reparation WHERE id=?",
        (or_id,)
    )
    print("Valeur enregistrée :",
          cur.fetchall())

               
    conn.commit()
    conn.close()
    recalculer_temps_prevu(or_id)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT temps_prevu FROM ordres_reparation WHERE id=?",
                (or_id,))
    print("Temps prevu apres recalcul :", cur.fetchone())
    conn.close()

    return numero_or
def recalculer_temps_prevu(or_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT temps
        FROM lignes_or
        WHERE or_id=?
    """, (or_id,))

    total_minutes = 0

    for (temps,) in cur.fetchall():
        if temps:
            try:
                h, m = temps.replace(" ", "").split("h")
                total_minutes += int(h) * 60 + int(m)
            except:
                pass

    heures = total_minutes // 60
    minutes = total_minutes % 60

    temps_prevu = f"{heures} h {minutes:02d}"

    cur.execute("""
        UPDATE ordres_reparation
        SET temps_prevu=?
        WHERE id=?
    """, (temps_prevu, or_id))

    conn.commit()
    conn.close()


def recuperer_email_client(client_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT email FROM clients WHERE id=?",
        (client_id,)
    )

    resultat = cur.fetchone()

    conn.close()

    if resultat:
        return resultat[0]

    return ""

    conn.commit()

    conn.close()

def importer_catalogue_fms():

    prestations = [ 
    ("ENT-001","Vidange moteur (Huile standard 10W40/5W40) + Filtre à huile","Entretien","FF","Forfait",1,49.17,20,0,30,59.00,1),

    ("ENT-002","Vidange moteur (Huile synthèse 5W30/0W20) + Filtre à huile","Entretien","FF","Forfait",1,65.83,20,0,30,79.00,1),

    ("ENT-003","Remplacement du filtre à air","Entretien","T1","Pièce",1,7.50,20,0,9,9.00,1),

    ("ENT-004","Remplacement du filtre d'habitacle (Pollen)","Entretien","T1","Pièce",1,10.00,20,0,12,12.00,1),

    ("ENT-005","Remplacement du filtre à carburant (Gazole / Essence)","Entretien","T1","Pièce",1,17.50,20,0,21,21.00,1),

    ("ENT-006","Révision complète (4 filtres + Vidange + 30 points de contrôle)","Entretien","FF","Forfait",1,157.50,20,1,30,189.00,1),

    ("ENT-007","Remplacement de 4 bougies d'allumage (Essence)","Entretien","T1","Pièce",1,25.00,20,0,30,30.00,1),

    ("ENT-008","Remplacement des bougies de préchauffage (Diesel - accès direct)","Entretien","T2","Pièce",1,48.00,20,0,48,57.60,1),

    ("ENT-009","Niveau & appoint additif AdBlue (Forfait 10L inclus)","Entretien","FF","Forfait",1,25.00,20,0,12,30.00,1),

    ("ENT-010","Mise à niveau de l'ensemble des fluides","Entretien","T1","Forfait",1,12.50,20,0,15,15.00,1),

    

]


    

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for prestation in prestations:
        try:
            cur.execute("""
                INSERT INTO prestations
                (
                    reference,
                    designation,
                    categorie,
                    type_tarification,
                    unite,
                    quantite,
                    prix_ht,
                    tva,
                    temps_heures,
                    temps_minutes,
                    prix_ttc,
                    actif
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, prestation)

        except sqlite3.IntegrityError:
            # La prestation existe déjà
            pass

    conn.commit()
    conn.close()
