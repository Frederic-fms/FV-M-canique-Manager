import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image
import sqlite3
import database


class PrestationManager:

    def __init__(self, parent):

        self.parent = parent

        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        self.entrees = {}
        self.labels = {}
        self.selection = None

        # ==========================
        # Fenêtre
        # ==========================
        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("FMS Manager - Prestations")
        self.fenetre.geometry("1500x850")
        self.fenetre.minsize(1300, 750)

        # Couleurs FMS
        self.COULEUR_FOND = "#202020"
        self.COULEUR_MENU = "#161616"
        self.COULEUR_BOUTON = "#d10000"
        self.COULEUR_HOVER = "#990000"

        self.fenetre.configure(fg_color=self.COULEUR_FOND)

        self.creer_interface()
    

    def creer_interface(self):
        

        # ==========================
        # Cadre principal
        # ==========================
        self.frame_principal = ctk.CTkFrame(
            self.fenetre,
            fg_color=self.COULEUR_FOND
        )
        self.frame_principal.pack(fill="both", expand=True)

        # ==========================
        # Bandeau supérieur
        # ==========================
        self.frame_haut = ctk.CTkFrame(
            self.frame_principal,
            height=80,
            fg_color=self.COULEUR_MENU,
            corner_radius=0
        )
        self.frame_haut.pack(fill="x")

        self.logo = ctk.CTkLabel(
            self.frame_haut,
            text="FMS",
            font=("Arial", 30, "bold"),
            text_color="#ff3030"
        )
        self.logo.pack(side="left", padx=20, pady=15)

        self.titre = ctk.CTkLabel(
            self.frame_haut,
            text="Gestion des prestations",
            font=("Arial", 24, "bold"),
            text_color="white"
        )
        self.titre.pack(side="left", padx=10)

        # ==========================
        # Corps
        # ==========================
        self.frame_corps = ctk.CTkFrame(
            self.frame_principal,
            fg_color=self.COULEUR_FOND
        )
        self.frame_corps.pack(fill="both", expand=True, padx=10, pady=10)

        # ==========================
        # Partie gauche
        # ==========================
        self.frame_gauche = ctk.CTkFrame(
            self.frame_corps,
            width=500,
            fg_color="#2b2b2b"
        )
        self.frame_gauche.pack(side="left", fill="y", padx=(0, 10))

        self.frame_gauche.pack_propagate(False)

        # ==========================
        # Recherche
        # ==========================
        self.label_recherche = ctk.CTkLabel(
            self.frame_gauche,
            text="Rechercher une prestation",
            font=("Arial", 16, "bold")
        )
        self.label_recherche.pack(pady=(15, 5))

        self.recherche = ctk.CTkEntry(
            self.frame_gauche,
            placeholder_text="Nom ou catégorie..."
        )
        self.recherche.pack(fill="x", padx=15)

        self.recherche.bind("<KeyRelease>",
        self.rechercher_prestation)

        # ==========================
        # Liste des prestations
        # ==========================
        self.tree = ttk.Treeview(
            self.frame_gauche,
            columns=("reference", "designation", "categorie", "temps", "prix_ttc"),
            show="headings",
            height=25
        )

        self.tree.heading("reference", text="Référence")
        self.tree.heading("designation", text="Désignation")
        self.tree.heading("categorie", text="Catégorie")
        self.tree.heading("temps", text="Temps")
        self.tree.heading("prix_ttc", text="Prix TTC")

        self.tree.column("reference", width=70)
        self.tree.column("designation", width=230)
        self.tree.column("categorie", width=90)
        self.tree.column("temps", width=70)
        self.tree.column("prix_ttc", width=70)


        self.tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )
        self.tree.bind("<Double-1>",
        self.selectionner_prestation)

        # ==========================
        # Partie droite
        # ==========================
        self.frame_droite = ctk.CTkFrame(
            self.frame_corps,
            fg_color="#2b2b2b"
        )
        self.frame_droite.pack(side="left", fill="both", expand=True)

        # ==========================
        # Titre
        # ==========================
        titre_formulaire = ctk.CTkLabel(
            self.frame_droite,
            text="Informations de la prestation",
            font=("Arial", 22, "bold"),
            text_color="white"
        )
        titre_formulaire.pack(pady=20)
        

        # ==========================
        # Cadre formulaire
        # ==========================
        formulaire = ctk.CTkFrame(
            self.frame_droite,
            fg_color="transparent"
        )
        
        formulaire.pack(fill="x", padx=30)

        formulaire.grid_columnconfigure(1, weight=1)
        formulaire.grid_columnconfigure(3, weight=1)
        # Liste des champs
        champs = [
            ("Référence", 0, 0),
            ("Désignation", 0, 2),
            ("Catégorie", 1, 0),
            ("Type de tarification", 1, 2),
            ("Unité", 2, 0),
            ("Quantité par défaut", 2, 2),
            ("Heures", 3, 0),
            ("Minutes", 3, 2),
            ("Prix HT (€)", 4, 0),
            ("TVA (%)", 4, 2),
            ("Prix TTC (€)", 5, 0),
        ]

        for texte, ligne, colonne in champs:

            label = ctk.CTkLabel(
                formulaire,
                text=texte,
                font=("Arial", 15, "bold")
            )

            label.grid(
                row=ligne,
                column=colonne,
                sticky="w",
                padx=10,
                pady=8
            )

            if texte == "Catégorie":
                entree = ctk.CTkComboBox(
                    formulaire,
                    width=200,
                    values=[
                    "Entretien",
                    "Mécanique",
                    "Freinage",
                    "Distribution",
                    "Pneumatiques",
                    "Diagnostic",
                    "Électricité",
                    "Climatisation",
                    "Carrosserie",
                    "Divers"
                ])
            elif texte == "Type de tarification":
                entree = ctk.CTkComboBox(
                formulaire,
                width=200,
                values=[
                    "Forfait",
                    "Horaire",
                    "Unitaire"
                ])

            elif texte == "Unité":
                entree = ctk.CTkComboBox(
                    formulaire,
                     width=200,
                     values=[
                    "Forfait",
                    "Heure",
                    "Pièce",
                    "Km",
                    "Litre"
                ])

            elif texte == "Heures":
                entree = ctk.CTkComboBox(
                    formulaire,
                    width=200,
                    values=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10" ]
                )
                entree.set("0")

            elif texte == "Minutes":
                entree = ctk.CTkComboBox(
                    formulaire,
                    width=200,
                    values=["00", "10", "15", "30", "45", "50"]
                )
                entree.set("00")
            else:
                entree =ctk.CTkEntry(formulaire,width=250)

            if texte == "Prix TTC (€)":
                entree.configure(state="readonly")

            entree.grid(
                row=ligne,
                column=colonne + 1,
                padx=10,
                pady=8
            )

            self.labels[texte] = label
            self.entrees[texte] = entree

            if texte == "Prix HT (€)":
                entree.bind("<KeyRelease>",
                            self.calculer_prix_ttc)
            if texte == "TVA (%)":
                entree.bind("<KeyRelease>",
                            self.calculer_prix_ttc)

        # ==========================
        # Boutons
        # ==========================
        frame_boutons = ctk.CTkFrame(
            self.frame_droite,
            fg_color="transparent"
        )
        frame_boutons.pack(pady=25, padx=25, anchor="e")

        ctk.CTkButton(
            frame_boutons,
            text="Nouveau",
            width=120,
            height=40,
            fg_color=self.COULEUR_BOUTON,
            hover_color=self.COULEUR_HOVER,
            command=self.nouvelle_prestation
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_boutons,
            text="Enregistrer",
            width=120,
            height=40,
            fg_color=self.COULEUR_BOUTON,
            hover_color=self.COULEUR_HOVER,
            command=self.enregistrer_prestation
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_boutons,
            text="Modifier",
            width=120,
            height=40,
            fg_color=self.COULEUR_BOUTON,
            hover_color=self.COULEUR_HOVER,
            command=self.modifier_prestation
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_boutons,
            text="Supprimer",
            width=120,
            height=40,
            fg_color=self.COULEUR_BOUTON,
            hover_color=self.COULEUR_HOVER,
            command=self.supprimer_prestation
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_boutons,
            text="Annuler",
            width=120,
            height=40,
            fg_color="#555555",
            hover_color="#444444",
            command=self.annuler
        ).pack(side="left", padx=10)

        self.charger_prestations()

        ctk.CTkButton(frame_boutons,
                      text="Importer catalogue",
                      width=120,
                      height=40,
                      fg_color="#0066cc",
                      hover_color="#004c99",
                      command=self.importer_catalogue
                      ).pack(side="left", padx=10)


    def calculer_prix_ttc(self, event=None):
        try:
            prix_ht = float(self.entrees["Prix HT (€)"].get().replace(",", "."))
            tva = float(self.entrees["TVA (%)"].get().replace(",", "."))

            prix_ttc = prix_ht * (1 + tva / 100)

            self.entrees["Prix TTC (€)"].configure(state="normal")
            self.entrees["Prix TTC (€)"].delete(0, "end")
            self.entrees["Prix TTC (€)"].insert(0, f"{prix_ttc:.2f}")
            self.entrees["Prix TTC (€)"].configure(state="readonly")

        except ValueError:
            self.entrees["Prix TTC (€)"].configure(state="normal")
            self.entrees["Prix TTC (€)"].delete(0, "end")
            self.entrees["Prix TTC (€)"].configure(state="readonly")

    def charger_prestations(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect("fms_manager.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT reference,
                   designation,
                   categorie,
                   temps_heures,
                   temps_minutes,
                   prix_ttc
            FROM prestations
            ORDER BY designation
        """)

        for ref, des, cat, h, m, prix in cur.fetchall():
            temps= f"{h} h {m:02d}"
            self.tree.insert(
                "",
                "end",
                values=(ref, des, cat, temps, prix)
            )

        conn.close()

    def selectionner_prestation(self, event):

        selection = self.tree.selection()

        if not selection:
            return

        reference = self.tree.item(selection[0], "values")[0]

        prestation = database.recuperer_prestation(reference)
        (reference,
        designation,
        categorie, type_tarification,
        unite, quantite, prix_ht, tva, temps_heures, temps_minutes,
        prix_ttc) = prestation

        self.entrees["Référence"].delete(0, "end")
        self.entrees["Référence"].insert(0, reference)

        self.entrees["Désignation"].delete(0, "end")
        self.entrees["Désignation"].insert(0, designation)

        self.entrees["Catégorie"].set(categorie)
        self.entrees["Type de tarification"].set(type_tarification)
        self.entrees["Unité"].set(unite)

        self.entrees["Quantité par défaut"].delete(0, "end")
        self.entrees["Quantité par défaut"].insert(0, str(quantite))

        self.entrees["Prix HT (€)"].delete(0, "end")
        self.entrees["Prix HT (€)"].insert(0, str(prix_ht))

        self.entrees["TVA (%)"].delete(0, "end")
        self.entrees["TVA (%)"].insert(0, str(tva))

        self.entrees["Heures"].set (str(temps_heures))
    
        self.entrees["Minutes"].set (str(temps_minutes))

        self.entrees["Prix TTC (€)"].configure(state="normal")
        self.entrees["Prix TTC (€)"].delete(0, "end")
        self.entrees["Prix TTC (€)"].insert(0, str(prix_ttc))
        self.entrees["Prix TTC (€)"].configure(state="readonly")



    def enregistrer_prestation(self):

        reference = self.entrees["Référence"].get()
        designation = self.entrees["Désignation"].get()
        categorie = self.entrees["Catégorie"].get()
        type_tarification = self.entrees["Type de tarification"].get()
        unite = self.entrees["Unité"].get()
        quantite = self.entrees["Quantité par défaut"].get()
        prix_ht = self.entrees["Prix HT (€)"].get()
        tva = self.entrees["TVA (%)"].get()
        temps_heures = self.entrees["Heures"].get()
        temps_minutes = self.entrees["Minutes"].get()
        prix_ttc = self.entrees["Prix TTC (€)"].get()

        database.ajouter_prestation(
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
        prix_ttc)

        self.charger_prestations()

        messagebox.showinfo(
            "FMS Manager",
            "Prestation enregistrée avec succès."
        )
    def modifier_prestation(self):

        reference = self.entrees["Référence"].get()
        designation = self.entrees["Désignation"].get()
        categorie = self.entrees["Catégorie"].get()
        type_tarification = self.entrees["Type de tarification"].get()
        unite = self.entrees["Unité"].get()
        quantite = self.entrees["Quantité par défaut"].get()
        prix_ht = self.entrees["Prix HT (€)"].get()
        tva = self.entrees["TVA (%)"].get()
        temps_heures = self.entrees["Heures"].get()
        temps_minutes = self.entrees["Minutes"].get()
        prix_ttc = self.entrees["Prix TTC (€)"].get()

        database.modifier_prestation(
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
        )

        self.charger_prestations()

        messagebox.showinfo(
            "FMS Manager",
            "Prestation modifiée avec succès."
        )

    def nouvelle_prestation(self):

        for nom, entree in self.entrees.items():

            if isinstance(entree, ctk.CTkEntry):

                if nom == "Prix TTC (€)":
                    entree.configure(state="normal")
                    entree.delete(0, "end")
                    entree.configure(state="readonly")
                else:
                    entree.delete(0, "end")

            elif isinstance(entree, ctk.CTkComboBox):
                if nom == "Heures":
                    entree.set("0")
                elif nom == "Minutes":
                    entree.set("00")
                else:
                    entree.set("")

            self.entrees["Référence"].configure(state="normal")

    def supprimer_prestation(self):

        reference = self.entrees["Référence"].get()

        if not reference:
            messagebox.showwarning(
                "FMS Manager",
                "Aucune prestation sélectionnée."
            )
            return

        reponse = messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer la prestation\n{reference} ?"
        )

        if not reponse:
            return

        database.supprimer_prestation(reference)

        self.charger_prestations()

        for entree in self.entrees.values():

            if isinstance(entree, ctk.CTkEntry):

                if entree == self.entrees["Prix TTC (€)"]:
                    entree.configure(state="normal")
                    entree.delete(0, "end")
                    entree.configure(state="readonly")
                else:
                    entree.delete(0, "end")

            elif isinstance(entree, ctk.CTkComboBox):
                entree.set("")

        messagebox.showinfo(
            "FMS Manager",
            "Prestation supprimée avec succès."
        )

    def rechercher_prestation(self, event=None):

        texte = self.recherche.get().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect("fms_manager.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT reference,
                   designation,
                   categorie,
                   prix_ttc
            FROM prestations
            WHERE lower(reference) LIKE ?
               OR lower(designation) LIKE ?
               OR lower(categorie) LIKE ?
            ORDER BY designation
        """, (
            f"%{texte}%",
            f"%{texte}%",
            f"%{texte}%"
        ))

        for prestation in cur.fetchall():
            self.tree.insert("", "end", values=prestation)

        conn.close()


    def annuler(self):
        self.nouvelle_prestation()    

    def importer_catalogue(self):

        reponse = messagebox.askyesno(
            "Catalogue FMS",
            "Importer le catalogue des prestations FMS ?"
        )

        if not reponse:
            return

        database.importer_catalogue_fms()

        self.charger_prestations()

        messagebox.showinfo(
            "FMS Manager",
            "Catalogue importé avec succès."
        )

