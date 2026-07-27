
import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox
from PIL import Image


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

        for texte in [
            "➕ Nouvelle",
            "💾 Enregistrer",
            "🖨 Imprimer PDF",
            "🗑 Supprimer",
            "🔄 Actualiser"
        ]:
            ctk.CTkButton(
                frame_boutons,
                text=texte,
                height=40,
                fg_color="#FC0411",
                hover_color="#BB0214"
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
        ctk.CTkLabel(frame_infos, text="Date", font=("Arial",10)).grid(row=1,column=2,sticky="w",padx=8)

        self.entry_numero = ctk.CTkEntry(frame_infos, height=24)
        self.entry_or = ctk.CTkEntry(frame_infos, height=24)
        self.entry_date = ctk.CTkEntry(frame_infos, height=24)

        self.entry_numero.grid(row=2,column=0,sticky="ew",padx=8,pady=(0,3))
        self.entry_or.grid(row=2,column=1,sticky="ew",padx=8,pady=(0,3))
        self.entry_date.grid(row=2,column=2,sticky="ew",padx=8,pady=(0,3))

        # ---------- Ligne 2 ----------

        ctk.CTkLabel(frame_infos, text="Client", font=("Arial",10)).grid(row=3,column=0,sticky="w",padx=8)
        ctk.CTkLabel(frame_infos, text="Immatriculation", font=("Arial",10)).grid(row=3,column=1,sticky="w",padx=8)

        self.entry_client = ctk.CTkEntry(frame_infos, state="disabled", height=24)
        self.entry_immat = ctk.CTkEntry(frame_infos, state="disabled", height=24)

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
            fg_color="#FC0411"
        ).pack(side="left", padx=(0,3))

        ctk.CTkButton(
            barre,
            text="✏ Modifier",
            width=110,
            height=24,
            fg_color="#FC0411"
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







        
def ouvrir(parent):
    FactureManager(parent)


