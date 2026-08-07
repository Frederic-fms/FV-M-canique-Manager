import customtkinter as ctk
import sqlite3
from tkinter import ttk


class CataloguePrestations(ctk.CTkToplevel):

    def __init__(self, parent, callback):

        super().__init__(parent)

        self.callback = callback

        self.title("Catalogue des prestations")

        self.geometry("1000x650")

        self.grab_set()

        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        self.creer_interface()

    def creer_interface(self):

        ctk.CTkLabel(
            self,
            text="Catalogue des prestations",
            font=("Arial", 22, "bold")
        ).pack(pady=15)

        self.recherche = ctk.CTkEntry(
            self,
            placeholder_text="Rechercher une prestation..."
        )

        self.recherche.pack(
            fill="x",
            padx=15,
            pady=10
        )

        self.recherche.bind(
            "<KeyRelease>",
            self.rechercher
        )

        self.tree = ttk.Treeview(
            self,
            columns=("reference", "designation", "categorie", "prix_ht", "tva", 
                     "prix_ttc", "temps_heures","temps_minutes",),
            show="headings",
            height=20)

        self.tree.heading("reference", text="Référence")
        self.tree.heading("designation", text="Désignation")
        self.tree.heading("categorie", text="Catégorie")
        self.tree.heading("prix_ht", text="prix_ht")
        self.tree.heading("tva", text="tva")
        self.tree.heading("prix_ttc", text="Prix TTC")
        self.tree.heading("temps_heures", text="H")
        self.tree.heading("temps_minutes", text="Min")

        self.tree.column("reference", width=120)
        self.tree.column("designation", width=450)
        self.tree.column("categorie", width=180)
        self.tree.column("prix_ht", width=90, anchor="e")
        self.tree.column("tva", width=60, anchor="center")
        self.tree.column("prix_ttc", width=90, anchor="e")
        self.tree.column("temps_heures", width=50, anchor="center")
        self.tree.column("temps_minutes", width=60, anchor="center")

        self.tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.tree.bind(
            "<Double-1>",
            self.choisir_prestation
        )

        self.charger_prestations()

    def charger_prestations(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cur.execute("""
            SELECT
                reference,
                designation,
                categorie,
                prix_ht,
                tva,
                prix_ttc,
                temps_heures,
                temps_minutes
            FROM prestations
            ORDER BY designation
        """)
        prestations=self.cur.fetchall()

        for prestation in prestations:
            self.tree.insert(
                "",
                "end",
                values=prestation
            )

    def choisir_prestation(self, event):

        selection = self.tree.selection()

        if not selection:
            return

        valeurs = self.tree.item(selection[0], "values")

        self.callback(valeurs)

        self.destroy()

    def rechercher(self, event=None):

        texte = self.recherche.get().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cur.execute("""
            SELECT
                reference,
                designation,
                categorie,
                prix_ht,
                tva,
                prix_ttc,
                temps_heures,
                temps_minutes
            FROM prestations
            WHERE
                reference LIKE ?
                OR designation LIKE ?
                OR categorie LIKE ?
            ORDER BY designation
        """, (
            f"%{texte}%",
            f"%{texte}%",
            f"%{texte}%"
        ))

        for prestation in self.cur.fetchall():
            self.tree.insert("", "end", values=prestation)
