import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

import sqlite3
import shutil
import os

try:
    from PIL import Image
except ImportError:
    Image = None


def ouvrir(parent):

    fenetre = ctk.CTkToplevel(parent)
    fenetre.title("Gestion des véhicules")
    fenetre.geometry("1500x900")
    fenetre.grab_set()

    principal = ctk.CTkFrame(
        fenetre,
        corner_radius=10
    )

    principal.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    gauche = ctk.CTkFrame(
        principal,
        width=400,
        corner_radius=10
    )

    gauche.pack(
        side="left",
        fill="y",
        padx=(0,10)
    )

    gauche.pack_propagate(False)

    droite = ctk.CTkFrame(
        principal,
        corner_radius=10
    )

    droite.pack(
        side="right",
        fill="both",
        expand=True
    )

    titre = ctk.CTkLabel(
        gauche,
        text="🚗 GESTION DES VÉHICULES",
        font=("Arial",28,"bold")
    )

    titre.pack(
        pady=(20,25)
    )
    champs = [
        "Client",
        "Immatriculation",
        "Marque",
        "Modèle",
        "Version",
        "Motorisation",
        "Carburant",
        "Boîte",
        "Année",
        "Kilométrage",
        "VIN",
        "Couleur"
    ]

    entrees = {}

    for champ in champs:

        ctk.CTkLabel(
            gauche,
            text=champ,
            font=("Arial",15)
        ).pack(
            anchor="w",
            padx=20,
            pady=(5,0)
        )

        if champ == "Client":

            widget = ctk.CTkComboBox(
                gauche,
                values=[],
                width=340,
                height=36
            )

        else:

            widget = ctk.CTkEntry(
                gauche,
                width=340,
                height=36
            )

        widget.pack(
            padx=20,
            pady=(0,8)
        )

        entrees[champ] = widget
    # ==========================================
    # Barre des boutons
    # ==========================================

    barre = ctk.CTkFrame(
        droite,
        fg_color="transparent"
    )

    barre.pack(
        fill="x",
        padx=15,
        pady=(15,10)
    )

    bouton_enregistrer = ctk.CTkButton(
        barre,
        text="💾 Enregistrer",
        width=170,
        height=45,
        fg_color="#d50000",
        hover_color="#b00000",
        font=("Arial",16,"bold")
    )
    bouton_enregistrer.pack(side="left", padx=5)

    bouton_modifier = ctk.CTkButton(
        barre,
        text="✏ Modifier",
        width=170,
        height=45,
        fg_color="#d50000",
        hover_color="#b00000",
        font=("Arial",16,"bold")
    )
    bouton_modifier.pack(side="left", padx=5)

    bouton_supprimer = ctk.CTkButton(
        barre,
        text="🗑 Supprimer",
        width=170,
        height=45,
        fg_color="#d50000",
        hover_color="#b00000",
        font=("Arial",16,"bold")
    )
    bouton_supprimer.pack(side="left", padx=5)

    recherche = ctk.CTkEntry(
        barre,
        width=300,
        height=45,
        placeholder_text="Rechercher..."
    )
    recherche.pack(side="right", padx=5)

    bouton_recherche = ctk.CTkButton(
        barre,
        text="🔍",
        width=55,
        height=45,
        fg_color="#d50000",
        hover_color="#b00000"
    )
    bouton_recherche.pack(side="right", padx=5)
    

    
    colonnes = (
        "Client",
        "Immatriculation",
        "Marque",
        "Modèle",
        "Version"
    )

    liste = ttk.Treeview(
        droite,
        columns=colonnes,
        show="headings",
        height=18
    )

    for col in colonnes:
        liste.heading(col, text=col)
        liste.column(col, width=180)

    liste.pack(
        fill="both",
        expand=True,
        padx=15
    )
    # ==========================================
    # Bas de la fenêtre
    # ==========================================

    bas = ctk.CTkFrame(droite)

    bas.pack(
        fill="x",
        padx=15,
        pady=15
    )

    # ---------- Photo ----------

    photo_frame = ctk.CTkFrame(
        bas,
        width=300,
        height=240
    )

    photo_frame.pack(
        side="left",
        padx=(0,10)
    )

    photo_frame.pack_propagate(False)

    ctk.CTkLabel(
        photo_frame,
        text="Photo",
        font=("Arial",20,"bold")
    ).pack(pady=10)

    photo_label = ctk.CTkLabel(
        photo_frame,
        text="📷\n\nAucune photo",
        font=("Arial",18),
        width=260,
        height=170
    )

    bouton_photo = ctk.CTkButton(
        photo_frame,
     text="📷 Choisir une photo",
     command=lambda:choisir_photo(),
     fg_color="#c62828",
     hover_color="#b71c1c"
     )

    bouton_photo.pack(pady=(5,10 ))


    # ---------- Observations ----------

    observations_frame = ctk.CTkFrame(bas)

    observations_frame.pack(
        side="left",
        fill="both",
        expand=True
    )

    ctk.CTkLabel(
        observations_frame,
        text="Observations",
        font=("Arial",20,"bold")
    ).pack(pady=10)

    observations = ctk.CTkTextbox(
        observations_frame,
        height=190
    )

    observations.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=(0,10)
    )
    # ==========================================
    # Chargement des clients
    # ==========================================

    def charger_clients():

        conn = sqlite3.connect("fms_manager.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT nom
            FROM clients
            ORDER BY nom
        """)

        clients = [ligne[0] for ligne in cur.fetchall()]

        conn.close()

        entrees["Client"].configure(values=clients)

        if clients:
            entrees["Client"].set(clients[0])
    # ==========================================
    # Chargement des véhicules
    # ==========================================

    def charger_vehicules():

        for item in liste.get_children():
            liste.delete(item)

        conn = sqlite3.connect("fms_manager.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT
                vehicules.id,
                clients.nom,
                vehicules.immatriculation,
                vehicules.marque,
                vehicules.modele,
                vehicules.version
            FROM vehicules
            LEFT JOIN clients
                ON clients.id = vehicules.client_id
            ORDER BY clients.nom, vehicules.marque
        """)

        vehicules = cur.fetchall()

        conn.close()

        for ligne in vehicules:

            liste.insert(
                "",
                "end",
                iid=ligne[0],
                values=(
                    ligne[1],
                    ligne[2],
                    ligne[3],
                    ligne[4],
                    ligne[5]
                )
            )
 # ==========================================
    # Véhicule sélectionné
    # ==========================================
    
    vehicule_selectionne = None
    photo_actuelle=None
    chemin_photo=""
    # ==========================================
    # Sélection d'un véhicule
    # ==========================================

    def choisir_photo():
        nonlocal chemin_photo

        fichier = filedialog.askopenfilename(
            title="Choisir une photo",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp"),
                ("Tous les fichiers", "*.*")
            ]
        )

        if fichier:
            chemin_photo = fichier

    def selectionner_vehicule(event):

        nonlocal vehicule_selectionne

        selection = liste.selection()

        if not selection:
            return

        vehicule_selectionne = int(selection[0])

        conn = sqlite3.connect("fms_manager.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT
                clients.nom,
                vehicules.immatriculation,
                vehicules.marque,
                vehicules.modele,
                vehicules.version,
                vehicules.motorisation,
                vehicules.carburant,
                vehicules.boite,
                vehicules.annee,
                vehicules.kilometrage,
                vehicules.vin,
                vehicules.couleur
            FROM vehicules
            LEFT JOIN clients
                ON clients.id = vehicules.client_id
            WHERE vehicules.id = ?
        """, (vehicule_selectionne,))

        ligne = cur.fetchone()

        conn.close()

        if ligne is None:
            return

        entrees["Client"].set("" if ligne[0] is None else ligne[0])

        noms = [
            "Immatriculation",
            "Marque",
            "Modèle",
            "Version",
            "Motorisation",
            "Carburant",
            "Boîte",
            "Année",
            "Kilométrage",
            "VIN",
            "Couleur"
        ]

        for i, nom in enumerate(noms, start=1):
            entrees[nom].delete(0, "end")
            entrees[nom].insert(0, "" if ligne[i] is None else ligne[i])

           
    # ==========================================
    # Enregistrer un véhicule
    # ==========================================

    def enregistrer():

     client = entrees["Client"].get().strip()
     nonlocal vehicule_selectionne

     if client == "":
        messagebox.showwarning(
            "FMS Manager",
            "Veuillez sélectionner un client."
        )
        return

     conn = sqlite3.connect("fms_manager.db")
     cur = conn.cursor()

     cur.execute(
        "SELECT id FROM clients WHERE nom=?",
        (client,)
     )

     resultat = cur.fetchone()

     if resultat is None:
        conn.close()
        messagebox.showerror(
            "Erreur",
            "Client introuvable."
        )
        return

     client_id = resultat[0]

     # Vérifie si l'immatriculation existe déjà
     cur.execute(
        "SELECT id FROM vehicules WHERE immatriculation=?",
        (
            entrees["Immatriculation"].get().strip(),
        )
     )
     doublon=cur.fetchone()
     if doublon:
      if vehicule_selectionne is None or doublon[0]!=vehicule_selectionne:
        conn.close()
        messagebox.showwarning(
            "FMS Manager",
            "Cette immatriculation existe déjà."
        )
        return
     if vehicule_selectionne is not None:

         cur.execute("""
            UPDATE vehicules
            SET
                client_id=?,
                immatriculation=?,
                marque=?,
                modele=?,
                version=?,
                motorisation=?,
                carburant=?,
                boite=?,
                annee=?,
                kilometrage=?,
                vin=?,
                couleur=?
            WHERE id=?
        """, (

            client_id,
            entrees["Immatriculation"].get().strip(),
            entrees["Marque"].get().strip(),
            entrees["Modèle"].get().strip(),
            entrees["Version"].get().strip(),
            entrees["Motorisation"].get().strip(),
            entrees["Carburant"].get().strip(),
            entrees["Boîte"].get().strip(),
            entrees["Année"].get().strip(),
            entrees["Kilométrage"].get().strip(),
            entrees["VIN"].get().strip(),
            entrees["Couleur"].get().strip(),
            vehicule_selectionne

        ))

     else:

          cur.execute("""
            INSERT INTO vehicules(
            client_id,
            immatriculation,
            marque,
            modele,
            version,
            motorisation,
            carburant,
            boite,
            annee,
            kilometrage,
            vin,
            couleur
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            client_id,
            entrees["Immatriculation"].get().strip(),
            entrees["Marque"].get().strip(),
            entrees["Modèle"].get().strip(),
            entrees["Version"].get().strip(),
            entrees["Motorisation"].get().strip(),
            entrees["Carburant"].get().strip(),
            entrees["Boîte"].get().strip(),
            entrees["Année"].get().strip(),
            entrees["Kilométrage"].get().strip(),
            entrees["VIN"].get().strip(),
            entrees["Couleur"].get().strip()
     ))

     conn.commit()
     conn.close()

     messagebox.showinfo(
        "FMS Manager",
        "Véhicule enregistré avec succès."
     )

     for champ, widget in entrees.items():
        if champ == "Client":
            continue
        widget.delete(0, "end")

     observations.delete("1.0", "end")

     charger_vehicules()
    
    # ==========================================
    # Initialisation
    # ==========================================
    bouton_enregistrer.configure(command=enregistrer)
    liste.bind("<<TreeviewSelect>>",selectionner_vehicule)
    charger_clients()
    charger_vehicules()
