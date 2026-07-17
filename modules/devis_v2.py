import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from datetime import datetime


class DevisManager:

    def __init__(self, parent):

        self.parent = parent

        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        self.lignes=[]
        self.creer_fenetre()
        

    def creer_fenetre(self):

        self.fenetre = ctk.CTkToplevel(self.parent)
        self.fenetre.title("FMS Manager V2 - Gestion des devis")
        self.fenetre.geometry("1500x900")
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
            pady=15
        )

        self.gauche = ctk.CTkScrollableFrame(
            self.principal,
            width=520
        )

        self.gauche.pack(
            side="left",
            fill="both",
            padx=(0, 10)
        )

        self.droite = ctk.CTkFrame(self.principal)

        self.droite.pack(
            side="right",
            fill="both",
            expand=True
        )
        self.creer_formulaire()

    def creer_formulaire(self):

     champs = [
        "Numéro devis",
        "Date",
        "Client",
        "Immatriculation",
        "Montant HT",
        "TVA",
        "Montant TTC"
    ]

     self.entrees = {}

     for champ in champs:

        ctk.CTkLabel(
            self.gauche,
            text=champ,
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 2))

        if champ == "Client":
         self.cur.execute("SELECT nom FROM clients ORDER BY nom")
         clients = [c[0] for c in self.cur.fetchall()]
         print(clients)

         entree = ctk.CTkComboBox(
           self.gauche,
           values=clients,
           width=450,
           command=self.client_selectionne)

        elif champ == "Immatriculation":
          entree = ctk.CTkEntry(
          self.gauche,
          width=450
         )

        else:
          entree = ctk.CTkEntry(
          self.gauche,
          width=450
         )


        entree.pack(padx=10, pady=(0, 8))

        self.entrees[champ] = entree

     self.entrees["Date"].insert(
        0,
        datetime.now().strftime("%d/%m/%Y")
    )
     self.entrees["Montant HT"].configure(state="readonly")
     self.entrees["TVA"].configure(state="readonly")
     self.entrees["Montant TTC"].configure(state="readonly")

     ctk.CTkLabel(
        self.gauche,
        text="Prestations",  
        font=("Arial",16,"bold")
    ).pack(anchor="w",padx=10,pady=(20,10))  

     entete=ctk.CTkFrame(self.gauche,
            fg_color="transparent")
     entete.pack(fill="x",padx=10)
     titres=[
        ("Référence",90),
        ("Désignation",180),
        ("Qté",50),
        ("PU HT",70),
        ("TVA",60),
        ("Total",80)
     ]

     for texte,largeur in titres:
        ctk.CTkLabel(
           entete,
           text=texte,
           width=largeur
        ).pack(side="left",padx=2)

     self.frame_lignes = ctk.CTkFrame(self.gauche, fg_color="transparent")
     self.frame_lignes.pack(fill="x", padx=10, pady=5)

     ligne = ctk.CTkFrame(self.frame_lignes, fg_color="transparent")
     ligne.pack(fill="x", pady=2)

     ref = ctk.CTkEntry(ligne, width=90)
     ref.pack(side="left", padx=2)

     designation = ctk.CTkEntry(ligne, width=180)
     designation.pack(side="left", padx=2)

     qte = ctk.CTkEntry(ligne, width=50)
     qte.pack(side="left", padx=2)

     pu = ctk.CTkEntry(ligne, width=70)
     pu.pack(side="left", padx=2)

     tva = ctk.CTkEntry(ligne, width=60)
     tva.pack(side="left", padx=2)

     total = ctk.CTkEntry(ligne, width=80, state="readonly")
     total.pack(side="left", padx=2)

     self.lignes.append({
         "ref":ref,
         "designation":
     designation,
         "qte": qte,
         "pu": pu,
         "tva": tva,
         "total": total
     })
     qte.bind("<KeyRelease>",
              lambda e:
              self.calculer_totaux())
     pu.bind("<KeyRelease>",lambda e:
             self.calculer_totaux())
     
     self.bouton_ajouter=ctk.CTkButton(
        self.gauche,
        text="+ Ajouter une ligne",
        command=self.ajouter_ligne
     )
     self.bouton_ajouter.pack(anchor="w",padx=10, pady=10)
     
    def calculer_totaux(self):
        total_ht = 0

        for ligne in self.lignes:
            try:
                qte =float(ligne["qte"].get().replace(",", ".") or 0)
                pu = float(ligne["pu"].get().replace(",", ".") or 0)

                total = qte * pu

                ligne["total"].configure(state="normal")
                ligne["total"].delete(0, "end")
                ligne["total"].insert(0, f"{total:.2f}")
                ligne["total"].configure(state="readonly")

                total_ht += total

            except ValueError:
              pass

        tva = total_ht * 0.20
        ttc = total_ht + tva

        self.entrees["Montant HT"].configure(state="normal")
        self.entrees["Montant HT"].delete(0, "end")
        self.entrees["Montant HT"].insert(0, f"{total_ht:.2f}")
        self.entrees["Montant HT"].configure(state="readonly")

        self.entrees["TVA"].configure(state="normal")
        self.entrees["TVA"].delete(0, "end")
        self.entrees["TVA"].insert(0, f"{tva:.2f}")
        self.entrees["TVA"].configure(state="readonly")

        self.entrees["Montant TTC"].configure(state="normal")
        self.entrees["Montant TTC"].delete(0, "end")
        self.entrees["Montant TTC"].insert(0, f"{ttc:.2f}")
        self.entrees["Montant TTC"].configure(state="readonly")


        

    def ajouter_ligne(self):

        ligne = ctk.CTkFrame(self.frame_lignes, fg_color="transparent")
        ligne.pack(fill="x", pady=2)
        self.bouton_ajouter.pack_forget()
        self.bouton_ajouter.pack(anchor="w",padx=10,pady=10)

        ctk.CTkEntry(ligne, width=90).pack(side="left", padx=2)
        ctk.CTkEntry(ligne, width=180).pack(side="left", padx=2)
        ctk.CTkEntry(ligne, width=50).pack(side="left", padx=2)
        ctk.CTkEntry(ligne, width=70).pack(side="left", padx=2)
        ctk.CTkEntry(ligne, width=60).pack(side="left", padx=2)

        ctk.CTkEntry(
            ligne,
            width=80,
            state="readonly"
        ).pack(side="left", padx=2)

    def client_selectionne(self, client):

       self.cur.execute("""
                        SELECT v.immatriculation
            FROM vehicules v JOIN clients c ON v.client_id= c.id
        WHERE c.nom=?
        limit 1""",
        (client,)
     )

       resultat = self.cur.fetchone()

       if resultat:
        self.entrees["Immatriculation"].delete(0, "end")
        self.entrees["Immatriculation"].insert(0, resultat[0])


def ouvrir(parent):
    DevisManager(parent)
