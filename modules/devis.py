import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from CTkListbox import CTkListbox
devis_selectionne = None

def ouvrir(parent):

    fenetre = ctk.CTkToplevel(parent)
    fenetre.title("Gestion des devis")
    fenetre.geometry("1200x700")

    gauche = ctk.CTkFrame(fenetre, width=350)
    gauche.pack(side="left", fill="y", padx=10, pady=10)

    droite = ctk.CTkFrame(fenetre)
    droite.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(
        gauche,
        text="Nouveau devis",
        font=("Arial", 22, "bold")
    ).pack(pady=15)

    champs = [
        "Numéro devis",
        "Date",
        "Client",
        "Immatriculation",
        "Montant HT",
        "TVA",
        "Montant TTC"
    ]

    entrees = {}

    for champ in champs:
        ctk.CTkLabel(
            gauche,
            text=champ,
            anchor="w"
        ).pack(fill="x", padx=10)

        entree = ctk.CTkEntry(
            gauche,
            width=300
        )
        entree.pack(padx=10, pady=(0,8))

        entrees[champ] = entree

    ctk.CTkLabel(
        gauche,
        text="Travaux"
    ).pack(fill="x", padx=10)

    travaux = ctk.CTkTextbox(
        gauche,
        width=300,
        height=120
    )
    travaux.pack(padx=10, pady=(0,10))
    def charger_liste():

        liste.delete("all")

        conn = sqlite3.connect("fms_manager.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT numero, date, client, montant_ttc
            FROM devis
            ORDER BY id DESC
        """)

        lignes = cur.fetchall()
        conn.close()

        if not lignes:
            liste.insert("end", "Aucun devis enregistré.")
            return

        for numero, date, client, montant in lignes:
            liste.insert(
                "end",
                f"{numero} | {date} | {client} | {montant} €\n"
            )


    def enregistrer():

        try:

            conn = sqlite3.connect("fms_manager.db")
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO devis(
                    numero,
                    date,
                    client,
                    immatriculation,
                    montant_ht,
                    tva,
                    montant_ttc,
                    travaux
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (

                entrees["Numéro devis"].get(),
                entrees["Date"].get(),
                entrees["Client"].get(),
                entrees["Immatriculation"].get(),
                entrees["Montant HT"].get(),
                entrees["TVA"].get(),
                entrees["Montant TTC"].get(),
                travaux.get("1.0", "end").strip()

            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "FMS Manager V2",
                "Devis enregistré avec succès."
            )

            charger_liste()

            for entree in entrees.values():
                entree.delete(0, "end")

            travaux.delete("1.0", "end")

        except Exception as erreur:

            messagebox.showerror(
                "Erreur",
                str(erreur)
            )
    def modifier():
        messagebox. showinfo(
            "FMS Manager V2",
            "Fonction Modifier en cours de création."
            )

    # ==========================
    # Boutons
    # ==========================

    cadre_boutons = ctk.CTkFrame(droite)
    cadre_boutons.pack(pady=15)

    ctk.CTkButton(
        cadre_boutons,
        text="📝 Enregistrer",
        width=150,
        command=enregistrer
    ).grid(row=0, column=0, padx=5)

    ctk.CTkButton(
        cadre_boutons,
        text="✏️ Modifier",
        width=150,
        command=modifier
    ).grid(row=0, column=1, padx=5)

    ctk.CTkButton(
        cadre_boutons,
        text="🗑️ Supprimer",
        width=150,
        state="disabled"
    ).grid(row=0, column=2, padx=5)

    ctk.CTkLabel(
        droite,
        text="Liste des devis",
        font=("Arial", 18, "bold")
    ).pack(pady=(15, 5))

    liste = CTkListbox(
        droite,
        width=650,
        height=180
         )
    liste.pack(fill="x", padx=10, pady=(0, 10))

    charger_liste()
