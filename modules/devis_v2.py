import customtkinter as ctk
import sqlite3
import os
import smtplib
import ssl
import win32api

from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from email.message import EmailMessage
from PIL import Image

import database

from modules.selection_client import SelectionClient
from modules.selection_vehicule import SelectionVehicule
from modules.catalogue_prestations import CataloguePrestations
from modules import pdf_manager


class DevisManager:

    def __init__(self, parent):

        self.parent = parent

        # Base de données
        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        # Vérification des tables
        self.verifier_base()

        # Variables
        self.devis_id = None
        self.client_id = None

        # Fenêtre
        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("FMS Manager - Devis")
        self.fenetre.geometry("1600x900")
        self.fenetre.minsize(1400, 900)
        self.fenetre.configure(fg_color="#464242")

        self.fenetre.grab_set()
        self.fenetre.focus_force()

        # Création interface
        self.creer_interface()

        # Initialisation
        self.nouveau_devis()
        self.charger_liste_devis()
        self.temps_unitaires = {}

    def creer_interface(self):

        # =====================================================
        # EN-TÊTE
        # =====================================================

        header = ctk.CTkFrame(
            self.fenetre,
            height=80,
            fg_color="#0A0606",
            corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        try:
            self.logo = ctk.CTkImage(
                light_image=Image.open("assets/logo_fms.png"),
                dark_image=Image.open("assets/logo_fms.png"),
                size=(150, 125)
            )

            ctk.CTkLabel(
                header,
                image=self.logo,
                text=""
            ).pack(side="left", padx=(20, 10))

        except Exception:
            pass

        titre = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )
        titre.pack(side="left")

        ctk.CTkLabel(
            titre,
            text="FMS Manager",
            font=("Arial", 24, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            titre,
            text="Gestion des devis",
            text_color="#D80606",
            font=("Arial", 15)
        ).pack(anchor="w")

        # =====================================================
        # CONTENU
        # =====================================================

        contenu = ctk.CTkFrame(
            self.fenetre,
            fg_color="transparent"
        )

        contenu.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        # =====================================================
        # COLONNE GAUCHE
        # =====================================================

        self.gauche = ctk.CTkFrame(
            contenu,
            width=420,
            fg_color="#0A0606",
            corner_radius=12
        )

        self.gauche.pack(
            side="left",
            fill="both",
            padx=(0, 10)
        )

        self.gauche.grid_rowconfigure(1, weight=1)
        self.gauche.grid_columnconfigure(0, weight=1)

        # =====================================================
        # RECHERCHE
        # =====================================================

        frame_recherche = ctk.CTkFrame(
            self.gauche,
            fg_color="#0A0606",
            height=90
        )

        frame_recherche.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=(15, 10)
        )

        ctk.CTkLabel(
            frame_recherche,
            text="🔍 Recherche",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.entry_recherche = ctk.CTkEntry(
            frame_recherche,
            placeholder_text="Nom du client ou N° devis..."
        )

        self.entry_recherche.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )
        self.entry_recherche.bind(
           "<KeyRelease>",
            self.rechercher_devis
        )

        # =====================================================
        # LISTE DES DEVIS
        # =====================================================

        frame_liste = ctk.CTkFrame(
            self.gauche,
            fg_color="#0A0606"
        )

        frame_liste.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15
        )

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            rowheight=28
        )

        self.table_devis = ttk.Treeview(
            frame_liste,
            columns=("numero", "client", "date"),
            show="headings"
        )

        self.table_devis.heading("numero", text="Devis")
        self.table_devis.heading("client", text="Client")
        self.table_devis.heading("date", text="Date")

        self.table_devis.column(
            "numero",
            width=100,
            anchor="center"
        )

        self.table_devis.column(
            "client",
            width=180
        )

        self.table_devis.column(
            "date",
            width=90,
            anchor="center"
        )

        self.table_devis.bind(
            "<<TreeviewSelect>>",
            self.ouvrir_devis
        )
        self.table_devis.bind(
           "<Double-1>",
            self.ouvrir_devis
        )

        scroll = ttk.Scrollbar(
            frame_liste,
            orient="vertical",
            command=self.table_devis.yview
        )

        self.table_devis.configure(
            yscrollcommand=scroll.set
        )

        self.table_devis.pack(
            side="left",
            fill="both",
            expand=True
        )

        scroll.pack(
            side="right",
            fill="y"
        )

        # =====================================================
        # BOUTONS
        # =====================================================

        frame_boutons = ctk.CTkFrame(
            self.gauche,
            fg_color="#0A0606",
            height=260
        )

        frame_boutons.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=15,
            pady=15
        )

        boutons = [

            ("➕ Nouveau", self.nouveau_devis),

            ("💾 Enregistrer", self.enregistrer_devis),

            ("🔄 Transformer en OR", self.transformer_en_or),

            ("🖨 Exporter / Envoyer", self.menu_export),

            ("🗑 Supprimer", self.supprimer_devis),

            ("🔄 Actualiser", self.charger_liste_devis)

        ]

        for texte, commande in boutons:

            ctk.CTkButton(
                frame_boutons,
                text=texte,
                height=30,
                fg_color="#FC0411",
                hover_color="#BB0214",
                command=commande
            ).pack(
                fill="x",
                pady=4
            )

        # =====================================================
        # COLONNE DROITE
        # =====================================================

        self.droite = ctk.CTkFrame(
            contenu,
            fg_color="#464242",
            corner_radius=12
        )

        self.droite.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

         # =====================================================
        # INFORMATIONS DU DEVIS
        # =====================================================

        frame_infos = ctk.CTkFrame(
            self.droite,
            height=160,
            fg_color="#0A0606",
            corner_radius=10
        )

        frame_infos.pack(
            fill="x",
            padx=20,
            pady=(10, 5)
        )

        frame_infos.pack_propagate(False)

        ctk.CTkLabel(
            frame_infos,
            text="📄 Informations du devis",
            font=("Arial", 12, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=10,
            pady=(6, 5)
        )

        for i in range(3):
            frame_infos.grid_columnconfigure(i, weight=1)

        # ===========================
        # Ligne 1
        # ===========================

        ctk.CTkLabel(
            frame_infos,
            text="N° devis"
        ).grid(row=1, column=0, sticky="w", padx=8)

        ctk.CTkLabel(
            frame_infos,
            text="Date"
        ).grid(row=1, column=2, sticky="w", padx=8)

        self.entry_numero = ctk.CTkEntry(
            frame_infos,
            height=26
        )

        self.entry_date = ctk.CTkEntry(
            frame_infos,
            height=26
        )

        self.entry_numero.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=(8, 5),
            pady=(0, 4)
        )

        self.entry_date.grid(
            row=2,
            column=2,
            sticky="ew",
            padx=(5, 8),
            pady=(0, 4)
        )

        # ===========================
        # Ligne 2
        # ===========================

        ctk.CTkLabel(
            frame_infos,
            text="Client"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=8
        )

        ctk.CTkLabel(
            frame_infos,
            text="Échéance"
        ).grid(
            row=3,
            column=2,
            sticky="w",
            padx=8
        )

        self.entry_client = ctk.CTkEntry(
            frame_infos,
            height=26
        )

        self.entry_echeance = ctk.CTkEntry(
            frame_infos,
            height=26
        )

        self.entry_client.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=(8, 0),
            pady=(0, 4)
        )

        self.entry_echeance.grid(
            row=4,
            column=2,
            sticky="ew",
            padx=(5, 8),
            pady=(0, 4)
        )

        btn_client = ctk.CTkButton(
            frame_infos,
            text="🔍",
            width=34,
            height=26,
            fg_color="#FC0411",
            hover_color="#BB0214",
            command=self.choisir_client
        )

        btn_client.grid(
            row=4,
            column=1,
            padx=5,
            sticky="w"
        )

        # ===========================
        # Ligne 3
        # ===========================

        ctk.CTkLabel(
            frame_infos,
            text="Immatriculation"
        ).grid(
            row=5,
            column=0,
            sticky="w",
            padx=8
        )

        ctk.CTkLabel(
            frame_infos,
            text="Statut"
        ).grid(
            row=5,
            column=2,
            sticky="w",
            padx=8
        )

        self.entry_immat = ctk.CTkEntry(
            frame_infos,
            height=26
        )

        self.combo_statut = ctk.CTkComboBox(
            frame_infos,
            values=[
                "En attente",
                "Accepté",
                "Refusé",
                "Transformé en OR"
            ],
            height=26
        )

        self.combo_statut.set("En attente")

        self.entry_immat.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=(8, 0),
            pady=(0, 6)
        )

        self.combo_statut.grid(
            row=6,
            column=2,
            sticky="ew",
            padx=(5, 8),
            pady=(0, 6)
        )

        btn_vehicule = ctk.CTkButton(
            frame_infos,
            text="🔍",
            width=34,
            height=26,
            fg_color="#FC0411",
            hover_color="#BB0214",
            command=self.choisir_vehicule
        )

        btn_vehicule.grid(
            row=6,
            column=1,
            padx=5,
            sticky="w"
        )

          # =====================================================
        # PRESTATIONS
        # =====================================================

        frame_prestations = ctk.CTkFrame(
            self.droite,
            fg_color="#0A0606",
            corner_radius=10,
            height=160
        )

        frame_prestations.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 5)
        )

        frame_prestations.pack_propagate(False)

        ctk.CTkLabel(
            frame_prestations,
            text="🔧 Prestations",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(6, 4))

        # ======================================
        # Barre de boutons
        # ======================================

        barre = ctk.CTkFrame(
            frame_prestations,
            fg_color="transparent"
        )

        barre.pack(
            fill="x",
            padx=10,
            pady=(0, 5)
        )

        ctk.CTkButton(
            barre,
            text="➕ Ajouter",
            width=120,
            height=28,
            fg_color="#FC0411",
            hover_color="#BB0214",
            command=self.ajouter_prestation
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            barre,
            text="✏ Modifier",
            width=120,
            height=28,
            fg_color="#FC0411",
            hover_color="#BB0214",
            command=self.modifier_prestation
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            barre,
            text="🗑 Supprimer",
            width=120,
            height=28,
            fg_color="#FC0411",
            hover_color="#BB0214",
            command=self.supprimer_prestation
        ).pack(side="left")

        # ======================================
        # Tableau des prestations
        # ======================================

        frame_table = ctk.CTkFrame(
            frame_prestations,
            fg_color="transparent"
        )

        frame_table.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        style = ttk.Style()

        style.configure(
            "Prestations.Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            rowheight=26
        )

        self.table_prestations = ttk.Treeview(
            frame_table,
            columns=(
                "designation",
                "quantite",
                "heures",
                "minutes",
                "pu",
                "total"
            ),
            show="headings",
            style="Prestations.Treeview"
        )

        self.table_prestations.heading(
            "designation",
            text="Désignation"
        )

        self.table_prestations.heading(
            "quantite",
            text="Qté"
        )

        self.table_prestations.heading(
            "heures",
            text="H"
        )

        self.table_prestations.heading(
            "minutes",
            text="Min"
        )

        self.table_prestations.heading(
            "pu",
            text="PU HT"
        )

        self.table_prestations.heading(
            "total",
            text="Total HT"
        )

        self.table_prestations.column(
            "designation",
            width=420
        )

        self.table_prestations.column(
            "quantite",
            width=70,
            anchor="center"
        )

        self.table_prestations.column(
            "heures",
            width=55,
            anchor="center"
        )

        self.table_prestations.column(
            "minutes",
            width=60,
            anchor="center"
        )

        self.table_prestations.column(
            "pu",
            width=100,
            anchor="e"
        )

        self.table_prestations.column(
            "total",
            width=110,
            anchor="e"
        )

        scroll_prestations = ttk.Scrollbar(
            frame_table,
            orient="vertical",
            command=self.table_prestations.yview
        )

        self.table_prestations.configure(
            yscrollcommand=scroll_prestations.set
        )

        self.table_prestations.pack(
            side="left",
            fill="both",
            expand=True
        )

        scroll_prestations.pack(
            side="right",
            fill="y"
        )

          # =====================================================
        # OBSERVATIONS
        # =====================================================

        frame_observations = ctk.CTkFrame(
            self.droite,
            height=80,
            fg_color="#0A0606",
            corner_radius=10
        )

        frame_observations.pack(
            fill="x",
            padx=10,
            pady=(5, 5)
        )

        frame_observations.pack_propagate(False)

        ctk.CTkLabel(
            frame_observations,
            text="📝 Observations",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(5, 3))

        self.txt_observations = ctk.CTkTextbox(
            frame_observations,
            height=45
        )

        self.txt_observations.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 8)
        )

        # =====================================================
        # TOTAUX
        # =====================================================

        frame_totaux = ctk.CTkFrame(
            self.droite,
            height=80,
            fg_color="#0A0606",
            corner_radius=10
        )

        frame_totaux.pack(
            fill="x",
            padx=20,
            pady=(5, 10)
        )

        frame_totaux.pack_propagate(False)

        frame_totaux.grid_columnconfigure(1, weight=1)
        frame_totaux.grid_columnconfigure(3, weight=1)

        # ---------- Ligne 1 ----------

        ctk.CTkLabel(
            frame_totaux,
            text="Total HT"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 2))

        self.label_ht = ctk.CTkLabel(
            frame_totaux,
            text="0,00 €"
        )

        self.label_ht.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            frame_totaux,
            text="TVA (0%)"
        ).grid(row=0, column=2, sticky="w", padx=(20, 10))

        self.label_tva = ctk.CTkLabel(
            frame_totaux,
            text="0,00 €"
        )

        self.label_tva.grid(row=0, column=3, sticky="w")

        # ---------- Ligne 2 ----------

        ctk.CTkLabel(
            frame_totaux,
            text="Remise"
        ).grid(row=1, column=0, sticky="w", padx=10)

        self.entry_remise = ctk.CTkEntry(
            frame_totaux,
            width=90,
            height=26
        )

        self.entry_remise.insert(0, "0")

        self.entry_remise.grid(
            row=1,
            column=1,
            sticky="w"
        )
        self.entry_remise.bind(
            "<KeyRelease>",
            lambda e: self.calculer_totaux()
        )

        ctk.CTkLabel(
            frame_totaux,
            text="Acompte"
        ).grid(row=1, column=2, sticky="w", padx=(20, 10))

        self.entry_deja_verse = ctk.CTkEntry(
            frame_totaux,
            width=90,
            height=26
        )

        self.entry_deja_verse.insert(0, "0")

        self.entry_deja_verse.grid(
            row=1,
            column=3,
            sticky="w"
        )
        self.entry_deja_verse.bind(
            "<KeyRelease>",
            lambda e: self.calculer_totaux()
        )

        # ---------- Ligne 3 ----------

        ctk.CTkLabel(
            frame_totaux,
            text="TOTAL TTC",
            font=("Arial", 16, "bold")
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=10,
            pady=(4, 4)
        )

        self.label_ttc = ctk.CTkLabel(
            frame_totaux,
            text="0,00 €",
            font=("Arial", 16, "bold"),
            text_color="#D72638"
        )

        self.label_ttc.grid(
            row=2,
            column=1,
            sticky="w"
        )

        ctk.CTkLabel(
            frame_totaux,
            text="Reste à payer",
            font=("Arial", 16, "bold")
        ).grid(
            row=2,
            column=2,
            sticky="w",
            padx=(20, 10)
        )

        self.label_reste = ctk.CTkLabel(
            frame_totaux,
            text="0,00 €",
            font=("Arial", 16, "bold"),
            text_color="#D72638"
        )

        self.label_reste.grid(
            row=2,
            column=3,
            sticky="w"
        )

     # =====================================================
    # BASE DE DONNÉES
    # =====================================================

    def verifier_base(self):

        self.cur.execute("""
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

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS lignes_devis(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                devis_id INTEGER,
                designation TEXT,
                quantite REAL,
                heures INTEGER DEFAULT 0,
                minutes INTEGER DEFAULT 0,
                prix_ht REAL,
                total REAL,
                FOREIGN KEY(devis_id) REFERENCES devis(id)
            )
        """)

        self.conn.commit()


    # =====================================================
    # NUMÉRO DE DEVIS
    # =====================================================

    def generer_numero_devis(self):

        annee = datetime.now().year

        self.cur.execute("""
            SELECT numero
            FROM devis
            WHERE numero LIKE ?
            ORDER BY id DESC
            LIMIT 1
        """, (f"DV-{annee}-%",))

        resultat = self.cur.fetchone()

        if resultat:
            numero = int(resultat[0].split("-")[-1]) + 1
        else:
            numero = 1

        return f"DV-{annee}-{numero:04d}"


    # =====================================================
    # NOUVEAU DEVIS
    # =====================================================

    def nouveau_devis(self):

        self.devis_id = None
        self.client_id = None

        self.entry_numero.delete(0, "end")
        self.entry_numero.insert(0, self.generer_numero_devis())

        self.entry_date.delete(0, "end")
        self.entry_date.insert(
            0,
            datetime.now().strftime("%d/%m/%Y")
        )

        self.entry_client.delete(0, "end")
        self.entry_immat.delete(0, "end")

        self.combo_statut.set("En attente")

        echeance = datetime.now() + timedelta(days=30)

        self.entry_echeance.delete(0, "end")
        self.entry_echeance.insert(
            0,
            echeance.strftime("%d/%m/%Y")
        )

        self.txt_observations.delete("1.0", "end")

        self.entry_remise.delete(0, "end")
        self.entry_remise.insert(0, "0")


        self.entry_deja_verse.delete(0, "end")
        self.entry_deja_verse.insert(0, "0")

        self.label_ht.configure(text="0,00 €")
        self.label_tva.configure(text="0,00 €")
        self.label_ttc.configure(text="0,00 €")
        self.label_reste.configure(text="0,00 €")

        for item in self.table_prestations.get_children():
            self.table_prestations.delete(item)

        self.fenetre.focus_force()

        self.entry_client.focus_set()

     # =====================================================
    # CHARGER LA LISTE DES DEVIS
    # =====================================================

    def charger_liste_devis(self):

        for item in self.table_devis.get_children():
            self.table_devis.delete(item)

        self.cur.execute("""
            SELECT numero, client, date
            FROM devis
            ORDER BY id DESC
        """)

        for devis in self.cur.fetchall():
            self.table_devis.insert("", "end", values=devis)


    # =====================================================
    # OUVRIR UN DEVIS
    # =====================================================

    def ouvrir_devis(self, event=None):

        selection = self.table_devis.selection()

        if not selection:
            return

        numero = self.table_devis.item(selection[0])["values"][0]

        self.cur.execute("""
            SELECT
                id,
                numero,
                date,
                client,
                client_id,
                immatriculation,
                statut,
                echeance,
                observations,
                remise,
                deja_verse,
                total_ht,
                tva,
                total_ttc
            FROM devis
            WHERE numero=?
        """, (numero,))

        devis = self.cur.fetchone()

        if devis is None:
            return

        self.devis_id = devis[0]
        self.client_id = devis[4]

        self.entry_numero.delete(0, "end")
        self.entry_numero.insert(0, devis[1])

        self.entry_date.delete(0, "end")
        self.entry_date.insert(0, devis[2])

        self.entry_client.delete(0, "end")
        self.entry_client.insert(0, devis[3])

        self.entry_immat.delete(0, "end")
        self.entry_immat.insert(0, devis[5])

        self.combo_statut.set(devis[6])

        self.entry_echeance.delete(0, "end")
        self.entry_echeance.insert(0, devis[7] or "")

        self.txt_observations.delete("1.0", "end")
        self.txt_observations.insert("1.0", devis[8] or "")

        self.entry_remise.delete(0, "end")
        self.entry_remise.insert(0, str(devis[9]))

        self.entry_deja_verse.delete(0, "end")
        self.entry_deja_verse.insert(0, str(devis[10]))

        # Vider le tableau des prestations

        for item in self.table_prestations.get_children():
            self.table_prestations.delete(item)

        # Charger les prestations

        self.cur.execute("""
            SELECT
                designation,
                quantite,
                heures,
                minutes,
                prix_ht,
                total
            FROM lignes_devis
            WHERE devis_id=?
        """, (self.devis_id,))

        for ligne in self.cur.fetchall():

            self.table_prestations.insert(
                "",
                "end",
                values=ligne
            )

        self.calculer_totaux()
        self.entry_client.focus_set()

     # =====================================================
    # CALCUL DES TOTAUX
    # =====================================================

    def calculer_totaux(self):

        total_ht = 0.0

        # Calcul des prestations
        for item in self.table_prestations.get_children():

            valeurs = self.table_prestations.item(item)["values"]

            if len(valeurs) != 6:
                continue

            try:
                total_ht += float(str(valeurs[5]).replace(",", "."))
            except Exception:
                pass

        # Remise
        try:
            remise = float(
                self.entry_remise.get().replace(",", ".")
            )
        except:
            remise = 0.0

        # TVA
        tva = 0.0

        # Total TTC
        total_ttc = total_ht + tva - remise

        # Déjà versé
        try:
            deja_verse = float(
                self.entry_deja_verse.get().replace(",", ".")
            )
        except:
            deja_verse = 0.0

        reste = total_ttc - deja_verse

        # Affichage

        self.label_ht.configure(
            text=f"{total_ht:.2f} €"
        )

        self.label_tva.configure(
            text=f"{tva:.2f} €"
        )

        self.label_ttc.configure(
            text=f"{total_ttc:.2f} €"
        )

        self.label_reste.configure(
            text=f"{reste:.2f} €"
        )

     # =====================================================
    # ENREGISTRER LE DEVIS
    # =====================================================

    def enregistrer_devis(self):

        # ---------- Montants ----------

        try:
            remise = float(self.entry_remise.get().replace(",", "."))
        except:
            remise = 0.0

        try:
            deja_verse = float(self.entry_deja_verse.get().replace(",", "."))
        except:
            deja_verse = 0.0

        total_ht = float(
            self.label_ht.cget("text")
            .replace("€", "")
            .replace(",", ".")
            .strip()
        )

        tva = float(
            self.label_tva.cget("text")
            .replace("€", "")
            .replace(",", ".")
            .strip()
        )

        total_ttc = float(
            self.label_ttc.cget("text")
            .replace("€", "")
            .replace(",", ".")
            .strip()
        )

        # =====================================================
        # NOUVEAU DEVIS
        # =====================================================

        if self.devis_id is None:

            self.cur.execute("""

                INSERT INTO devis (

                    numero,
                    date,
                    client,
                    client_id,
                    immatriculation,
                    statut,
                    echeance,
                    observations,
                    remise,
                    deja_verse,
                    total_ht,
                    tva,
                    total_ttc

                )

                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)

            """, (

                self.entry_numero.get(),
                self.entry_date.get(),
                self.entry_client.get(),
                self.client_id,
                self.entry_immat.get(),
                self.combo_statut.get(),
                self.entry_echeance.get(),
                self.txt_observations.get("1.0", "end").strip(),
                remise,
                deja_verse,
                total_ht,
                tva,
                total_ttc

            ))

            self.conn.commit()

            self.devis_id = self.cur.lastrowid

        # =====================================================
        # MODIFICATION
        # =====================================================

        else:

            self.cur.execute("""

                UPDATE devis

                SET

                    numero=?,
                    date=?,
                    client=?,
                    client_id=?,
                    immatriculation=?,
                    statut=?,
                    echeance=?,
                    observations=?,
                    remise=?,
                    deja_verse=?,
                    total_ht=?,
                    tva=?,
                    total_ttc=?

                WHERE id=?

            """, (

                self.entry_numero.get(),
                self.entry_date.get(),
                self.entry_client.get(),
                self.client_id,
                self.entry_immat.get(),
                self.combo_statut.get(),
                self.entry_echeance.get(),
                self.txt_observations.get("1.0", "end").strip(),
                remise,
                deja_verse,
                total_ht,
                tva,
                total_ttc,
                self.devis_id

            ))

            self.conn.commit()

             # =====================================================
        # ENREGISTREMENT DES PRESTATIONS
        # =====================================================

        self.cur.execute(
            "DELETE FROM lignes_devis WHERE devis_id=?",
            (self.devis_id,)
        )

        for item in self.table_prestations.get_children():

            valeurs = self.table_prestations.item(item)["values"]

            if len(valeurs) != 6:
                continue

            designation = str(valeurs[0])

            try:
                quantite = float(valeurs[1])
            except:
                quantite = 1.0

            try:
                heures = int(valeurs[2])
            except:
                heures = 0

            try:
                minutes = int(valeurs[3])
            except:
                minutes = 0

            try:
                prix_ht = float(str(valeurs[4]).replace(",", "."))
            except:
                prix_ht = 0.0

            try:
                total = float(str(valeurs[5]).replace(",", "."))
            except:
                total = 0.0

            self.cur.execute("""
                INSERT INTO lignes_devis
                (
                    devis_id,
                    designation,
                    quantite,
                    heures,
                    minutes,
                    temps_heures_unitaire,
                    temps_minutes_unitaire,
                    prix_ht,
                    total
                )
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (

                self.devis_id,
                designation,
                quantite,
                heures,
                minutes,

                heures,   #Temps unitaire(provisoirement)
                minutes,  #Temps unitaire(provisoirement)
                
                prix_ht,
                total

            ))

        self.conn.commit()

        # =====================================================
        # FIN
        # =====================================================

        self.charger_liste_devis()

        messagebox.showinfo(
            "FMS Manager",
            "Le devis a été enregistré avec succès."
        )

     # =====================================================
    # FENÊTRE AJOUT / MODIFICATION PRESTATION
    # =====================================================

    def ouvrir_fenetre_prestation(self, mode="ajout", item=None):

        fenetre = ctk.CTkToplevel(self.fenetre)
        fenetre.title("Prestation")
        fenetre.geometry("520x420")
        fenetre.resizable(False, False)
        fenetre.grab_set()

        # ==========================================
        # Désignation
        # ==========================================

        ctk.CTkLabel(
            fenetre,
            text="Désignation"
        ).pack(pady=(15,5))

        entry_designation = ctk.CTkEntry(
            fenetre,
            width=420
        )
        entry_designation.pack()

        # ==========================================
        # Quantité
        # ==========================================

        ctk.CTkLabel(
            fenetre,
            text="Quantité"
        ).pack(pady=(12,5))

        entry_qte = ctk.CTkEntry(
            fenetre,
            width=120
        )
        entry_qte.insert(0,"1")
        entry_qte.pack()

        # ==========================================
        # Heures
        # ==========================================

        ctk.CTkLabel(
            fenetre,
            text="Heures"
        ).pack(pady=(12,5))

        entry_heures = ctk.CTkEntry(
            fenetre,
            width=120
        )
        entry_heures.insert(0,"0")
        entry_heures.pack()

        # ==========================================
        # Minutes
        # ==========================================

        ctk.CTkLabel(
            fenetre,
            text="Minutes"
        ).pack(pady=(12,5))

        entry_minutes = ctk.CTkEntry(
            fenetre,
            width=120
        )
        entry_minutes.insert(0,"0")
        entry_minutes.pack()

        # ==========================================
        # Prix HT
        # ==========================================

        ctk.CTkLabel(
            fenetre,
            text="Prix HT"
        ).pack(pady=(12,5))

        entry_prix = ctk.CTkEntry(
            fenetre,
            width=140
        )
        entry_prix.pack()
         # ==========================================
        # Si modification
        # ==========================================

        if mode == "modification" and item is not None:

            valeurs = self.table_prestations.item(item)["values"]

            entry_designation.insert(0, valeurs[0])

            entry_qte.delete(0, "end")
            entry_qte.insert(0, str(valeurs[1]))

            entry_heures.delete(0, "end")
            entry_heures.insert(0, str(valeurs[2]))

            entry_minutes.delete(0, "end")
            entry_minutes.insert(0, str(valeurs[3]))

            entry_prix.delete(0, "end")
            entry_prix.insert(0, str(valeurs[4]))


        # ==========================================
        # Validation
        # ==========================================

        def valider():

            try:

                qte = float(entry_qte.get().replace(",", "."))

                prix = float(entry_prix.get().replace(",", "."))

                if mode == "modification" and item in self.temps_unitaires:

                    h_unitaire, m_unitaire = self.temps_unitaires[item]

                    total_minutes = int((h_unitaire * 60 + m_unitaire) * qte)

                    heures = total_minutes // 60
                    minutes = total_minutes % 60

                else:

                    heures = int(entry_heures.get() or 0)
                    minutes = int(entry_minutes.get() or 0)

            except ValueError:

                messagebox.showerror(
                    "Erreur",
                    "Veuillez saisir des valeurs numériques."
                )
                return


            total = round(qte * prix, 2)

            valeurs = (
                entry_designation.get(),
                qte,
                heures,
                minutes,
                prix,
                total
            )

            if mode == "ajout":

                self.table_prestations.insert(
                    "",
                    "end",
                    values=valeurs
                )

            else:

                self.table_prestations.item(
                    item,
                    values=valeurs
                )
            if item in self.temps_unitaires:
                self.temps_unitaires[item]=(heures, minutes)
            self.calculer_totaux()

            fenetre.destroy()


        # ==========================================
        # Boutons
        # ==========================================

        ctk.CTkButton(
            fenetre,
            text="Valider",
            width=180,
            fg_color="#FC0411",
            hover_color="#BB0214",
            command=valider
        ).pack(pady=(20,8))

        ctk.CTkButton(
            fenetre,
            text="Annuler",
            width=180,
            fg_color="gray",
            command=fenetre.destroy
        ).pack()

     # =====================================================
    # AJOUTER UNE PRESTATION
    # =====================================================

    def ajouter_prestation(self):

        CataloguePrestations(

        self.fenetre,

        self.retour_prestation

    )


    # =====================================================
    # MODIFIER UNE PRESTATION
    # =====================================================

    def modifier_prestation(self):

        selection = self.table_prestations.selection()

        if not selection:

            messagebox.showwarning(
                "FMS Manager",
                "Sélectionnez une prestation."
            )
            return

        self.ouvrir_fenetre_prestation(
            mode="modification",
            item=selection[0]
        )


    # =====================================================
    # SUPPRIMER UNE PRESTATION
    # =====================================================

    def supprimer_prestation(self):

        selection = self.table_prestations.selection()

        if not selection:

            messagebox.showwarning(
                "FMS Manager",
                "Sélectionnez une prestation."
            )
            return

        if not messagebox.askyesno(
            "Confirmation",
            "Voulez-vous supprimer cette prestation ?"
        ):
            return

        self.table_prestations.delete(selection[0])

        self.calculer_totaux()

     # =====================================================
    # RETOUR CATALOGUE PRESTATIONS
    # =====================================================

    def retour_prestation(self, valeurs):

        (
            reference,
            designation,
            categorie,
            prix_ht,
            tva,
            prix_ttc,
            temps_heures,
            temps_minutes
        ) = valeurs
        item =self.table_prestations.insert(

            "",

            "end",

            values=(

                designation,
                1,          # Quantité
                int(temps_heures),          # Heures
                int(temps_minutes),          # Minutes
                float(prix_ht),
                float(prix_ht)

            )

        )
        self.temps_unitaires[item]=(
            int(temps_heures),
            int(temps_minutes)
        )

        self.calculer_totaux()

       # =====================================================
    # CHOISIR UN CLIENT
    # =====================================================

    def choisir_client(self):

        SelectionClient(
            self.fenetre,
            self.retour_client
        )


    # =====================================================
    # RETOUR CLIENT
    # =====================================================

    def retour_client(self, valeurs):

        client_id, type_client, nom, prenom, telephone, ville = valeurs

        self.client_id = client_id

        self.entry_client.delete(0, "end")

        if type_client.lower() == "particulier":

            self.entry_client.insert(
                0,
                f"{nom} {prenom}"
            )

        else:

            self.entry_client.insert(
                0,
                nom
            )


    # =====================================================
    # CHOISIR UN VÉHICULE
    # =====================================================

    def choisir_vehicule(self):

        if self.client_id is None:

            messagebox.showwarning(
                "FMS Manager",
                "Sélectionnez d'abord un client."
            )
            return

        SelectionVehicule(

            self.fenetre,

            self.retour_vehicule,

            self.client_id

        )


    # =====================================================
    # RETOUR VÉHICULE
    # =====================================================

    def retour_vehicule(self, valeurs):

        (
            immatriculation,
            marque,
            modele,
            motorisation,
            nom,
            prenom
        ) = valeurs

        self.entry_immat.delete(0, "end")
        self.entry_immat.insert(
            0,
            immatriculation
        )

        self.entry_client.delete(0, "end")
        self.entry_client.insert(
            0,
            f"{nom} {prenom}"
        )

     # =====================================================
    # IMPRIMER / GÉNÉRER LE PDF
    # =====================================================

    def imprimer_pdf(self):

        # ==========================================
        # Vérifications
        # ==========================================

        if self.client_id is None:

            messagebox.showwarning(
                "FMS Manager",
                "Veuillez sélectionner un client."
            )
            return

        if self.devis_id is None:

            messagebox.showwarning(
                "FMS Manager",
                "Veuillez enregistrer le devis avant de générer le PDF."
            )
            return

        # ==========================================
        # Informations client
        # ==========================================

        self.cur.execute("""

            SELECT

                prenom,
                telephone,
                email,
                adresse,
                code_postal,
                ville

            FROM clients

            WHERE id=?

        """, (self.client_id,))

        client = self.cur.fetchone()

        if client is None:

            messagebox.showerror(
                "FMS Manager",
                "Impossible de retrouver le client."
            )
            return

        # ==========================================
        # Informations véhicule
        # ==========================================

        self.cur.execute("""

            SELECT

                marque,
                modele,
                kilometrage

            FROM vehicules

            WHERE immatriculation=?

        """, (self.entry_immat.get(),))

        vehicule = self.cur.fetchone()

        if vehicule is None:

            messagebox.showerror(
                "FMS Manager",
                "Impossible de retrouver le véhicule."
            )
            return

        # ==========================================
        # Prestations
        # ==========================================

        prestations = []

        for item in self.table_prestations.get_children():

            designation, qte, heures, minutes, prix_ht, total = \
                self.table_prestations.item(item)["values"]

            prestations.append(

                (

                    "",

                    designation,

                    qte,

                    prix_ht,

                    0,

                    total

                )

            )

               # ==========================================
        # Génération du PDF
        # ==========================================

        fichier = pdf_manager.creer_pdf(

            numero=self.entry_numero.get(),
            date=self.entry_date.get(),

            client=self.entry_client.get(),
            immatriculation=self.entry_immat.get(),

            prenom=client[0],
            telephone=client[1],
            email=client[2],
            adresse=client[3],
            code_postal=client[4],
            ville=client[5],

            marque=vehicule[0],
            modele=vehicule[1],
            kilometrage=vehicule[2],

            prestations=prestations,

            montant_ht=float(
                self.label_ht.cget("text")
                .replace("€", "")
                .replace(",", ".")
                .strip()
            ),

            tva=float(
                self.label_tva.cget("text")
                .replace("€", "")
                .replace(",", ".")
                .strip()
            ),

            montant_ttc=float(
                self.label_ttc.cget("text")
                .replace("€", "")
                .replace(",", ".")
                .strip()
            )

        )

        # ==========================================
        # Fin
        # ==========================================

        messagebox.showinfo(
            "FMS Manager",
            f"PDF créé avec succès.\n\n{fichier}"
        )

        try:

            win32api.ShellExecute(
                0,
                "open",
                fichier,
                None,
                ".",
                1
            )

        except Exception:
            pass

        return fichier

     # =====================================================
    # ENVOYER LE DEVIS PAR E-MAIL
    # =====================================================

    def envoyer_mail(self):

        fen = ctk.CTkToplevel(self.fenetre)
        fen.title("Envoyer le devis")
        fen.geometry("620x430")
        fen.resizable(False, False)
        fen.grab_set()

        # =============================
        # Destinataire
        # =============================

        ctk.CTkLabel(
            fen,
            text="Destinataire"
        ).pack(anchor="w", padx=20, pady=(15,0))

        entry_email = ctk.CTkEntry(
            fen,
            width=560
        )
        entry_email.pack(padx=20)

        email_client = database.recuperer_email_client(
            self.client_id
        )

        if email_client:
            entry_email.insert(0, email_client)

        # =============================
        # Objet
        # =============================

        ctk.CTkLabel(
            fen,
            text="Objet"
        ).pack(anchor="w", padx=20, pady=(10,0))

        entry_objet = ctk.CTkEntry(
            fen,
            width=560
        )

        entry_objet.pack(padx=20)

        entry_objet.insert(
            0,
            f"Devis {self.entry_numero.get()}"
        )

        # =============================
        # Message
        # =============================

        ctk.CTkLabel(
            fen,
            text="Message"
        ).pack(anchor="w", padx=20, pady=(10,0))

        txt_message = ctk.CTkTextbox(
            fen,
            width=560,
            height=180
        )

        txt_message.pack(
            padx=20,
            pady=5
        )

        txt_message.insert(
            "1.0",
        f"""Bonjour,

        Veuillez trouver ci-joint votre devis {self.entry_numero.get()}.

        Je reste à votre disposition pour toute information complémentaire.

        Cordialement,

        Fred Méca Services
        """
        )
         # ==========================================
        # Fonction d'envoi
        # ==========================================

        def envoyer():

            try:

                pdf = self.imprimer_pdf()

                msg = EmailMessage()

                msg["Subject"] = entry_objet.get()
                msg["From"] = "fred.meca.services62@gmail.com"
                msg["To"] = entry_email.get()

                msg.set_content(
                    txt_message.get("1.0", "end")
                )

                with open(pdf, "rb") as f:

                    msg.add_attachment(
                        f.read(),
                        maintype="application",
                        subtype="pdf",
                        filename=os.path.basename(pdf)
                    )

                contexte = ssl.create_default_context()

                with smtplib.SMTP_SSL(
                    "smtp.gmail.com",
                    465,
                    context=contexte
                ) as smtp:

                    smtp.login(
                        "fred.meca.services62@gmail.com",
                        "ghmbtfftprlegfco"
                    )

                    smtp.send_message(msg)

                messagebox.showinfo(
                    "FMS Manager",
                    "Le devis a été envoyé avec succès."
                )

                fen.destroy()

            except Exception as e:

                messagebox.showerror(
                    "Erreur",
                    str(e)
                )

        # ==========================================
        # Boutons
        # ==========================================

        ctk.CTkButton(

            fen,

            text="📨 Envoyer",

            width=180,

            fg_color="#FC0411",

            hover_color="#BB0214",

            command=envoyer

        ).pack(pady=(10,5))

        ctk.CTkButton(

            fen,

            text="❌ Annuler",

            width=180,

            fg_color="gray",

            command=fen.destroy

        ).pack()

      # =====================================================
    # MENU EXPORT
    # =====================================================

    def menu_export(self):

        fen = ctk.CTkToplevel(self.fenetre)
        fen.title("Exporter le devis")
        fen.geometry("320x180")
        fen.resizable(False, False)
        fen.grab_set()

        ctk.CTkLabel(
            fen,
            text="Choisissez une action",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        ctk.CTkButton(

            fen,

            text="📄 Générer le PDF",

            width=220,

            fg_color="#FC0411",

            hover_color="#BB0214",

            command=lambda: [

                fen.destroy(),

                self.imprimer_pdf()

            ]

        ).pack(pady=5)

        ctk.CTkButton(

            fen,

            text="📧 Envoyer par e-mail",

            width=220,

            fg_color="#FC0411",

            hover_color="#BB0214",

            command=lambda: [

                fen.destroy(),

                self.envoyer_mail()

            ]

        ).pack(pady=5)

     # =====================================================
    # TRANSFORMER EN ORDRE DE RÉPARATION
    # =====================================================

    def transformer_en_or(self):

        if self.devis_id is None:

            messagebox.showwarning(
                "FMS Manager",
                "Veuillez enregistrer le devis avant de le transformer."
            )
            return

        if not messagebox.askyesno(
            "Confirmation",
            "Transformer ce devis en ordre de réparation ?"
        ):
            return

        # Mise à jour du statut

        self.combo_statut.set("Transformé en OR")

        self.cur.execute("""

            UPDATE devis

            SET statut=?

            WHERE id=?

        """, (

            "Transformé en OR",

            self.devis_id

        ))

        self.conn.commit()

        # Création de l'OR

        numero_or = database.creer_or_depuis_devis(

            self.entry_numero.get(),

            self.entry_date.get(),

            self.entry_client.get(),

            self.client_id,

            self.entry_immat.get(),

            self.txt_observations.get(
                "1.0",
                "end"
            ).strip()

        )

        messagebox.showinfo(

            "FMS Manager",

            f"""Le devis a été transformé avec succès.

        Numéro OR : {numero_or}"""

        )

        self.charger_liste_devis()

     # =====================================================
    # SUPPRIMER UN DEVIS
    # =====================================================

    def supprimer_devis(self):

        if self.devis_id is None:

            messagebox.showwarning(
                "FMS Manager",
                "Sélectionnez un devis."
            )
            return

        if not messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment supprimer ce devis ?"
        ):
            return

        self.cur.execute(
            "DELETE FROM lignes_devis WHERE devis_id=?",
            (self.devis_id,)
        )

        self.cur.execute(
            "DELETE FROM devis WHERE id=?",
            (self.devis_id,)
        )

        self.conn.commit()

        self.nouveau_devis()

        self.charger_liste_devis()

        messagebox.showinfo(
            "FMS Manager",
            "Le devis a été supprimé."
        )

     # =====================================================
    # RECHERCHER UN DEVIS
    # =====================================================

    def rechercher_devis(self, event=None):

        recherche = self.entry_recherche.get().strip().lower()

        for item in self.table_devis.get_children():
            self.table_devis.delete(item)

        self.cur.execute("""
            SELECT
                numero,
                client,
                date
            FROM devis
            WHERE
                LOWER(numero) LIKE ?
                OR LOWER(client) LIKE ?
                OR LOWER(immatriculation) LIKE ?
            ORDER BY id DESC
        """, (
            f"%{recherche}%",
            f"%{recherche}%",
            f"%{recherche}%"
        ))

        for ligne in self.cur.fetchall():

            self.table_devis.insert(
                "",
                "end",
                values=ligne
            )
    
def ouvrir(parent):
    DevisManager(parent)