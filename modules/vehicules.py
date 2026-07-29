import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox
from PIL import Image


class VehiculeManager:
    def __init__(self, parent, id_client=None):
        self.parent = parent
        self.id_client=id_client

        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        self.creer_table()

        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("FMS Manager - Vehicules")
        self.fenetre.geometry("1600x900")
        self.fenetre.configure(fg_color="#464242")

        self.creer_interface()
        self.charger_clients()
        self.charger_vehicules()


    def creer_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicules(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            immatriculation TEXT,
            marque TEXT,
            modele TEXT,
            motorisation TEXT,
            annee TEXT,
            carburant TEXT,
            kilometrage TEXT,
            vin TEXT,
            couleur TEXT,
            mise_en_circulation TEXT,
            contrôle_technique TEXT,
            observations TEXT
        )
        """)
        self.conn.commit()

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
            self.logo = ctk.CTkImage(
                light_image=Image.open("assets/logo_fms.png"),
                dark_image=Image.open("assets/logo_fms.png"),
                size=(150, 120)
            )

            ctk.CTkLabel(
                header,
                image=self.logo,
                text=""
            ).pack(side="left", padx=20)

        except Exception:
            pass

        titre = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )
        titre.pack(side="left", padx=10)

        ctk.CTkLabel(
            titre,
            text="FMS Manager",
            font=("Arial", 24, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            titre,
            text="Gestion des vehicules",
            text_color="#D80606",
            font=("Arial", 15)
        ).pack(anchor="w")

        # ==========================
        # CONTENU
        # ==========================

        self.contenu = ctk.CTkFrame(
            self.fenetre,
            fg_color="transparent"
        )
        self.contenu.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        # ==========================
        # COLONNE GAUCHE
        # ==========================

        self.gauche = ctk.CTkFrame(
            self.contenu,
            width=500,
            fg_color="#0A0606",
            corner_radius=10
        )
        self.gauche.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )
        self.gauche.pack_propagate(False)

        ctk.CTkLabel(
            self.gauche,
            text="Vehicules",
            font=("Arial", 22, "bold")
        ).pack(pady=(15, 10))

        self.recherche = ctk.CTkEntry(
            self.gauche,
            placeholder_text="Rechercher un vehicule..."
        )
        self.recherche.pack(fill="x", padx=15, pady=(0, 10))
        self.recherche.bind("<KeyRelease>",
        self.rechercher_vehicule)

        self.liste = ttk.Treeview(
            self.gauche,
            columns=("Immatriculation", "Vehicule"),
            show="headings",
            height=22
        )

        self.liste.heading("Immatriculation", text="Immatriculation")
        self.liste.heading("Vehicule", text="Vehicule")

        self.liste.column("Immatriculation", width=240, anchor="w")
        self.liste.column("Vehicule", width=130, anchor="center")

        self.liste.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.liste.bind(
            "<<TreeviewSelect>>",
            self.selection_vehicule
        )

        # ==========================
        # COLONNE DROITE
        # ==========================

        self.droite = ctk.CTkFrame(
            self.contenu,
            fg_color="#0A0606",
            corner_radius=10
        )
        self.droite.pack(
            side="left",
            fill="both",
            expand=True
        )

        cadre_infos = ctk.CTkFrame(
            self.droite,
            fg_color="transparent"
        )
        cadre_infos.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            cadre_infos,
            text="Informations vehicule",
            font=("Arial", 22, "bold")
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 20))

        self.labels = {}
        self.entrees = {}

        ctk.CTkLabel(
            cadre_infos,
            text="Client"
        ).grid(row=1, column=0,
               padx=10, pady=5, sticky="w")

        self.client_combo=ctk.CTkComboBox(
            cadre_infos,
            width=260,
            values=[]
        )
        self.client_combo.grid(
            row=1,
            column=1,
            padx=10,
            pady=5,
            sticky="ew"
        )

        #Sélection automatique du client
        if self.id_client:
            self.cur.execute("SELECT nom, prenom FROM clients WHERE id=?",
                             (self.id_client,))
            client=self.cur.fetchone()
            if client:
                self.client_combo.set(f"{client[0]}{client[1]}")

        champs = [
            ("Immatriculation", 1, 2),
            ("Marque",2, 0),
            ("Modèle", 2, 2),
            ("Motorisation", 3, 0),
            ("Année", 3, 2),
            ("Carburant", 4, 0),
            ("Kilométrage", 4, 2),
            ("vin", 5, 0),
            ("Couleur", 5, 2),
            ("Mise en circulation", 6, 0),
            ("Controle technique", 6, 2),
        ]

        for texte, ligne, colonne in champs:

            label=ctk.CTkLabel(
                cadre_infos,
                text=texte
            )
            label.grid(
                row=ligne,
                column=colonne,
                padx=10,
                pady=5,
                sticky="w"
            )
            self.labels[texte]=label

            entree = ctk.CTkEntry(
                cadre_infos,
                width=260
            )

            entree.grid(
                row=ligne,
                column=colonne + 1,
                padx=10,
                pady=5,
                sticky="ew"
            )

            self.entrees[texte] = entree

        cadre_infos.grid_columnconfigure(1, weight=1)
        cadre_infos.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            self.droite,
            text="Observations",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=20)

        self.observations = ctk.CTkTextbox(
            self.droite,
            height=90
        )

        self.observations.pack(
            fill="x",
            padx=20,
            pady=(5, 8)
        )

        # ==========================
        # BOUTONS
        # ==========================

        cadre_boutons = ctk.CTkFrame(
            self.droite,
            fg_color="transparent"
        )
        cadre_boutons.pack(
            fill="x",
            padx=20,
            pady=(10,5)
        )

        self.btn_nouveau = ctk.CTkButton(
            cadre_boutons,
            text="➕ Nouveau",
            width=100,
            height=40,
            corner_radius=10,
            font=("Arial",15, "bold"),
            command=self.nouveau_vehicule,
            fg_color="#1976D2",
            hover_color="#1565C0",
            text_color="white"
        )

        self.btn_nouveau.grid(row=0, column=0, padx=5, pady=5)

        self.btn_enregistrer = ctk.CTkButton(
            cadre_boutons,
            text="💾 Enregistrer",
            width=100,
            height=40,
            corner_radius=10,
            font=("Arial",15, "bold"),
            command=self.enregistrer_vehicule,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            text_color="white"
        )
        self.btn_enregistrer.grid(row=0, column=1, padx=5, pady=5)

        self.btn_modifier = ctk.CTkButton(
            cadre_boutons,
            text="✏ Modifier",
            width=100,
            height=40,
            corner_radius=10,
            font=("Arial",15, "bold"),
            command=self.modifier_vehicule,
            fg_color="#F57C00",
            hover_color= "#E65100",
            text_color="white"
        )
        self.btn_modifier.grid(row=0, column=2, padx=5, pady=5)

        self.btn_supprimer = ctk.CTkButton(
            cadre_boutons,
            text="🗑 Supprimer",
            width=100,
            height=40,
            corner_radius=10,
            font=("Arial",15, "bold"),
            command=self.supprimer_vehicule,
            fg_color="#C62828",
            hover_color="#B71C1C",
            text_color="white"
        )
        self.btn_supprimer.grid(row=0, column=3, padx=5, pady=5)

        self.btn_actualiser = ctk.CTkButton(
            cadre_boutons,
            text="🔄 Actualiser",
            width=100,
            height=40,
            corner_radius=10,
            font=("Arial",15, "bold"),
            command=self.charger_vehicules,
            fg_color="#455A64",
            hover_color="#37474F",
            text_color="white"
        )
        self.btn_actualiser.grid(row=0, column=4, padx=5, pady=5)

        self.frame_modules=ctk.CTkFrame(
            self.droite,
            fg_color="transparent"
        )
        self.frame_modules.pack(pady=(5, 10))

        self.btn_vehicules = ctk.CTkButton(
            self.frame_modules,
            text="🚗 Vehicules",
            fg_color="#D80606",
            hover_color="#B00505",
            width=130,
            height=40,
            corner_radius=10,
            text_color="white"
        )
        self.btn_vehicules.pack(side="left", padx=5)


        self.btn_devis = ctk.CTkButton(
            self.frame_modules,
            text="📄 Devis",
            fg_color="#D80606",
            hover_color="#B00505",
            width=130,
            height=40,
            corner_radius=10,
            text_color="white"
        )
        self.btn_devis.pack(side="left", padx=5)


        self.btn_reparation = ctk.CTkButton(
            self.frame_modules,
            text="🔧 Réparation",
            fg_color="#D80606",
            hover_color="#B00505",
            width=130,
            height=40,
            corner_radius=10,
            text_color="white"
        )
        self.btn_reparation.pack(side="left", padx=5)


        self.btn_factures = ctk.CTkButton(
            self.frame_modules,
            text="🧾 Factures",
            fg_color="#D80606",
            hover_color="#B00505",
            width=130,
            height=40,
            corner_radius=10,
            text_color="white"
        )
        self.btn_factures.pack(side="left", padx=5)

    def charger_clients(self):

        self.cur.execute("""
            SELECT id, nom, prenom
            FROM clients
            ORDER BY nom
        """)

        self.clients = {}

        liste = []

        for id_client, nom, prenom in self.cur.fetchall():

            texte = f"{nom} {prenom}"

            self.clients[texte] = id_client

            liste.append(texte)

        self.client_combo.configure(values=liste)

        if self.id_client:
            for nom_client, id_c in self.clients.items():
                if id_c == self.id_client:
                 self.client_combo.set(nom_client)
                 break
        elif liste:
            self.client_combo.set(liste[0])


    # ==========================
    # NOUVEAU VEHICULE
    # ==========================
    def nouveau_vehicule(self):
        for entree in self.entrees.values():
            entree.delete(0, "end")

        if self.liste.selection():
            self.liste.selection_remove(self.liste.selection())

    # ==========================
    # ENREGISTRER VEHICULE
    # ==========================
    def enregistrer_vehicule(self):

        client = self.client_combo.get()
        client_id = self.clients.get(client)

        if client_id is None:
            messagebox.showwarning(
                "Attention",
                "Sélectionnez un client."
            )
            return

        immatriculation = self.entrees["Immatriculation"].get().strip()

        if not immatriculation:
            messagebox.showwarning(
                "Attention",
                "L'immatriculation est obligatoire."
    )
            return


        self.cur.execute("""
            INSERT INTO vehicules(
                client_id,
                immatriculation,
                marque,
                modele,
                motorisation,
                carburant,
                annee,
                kilometrage,
                vin,
                observations
            )
            VALUES(?,?,?,?,?,?,?,?,?,?)
        """, (
            client_id,
            self.entrees["Immatriculation"].get(),
            self.entrees["Marque"].get(),
            self.entrees["Modèle"].get(),
            self.entrees["Motorisation"].get(),
            self.entrees["Carburant"].get(),
            self.entrees["Année"].get(),
            self.entrees["Kilométrage"].get(),
            self.entrees["vin"].get(),
            self.observations.get("1.0", "end").strip()
        ))

        self.conn.commit()

        self.nouveau_vehicule()
        self.charger_vehicules()

        messagebox.showinfo(
            "FMS Manager",
            "Vehicule enregistré avec succès."
        )

    # ==========================
    # CHARGER LES VEHICULES
    # ==========================
    def charger_vehicules(self):

        for item in self.liste.get_children():
            self.liste.delete(item)

        if self.id_client:

            self.cur.execute("""
                SELECT
                    id,
                    immatriculation,
                    marque,
                    modele
                FROM vehicules
                WHERE client_id=?
                ORDER BY immatriculation
            """, (self.id_client,))

        else:

            self.cur.execute("""
                SELECT
                    id,
                    immatriculation,
                    marque,
                    modele
                FROM vehicules
                ORDER BY immatriculation
            """)


        for id_vehicule, immatriculation, marque, modele in self.cur.fetchall():

            self.liste.insert(
                "",
                "end",
                iid=str(id_vehicule),
                values=(
                    immatriculation,
                    f"{marque} {modele}"
                )
            )

    # ==========================
    # SÉLECTION VEHICULE
    # ==========================
    def selection_vehicule(self, event=None):

        selection = self.liste.selection()

        if not selection:
            return

        id_vehicule = selection[0]

        self.cur.execute("""
            SELECT
                client_id,
                immatriculation,
                marque,
                modele,
                motorisation,
                carburant,
                annee,
                kilometrage,
                vin,
                observations
            FROM vehicules
            WHERE id=?
        """, (id_vehicule,))

        vehicule = self.cur.fetchone()

        if vehicule is None:
            return

        champs = [
            "Immatriculation",
            "Marque",
            "Modèle",
            "Motorisation",
            "Carburant",
            "Année",
            "Kilométrage",
            "vin"
        ]

        for i, champ in enumerate(champs, start=1):
            self.entrees[champ].delete(0, "end")
            self.entrees[champ].insert(0, vehicule[i] if vehicule[i] else "")

        client_id=vehicule[0]
        for nom_client, id_c in self.clients.items():
         if id_c == client_id:
            self.client_combo.set(nom_client)
            break

        self.observations.delete("1.0", "end")
        self.observations.insert("1.0", vehicule[8] if vehicule[8] else "")

    # ==========================
    # MODIFIER VEHICULE
    # ==========================
    def modifier_vehicule(self):

        selection = self.liste.selection()

        if not selection:
            messagebox.showwarning(
                "Attention",
                "Sélectionnez un vehicule."
            )
            return

        id_vehicule = selection[0]

        self.cur.execute("""
            UPDATE vehicules
            SET
                immatriculation=?,
                marque=?,
                modele=?,
                motorisation=?,
                carburant=?,
                annee=?,
                kilometrage=?,
                vin=?,
                observations=?
            WHERE id=?
        """, (
            self.entrees["Immatriculation"].get(),
            self.entrees["Marque"].get(),
            self.entrees["Modèle"].get(),
            self.entrees["Motorisation"].get(),
            self.entrees["Carburant"].get(),
            self.entrees["Année"].get(),
            self.entrees["Kilométrage"].get(),
            self.entrees["vin"].get(),
            self.observations.get("1.0", "end").strip(),
            id_vehicule
        ))

        self.conn.commit()

        self.charger_vehicules()

        messagebox.showinfo(
            "FMS Manager",
            "Vehicule modifié avec succès."
        )
    # ==========================
    # SUPPRIMER VEHICULE
    # ==========================
    def supprimer_vehicule(self):

        selection = self.liste.selection()

        if not selection:
            messagebox.showwarning(
                "Attention",
                "Sélectionnez un vehicule."
            )
            return

        if not messagebox.askyesno(
            "Confirmation",
            "Supprimer ce vehicule ?"
        ):
            return

        id_vehicule = selection[0]

        self.cur.execute(
            "DELETE FROM vehicules WHERE id=?",
            (id_vehicule,)
        )

        self.conn.commit()

        self.nouveau_vehicule()
        self.charger_vehicules()

        messagebox.showinfo(
            "FMS Manager",
            "Vehicule supprimé."
        )

    # ==========================
    # RECHERCHER VEHICULE
    # ==========================
    def rechercher_vehicule(self, event=None):

        texte = self.recherche.get().strip()

        for item in self.liste.get_children():
            self.liste.delete(item)

        self.cur.execute("""
            SELECT
                id,
                immatriculation,
                marque,
                modele
            FROM vehicules
            WHERE
                immatriculation LIKE ?
                OR marque LIKE ?
                OR modele LIKE ?
            ORDER BY immatriculation
        """, (
            f"%{texte}%",
            f"%{texte}%",
            f"%{texte}%"
        ))

        for id_vehicule, immatriculation, marque, modele in self.cur.fetchall():

            self.liste.insert(
                "",
                "end",
                iid=str(id_vehicule),
                values=(
                    immatriculation,
                    f"{marque} {modele}"
                )
            )
