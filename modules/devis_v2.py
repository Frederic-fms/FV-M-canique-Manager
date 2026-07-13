import customtkinter as ctk
import sqlite3

from tkinter import messagebox
from datetime import datetime

from modules import pdf_manager


class DevisManager:

    def __init__(self, parent):

        self.parent = parent

        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        self.devis_selectionne = None

        self.lignes = []

        self.creer_fenetre()

    def creer_fenetre(self):

     self.fenetre = ctk.CTkToplevel(self.parent)
     self.fenetre.title("FMS Manager V2 - Gestion des devis")
     self.fenetre.geometry("1450x850")

     self.fenetre.grab_set()

     titre = ctk.CTkLabel(
        self.fenetre,
        text="Gestion des devis",
        font=("Arial", 28, "bold")
     )

     titre.pack(pady=15)

     self.principal = ctk.CTkFrame(self.fenetre)

     self.principal.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=10
     )

     self.gauche = ctk.CTkFrame(
        self.principal,
        width=430
     )

     self.gauche.pack(
        side="left",
        fill="y",
        padx=(0,10)
     )

     self.droite = ctk.CTkFrame(
        self.principal
     )

     self.droite.pack(
        side="right",
        fill="both",
        expand=True
     )

     self.creer_formulaire()
     self.creer_liste()

    def creer_formulaire(self):

     self.entrees = {}

     champs = [
        "Numéro devis",
        "Date",
        "Client",
        "Immatriculation",
        "Montant HT",
        "TVA",
        "Montant TTC"
     ]

     for champ in champs:

        ctk.CTkLabel(
            self.gauche,
            text=champ
        ).pack(anchor="w", padx=10, pady=(8, 0))

        entree = ctk.CTkEntry(
            self.gauche,
            width=390
        )

        entree.pack(padx=10)

        self.entrees[champ] = entree

     # Date du jour
     self.entrees["Date"].insert(
        0,
        datetime.now().strftime("%d/%m/%Y")
     )

     # Ces champs seront calculés automatiquement
     self.entrees["Montant HT"].configure(state="readonly")
     self.entrees["TVA"].configure(state="readonly")
     self.entrees["Montant TTC"].configure(state="readonly")

     # ==========================
     # PRESTATIONS
     # ==========================

     ctk.CTkLabel(
        self.gauche,
        text="Prestations",
        font=("Arial", 15, "bold")
     ).pack(anchor="w", padx=10, pady=(20, 5))

     self.tableau = ctk.CTkFrame(self.gauche)
     self.tableau.pack(fill="x", padx=10)

     entetes = [
        ("Désignation", 0),
        ("Qté", 1),
        ("Prix TTC", 2),
        ("Total", 3)
     ]

     for texte, colonne in entetes:

         ctk.CTkLabel(
            self.tableau,
            text=texte,
            font=("Arial", 11, "bold")
         ).grid(
            row=0,
            column=colonne,
            padx=5,
            pady=5
         )
        # =====================================
        # Première ligne de prestation
        # =====================================

         self.designation = ctk.CTkEntry(
         self.tableau,
         width=180
         )
         self.designation.grid(row=1, column=0, padx=5, pady=5)

         self.qte = ctk.CTkEntry(
         self.tableau,
         width=50
         )
         self.qte.insert(0, "1")
         self.qte.grid(row=1, column=1, padx=5)

         self.prix = ctk.CTkEntry(
         self.tableau,
         width=80
         )
         self.prix.grid(row=1, column=2, padx=5)

         self.total = ctk.CTkLabel(
         self.tableau,
         text="0.00 €",
         width=80
         )
         self.total.grid(row=1, column=3, padx=5)
         self.qte.bind("<KeyRelease>",
         self.calculer_total)
         self.prix.bind("<KeyRelease>",
         self.calculer_total)

         self.btn_ajouter = ctk.CTkButton(
         self.gauche,
         text="➕ Ajouter une prestation",
         command=self.ajouter_ligne
         )

         self.btn_ajouter.pack(pady=10)
   
         self.btn_enregistrer = ctk.CTkButton(
         self.gauche,
         text="💾 Enregistrer",
         command=self.enregistrer
         )
         self.btn_enregistrer.pack(pady=5)

         self.btn_pdf = ctk.CTkButton(
         self.gauche,
         text="📄 Générer le PDF",
         command=self.creer_pdf
)
         self.btn_pdf.pack(pady=5)

    def enregistrer(self):
     import sqlite3

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
        self.entrees["Numéro devis"].get(),
        self.entrees["Date"].get(),
        self.entrees["Client"].get(),
        self.entrees["Immatriculation"].get(),
        float(self.entrees["Montant HT"].get().replace(",", ".")),
        float(self.entrees["TVA"].get().replace(",", ".")),
        float(self.entrees["Montant TTC"].get().replace(",", ".")),

        self.designation.get()
     ))

     conn.commit()
     conn.close()

     from tkinter import messagebox
     messagebox.showinfo(
        "FMS Manager",
        "Le devis à été enregistré avec succès."
     )

    def calculer_total(self, event=None):

     try:
         qte = float(self.qte.get().replace(",", "."))
     except ValueError:
         qte = 0

     try:
         prix = float(self.prix.get().replace(",", "."))
     except ValueError:
         prix = 0

     total = qte * prix

     self.total.configure(text=f"{total:.2f} €")

     # Auto-entrepreneur
     ht = total
     tva = 0
     ttc = total

     for champ, valeur in [
        ("Montant HT", ht),
        ("TVA", tva),
        ("Montant TTC", ttc)
     ]:
        self.entrees[champ].configure(state="normal")
        self.entrees[champ].delete(0, "end")
        self.entrees[champ].insert(0, f"{valeur:.2f}")
        self.entrees[champ].configure(state="readonly")

    def enregistrer(self):
       print("Enregistrement du devis...")
       numero = self.entrees["Numéro devis"].get()
       date = self.entrees["Date"].get()
       client = self.entrees["Client"].get()
       immatriculation = self.entrees["Immatriculation"].get()

       travaux = ""

       for ligne in self.lignes:
        designation = ligne["designation"].get()
       qte = ligne["qte"].get()
       prix = ligne["prix"].get()

       if designation.strip():
        travaux += f"{designation} | Qté:{qte} | Prix:{prix} €\n"


       montant_ht = self.entrees["Montant HT"].get()
       tva = self.entrees["TVA"].get()
       montant_ttc = self.entrees["Montant TTC"].get()

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
           numero,
           date,
           client,
           immatriculation,
           montant_ht,
           tva,
           montant_ttc,
           travaux
         ))

       conn.commit()
       conn.close()
       print("Devis enregistré avec succès.")

    def ajouter_ligne(self):

     ligne = len(self.lignes) + 2

     designation = ctk.CTkEntry(
         self.tableau,
         width=180
     )
     designation.grid(row=ligne, column=0, padx=5, pady=2)

     qte = ctk.CTkEntry(
         self.tableau,
         width=50
     )
     qte.insert(0, "1")
     qte.grid(row=ligne, column=1)

     prix = ctk.CTkEntry(
         self.tableau,
         width=80
     )
     prix.grid(row=ligne, column=2)

     total = ctk.CTkLabel(
         self.tableau,
         text="0.00 €",
         width=80
     )
     total.grid(row=ligne, column=3)

     self.lignes.append({
         "designation": designation,
         "qte": qte,
         "prix": prix,
         "total": total
     })

     qte.bind("<KeyRelease>", self.calculer_total)
     prix.bind("<KeyRelease>", self.calculer_total)

    def creer_liste(self):

     ctk.CTkLabel(
         self.droite,
         text="Liste des devis",
         font=("Arial", 18, "bold")
     ).pack(pady=10)

     self.liste = ctk.CTkTextbox(
         self.droite,
         width=850,
         height=650
     )

     self.liste.pack(
         fill="both",
         expand=True,
         padx=10,
         pady=10
     )

     self.charger_liste()

    def charger_liste(self):

     self.liste.delete("1.0", "end")

     self.cur.execute("""
        SELECT
            numero,
            date,
            client,
            montant_ttc
        FROM devis
        ORDER BY id DESC
     """)

     devis = self.cur.fetchall()

     if not devis:

        self.liste.insert(
            "end",
            "Aucun devis enregistré."
        )

        return

     for numero, date, client, montant in devis:

        self.liste.insert(
            "end",
            f"{numero} | {date} | {client} | {montant:.2f} €\n"
        )
def ouvrir(parent):
   fenetre=ctk.CTkToplevel(parent)
   DevisManager(fenetre)        
         


