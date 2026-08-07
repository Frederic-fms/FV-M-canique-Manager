import customtkinter as ctk
import sqlite3
from tkinter import ttk

class SelectionVehicule:

    def __init__(self, parent, callback, client_id):

        self.parent = parent
        self.callback= callback
        self.client_id=client_id

        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("Sélection d'un vehicule")
        self.fenetre.geometry("900x500")

        self.creer_interface()
        self.charger_vehicules()
        self.fenetre.grab_set()

    def creer_interface(self):

        # Barre de recherche
        self.recherche = ctk.CTkEntry(
            self.fenetre,
            placeholder_text="Rechercher un vehicule..."
        )
        self.recherche.pack(fill="x", padx=10, pady=10)

        # Tableau des vehicules
        colonnes = (
            "immatriculation",
            "marque",
            "modele",
            "motorisation",
            "nom",
            "prenom"
        )

        self.table = ttk.Treeview(
            self.fenetre,
            columns=colonnes,
            show="headings",
            height=15
        )

        self.table.heading("immatriculation", text="Immatriculation")
        self.table.heading("marque", text="Marque")
        self.table.heading("modele", text="Modele")
        self.table.heading("motorisation", text="Motorisation")
        self.table.heading("nom", text="Nom")
        self.table.heading("prenom", text="Prenom")
        

        self.table.column("immatriculation", width=100)
        self.table.column("marque", width=180)
        self.table.column("modele", width=150)
        self.table.column("motorisation", width=140)
        

        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        self.table.bind("<Double-1>",
        self.selectionner_vehicule)

    def selectionner_vehicule(self, event=None):

        selection = self.table.selection()

        if not selection:
            return

        valeurs = self.table.item(selection[0], "values")

        self.callback(valeurs)

        self.fenetre.destroy()

    def charger_vehicules(self):

        self.table.delete(*self.table.get_children())

        self.cur.execute("""
            SELECT
            v.immatriculation,
            v.marque,
            v.modele,
            v.motorisation,
            c.nom,
            c.prenom
            FROM vehicules v
            LEFT JOIN clients c
            ON v.client_id= c.id
            WHERE v.client_id=?
            ORDER BY v.immatriculation
        """, (self.client_id,))

        for vehicule in self.cur.fetchall():
            self.table.insert("", "end", values=vehicule)
