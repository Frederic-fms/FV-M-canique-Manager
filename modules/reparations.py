import customtkinter as ctk
import sqlite3
import os
import win32api
import database
from modules.selection_client import SelectionClient
from modules.selection_vehicule import SelectionVehicule
from modules.catalogue_prestations import CataloguePrestations
from tkinter import ttk, messagebox
from PIL import Image
from datetime import datetime
from modules import pdf_manager
from modules import pdf_or
from modules import reparations
import smtplib
from email.message import EmailMessage
import ssl
import tkinter as tk


class ReparationManager:

    def __init__(self, parent):
        self.parent = parent

        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()
        self.verifier_base()
        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("FMS Manager - Ordres de réparation")
        self.fenetre.geometry("1600x900")
        self.fenetre.minsize(1400,900)
        self.fenetre.configure(fg_color="#464242")

        self.creer_interface()

        
        self.generer_numero_or()
        self.charger_liste_or()
        self.client_id=None
        self.or_id=None
        

    def creer_interface(self):

        # ==========================
        # EN-TÊTE
        # ==========================

        header = ctk.CTkFrame(
            self.fenetre,
            height=80,
            fg_color="#0A0606",
            corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        try:
            logo = ctk.CTkImage(
                light_image=Image.open("assets/logo_fms.png"),
                dark_image=Image.open("assets/logo_fms.png"),
                size=(150, 125)
            )

            ctk.CTkLabel(
                header,
                image=logo,
                text=""
            ).pack(side="left", padx=(20, 10))

            self.logo = logo

        except:
            pass

        titre = ctk.CTkFrame(header, fg_color="transparent")
        titre.pack(side="left")

        ctk.CTkLabel(
            titre,
            text="FMS Manager",
            font=("Arial", 24, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            titre,
            text="Ordres de réparation",
            text_color="#D80606",
            font=("Arial", 15)
        ).pack(anchor="w")


        # ==========================
        # CONTENU
        # ==========================

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
        self.gauche=ctk.CTkFrame(
            contenu,
            width=420,
            fg_color="#0A0606",
            corner_radius=12
        )
        self.gauche.pack(
            side="left",
            fill="both",
            padx=(0,10)
        )

        # ==========================
        # COLONNE GAUCHE
        # ==========================

        self.gauche.grid_rowconfigure(1, weight=1)
        self.gauche.grid_columnconfigure(0, weight=1)

        # ---------- Recherche ----------

        frame_recherche = ctk.CTkFrame(
            self.gauche,
            fg_color="#0A0606",
            height=90
        )
        frame_recherche.grid(row=0, column=0, sticky="ew", padx=15, pady=(15,10))

        ctk.CTkLabel(
            frame_recherche,
            text="🔍 Recherche",
            font=("Arial",18,"bold")
        ).pack(anchor="w", padx=10, pady=(10,5))

        self.entry_recherche = ctk.CTkEntry(
            frame_recherche,
            placeholder_text="Nom du client ou N° de or..."
        )
        self.entry_recherche.pack(fill="x", padx=10, pady=(0,10))

        # ---------- Liste ----------

        frame_liste = ctk.CTkFrame(
            self.gauche,
            fg_color="#0A0606"
        )
        frame_liste.grid(row=1, column=0, sticky="nsew", padx=15)

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            rowheight=28,
            fieldbackground="white"
        )

        self.table_or = ttk.Treeview(
            frame_liste,
            columns=("numero","client","date"),
            show="headings"
        )
        self.table_or.bind("<<TreeviewSelect>>",
        self.ouvrir_or)

        self.table_or.heading("numero", text="devis")
        self.table_or.heading("client", text="Client")
        self.table_or.heading("date", text="Date")

        self.table_or.column("numero", width=100)
        self.table_or.column("client", width=170)
        self.table_or.column("date", width=90)

        scroll = ttk.Scrollbar(
            frame_liste,
            orient="vertical",
            command=self.table_or.yview
        )

        self.table_or.configure(yscrollcommand=scroll.set)

        self.table_or.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # ---------- Boutons ----------

        frame_boutons = ctk.CTkFrame(
            self.gauche,
            fg_color="#0A0606",
            height=270
        )
        frame_boutons.grid(row=2, column=0, sticky="ew", padx=15, pady=15)

        ctk.CTkButton(
            frame_boutons,
              text="➕ Nouveau",
              height=30,
              hover_color="#0233bb",
              command=self.nouveau_or
              ).pack(fill="x", pady=4)

        ctk.CTkButton(
            frame_boutons,
            text="💾 Enregistrer",
            height=30,
            fg_color="#fc0411",
            hover_color="#bb0214",
            command=self.enregistrer_or
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            frame_boutons,
            text="🔄 Créer Facture",
            height=30,
            fg_color="#fc0411",
            hover_color="#bb0214",
            command=self.transformer_en_facture,
            width=180
        ).pack(fill="x", pady=4)
        ctk.CTkButton(
            frame_boutons,
              text="🖨 Exporter / Envoyer",
              height=30,
              fg_color="#fc0411",
              hover_color="#bb0214",
              command=self.menu_export
              ).pack(fill="x", pady=4)

        ctk.CTkButton(
            frame_boutons,
              text="🗑 Supprimer",
              height=30,
              fg_color="#fc0411",
              hover_color="#bb0214",
              command=self.supprimer_or
              ).pack(fill="x", pady=4)

        ctk.CTkButton(
            frame_boutons,
              text="🔄 Actualiser",
              height=30,
              fg_color="#fc0411",
              hover_color="#bb0214",
              command=self.charger_liste_or
              ).pack(fill="x", pady=4)


        # ==========================
        # COLONNE DROITE
        # ==========================

        self.droite = ctk.CTkFrame(
            contenu,
            fg_color="#464242",
            corner_radius=12
        )
        self.droite.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(10, 0),
            pady=0
        )

        # ==========================
        # INFORMATIONS
        # ==========================

        frame_infos = ctk.CTkFrame(
            self.droite,
            height=160,
            fg_color="#0A0606",
            corner_radius=10
        )
        frame_infos.pack(fill="x", padx=20, pady=(10,5)) 
        frame_infos.pack_propagate(False)
        # ==========================================
        # INFORMATIONS DU DEVIS
        # ==========================================

        ctk.CTkLabel(
            frame_infos,
            text="📄 Informations du l'ordre de réparation",
            font=("Arial", 11, "bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(5,3))

        for i in range(3):
            frame_infos.grid_columnconfigure(i, weight=1)

        # ---------- Ligne 1 ----------

        ctk.CTkLabel(frame_infos, text="N° or", font=("Arial",10)).grid(row=1,column=0,sticky="w",padx=8)
        ctk.CTkLabel(frame_infos, text="Date", font=("Arial",10)).grid(row=1,column=2,sticky="w",padx=8)

        self.entry_numero = ctk.CTkEntry(frame_infos, height=24)

        self.entry_date = ctk.CTkEntry(frame_infos, height=24)

        self.entry_numero.grid(row=2,column=0,sticky="ew",padx=(8,0),pady=(0,3))


        self.entry_date.grid(row=2,column=2,sticky="ew",padx=(0,8),pady=(0,3))

        # ---------- Ligne 2 ----------

        ctk.CTkLabel(frame_infos, text="Client", font=("Arial",10)).grid(row=3,column=0,sticky="w",padx=8)
        ctk.CTkLabel(frame_infos, text="Immatriculation", font=("Arial",10)).grid(row=5,column=0,sticky="w",padx=8)

        self.entry_client = ctk.CTkEntry(frame_infos, state="normal", height=24)

        self.entry_immat = ctk.CTkEntry(frame_infos, state="normal", height=24)

        self.entry_client.grid(row=4,column=0,sticky="ew",padx=(8,0),pady=(0,3))
        btn_client = ctk.CTkButton(
            frame_infos,
            text="🔍",
            width=30,
            height=24,
            fg_color="#fc0411",
            hover_color="#bb0214",
            command=self.choisir_client
        )
        btn_client.grid(row=4, column=1,sticky="w", padx=(8,0), pady=(0,3))


        self.entry_immat.grid(row=6,column=0,sticky="ew",padx=(8,0),pady=(0,3))
        btn_vehicule = ctk.CTkButton(
            frame_infos,
            text="🔍",
            width=30,
            height=24,
            fg_color="#fc0411",
            hover_color="#bb0214",
            command=self.choisir_vehicule
        )
        btn_vehicule.grid(row=6, column=1,sticky="w", padx=(8,0), pady=(0,3))

        # ---------- Ligne 3 ----------


        ctk.CTkLabel(frame_infos, text="Statut", font=("Arial",10)).grid(row=5,column=2,sticky="w",padx=8)
        ctk.CTkLabel(frame_infos, text="Échéance", font=("Arial",10)).grid(row=3,column=2,sticky="w",padx=8)

        

        self.combo_statut = ctk.CTkComboBox(
            frame_infos,
            values=["En attente","Accepté","Refusé","Transformé en OR"],
            height=24
        )
        self.combo_statut.set("En attente")

        self.entry_echeance = ctk.CTkEntry(frame_infos, height=20)


        self.combo_statut.grid(row=6,column=2,sticky="ew",padx=(0,8),pady=(0,3))
        self.entry_echeance.grid(row=4,column=2,sticky="ew",padx=(0,8),pady=(0,3))


        # ==========================
        # PRESTATIONS
        # ==========================

        frame_prestations = ctk.CTkFrame(
            self.droite,
            fg_color="#0A0606",
            corner_radius=10
        )
        frame_prestations.configure(height=160)
        frame_prestations.pack(fill="x",padx=20,pady=(0,5))
        frame_prestations.pack_propagate(False)
        # ==========================================
        # PRESTATIONS
        # ==========================================

        ctk.CTkLabel(
            frame_prestations,
            text="🔧 Prestations",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=10, pady=(5,3))

        # ---------- Barre de boutons ----------

        barre = ctk.CTkFrame(
            frame_prestations,
            fg_color="transparent"
        )
        barre.pack(fill="x", padx=10, pady=(0,3))

        ctk.CTkButton(
            barre,
            text="➕ Ajouter",
            width=110,
            height=24,
            fg_color="#FC0411",
            command=self.ajouter_prestation
        ).pack(side="left", padx=(0,3))

        ctk.CTkButton(
            barre,
            text="✏ Modifier",
            width=110,
            height=24,
            fg_color="#FC0411",
            command=self.modifier_prestation
        ).pack(side="left", padx=(0,3))

        ctk.CTkButton(
            barre,
            text="🗑 Supprimer",
            width=110,
            height=24,
            fg_color="#FC0411",
            command=self.supprimer_prestation
        ).pack(side="left")

        # ---------- Tableau ----------

        frame_table = ctk.CTkFrame(
            frame_prestations,
            fg_color="transparent"
        )
        frame_table.pack(fill="both", expand=True, padx=10, pady=(0,10))

        style.configure(
            "Prestations.Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            rowheight=24
        )

        self.table_prestations = ttk.Treeview(
            frame_table,
            columns=("designation","quantite","temps","pu","total"),
            show="headings",
            style="Prestations.Treeview"
        )

        self.table_prestations.heading("designation", text="Désignation")
        self.table_prestations.heading("quantite", text="Qté")
        self.table_prestations.heading("temps", text="Temps")
        self.table_prestations.heading("pu", text="PU_HT")
        self.table_prestations.heading("total", text="Total")

        self.table_prestations.column("designation", width=330)
        self.table_prestations.column("quantite", width=60, anchor="center")
        self.table_prestations.column("temps", width=90, anchor="center")
        self.table_prestations.column("pu", width=100, anchor="e")
        self.table_prestations.column("total", width=100, anchor="e")

        scroll = ttk.Scrollbar(
            frame_table,
            orient="vertical",
            command=self.table_prestations.yview
        )

        self.table_prestations.configure(
            yscrollcommand=scroll.set
        )

        self.table_prestations.pack(
            side="left",
            fill="both",
            expand=True
        )

        scroll.pack(
            side="right",
            fill="y"
        )

        # ==========================================
        # TRAVAUX
        # ==========================================

        frame_travaux = ctk.CTkFrame(
            self.droite,
            fg_color="#0A0606",
            corner_radius=10
        )
        frame_travaux.pack(fill="x", padx=10, pady=(5,5))

        # Travaux prévus
        ctk.CTkLabel(
            frame_travaux,
            text="🛠 Travaux prévus",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=10, pady=(8,2))

        self.txt_travaux_prevus = ctk.CTkTextbox(
            frame_travaux,
            height=70
        )
        self.txt_travaux_prevus.pack(fill="x", padx=10)

        # Travaux effectués
        ctk.CTkLabel(
            frame_travaux,
            text="✅ Travaux effectués",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=10, pady=(8,2))

        self.txt_travaux_effectues = ctk.CTkTextbox(
            frame_travaux,
            height=70
        )
        self.txt_travaux_effectues.pack(fill="x", padx=10, pady=(0,10))

        # ==========================================
        # OBSERVATIONS
        # ==========================================

        frame_observations = ctk.CTkFrame(
            self.droite,
            height=70,
            fg_color="#0A0606",
            corner_radius=10
        )
        frame_observations.pack(fill="x", padx=10, pady=(5,5))
        frame_observations.pack_propagate(False)

        ctk.CTkLabel(
            frame_observations,
            text="📝 Observations",
            font=("Arial",10,"bold")
        ).pack(anchor="w", padx=10, pady=(5,3))

        self.txt_observations = ctk.CTkTextbox(
            frame_observations,
            height=35
        )

        self.txt_observations.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0,8)
        )

        # ==========================================
        # TEMPS DE MAIN-D'ŒUVRE
        # ==========================================

        frame_temps = ctk.CTkFrame(
            self.droite,
            fg_color="#0A0606",
            corner_radius=10
        )
        frame_temps.pack(fill="x", padx=10, pady=(5,5))

        ctk.CTkLabel(
            frame_temps,
            text="⏱ Temps de main-d'œuvre",
            font=("Arial",10,"bold")
        ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(frame_temps, text="Temps prévu (h)").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_temps_prevu = ctk.CTkEntry(frame_temps, width=80)
        self.entry_temps_prevu.grid(row=1, column=1, padx=5)

        ctk.CTkLabel(frame_temps, text="Temps réel (h)").grid(row=1, column=2, padx=(25,10), pady=5, sticky="w")
        self.entry_temps_reel = ctk.CTkEntry(frame_temps, width=80)
        self.entry_temps_reel.grid(row=1, column=3, padx=5)

    
    def generer_numero_or(self):
        annee = datetime.now().year

        self.cur.execute("""
            SELECT numero
            FROM ordres_reparation
            WHERE numero LIKE ?
            ORDER BY id DESC
            LIMIT 1
        """, (f"OR-{annee}-%",))

        resultat = self.cur.fetchone()

        if resultat:
            dernier = int(resultat[0].split("-")[-1]) + 1
        else:
            dernier = 1

        numero = f"OR-{annee}-{dernier:04d}"

        self.entry_numero.delete(0, "end")
        self.entry_numero.insert(0, numero)

        return numero


    def supprimer_or(self):

        selection = self.table_or.selection()

        if not selection:
            messagebox.showwarning(
                "FMS Manager",
                "Sélectionnez un ordre de réparation."
            )
            return

        if not messagebox.askyesno(
            "Confirmation",
            "Voulez-vous supprimer cet ordre de réparation ?"
        ):
            return

        numero = self.table_or.item(selection[0])["values"][0]

        self.cur.execute(
            "SELECT id FROM ordres_reparation WHERE numero=?",
            (numero,)
        )

        resultat = self.cur.fetchone()

        if not resultat:
            return

        or_id = resultat[0]

        self.cur.execute(
            "DELETE FROM lignes_or WHERE or_id=?",
            (or_id,)
        )
        database.recalculer_temps_prevu(self.or_id)

        self.cur.execute(
            "DELETE FROM ordres_reparation WHERE id=?",
            (or_id,)
        )

        self.conn.commit()

        self.nouveau_or()
        self.charger_liste_or()

        messagebox.showinfo(
            "FMS Manager",
            "Ordre de réparation supprimé avec succès."
        )


    def charger_liste_or(self):

        for item in self.table_or.get_children():
            self.table_or.delete(item)

        self.cur.execute("""
            SELECT numero, client, date
            FROM ordres_reparation
            ORDER BY id DESC
        """)

        for ligne in self.cur.fetchall():
            self.table_or.insert("", "end", values=ligne)

    def ouvrir_or(self, event=None):

        selection = self.table_or.selection()

        if not selection:
            return

        numero = self.table_or.item(selection[0])["values"][0]

        self.cur.execute("""
            SELECT
                id,
                numero,
                date,
                client,
                client_id,
                immatriculation,
                kilometrage,
                travaux_prevus,
                travaux_effectues,
                temps_prevu,
                temps_reel,
                observations,
                statut
            FROM ordres_reparation
            WHERE numero=?
        """, (numero,))

        or_data = self.cur.fetchone()

        if not or_data:
            return

        self.or_id = or_data[0]
        self.client_id = or_data[4]

        self.entry_numero.delete(0, "end")
        self.entry_numero.insert(0, or_data[1])

        self.entry_date.delete(0, "end")
        self.entry_date.insert(0, or_data[2])

        self.entry_client.delete(0, "end")
        self.entry_client.insert(0, or_data[3])

        self.entry_immat.delete(0, "end")
        self.entry_immat.insert(0, or_data[5])

        self.txt_travaux_prevus.delete("1.0", "end")
        self.txt_travaux_prevus.insert("1.0", or_data[7] or "")

        self.txt_travaux_effectues.delete("1.0", "end")
        self.txt_travaux_effectues.insert("1.0", or_data[8] or "")

        self.entry_temps_prevu.delete(0, "end")
        self.entry_temps_prevu.insert(0, or_data[9] or "")

        self.entry_temps_reel.delete(0, "end")
        self.entry_temps_reel.insert(0, or_data[10] or "")

        self.txt_observations.delete("1.0", "end")
        self.txt_observations.insert("1.0", or_data[11] or "")

        self.combo_statut.set(or_data[12])

        for item in self.table_prestations.get_children():
            self.table_prestations.delete(item)

        self.cur.execute("""
            SELECT
                designation,
                quantite,
                temps,
                prix_ht,
                total
            FROM lignes_or
            WHERE or_id=?
        """, (self.or_id,))

        for ligne in self.cur.fetchall():
            self.table_prestations.insert("", "end", values=ligne)

    


    def enregistrer_or(self):

        if not self.entry_client.get().strip():
            messagebox.showwarning(
                "FMS Manager",
                "Veuillez sélectionner un client."
            )
            return

        if self.or_id is None:

            self.cur.execute("""
                INSERT INTO ordres_reparation
                (
                    numero,
                    date,
                    client,
                    client_id,
                    immatriculation,
                    kilometrage,
                    travaux_prevus,
                    travaux_effectues,
                    temps_prevu,
                    temps_reel,
                    observations,
                    statut
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                self.entry_numero.get(),
                self.entry_date.get(),
                self.entry_client.get(),
                self.client_id,
                self.entry_immat.get(),
                0,
                self.txt_travaux_prevus.get("1.0", "end").strip(),
                self.txt_travaux_effectues.get("1.0", "end").strip(),
                self.entry_temps_prevu.get(),
                self.entry_temps_reel.get(),
                self.txt_observations.get("1.0", "end").strip(),
                self.combo_statut.get()
            ))

            self.conn.commit()
            self.or_id = self.cur.lastrowid

        else:

            self.cur.execute("""
                UPDATE ordres_reparation
                SET
                    numero=?,
                    date=?,
                    client=?,
                    client_id=?,
                    immatriculation=?,
                    kilometrage=?,
                    travaux_prevus=?,
                    travaux_effectues=?,
                    temps_prevu=?,
                    temps_reel=?,
                    observations=?,
                    statut=?
                WHERE id=?
            """, (
                self.entry_numero.get(),
                self.entry_date.get(),
                self.entry_client.get(),
                self.client_id,
                self.entry_immat.get(),
                0,
                self.txt_travaux_prevus.get("1.0", "end").strip(),
                self.txt_travaux_effectues.get("1.0", "end").strip(),
                self.entry_temps_prevu.get(),
                self.entry_temps_reel.get(),
                self.txt_observations.get("1.0", "end").strip(),
                self.combo_statut.get(),
                self.or_id
            ))

            self.conn.commit()

        self.cur.execute(
            "DELETE FROM lignes_or WHERE or_id=?",
            (self.or_id,)
        )

        for item in self.table_prestations.get_children():

            valeurs = self.table_prestations.item(item)["values"]

            self.cur.execute("""
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
                self.or_id,
                valeurs[0],
                valeurs[1],
                valeurs[2],
                valeurs[3],
                valeurs[4]
            ))

        self.calculer_temps_prevu()
        self.conn.commit()

        self.charger_liste_or()

        messagebox.showinfo(
            "FMS Manager",
            "Ordre de réparation enregistré avec succès."
        )

    def ouvrir_fenetre_prestation(self, mode="ajout", item=None):

        fenetre = ctk.CTkToplevel(self.fenetre)
        fenetre.title("Prestation")
        fenetre.geometry("500x320")
        fenetre.grab_set()

        ctk.CTkLabel(
            fenetre,
            text="Désignation"
        ).pack(pady=(15, 5))

        designation = ctk.CTkEntry(
            fenetre,
            width=380
        )
        designation.pack()

        ctk.CTkLabel(
            fenetre,
            text="Quantité"
        ).pack(pady=(10, 5))

        quantite = ctk.CTkEntry(
            fenetre,
            width=120
        )
        quantite.insert(0, "1")
        quantite.pack()

        ctk.CTkLabel(
            fenetre,
            text="Prix HT"
        ).pack(pady=(10, 5))

        prix = ctk.CTkEntry(
            fenetre,
            width=120
        )
        prix.pack()

        if mode == "modification" and item:

            valeurs = self.table_prestations.item(item, "values")

            designation.insert(0, valeurs[0])

            quantite.delete(0, "end")
            quantite.insert(0, str(valeurs[1]))

            prix.delete(0, "end")
            prix.insert(0, str(valeurs[3]))

        def valider():

            try:
                qte = float(quantite.get().replace(",", "."))
                pu = float(prix.get().replace(",", "."))
            except ValueError:
                messagebox.showerror(
                    "Erreur",
                    "La quantité et le prix doivent être des nombres."
                )
                return

            total = round(qte * pu, 2)

            valeurs = (
                designation.get(),
                qte,
                "0 h 00",
                pu,
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

            self.calculer_totaux()
            fenetre.destroy()

        ctk.CTkButton(
            fenetre,
            text="Valider",
            command=valider
        ).pack(pady=20)

    def ajouter_prestation(self):
        CataloguePrestations(
            self.fenetre,
            self.retour_prestation
        )


    def modifier_prestation(self):
        selection = self.table_prestations.selection()

        if not selection:
            messagebox.showwarning(
                "Attention",
                "Sélectionnez une prestation."
            )
            return

        self.ouvrir_fenetre_prestation(
            mode="modification",
            item=selection[0]
        )


    def calculer_totaux(self):

        total_ht = 0

        for item in self.table_prestations.get_children():
            valeurs = self.table_prestations.item(item)["values"]

            try:
                total_ht += float(str(valeurs[4]).replace(",", "."))
            except (ValueError, IndexError):
                pass

        tva = round(total_ht * 0.20, 2)
        total_ttc = round(total_ht + tva, 2)

        if hasattr(self, "label_ht"):
            self.label_ht.configure(text=f"{total_ht:.2f} €")

        if hasattr(self, "label_tva"):
            self.label_tva.configure(text=f"{tva:.2f} €")

        if hasattr(self, "label_ttc"):
            self.label_ttc.configure(text=f"{total_ttc:.2f} €")

        self.calculer_temps_prevu()

    def calculer_temps_prevu(self):
        total_minutes = 0

        for item in self.table_prestations.get_children():
            valeurs = self.table_prestations.item(item)["values"]

            try:
                texte = str(valeurs[2]) # colonne Temps
                h, m = texte.split(" h ")
                total_minutes += int(h) * 60 + int(m)
            except:
                pass

        heures = total_minutes // 60
        minutes = total_minutes % 60

        self.entry_temps_prevu.delete(0, "end")
        self.entry_temps_prevu.insert(0, f"{heures} h {minutes:02d}")


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



    def nouveau_or(self):

        self.or_id = None
        self.client_id = None

        self.generer_numero_or()

        self.entry_date.delete(0, "end")
        self.entry_date.insert(0, datetime.now().strftime("%d/%m/%Y"))

        self.entry_client.delete(0, "end")
        self.entry_immat.delete(0, "end")

        self.txt_travaux_prevus.delete("1.0", "end")
        self.txt_travaux_effectues.delete("1.0", "end")
        self.txt_observations.delete("1.0", "end")

        self.entry_temps_prevu.delete(0, "end")
        self.entry_temps_reel.delete(0, "end")

        self.combo_statut.set("En attente")

        for item in self.table_prestations.get_children():
            self.table_prestations.delete(item)

        self.fenetre.focus_force()

    def choisir_or(self):
        messagebox.showinfo(
            "Ordres de réparation",
            "Cette fonction sera disponible lorsque le module OR sera terminé."
        )

    def charger_depuis_or(self, numero_or, client, immatriculation, observations, temps):

        #self.entry_or.delete(0, "end")
        #self.entry_or.insert(0, numero_or)

        self.entry_client.delete(0, "end")
        self.entry_client.insert(0, client)

        self.entry_immat.delete(0, "end")
        self.entry_immat.insert(0, immatriculation)

        self.entry_temps_prevu.delete(0, "end")
        self.entry_temps_prevu.insert(0, temps)

        self.txt_observations.delete("1.0", "end")
        self.txt_observations.insert("1.0", observations)

    

    def verifier_base(self):

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS ordres_reparation(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE,
                date TEXT,
                client TEXT,
                client_id INTEGER,
                immatriculation TEXT,
                kilometrage INTEGER DEFAULT 0,
                travaux_prevus TEXT,
                travaux_effectues TEXT,
                temps_prevu TEXT,
                temps_reel TEXT,
                observations TEXT,
                statut TEXT
            )
        """)

        self.cur.execute("""
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

        self.conn.commit()


    def choisir_client(self):
        SelectionClient(
            self.fenetre,
            self.retour_client
        )
        

    def retour_prestation(self, valeurs):
        print(valeurs)
        return
        reference, designation, categorie, prix_ht, tva, prix_ttc, temps_heures, temps_minutes = valeurs
        temps = f"{int(temps_heures)} h {int(temps_minutes):02d}"
        print("Temps reçu :", temps)
        print("Valeurs reçues :", valeurs)
        self.table_prestations.insert(
            "",
            "end",
            values=(
                designation,
                1,
                temps,
                float(prix_ht),
                float(prix_ht)
            )
        )

        self.calculer_totaux()


    def retour_client(self, valeurs):

        client_id, type_client, nom, prenom, telephone, ville = valeurs
        self.client_id=client_id

        self.entry_client.delete(0, "end")

        if type_client.lower() == "particulier":
            self.entry_client.insert(0, f"{nom} {prenom}")
        else:
            self.entry_client.insert(0, nom)

    def choisir_vehicule(self):
        SelectionVehicule(self.fenetre,
                          self.retour_vehicule,
                          self.client_id)

    def retour_vehicule(self, valeurs):
        immatriculation, marque, modèle, motorisation, nom, prenom=valeurs
        self.entry_immat.delete(0,"end")
        self.entry_immat.insert(0,immatriculation)
        self.entry_client.delete(0,"end")
        self.entry_client.insert(0,f"{nom} {prenom}")
        
    def imprimer_pdf(self):
        print("Client ID :",self.client_id)
        print("Devis ID :",self.or_id)
        print("Client :",self.entry_client.get())
        print("Immat :",self.entry_immat.get())
        # -------- Client --------
        self.cur.execute("""
            SELECT prenom,
                   telephone,
                   email,
                   adresse,
                   code_postal,
                   ville
            FROM clients
            WHERE id=?
        """, (self.client_id,))
        client = self.cur.fetchone()

        if not client:
            messagebox.showerror(
                "FMS Manager",
                "Impossible de retrouver les informations du client."
            )
            return

        # -------- Véhicule --------
        print("Immat :",
              self.entry_immat.get())
        self.cur.execute("""
            SELECT marque,
                   modele,
                   kilometrage
            FROM vehicules
            WHERE immatriculation=?
        """, (self.entry_immat.get(),))
        print("Immatriculation recherchée :",
              self.entry_immat.get())
        vehicule = self.cur.fetchone()

        if not vehicule:
            messagebox.showerror(
                "FMS Manager",
                "Impossible de retrouver le véhicule."
            )
            return

        # -------- Prestations --------
        prestations = []

        for item in self.table_prestations.get_children():

            designation, qte, temps, prix_ht, total = self.table_prestations.item(item)["values"]
            

            prestations.append((
                "", # Référence
                designation,
                qte,
                temps,
                float(prix_ht),
                float(total)
            ))

        # -------- Création du PDF --------
        temps_prevu =self.entry_temps_prevu.get()

        
        temps_reel = self.entry_temps_reel.get().strip()
        if not temps_reel :
            temps_reel = "-"
        fichier = pdf_or.creer_pdf_or(
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
            travaux_prevus=self.txt_travaux_prevus.get("1.0", "end").strip(),
            travaux_effectues=self.txt_travaux_effectues.get("1.0", "end").strip(),
            temps_prevu=temps_prevu,
            temps_reel=temps_reel,
            observations=self.txt_observations.get("1.0", "end").strip()
        )

        messagebox.showinfo(
            "FMS Manager",
            f"PDF créé avec succès.\n\n{fichier}"
        )
        win32api.ShellExecute(
            0,
            "open",
            fichier,
            None,
            ".",
            1
        )
        return fichier

    def imprimer_direct(self):
        fichier=self.imprimer_pdf()
        import win32api
        win32api.ShellExecute(
            0,
            "print",
            fichier,
            None,
            ".",
            0
        )

    def envoyer_mail(self):

        fen = ctk.CTkToplevel(self.fenetre)
        fen.title("Envoyer le devis")
        fen.geometry("600x420")

        ctk.CTkLabel(fen, text="Destinataire").pack(anchor="w", padx=20, pady=(15,0))
        email = ctk.CTkEntry(fen, width=520)
        email.pack(padx=20)

        ctk.CTkLabel(fen, text="Objet").pack(anchor="w", padx=20, pady=(10,0))
        objet = ctk.CTkEntry(fen, width=520)
        objet.pack(padx=20)

        ctk.CTkLabel(fen, text="Message").pack(anchor="w", padx=20, pady=(10,0))
        texte = ctk.CTkTextbox(fen, width=520, height=170)
        texte.pack(padx=20, pady=5)
        email.insert(0, database.recuperer_email_client(self.client_id))
        objet.insert(0, f"Devis {self.entry_numero.get()}")

        texte.insert(
            "1.0",
            f"""Bonjour,

        Veuillez trouver ci-joint votre ordres de reparation {self.entry_numero.get()}.

        Je reste à votre disposition pour toute question.

        Cordialement,

        FRED.MECA.SERVICES"""
        )
        def envoyer():

            try:
                pdf = self.imprimer_pdf()

                msg = EmailMessage()
                msg["Subject"] = objet.get()
                msg["From"] = "fred.meca.services62@gmail.com"
                msg["To"] = email.get()

                msg.set_content(texte.get("1.0", "end"))

                with open(pdf, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype="application",
                        subtype="pdf",
                        filename=os.path.basename(pdf)
                    )

                contexte = ssl.create_default_context()

                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexte) as smtp:
                    smtp.login(
                        "fred.meca.services62@gmail.com",
                        "ghmbtfftprlegfco"
                    )
                    smtp.send_message(msg)

                messagebox.showinfo(
                    "Succès",
                    "L'ordres de réparation a été envoyé avec succès."
                )

            except Exception as e:
                messagebox.showerror(
                    "Erreur",
                    str(e)
                )


        ctk.CTkButton(
            fen,
            text="📨 Envoyer",
            width=180,
            command=envoyer
        ).pack(pady=10)

        ctk.CTkButton(
            fen,
            text="❌ Annuler",
            width=180,
            fg_color="gray",
            command=fen.destroy
        ).pack()



    def menu_export(self):
        menu = tk.Menu(self.fenetre, tearoff=0)

        menu.add_command(
            label="📄 Aperçu PDF",
            command=self.imprimer_pdf
        )

        menu.add_command(
            label="🖨️ Imprimer",
            command=self.imprimer_direct
        )

        menu.add_command(
            label="✉️ Envoyer par e-mail",
            command=self.envoyer_mail
        )

        menu.post(
            self.fenetre.winfo_pointerx(),
            self.fenetre.winfo_pointery()
        )



    def transformer_en_facture(self):
        self.combo_statut.set("Transformé en OR")

        if self.or_id:
            self.cur.execute("""
                UPDATE ordres_reparation
                SET statut=?
                WHERE id=?
            """, ("Transformé en OR", self.or_id))
            self.conn.commit()

            numero_or=self.generer_numero_or()
            database.creer_or_depuis_devis
            (
                numero_or,
                self.entry_date.get(),
                self.entry_client.get(),
                self.entry_immat.get(),
                self.txt_observations.get("1.0", "end").strip()
            )
            self.entry_date.get(),
            self.entry_client.get(),
            self.entry_immat.get(),
            self.txt_observations.get("1.0", "end").strip()
        
        messagebox.showinfo(
            "FMS Manager",
            "Le devis a été transformé en ordre de réparation."
        )


def ouvrir(parent):
    ReparationManager(parent)


