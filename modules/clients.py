import customtkinter as ctk
import sqlite3
from tkinter import messagebox


def ouvrir(parent):

    fenetre = ctk.CTkToplevel(parent)
    fenetre.title("Gestion des clients")
    fenetre.geometry("1200x700")

    titre = ctk.CTkLabel(
        fenetre,
        text="👤 Gestion des clients",
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
        "Nom",
        "Prénom",
        "Téléphone",
        "Email",
        "Adresse",
        "Code postal",
        "Ville"
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

    ctk.CTkLabel(
        droite,
        text="Observations",
        font=("Arial", 18, "bold")
    ).pack(pady=(10,5))

    observations = ctk.CTkTextbox(
        droite,
        width=650,
        height=200
    )

    observations.pack(fill="both", expand=True, padx=10)
    # ==========================
    # Fonction Enregistrer
    # ==========================

    def enregistrer():

        try:

            conn = sqlite3.connect("fms_manager.db")
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO clients (
                    nom,
                    prenom,
                    telephone,
                    email,
                    adresse,
                    code_postal,
                    ville,
                    observations
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (

                entrees["Nom"].get(),
                entrees["Prénom"].get(),
                entrees["Téléphone"].get(),
                entrees["Email"].get(),
                entrees["Adresse"].get(),
                entrees["Code postal"].get(),
                entrees["Ville"].get(),
                observations.get("1.0", "end").strip()

            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "FMS Manager V2",
                "Client enregistré avec succès."
            )

            charger_liste()
            
            for entree in entrees.values():
                entree.delete(0, "end")

            observations.delete("1.0", "end")

        except Exception as erreur:

            messagebox.showerror(
                "Erreur",
                str(erreur)
            )
    # ==========================
    # Boutons
    # ==========================

    cadre_boutons = ctk.CTkFrame(droite)
    cadre_boutons.pack(pady=15)

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
    # Liste des clients
    # ==========================

    ctk.CTkLabel(
        droite,
        text="Liste des clients",
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
                nom,
                prenom,
                telephone
            FROM clients
            ORDER BY nom, prenom
        """)

        lignes = cur.fetchall()

        conn.close()

        if not lignes:
            liste.insert("end", "Aucun client enregistré.")
            return

        for nom, prenom, telephone in lignes:

            liste.insert(
                "end",
                f"{nom} {prenom} | {telephone}\n"
            )

    charger_liste()
