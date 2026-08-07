import customtkinter as ctk
import sqlite3
from tkinter import ttk

class SelectionClient:

    def __init__(self, parent, callback):

        self.parent = parent
        self.callback= callback

        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("Sélection d'un client")
        self.fenetre.geometry("900x500")

        self.creer_interface()
        self.charger_clients()
        self.fenetre.grab_set()

    def creer_interface(self):

        # Barre de recherche
        self.recherche = ctk.CTkEntry(
            self.fenetre,
            placeholder_text="Rechercher un client..."
        )
        self.recherche.pack(fill="x", padx=10, pady=10)

        # Tableau des clients
        colonnes = (
            "type",
            "nom",
            "prenom",
            "telephone",
            "ville"
        )

        self.table = ttk.Treeview(
            self.fenetre,
            columns=colonnes,
            show="headings",
            height=15
        )

        self.table.heading("type", text="Type")
        self.table.heading("nom", text="Nom")
        self.table.heading("prenom", text="Prénom")
        self.table.heading("telephone", text="Téléphone")
        self.table.heading("ville", text="Ville")

        self.table.column("type", width=100)
        self.table.column("nom", width=180)
        self.table.column("prenom", width=150)
        self.table.column("telephone", width=140)
        self.table.column("ville", width=180)

        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        self.table.bind("<Double-1>",
        self.selectionner_client)

    def selectionner_client(self, event=None):

        selection = self.table.selection()

        if not selection:
            return

        index = self.table.index(selection[0])

        self.cur.execute("""
            SELECT id, type_client, nom, prenom, telephone, ville
            FROM clients
            ORDER BY nom
        """)

        valeurs = self.cur.fetchall()[index]

        self.callback(valeurs)

        self.fenetre.destroy()


    def charger_clients(self):

        self.table.delete(*self.table.get_children())

        self.cur.execute("""
            SELECT id, type_client, nom, prenom, telephone, ville
            FROM clients
            ORDER BY nom
        """)

        for client in self.cur.fetchall():
            self.table.insert("", "end", values=client[1:])
