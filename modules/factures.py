
import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox
from PIL import Image
from datetime import datetime


class FactureManager:

    def __init__(self, parent):
        self.parent = parent

        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("FMS Manager - Factures")
        self.fenetre.geometry("1600x900")
        self.fenetre.minsize(1400,900)
        self.fenetre.configure(fg_color="#464242")

        self.creer_interface()

        self.creer_tables()
        self.generer_numero_facture()
        self.charger_factures()


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
            text="Gestion des factures",
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
            placeholder_text="Nom du client ou N° de facture..."
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

        self.table_factures = ttk.Treeview(
            frame_liste,
            columns=("numero","client","date"),
            show="headings"
        )

        self.table_factures.heading("numero", text="Facture")
        self.table_factures.heading("client", text="Client")
        self.table_factures.heading("date", text="Date")

        self.table_factures.column("numero", width=100)
        self.table_factures.column("client", width=170)
        self.table_factures.column("date", width=90)

        scroll = ttk.Scrollbar(
            frame_liste,
            orient="vertical",
            command=self.table_factures.yview
        )

        self.table_factures.configure(yscrollcommand=scroll.set)

        self.table_factures.pack(side="left", fill="both", expand=True)
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
              text="➕ Nouvelle",
              height=40,
              hover_color="#0233bb",
              command=self.nouvelle_facture
              ).pack(fill="x", pady=4)

        ctk.CTkButton(
            frame_boutons,
            text="💾 Enregistrer",
            height=40,
            fg_color="#fc0411",
            hover_color="#bb0214",
            command=self.enregistrer_facture
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            frame_boutons,
              text="🖨 Imprimer PDF",
              height=40,
              fg_color="#fc0411",
              hover_color="#bb0214",
              ).pack(fill="x", pady=4)

        ctk.CTkButton(
            frame_boutons,
              text="🗑 Supprimer",
              height=40,
              fg_color="#fc0411",
              hover_color="#bb0214",
              command=self.supprimer_prestation
              ).pack(fill="x", pady=4)

        ctk.CTkButton(
            frame_boutons,
              text="🔄 Actualiser",
              height=40,
              fg_color="#fc0411",
              hover_color="#bb0214",
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
        # INFORMATIONS DE LA FACTURE
        # ==========================================

        ctk.CTkLabel(
            frame_infos,
            text="📄 Informations de la facture",
            font=("Arial", 11, "bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(5,3))

        for i in range(3):
            frame_infos.grid_columnconfigure(i, weight=1)

        # ---------- Ligne 1 ----------

        ctk.CTkLabel(frame_infos, text="N° Facture", font=("Arial",10)).grid(row=1,column=0,sticky="w",padx=8)
        ctk.CTkLabel(frame_infos, text="N° OR", font=("Arial",10)).grid(row=1,column=1,sticky="w",padx=8)
        ctk.CTkLabel(frame_infos, text="Date", font=("Arial",10)).grid(row=1,column=3,sticky="w",padx=8)

        self.entry_numero = ctk.CTkEntry(frame_infos, height=24)
        self.entry_or = ctk.CTkEntry(frame_infos, height=24)
        self.entry_date = ctk.CTkEntry(frame_infos, height=24)

        self.entry_numero.grid(row=2,column=0,sticky="ew",padx=8,pady=(0,3))
        self.entry_or.grid(row=2,column=1,sticky="ew",padx=8,pady=(0,3))

        ctk.CTkButton(
            frame_infos,
            text="🔍",
            width=30,
            height=24,
            fg_color="#FC0411",
            hover_color="#BB0214",
            command=self.choisir_or
        ).grid(row=2, column=2, sticky="w", padx=(2, 8), pady=(0,3))

        self.entry_date.grid(row=2,column=3,sticky="ew",padx=8,pady=(0,3))

        # ---------- Ligne 2 ----------

        ctk.CTkLabel(frame_infos, text="Client", font=("Arial",10)).grid(row=3,column=0,sticky="w",padx=8)
        ctk.CTkLabel(frame_infos, text="Immatriculation", font=("Arial",10)).grid(row=3,column=1,sticky="w",padx=8)

        self.entry_client = ctk.CTkEntry(frame_infos, state="normal", height=24)
        self.entry_immat = ctk.CTkEntry(frame_infos, state="normal", height=24)

        self.entry_client.grid(row=4,column=0,sticky="ew",padx=8,pady=(0,3))
        self.entry_immat.grid(row=4,column=1,sticky="ew",padx=8,pady=(0,3))

        # ---------- Ligne 3 ----------

        ctk.CTkLabel(frame_infos, text="Paiement", font=("Arial",10)).grid(row=5,column=0,sticky="w",padx=8)
        ctk.CTkLabel(frame_infos, text="Statut", font=("Arial",10)).grid(row=5,column=1,sticky="w",padx=8)
        ctk.CTkLabel(frame_infos, text="Échéance", font=("Arial",10)).grid(row=5,column=2,sticky="w",padx=8)

        self.combo_paiement = ctk.CTkComboBox(
            frame_infos,
            values=["Espèces","Carte","Chèque","Virement","Autre"],
            height=24
        )

        self.combo_statut = ctk.CTkComboBox(
            frame_infos,
            values=["En attente","Payée","Impayée"],
            height=24
        )
        self.combo_statut.set("En attente")

        self.entry_echeance = ctk.CTkEntry(frame_infos, height=24)

        self.combo_paiement.grid(row=6,column=0,sticky="ew",padx=8,pady=(0,8))
        self.combo_statut.grid(row=6,column=1,sticky="ew",padx=8,pady=(0,8))
        self.entry_echeance.grid(row=6,column=2,sticky="ew",padx=8,pady=(0,8))


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
            fg_color="#FC0411"
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
            columns=("designation","qte","pu","total"),
            show="headings",
            style="Prestations.Treeview"
        )

        self.table_prestations.heading("designation", text="Désignation")
        self.table_prestations.heading("qte", text="Qté")
        self.table_prestations.heading("pu", text="PU HT")
        self.table_prestations.heading("total", text="Total")

        self.table_prestations.column("designation", width=430)
        self.table_prestations.column("qte", width=70, anchor="center")
        self.table_prestations.column("pu", width=110, anchor="e")
        self.table_prestations.column("total", width=110, anchor="e")

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
        # TOTAUX
        # ==========================================

        frame_totaux = ctk.CTkFrame(
            self.droite,
            height=80,
            fg_color="#0A0606",
            corner_radius=10
        )
        frame_totaux.pack(fill="x", padx=10, pady=(5,10))
        frame_totaux.pack_propagate(False)

        frame_totaux.grid_columnconfigure(1, weight=1)
        frame_totaux.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(frame_totaux, text="Total HT").grid(row=0, column=0, sticky="w", padx=10, pady=(5,3))
        self.label_ht = ctk.CTkLabel(frame_totaux, text="0,00 €")
        self.label_ht.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(frame_totaux, text="TVA (0 %)").grid(row=0, column=2, sticky="w", padx=(20,10), pady=(5,3))
        self.label_tva = ctk.CTkLabel(frame_totaux, text="0,00 €")
        self.label_tva.grid(row=0, column=3, sticky="w")

        ctk.CTkLabel(frame_totaux, text="Remise").grid(row=1, column=0, sticky="w", padx=10, pady=3)
        self.entry_remise = ctk.CTkEntry(frame_totaux, width=90, height=26)
        self.entry_remise.grid(row=1, column=1, sticky="w")

        ctk.CTkLabel(frame_totaux, text="Déjà versé").grid(row=1, column=2, sticky="w", padx=(20,10))
        self.entry_deja_verse = ctk.CTkEntry(frame_totaux, width=90, height=26)
        self.entry_deja_verse.grid(row=1, column=3, sticky="w")

        ctk.CTkLabel(
            frame_totaux,
            text="TOTAL TTC",
            font=("Arial",16,"bold")
        ).grid(row=2, column=0, sticky="w", padx=10, pady=3)

        self.label_ttc = ctk.CTkLabel(
            frame_totaux,
            text="0,00 €",
            font=("Arial",16,"bold"),
            text_color="#D72638"
        )
        self.label_ttc.grid(row=2, column=1, sticky="w")

        ctk.CTkLabel(
           frame_totaux,
           text="Reste à payer",
           font=("Arial",16,"bold")
        ).grid(row=2, column=2, sticky="w", padx=(20,10))

        self.label_reste = ctk.CTkLabel(
            frame_totaux,
            text="0,00 €",
            font=("Arial",16,"bold"),
            text_color="#D72638"
        )
        self.label_reste.grid(row=2, column=3, sticky="w")

    def creer_tables(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS factures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE,
            numero_or TEXT,
            client TEXT,
            immatriculation TEXT,
            date_facture TEXT,
            paiement TEXT,
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

        self.conn.commit()

    
    def generer_numero_facture(self):

        annee = datetime.now().year

        self.cur.execute("SELECT COUNT(*) FROM factures")

        numero = self.cur.fetchone()[0] + 1

        numero = f"F{annee}-{numero:06d}"

        self.entry_numero.configure(state="normal")
        self.entry_numero.delete(0, "end")
        self.entry_numero.insert(0, numero)
        self.entry_numero.configure(state="disabled")

    def charger_factures(self):

        for item in self.table_factures.get_children():
            self.table_factures.delete(item)

        self.cur.execute("""
            SELECT numero, client, date
            FROM factures
            ORDER BY id DESC
        """)

        for ligne in self.cur.fetchall():
            self.table_factures.insert("", "end", values=ligne)

    def enregistrer_facture(self):

        self.cur.execute("""
            INSERT INTO factures
            (
                numero,
                numero_or,
                client,
                immatriculation,
                date_facture,
                paiement,
                statut,
                echeance,
                observations,
                remise,
                deja_verse,
                total_ht,
                tva,
                total_ttc
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (

            self.entry_numero.get(),
            self.entry_or.get(),
            self.entry_client.get(),
            self.entry_immat.get(),
            self.entry_date.get(),
            self.combo_paiement.get(),
            self.combo_statut.get(),
            self.entry_echeance.get(),
            self.txt_observations.get("1.0", "end").strip(),
            0,
            0,
            0,
            0,
            0

        ))

        self.conn.commit()

        messagebox.showinfo(
            "FMS Manager",
            "Facture enregistrée avec succès."
    )

        self.charger_factures()
        self.generer_numero_facture()

    def ajouter_prestation(self):

        fenetre = ctk.CTkToplevel(self.fenetre)
        fenetre.title("Nouvelle prestation")
        fenetre.geometry("450x250")

        ctk.CTkLabel(fenetre, text="Désignation").pack(pady=(10,0))
        designation = ctk.CTkEntry(fenetre, width=350)
        designation.pack()

        ctk.CTkLabel(fenetre, text="Quantité").pack(pady=(10,0))
        quantite = ctk.CTkEntry(fenetre)
        quantite.insert(0, "1")
        quantite.pack()

        ctk.CTkLabel(fenetre, text="Prix HT").pack(pady=(10,0))
        prix = ctk.CTkEntry(fenetre)
        prix.pack()

        def valider():
            try:
                qte = float(quantite.get().replace(",", "."))
                pu = float(prix.get().replace(",", "."))
                total = qte * pu

                self.table_prestations.insert(
                    "",
                    "end",
                    values=(
                        designation.get(),
                        qte,
                        f"{pu:.2f}",
                        f"{total:.2f}"
                    )
                )
                self.calculer_totaux()

                fenetre.destroy()

            except ValueError:
                messagebox.showerror(
                    "Erreur",
                    "Quantité ou prix incorrect."
                )

        ctk.CTkButton(
            fenetre,
            text="Ajouter",
            command=valider
        ).pack(pady=20)

    def calculer_totaux(self):

        total_ht = 0

        for item in self.table_prestations.get_children():

            valeurs = self.table_prestations.item(item)["values"]

            total_ht += float(str(valeurs[3]).replace(",", "."))

        tva = total_ht * 0.20

        try:
            remise = float(self.entry_remise.get().replace(",", "."))
        except:
            remise = 0

        total_ttc = total_ht + tva - remise

        try:
            deja_verse = float(self.entry_deja_verse.get().replace(",", "."))
        except:
            deja_verse = 0

        reste = total_ttc - deja_verse

        self.label_ht.configure(text=f"{total_ht:.2f} €")
        self.label_tva.configure(text=f"{tva:.2f} €")
        self.label_ttc.configure(text=f"{total_ttc:.2f} €")
        self.label_reste.configure(text=f"{reste:.2f} €")

    def supprimer_prestation(self):

        selection = self.table_prestations.selection()

        if not selection:
            messagebox.showwarning(
                "FMS Manager",
                "Sélectionnez une prestation."
            )
            return

        self.table_prestations.delete(selection[0])

        self.calculer_totaux()

    def modifier_prestation(self):

        messagebox.showinfo(
            "FMS Manager",
            "La modification des prestations sera ajoutée à l'étape suivante."
        )

    def nouvelle_facture(self):

        self.generer_numero_facture()

        self.entry_or.delete(0, "end")
        self.entry_client.delete(0, "end")
        self.entry_immat.delete(0, "end")
        self.entry_date.delete(0, "end")
        self.entry_echeance.delete(0, "end")

        self.combo_paiement.set("Espèces")
        self.combo_statut.set("En attente")

        self.entry_remise.delete(0, "end")
        self.entry_deja_verse.delete(0, "end")

        self.txt_observations.delete("1.0", "end")

        for item in self.table_prestations.get_children():
            self.table_prestations.delete(item)

        self.label_ht.configure(text="0,00 €")
        self.label_tva.configure(text="0,00 €")
        self.label_ttc.configure(text="0,00 €")
        self.label_reste.configure(text="0,00 €")

    def choisir_or(self):
        messagebox.showinfo(
            "Ordres de réparation",
            "Cette fonction sera disponible lorsque le module OR sera terminé."
        )

    def charger_depuis_or(self, numero_or, client, immatriculation, observations, temps):

        self.entry_or.delete(0, "end")
        self.entry_or.insert(0, numero_or)

        self.entry_client.delete(0, "end")
        self.entry_client.insert(0, client)

        self.entry_immat.delete(0, "end")
        self.entry_immat.insert(0, immatriculation)

        self.txt_observations.delete("1.0", "end")
        self.txt_observations.insert("1.0", observations)


def ouvrir(parent):
    FactureManager(parent)


