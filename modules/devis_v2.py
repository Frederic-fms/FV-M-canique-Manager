import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from datetime import datetime
from tkinter import ttk
from modules import pdf_manager
from modules import reparations
import os
import win32api


class DevisManager:

    def __init__(self, parent):

        self.parent = parent

        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()
        self.verifier_base()

        self.lignes=[]
        self.devis_selectionne=None
        self.creer_fenetre()
        
    def verifier_base(self):

     self.cur.execute("""
        CREATE TABLE IF NOT EXISTS devis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            date TEXT,
            client TEXT,
            immatriculation TEXT,
            montant_ht REAL,
            tva REAL,
            montant_ttc REAL
        )
     """)

     self.cur.execute("""
        CREATE TABLE IF NOT EXISTS lignes_devis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            devis_id INTEGER,
            reference TEXT,
            designation TEXT,
            quantite REAL,
            prix_ht REAL,
            tva REAL,
            total REAL
        )
     """)

     self.conn.commit()

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
        dernier = int(resultat[0].split("-")[-1]) + 1
     else:
        dernier = 1

     return f"DV-{annee}-{dernier:04d}"


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
            width=620
        )
        self.gauche.pack(
            side="left",
            fill="both",
            expand=False,
            padx=(0, 10)
        )
        
        self.droite = ctk.CTkFrame(self.principal)

        self.droite.pack(
            side="right",
            fill="both",
            expand=True,
            padx=10
        )
        self.creer_liste_devis()
        self.creer_formulaire()

    def creer_liste_devis(self):

     from tkinter import ttk

     colonnes = (
        "numero",
        "date",
        "client",
        "immatriculation",
        "ttc"
     )

     self.table = ttk.Treeview(
        self.droite,
        columns=colonnes,
        show="headings",
        height=25
     )

     self.table.heading("numero", text="N°")
     self.table.heading("date", text="Date")
     self.table.heading("client", text="Client")
     self.table.heading("immatriculation", text="Immatriculation")
     self.table.heading("ttc", text="TTC")

     self.table.column("numero", width=130)
     self.table.column("date", width=90)
     self.table.column("client", width=220)
     self.table.column("immatriculation", width=120)
     self.table.column("ttc", width=90)

     self.table.pack(fill="x", expand=False, padx=10, pady=10)
     self.table.bind("<<TreeviewSelect>>",
     self.selectionner_devis)

     self.charger_devis()

    def charger_devis(self):

     for item in self.table.get_children():
        self.table.delete(item)

     self.cur.execute("""
        SELECT
            id,
            numero,
            date,
            client,
            immatriculation,
            montant_ttc
         FROM devis
         ORDER BY id DESC
         """)
     resultats=self.cur.fetchall()
     print(resultats)
     for devis in resultats:
        self.table.insert(
            "",
            "end",
            iid=devis[0],
            values=devis[1:]
        )

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
           width=420,
           command=self.client_selectionne)

        elif champ == "Immatriculation":
          entree = ctk.CTkEntry(
          self.gauche,
          width=420
         )

        else:
          entree = ctk.CTkEntry(
          self.gauche,
          width=420
         )


        entree.pack(padx=10, pady=(0, 8))

        self.entrees[champ] = entree

     self.entrees["Date"].insert(
        0,
        datetime.now().strftime("%d/%m/%Y")
    )
     self.entrees["Numéro devis"].insert(0,
     self.generer_numero_devis())
     self.entrees["Numéro devis"].configure(state="readonly")
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

     self.table_prestations = ttk.Treeview(
     self.gauche,
     columns=("ref", "designation", "qte", "pu", "tva", "total"),
     show="headings",
     height=15
     )

     self.table_prestations.heading("ref", text="Référence")
     self.table_prestations.heading("designation", text="Désignation")
     self.table_prestations.heading("qte", text="Qté")
     self.table_prestations.heading("pu", text="PU HT")
     self.table_prestations.heading("tva", text="TVA")
     self.table_prestations.heading("total", text="Total")

     self.table_prestations.column("ref", width=90)
     self.table_prestations.column("designation", width=180)
     self.table_prestations.column("qte", width=50)
     self.table_prestations.column("pu", width=70)
     self.table_prestations.column("tva", width=60)
     self.table_prestations.column("total", width=80)

     self.table_prestations.pack(fill="both", expand=True,
                                  padx=10, pady=5)
     self.bouton_ajouter = ctk.CTkButton(
     self.gauche,
     text="+ Ajouter une ligne",
     command=self.ajouter_ligne,
     fg_color="#1f6aa5"
     )
     self.bouton_ajouter.pack(anchor="w", padx=10, pady=5)



     self.frame_lignes = ctk.CTkFrame(self.gauche, fg_color="transparent")
     self.frame_lignes.pack(fill="both", expand=True,
                             padx=10, pady=(10,5))

     self.ent_ref = ctk.CTkEntry(self.frame_lignes, width=120)
     self.ent_ref.pack(side="left", padx=2)

     self.ent_designation = ctk.CTkEntry(self.frame_lignes, width=260)
     self.ent_designation.pack(side="left", padx=2)

     self.ent_qte = ctk.CTkEntry(self.frame_lignes, width=60)
     self.ent_qte.pack(side="left", padx=2)

     self.ent_pu = ctk.CTkEntry(self.frame_lignes, width=80)
     self.ent_pu.pack(side="left", padx=2)

     self.ent_tva = ctk.CTkEntry(self.frame_lignes, width=60)
     self.ent_tva.pack(side="left", padx=2)

     self.ent_total = ctk.CTkEntry(self.frame_lignes, width=90)
     self.ent_total.pack(side="left", padx=2)

     self.ent_qte.bind("<KeyRelease>",lambda e:
     self.calculer_totaux())
     self.ent_pu.bind("<KeyRelease>",lambda e:
     self.calculer_totaux())
     self.ent_tva.bind("<KeyRelease>",lambda e:
     self.calculer_totaux())

     self.table_prestations.bind("<Double-1>",
     self.modifier_ligne)
     self.table_prestations.insert(
        "",
        "end",
        values=("", "", "", "",
                "", "",)
     )
     
     frame_boutons = ctk.CTkFrame(self.gauche, fg_color="transparent")
     frame_boutons.pack(pady=15)

     frame_boutons1=ctk.CTkFrame(frame_boutons,
                  fg_color="transparent")
     frame_boutons1.pack(pady=(0,5))

     frame_boutons2=ctk.CTkFrame(frame_boutons,
                  fg_color="transparent")
     frame_boutons2.pack()

     ctk.CTkButton(
      frame_boutons1,
        text="💾 Enregistrer",
        width=90,
        fg_color="green",
        command=self.enregistrer_devis
     ).grid(row=0, column=0, padx=5)

     ctk.CTkButton(
        frame_boutons1,
        text="✏️ Modifier",
        width=90,
        fg_color="#f39c12",
        command=self.modifier_devis
     ).grid(row=0, column=1, padx=5)

     ctk.CTkButton(
        frame_boutons1,
        text="🗑️ Supprimer",
        width=90,
        fg_color="#d63031",
        command=self.supprimer_devis
     ).grid(row=0, column=2, padx=5)

     ctk.CTkButton(
        frame_boutons1,
        text="🖨️ Imprimer",
        width=90,
        command=self.imprimer_devis
     ).grid(row=0, column=3, padx=5)

     ctk.CTkButton(
        frame_boutons2,
        text="📄 PDF",
        width=90,
        command=self.exporter_pdf
     ).grid(row=0, column=4, padx=5)

     ctk.CTkButton(
        frame_boutons2,
        text="👁️ Aperçu",
        command=self.apercu_devis
     ).grid(row=0, column=5, padx=5)

     ctk.CTkButton(
        frame_boutons2,
        text="📧 E-mail",
        width=90,
        command=self.envoyer_email
     ).grid(row=0, column=6, padx=5)

     ctk.CTkButton(
        frame_boutons2,
        text="🔧 Créer OR",
        command=self.creer_ordre_reparation
     ).grid(row=0, column=7, padx=5)

     


     
    def ajouter_ligne(self):

        self.table_prestations.insert(
            "",
            "end",
            values=(
                self.ent_ref.get(),
                self.ent_designation.get(),
                self.ent_qte.get(),
                self.ent_pu.get(),
                self.ent_tva.get(),
                self.ent_total.get()
            )
        )

        self.ent_ref.delete(0, "end")
        self.ent_designation.delete(0, "end")
        self.ent_qte.delete(0, "end")
        self.ent_pu.delete(0, "end")
        self.ent_tva.delete(0, "end")
        self.ent_total.delete(0, "end")
        self.calculer_total_devis()

    def modifier_ligne(self, event):
        item = self.table_prestations.focus()

        if not item:
            return

        valeurs = self.table_prestations.item(item, "values")

        self.ent_ref.delete(0, "end")
        self.ent_designation.delete(0, "end")
        self.ent_qte.delete(0, "end")
        self.ent_pu.delete(0, "end")
        self.ent_tva.delete(0, "end")
        self.ent_total.delete(0, "end")

        self.ent_ref.insert(0, valeurs[0])
        self.ent_designation.insert(0, valeurs[1])
        self.ent_qte.insert(0, valeurs[2])
        self.ent_pu.insert(0, valeurs[3])
        self.ent_tva.insert(0, valeurs[4])
        self.ent_total.insert(0, valeurs[5])

        self.table_prestations.delete(item)

    def calculer_totaux(self):
        try:
            qte = float(self.ent_qte.get())
            pu = float(self.ent_pu.get())
            tva = float(self.ent_tva.get())

            total = qte * pu * (1 + tva / 100)

            self.ent_total.configure(state="normal")
            self.ent_total.delete(0, "end")
            self.ent_total.insert(0, f"{total:.2f}")
            self.ent_total.configure(state="readonly")

        except ValueError:
            self.ent_total.configure(state="normal")
            self.ent_total.delete(0, "end")
            self.ent_total.configure(state="readonly")

    def calculer_total_devis(self):
        montant_ht = 0
        tva = 0
        montant_ttc = 0

        for item in self.table_prestations.get_children():
            valeurs = self.table_prestations.item(item, "values")

            try:
                montant_ht += float(valeurs[3]) * float(valeurs[2])
                tva += (float(valeurs[3]) * float(valeurs[2])) * float(valeurs[4]) / 100
                montant_ttc += float(valeurs[5])
            except:
                pass

        for champ, valeur in [
            ("Montant HT", montant_ht),
            ("TVA", tva),
            ("Montant TTC", montant_ttc),
        ]:
            self.entrees[champ].configure(state="normal")
            self.entrees[champ].delete(0, "end")
            self.entrees[champ].insert(0, f"{valeur:.2f}")
            self.entrees[champ].configure(state="readonly")
    
    
    def enregistrer_devis(self):

        # Création ou modification du devis
        if self.devis_selectionne is None:

            self.cur.execute("""
                INSERT INTO devis (
                    numero,
                    date,
                    client,
                    immatriculation,
                    montant_ht,
                    tva,
                    montant_ttc
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.entrees["Numéro devis"].get(),
                self.entrees["Date"].get(),
                self.entrees["Client"].get(),
                self.entrees["Immatriculation"].get(),
                float(self.entrees["Montant HT"].get() or 0),
                float(self.entrees["TVA"].get() or 0),
                float(self.entrees["Montant TTC"].get() or 0)
            ))

            devis_id = self.cur.lastrowid

        else:

            devis_id = self.devis_selectionne

            self.cur.execute("""
                UPDATE devis
                SET
                    numero=?,
                    date=?,
                    client=?,
                    immatriculation=?,
                    montant_ht=?,
                    tva=?,
                    montant_ttc=?
                WHERE id=?
            """, (
                self.entrees["Numéro devis"].get(),
                self.entrees["Date"].get(),
                self.entrees["Client"].get(),
                self.entrees["Immatriculation"].get(),
                float(self.entrees["Montant HT"].get() or 0),
                float(self.entrees["TVA"].get() or 0),
                float(self.entrees["Montant TTC"].get() or 0),
                devis_id
            ))

            # Supprime les anciennes prestations
            self.cur.execute(
                "DELETE FROM lignes_devis WHERE devis_id=?",
                (devis_id,)
            )

        # Enregistre les prestations du Treeview
        for item in self.table_prestations.get_children():

            valeurs = self.table_prestations.item(item, "values")

            self.cur.execute("""
                INSERT INTO lignes_devis (
                    devis_id,
                    reference,
                    designation,
                    quantite,
                    prix_ht,
                    tva,
                    total
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                devis_id,
                valeurs[0],
                valeurs[1],
                float(valeurs[2] or 0),
                float(valeurs[3] or 0),
                float(valeurs[4] or 0),
                float(valeurs[5] or 0)
            ))
        print("ID devis :", devis_id)
        self.cur.execute(
           "SELECT * FROM lignes_devis WHERE devis_id=?",
           (devis_id,)
        )
        print(self.cur.fetchall())
        self.conn.commit()

        self.devis_selectionne = None

        self.charger_devis()

        messagebox.showinfo(
            "Succès",
            "Devis enregistré avec succès."
        )

    def modifier_devis(self):
        from tkinter import messagebox

        print("MODIFIER :", self.devis_selectionne)

        if self.devis_selectionne is None:
            messagebox.showwarning(
                "Modification",
                "Sélectionnez un devis dans la liste."
            )
            return

        self.enregistrer_devis()


     

    def supprimer_devis(self):
        from tkinter import messagebox

        if self.devis_selectionne is None:
            messagebox.showwarning(
                "Suppression",
                "Sélectionnez un devis à supprimer."
            )
            return

        if not messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment supprimer ce devis ?"
        ):
            return

        # Supprime les prestations
        self.cur.execute(
            "DELETE FROM lignes_devis WHERE devis_id=?",
            (self.devis_selectionne,)
        )

        # Supprime le devis
        self.cur.execute(
            "DELETE FROM devis WHERE id=?",
            (self.devis_selectionne,)
    )

        self.conn.commit()

        self.devis_selectionne = None

        self.charger_devis()

        # Vide le tableau des prestations
        for item in self.table_prestations.get_children():
            self.table_prestations.delete(item)

        messagebox.showinfo(
            "Succès",
            "Le devis a été supprimé."
        )
        
    def imprimer_devis(self):
        import win32api
        from tkinter import messagebox

        fichier=self.exporter_pdf()
        if not fichier:
           return
        try:
           win32api.ShellExecute(
              0,
              "print",
              fichier,
              None,
              ".",
              0
           )
        except Exception:
           messagebox.showwarning(
              "Impression"
              "Aucune imprimante n'est disponible.\n\n"
              "Le devis PDF a bien été créé. \n"
              "Connectez une imprimante pour pouvoir l'imprimer."
           )

    def apercu_devis(self):
       import os
       fichier=self.exporter_pdf(False)
       if fichier:
          os.startfile(fichier)    

    def envoyer_email(self):
        import os
        import webbrowser
        from tkinter import messagebox

        fichier = self.exporter_pdf()

        if not fichier:
            return

        if not hasattr(self, "email") or self.email == "":
            messagebox.showwarning(
                "E-mail",
                "Aucune adresse e-mail n'est enregistrée pour ce client."
            )
            return

        sujet = "Votre devis"

        webbrowser.open(
            f"mailto:{self.email}?subject={sujet}"
        )

        messagebox.showinfo(
            "E-mail",
            "Votre logiciel de messagerie va s'ouvrir.\n"
            "Joignez simplement le PDF :\n\n"
            + fichier
        )
    def exporter_pdf(self, afficher_message=True):

        from tkinter import messagebox
        from modules import pdf_manager

        if self.devis_selectionne is None:
            
            messagebox.showwarning(
                "PDF",
                "Sélectionnez un devis."
            )
            return

        prestations = []

        for item in self.table_prestations.get_children():
            prestations.append(
                self.table_prestations.item(item)["values"]
            )
        print("Client :", repr(self.entrees["Client"].get()))
        print("Immat :", repr(self.entrees["Immatriculation"].get()))
        print("Client sélectionné :", self.entrees["Client"].get())

        self.cur.execute("""
        SELECT
            c.prenom,
            c.telephone,
            c.email,
            c.adresse,
            c.code_postal,
            c.ville,
            v.marque,
            v.modele,
            v.kilometrage
        FROM clients c
        LEFT JOIN vehicules v
        ON c.id = v.client_id
        WHERE c.nom = ?
        AND v.immatriculation = ?
        """,
        (
            self.entrees["Client"].get(),
            self.entrees["Immatriculation"].get()
        ))

        infos = self.cur.fetchone()
        print("INFOS =", infos)

        if infos is None:
            raise Exception("Aucun résultat trouvé par la requête SQL")

        (prenom,
        telephone,
        email,
        adresse,
        code_postal,
        ville,
        marque,
        modele,
        kilometrage) = infos


        fichier = pdf_manager.creer_pdf(
        numero=self.entrees["Numéro devis"].get(),
        date=self.entrees["Date"].get(),
        client=self.entrees["Client"].get(),
        immatriculation=self.entrees["Immatriculation"].get(),
        prenom=prenom,
        telephone=telephone,
        email=email,
        adresse=adresse,
        code_postal=code_postal,
        ville=ville,
        marque=marque,
        modele=modele,
        kilometrage=kilometrage,
        prestations=prestations,
        montant_ht=float(self.entrees["Montant HT"].get()),
        tva=float(self.entrees["TVA"].get()),
        montant_ttc=float(self.entrees["Montant TTC"].get())
        )
        if afficher_message:
            messagebox.showinfo(
            "PDF",
            f"PDF créé avec succès.\n\n{fichier}"
        )
        return fichier

    def creer_ordre_reparation(self):

        if not hasattr(self, "devis_selectionne"):
            return

        prestations=[]
        for item in self.table_prestations.get_children():
           prestations.append(self.table_prestations.item(item)
           ["values"])

        
        rep = reparations.ouvrir(self.parent)

        rep.charger_devis(
            self.entrees["Numéro devis"].get(),
            self.entrees["Client"].get(),
            self.entrees["Immatriculation"].get(),
            prestations
        )
 
    def vider_lignes(self):
       for item in self.table_prestations.get_children():
        self.table_prestations.delete(item)

    def selectionner_devis(self, event):

     selection = self.table.selection()

     if not selection:
        return

     self.devis_selectionne = int(selection[0])

     self.cur.execute("""
        SELECT
            numero,
            date,
            client,
            immatriculation,
            montant_ht,
            tva,
            montant_ttc
        FROM devis
        WHERE id=?
     """, (self.devis_selectionne,))

     devis = self.cur.fetchone()
     self.cur.execute("""
     SELECT email FROM clients WHERE nom=?""", (devis[2],))
     resultat=self.cur.fetchone()
     if resultat:
        self.email=resultat[0]
     else:
        self.email=""

     if not devis:
        return

     champs = [
        "Numéro devis",
        "Date",
        "Client",
        "Immatriculation",
        "Montant HT",
        "TVA",
        "Montant TTC"
     ]

     for i, champ in enumerate(champs):

        etat = self.entrees[champ].cget("state")

        if etat == "readonly":
            self.entrees[champ].configure(state="normal")
        if champ == "Client":
            self.entrees[champ].set(devis[i])
        else:

            self.entrees[champ].delete(0, "end")
            self.entrees[champ].insert(0, devis[i])

        if champ in (
            "Numéro devis",
            "Montant HT",
            "TVA",
            "Montant TTC"
        ):
            self.entrees[champ].configure(state="readonly")

     for item in self.table_prestations.get_children():
      self.table_prestations.delete(item)

     self.cur.execute("""
            SELECT
                reference,
                designation,
                quantite,
                prix_ht,
                tva,
                total
            FROM lignes_devis
            WHERE devis_id = ?
            ORDER BY id
        """, 
    (self.devis_selectionne,))
     lignes=self.cur.fetchall()
     print("PRESTATIONS :", lignes)
     for ligne in lignes:
      self.table_prestations.insert(
           "", "end", values=ligne
        )



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
