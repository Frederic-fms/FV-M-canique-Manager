import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class FactureManager:

    def __init__(self, parent):
        self.parent = parent
        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("Gestion des factures")
        self.fenetre.geometry("1600x900")
        self.fenetre.configure(fg_color="#1E1E1E")

        # ===== En-tête =====
        self.header = ctk.CTkFrame(
            self.fenetre,
            height=70,
            fg_color="#202020",
            corner_radius=0
        )
        self.header.pack(fill="x")

        ctk.CTkLabel(
            self.header,
            text="📄 FACTURES",
            font=("Arial", 28, "bold"),
            text_color="#FFFFFF"
        ).pack(side="left", padx=25, pady=15)

        # ===== Contenu =====
        self.contenu = ctk.CTkFrame(
            self.fenetre,
            fg_color="transparent"
)
        self.contenu.pack(fill="both", expand=True, padx=15, pady=15)

        # ===== Partie gauche =====
        self.gauche = ctk.CTkFrame(
            self.contenu,
            width=520,
            fg_color="#2B2B2B",
            corner_radius=12
        )
        self.gauche.pack(side="left", fill="both", padx=(0,10))

        # ===== Partie droite =====
        self.droite = ctk.CTkFrame(
        self.contenu,
            fg_color="#2B2B2B",
            corner_radius=12
        )
        self.droite.pack(side="right", fill="both", expand=True)

        self.creer_formulaire()
        self.charger_factures()


    def creer_formulaire(self):
        
        self.gauche.pack_propagate(False)
        self.droite.pack_propagate(False)

        # =========================
        # RECHERCHE
        # =========================

        ctk.CTkLabel(
           self.gauche,
           text="Recherche",
           font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=20, pady=(20,5))

        self.entry_recherche = ctk.CTkEntry(
            self.gauche,
            placeholder_text="Nom client, facture..."
        )

        self.entry_recherche.pack(
            fill="x",
            padx=20,
            pady=(0,15)
        )
        self.entry_recherche.bind("<KeyRelease>",
        self.rechercher_factures)

        # =========================
        # LISTE DES FACTURES
        # =========================

        self.table_factures = ttk.Treeview(
            self.gauche,
            columns=("numero","client","date","montant"),
            show="headings",
            height=25
        )

        self.table_factures.heading("numero", text="Facture")
        self.table_factures.heading("client", text="Client")
        self.table_factures.heading("date", text="Date")
        self.table_factures.heading("montant", text="Montant")

        self.table_factures.column("numero", width=120)
        self.table_factures.column("client", width=180)
        self.table_factures.column("date", width=100)
        self.table_factures.column("montant", width=100)

        self.table_factures.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )
        self.table_factures.bind("<<TreeviewSelect>>",
        self.ouvrir_facture)
        ctk.CTkLabel(self.droite,
                     text="Informations de la facture",
                     font=("Arial", 22, "bold")
                     ).pack(anchor="w", padx=20, pady=(20,10))
        # =========================
        # STATUT
        # =========================

        frame_statut = ctk.CTkFrame(
            self.droite,
            fg_color="transparent"
        )

        frame_statut.pack(fill="x", padx=20, pady=(5,20))

        self.lbl_statut = ctk.CTkLabel(
            frame_statut,
            text="🟠 EN ATTENTE",
            width=150,
            height=35,
            fg_color="#E67E22",
            corner_radius=18,
            text_color="white",
            font=("Arial",14,"bold")
        )

        self.lbl_statut.pack(side="right")
        ctk.CTkLabel(
            frame_statut,
            text="Statut :"
        ).pack(side="left", padx=(0,10))

        self.combo_statut = ctk.CTkComboBox(
            frame_statut,
            values=[
                "En attente",
                "Payée",
                "Impayée"
            ],
            width=160,
            command=self.changer_statut
        )

        self.combo_statut.set("En attente")
        self.combo_statut.pack(side="left")


        
        frame_ligne1 = ctk.CTkFrame(self.droite, fg_color="transparent")
        frame_ligne1.pack(fill="x", padx=20)

        # N° Facture
        frame_num = ctk.CTkFrame(frame_ligne1, fg_color="transparent")
        frame_num.pack(side="left", expand=True, fill="x", padx=(0,10))

        ctk.CTkLabel(frame_num, text="N° Facture").pack(anchor="w")

        self.entry_numero_facture = ctk.CTkEntry(frame_num)
        self.entry_numero_facture.pack(fill="x")
        self.entry_numero_facture.insert(0,
        self.generer_numero_facture())

        # N° OR
        frame_or = ctk.CTkFrame(frame_ligne1, fg_color="transparent")
        frame_or.pack(side="left", expand=True, fill="x")

        ctk.CTkLabel(frame_or, text="N° OR").pack(anchor="w")

        self.entry_numero_or = ctk.CTkEntry(frame_or)
        self.entry_numero_or.pack(fill="x")

        # Date
        frame_date = ctk.CTkFrame(frame_ligne1, fg_color="transparent")
        frame_date.pack(side="left", expand=True, fill="x", padx=(10,0))

        ctk.CTkLabel(frame_date, text="Date").pack(anchor="w")

        self.entry_date = ctk.CTkEntry(frame_date)
        self.entry_date.pack(fill="x")

        self.entry_date.insert(
            0,
            datetime.now().strftime("%d/%m/%Y")
        )

        frame_ligne2 = ctk.CTkFrame(self.droite, fg_color="transparent")
        frame_ligne2.pack(fill="x", padx=20, pady=(15,0))

        # Client
        frame_client = ctk.CTkFrame(frame_ligne2, fg_color="transparent")
        frame_client.pack(side="left", expand=True, fill="x", padx=(0,10))

        ctk.CTkLabel(frame_client, text="Client").pack(anchor="w")

        self.entry_client = ctk.CTkEntry(frame_client)
        self.entry_client.pack(fill="x")

        # Immatriculation
        frame_immat = ctk.CTkFrame(frame_ligne2, fg_color="transparent")
        frame_immat.pack(side="left", expand=True, fill="x")

        ctk.CTkLabel(frame_immat, text="Immatriculation").pack(anchor="w")

        self.entry_immat = ctk.CTkEntry(frame_immat)
        self.entry_immat.pack(fill="x")

        # =========================
        # MODE DE PAIEMENT
        # =========================

        frame_paiement = ctk.CTkFrame(
            self.droite,
            fg_color="transparent"
        )

        frame_paiement.pack(fill="x", padx=20, pady=(15,0))

        ctk.CTkLabel(
            frame_paiement,
            text="Mode de paiement"
        ).pack(side="left")

        self.combo_paiement = ctk.CTkComboBox(
            frame_paiement,
            values=[
                "Espèces",
                "Carte bancaire",
                "Virement"
            ],
            width=220
        )

        self.combo_paiement.set("Carte bancaire")

        self.combo_paiement.pack(
            side="left",
            padx=20
)

        # =========================
        # PRESTATIONS
        # =========================

        ctk.CTkLabel(
           self.droite,
           text="Prestations réalisées",
           font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=20, pady=(20,5))

        self.txt_prestations = ctk.CTkTextbox(
            self.droite,
            height=250
        )

        self.txt_prestations.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0,15)
        )

        # =========================
        # TOTAL
        # =========================

        frame_total = ctk.CTkFrame(
            self.droite,
            fg_color="#222222",
            corner_radius=12
        )

        frame_total.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            frame_total,
            text="Montant",
            font=("Arial",16)
        ).grid(row=0,column=0,padx=20,pady=(15,5),sticky="w")

        self.entry_ht = ctk.CTkEntry(
            frame_total,
            width=180
        )
        self.entry_ht.grid(row=0,column=1,padx=20,pady=(15,5))
        self.entry_ht.bind("<KeyRelease>",self.calculer_total)

        ctk.CTkLabel(
            frame_total,
            text="TVA (0%)",
            font=("Arial",16)
        ).grid(row=1,column=0,padx=20,pady=5,sticky="w")

        self.entry_tva = ctk.CTkEntry(
            frame_total,
            width=180
        )

        self.entry_tva.insert(0,"0,00 €")

        self.entry_tva.grid(
            row=1,
            column=1,
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            frame_total,
            text="TOTAL À PAYER",
            font=("Arial",20,"bold"),
            text_color="#D72638"
        ).grid(row=2,column=0,padx=20,pady=(10,15),sticky="w")

        self.entry_ttc = ctk.CTkEntry(
            frame_total,
            width=180,
            font=("Arial",18,"bold")
        )

        self.entry_ttc.grid(
            row=2,
            column=1,
            padx=20,
            pady=(10,15)
        )


        # =========================
        # BOUTONS
        # =========================

        frame_boutons = ctk.CTkFrame(
            self.droite,
            fg_color="transparent"
        )

        frame_boutons.pack(
            fill="x",
            padx=20,
            pady=(20,20)
        )

        ctk.CTkButton(
        frame_boutons,
        text="➕ Nouvelle",
        width=170,
        height=45,
        corner_radius=10,
        fg_color="#1565C0",
        hover_color="#0D47A1",
        font=("Arial",15,"bold"),
        command=self.nouvelle_facture
    ).pack(side="left", padx=5)

        # Enregistrer
        ctk.CTkButton(
            frame_boutons,
            text="💾 Enregistrer",
            width=170,
            height=45,
            corner_radius=10,
            fg_color="#D72638",
            hover_color="#B71C2C",
            font=("Arial",15,"bold"),
            command=self.enregistrer_facture
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_boutons,
            text="🗑 Supprimer",
            width=170,
            height=45,
            corner_radius=10,
            fg_color="#8B0000",
            hover_color="#5A0000",
            font=("Arial",15,"bold"),
            command=self.supprimer_facture
        ).pack(side="left", padx=5)

        # Imprimer
        ctk.CTkButton(
            frame_boutons,
            text="🖨️ Imprimer",
            width=170,
            height=45,
            corner_radius=10,
            fg_color="#3A3A3A",
            hover_color="#4B4B4B",
            font=("Arial",15,"bold"),
            command=self.imprimer_facture
        ).pack(side="left", padx=5)

        # Fermer
        ctk.CTkButton(
            frame_boutons,
            text="❌ Fermer",
            width=170,
            height=45,
            corner_radius=10,
            fg_color="#222222",
            hover_color="#111111",
            font=("Arial",15,"bold"),
            command=self.fenetre.destroy
        ).pack(side="right", padx=5)

    def generer_numero_facture(self):
        annee = datetime.now().year

        self.cur.execute(
            "SELECT COUNT(*) FROM factures"
        )

        numero = self.cur.fetchone()[0] + 1

        return f"F{annee}-{numero:04d}"

    def calculer_total(self, event=None):
        try:
            montant = self.entry_ht.get().replace(",", ".")

            if montant == "":
                montant = 0

            montant = float(montant)

            self.entry_tva.delete(0, "end")
            self.entry_tva.insert(0, "0,00 €")

            self.entry_ttc.delete(0, "end")
            self.entry_ttc.insert(0, f"{montant:.2f} €")

        except:
            pass

    def rechercher_factures(self, event=None):

        texte = self.entry_recherche.get().lower()

        for ligne in self.table_factures.get_children():
            self.table_factures.delete(ligne)

        self.cur.execute("""
            SELECT numero, client, date, montant_ttc
            FROM factures
            ORDER BY id DESC
        """)

        for facture in self.cur.fetchall():

            numero = str(facture[0]).lower()
            client = str(facture[1]).lower()

            if texte in numero or texte in client:
                self.table_factures.insert("", "end", values=facture)
 
    def charger_factures(self):
        # Vider la liste
        for ligne in self.table_factures.get_children():
            self.table_factures.delete(ligne)

        # Charger les factures
        self.cur.execute("""
            SELECT numero, client, date, montant_ttc
            FROM factures
            ORDER BY id DESC
        """)

        for facture in self.cur.fetchall():
            self.table_factures.insert("", "end", values=facture)


    def ouvrir_facture(self, event):

        selection = self.table_factures.focus()

        if not selection:
            return

        numero = self.table_factures.item(selection)["values"][0]

        self.cur.execute("""
            SELECT numero,
                   date,
                   client,
                   immatriculation,
                   montant_ht,
                   tva,
                   montant_ttc,
                   travaux,
                   mode_paiement,
                   statut
            FROM factures
            WHERE numero=?
        """, (numero,))

        facture = self.cur.fetchone()

        if facture is None:
            return

        self.entry_numero_facture.delete(0, "end")
        self.entry_numero_facture.insert(0, facture[0])

        self.entry_date.delete(0, "end")
        self.entry_date.insert(0, facture[1])

        self.entry_client.delete(0, "end")
        self.entry_client.insert(0, facture[2])

        self.entry_immat.delete(0, "end")
        self.entry_immat.insert(0, facture[3])

        self.entry_ht.delete(0, "end")
        self.entry_ht.insert(0, facture[4])

        self.entry_tva.delete(0, "end")
        self.entry_tva.insert(0, facture[5])

        self.entry_ttc.delete(0, "end")
        self.entry_ttc.insert(0, facture[6])

        self.txt_prestations.delete("1.0", "end")
        self.txt_prestations.insert("1.0", facture[7])

        self.combo_paiement.set(facture[8])

        self.combo_statut.set(facture[9])
        self.changer_statut(facture[9])

    def supprimer_facture(self):

        selection = self.table_factures.focus()

        if not selection:
            messagebox.showwarning(
                "Attention",
                "Sélectionnez une facture."
            )
            return

        numero = self.table_factures.item(selection)["values"][0]

        if not messagebox.askyesno(
            "Confirmation",
            f"Supprimer la facture {numero} ?"
        ):
            return

        self.cur.execute(
            "DELETE FROM factures WHERE numero=?",
            (numero,)
        )

        self.conn.commit()

        self.charger_factures()

        self.nouvelle_facture()

        messagebox.showinfo(
            "Succès",
            "Facture supprimée."
        )

    def nouvelle_facture(self):

        self.entry_numero_facture.delete(0, "end")
        self.entry_numero_facture.insert(
            0,
            self.generer_numero_facture()
        )

        self.entry_numero_or.delete(0, "end")

        self.entry_date.delete(0, "end")
        self.entry_date.insert(
            0,
            datetime.now().strftime("%d/%m/%Y")
        )

        self.entry_client.delete(0, "end")
        self.entry_immat.delete(0, "end")

        self.txt_prestations.delete("1.0", "end")

        self.entry_ht.delete(0, "end")

        self.entry_tva.delete(0, "end")
        self.entry_tva.insert(0, "0,00 €")

        self.entry_ttc.delete(0, "end")

        self.lbl_statut.configure(
            text="🟠 EN ATTENTE",
            fg_color="#E67E22"
        )

    def changer_statut(self, choix):

        if choix == "Payée":
            self.lbl_statut.configure(
                text="🟢 PAYÉE",
                fg_color="#2E8B57"
            )

        elif choix == "Impayée":
            self.lbl_statut.configure(
                text="🔴 IMPAYÉE",
                fg_color="#C62828"
            )

        else:
            self.lbl_statut.configure(
                text="🟠 EN ATTENTE",
                fg_color="#E67E22"
            )

    def enregistrer_facture(self):
        try:

            self.cur.execute(
                "SELECT id FROM factures WHERE numero=?",
                (self.entry_numero_facture.get(),)
            )

            existe = self.cur.fetchone()

            if existe:

                self.cur.execute("""
                    UPDATE factures
                    SET
                        date=?,
                        client=?,
                        immatriculation=?,
                        montant_ht=?,
                        tva=?,
                        montant_ttc=?,
                        travaux=?,
                        mode_paiement=?,
                        statut=?
                    WHERE numero=?
                """,(
                    self.entry_date.get(),
                    self.entry_client.get(),
                    self.entry_immat.get(),
                    float(self.entry_ht.get().replace(",", ".") or 0),
                    0,
                    float(
                        self.entry_ttc.get()
                        .replace("€","")
                        .replace(",",".")
                        .strip() or 0
                    ),
                    self.txt_prestations.get("1.0","end").strip(),
                    self.self.combo_paiement.get(),
                    self.self.combo_statut.get(),
                    self.entry_numero_facture.get()
                ))

            else:

                self.cur.execute("""
                    INSERT INTO factures(
                        numero,
                        date,
                        client,
                        immatriculation,
                        montant_ht,
                        tva,
                        montant_ttc,
                        travaux,
                        mode_paiement,
                        statut
                    )
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (
                    self.entry_numero_facture.get(),
                    self.entry_date.get(),
                    self.entry_client.get(),
                    self.entry_immat.get(),
                    float(self.entry_ht.get().replace(",", ".") or 0),
                    0,
                    float(
                        self.entry_ttc.get()
                        .replace("€","")
                        .replace(",",".")
                        .strip() or 0
                    ),
                    self.txt_prestations.get("1.0","end").strip(),
                    self.combo_paiement.get(),
                    self.combo_statut.get()
                ))

            self.conn.commit()
            self.charger_factures()

            messagebox.showinfo(
                "Succès",
                "Facture enregistrée."
            )

        except Exception as e:
            messagebox.showerror(
                "Erreur",
                str(e)
            )


    def imprimer_facture(self):

        pdf = SimpleDocTemplate(
            f"Facture_{self.entry_numero_facture.get()}.pdf",
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        elements = []

        titre = Table([
            ["FMS MANAGER"],
            [f"FACTURE N° {self.entry_numero_facture.get()}"],
            [f"Date : {self.entry_date.get()}"]
        ])

        titre.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D72638")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("FONTSIZE",(0,0),(-1,-1),18),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("BOTTOMPADDING",(0,0),(-1,0),12),
            ("GRID",(0,0),(-1,-1),0.5,colors.grey)
        ]))

        elements.append(titre)

        client = Table([
        ["CLIENT"],
        [f"Nom : {self.entry_client.get()}"],
        [f"Immatriculation : {self.entry_immat.get()}"],
        [f"Mode de paiement : {self.combo_paiement.get()}"],
        [f"Statut : {self.combo_statut.get()}"]
        ])

        client.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#333333")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BOTTOMPADDING",(0,0),(-1,0),8),
            ("TOPPADDING",(0,0),(-1,-1),6),
            ("LEFTPADDING",(0,0),(-1,-1),10)
            ]))

        elements.append(client)

        prestations = Table([
            ["PRESTATIONS RÉALISÉES"],
            [self.txt_prestations.get("1.0", "end").strip()]
        ])

        prestations.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D72638")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BOTTOMPADDING",(0,0),(-1,0),8),
            ("TOPPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(-1,-1),10)
        ]))

        elements.append(prestations)

        total = Table([
            ["Montant HT", f"{self.entry_ht.get()} €"],
            ["TVA (0%)", "0,00 €"],
            ["TOTAL À PAYER", f"{self.entry_ttc.get()}"]
        ])

        total.setStyle(TableStyle([
            ("BACKGROUND",(0,2),(1,2),colors.HexColor("#D72638")),
            ("TEXTCOLOR",(0,2),(1,2),colors.white),
            ("GRID",(0,0),(-1,-1),0.5,colors.black),
            ("ALIGN",(1,0),(1,-1),"RIGHT"),
            ("BOTTOMPADDING",(0,0),(-1,-1),8)
        ]))

        elements.append(total)

        from reportlab.platypus import Spacer
        elements.append(Spacer(1,1*cm))

        signature = Table([
            ["Signature du client", "Signature FMS Manager"],
            ["", ""]
        ], colWidths=[8*cm, 8*cm])

        signature.setStyle(TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BOTTOMPADDING",(0,1),(-1,1),35),
            ("ALIGN",(0,0),(-1,-1),"CENTER")
        ]))

        elements.append(signature)

        elements.append(Spacer(1, 1*cm))

        footer = Table([
            ["Merci pour votre confiance !"],
            ["FMS Manager - Mécanique à domicile"]
        ])

        footer.setStyle(TableStyle([
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("TEXTCOLOR",(0,0),(-1,-1),colors.grey),
            ("FONTSIZE",(0,0),(-1,-1),11)
        ]))

        elements.append(footer)




        pdf.build(elements)        

        messagebox.showinfo(
            "PDF",
            "Facture PDF créée avec succès."
        )

    def charger_depuis_or(
        self,
        numero_or,
        client,
        immatriculation,
        travaux,
        temps
    ):
        # Numéro OR
        self.entry_numero_or.delete(0, "end")
        self.entry_numero_or.insert(0, numero_or)

        # Client
        self.entry_client.delete(0, "end")
        self.entry_client.insert(0, client)

        # Immatriculation
        self.entry_immat.delete(0, "end")
        self.entry_immat.insert(0, immatriculation)


def ouvrir(parent):
    return(
    FactureManager(parent))