import customtkinter as ctk
import sqlite3
from tkinter import messagebox


def ouvrir(parent):

    fenetre = ctk.CTkToplevel(parent)
    fenetre.title("Gestion des véhicules")
    fenetre.geometry("1200x700")

    titre = ctk.CTkLabel(
        fenetre,
        text="🚗 Gestion des véhicules",
        font=("Arial", 28, "bold")
    )
    titre.pack(pady=20)

    principal = ctk.CTkFrame(fenetre)
    principal.pack(fill="both", expand=True, padx=15, pady=15)

    gauche = ctk.CTkFrame(principal, width=380)
    gauche.pack(side="left", fill="y", padx=10)

    droite = ctk.CTkFrame(principal)
    droite.pack(side="right", fill="both", expand=True, padx=10)

    champs = [
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
            text=champ
        ).pack(anchor="w", padx=10, pady=(6,0))

        entree = ctk.CTkEntry(
            gauche,
            width=330
        )

        entree.pack(padx=10)

        entrees[champ] = entree

# ==========================
    # Fonction Enregistrer
    # ==========================

    def enregistrer():

        try:

            conn = sqlite3.connect("fms_manager.db")
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO vehicules (
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (

                entrees["Immatriculation"].get(),
                entrees["Marque"].get(),
                entrees["Modèle"].get(),
                entrees["Version"].get(),
                entrees["Motorisation"].get(),
                entrees["Carburant"].get(),
                entrees["Boîte"].get(),
                entrees["Année"].get(),
                entrees["Kilométrage"].get(),
                entrees["VIN"].get(),
                entrees["Couleur"].get()

            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "FMS Manager V2",
                "Véhicule enregistré avec succès."
            )
            charger_liste()
            
            for entree in entrees.values():
                entree.delete(0, "end")

        except Exception as erreur:

            messagebox.showerror(
                "Erreur",
                str(erreur)
            )
            
   # ==========================
    # Boutons
    # ==========================

    cadre_boutons = ctk.CTkFrame(droite)
    cadre_boutons.pack(pady=20)

    ctk.CTkButton(
        cadre_boutons,
        text="💾 Enregistrer",
        width=150,
        command=enregistrer
    ).grid(row=0, column=0, padx=5)

    ctk.CTkButton(
        cadre_boutons,
        text="✏ Modifier",
        width=150,
        state="disabled"
    ).grid(row=0, column=1, padx=5)

    ctk.CTkButton(
        cadre_boutons,
        text="🗑 Supprimer",
        width=150,
        state="disabled"
    ).grid(row=0, column=2, padx=5)

    ctk.CTkButton(
        cadre_boutons,
        text="🔍 Rechercher",
        width=150,
        state="disabled"
    ).grid(row=0, column=3, padx=5)

    # ==========================
    # Observations
    # ==========================

    ctk.CTkLabel(
        droite,
        text="Observations",
        font=("Arial", 18, "bold")
    ).pack(pady=(15, 5))

    observations = ctk.CTkTextbox(
        droite,
        width=650,
        height=220
    )

    observations.pack(fill="both", expand=True, padx=10)

   # ==========================
    # Liste des véhicules
    # ==========================

    ctk.CTkLabel(
        droite,
        text="Liste des véhicules",
        font=("Arial", 18, "bold")
    ).pack(pady=(15, 5))

    liste = ctk.CTkTextbox(
        droite,
        width=650,
        height=180
    )

    liste.pack(fill="x", padx=10, pady=(0, 10))

    def charger_liste():

        liste.delete("1.0", "end")

        conn = sqlite3.connect("fms_manager.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT
                immatriculation,
                marque,
                modele
            FROM vehicules
            ORDER BY marque, modele
        """)

        for immat, marque, modele in cur.fetchall():

            liste.insert(
                "end",
                f"{immat} | {marque} {modele}\n"
            )

        conn.close()

    charger_liste()
