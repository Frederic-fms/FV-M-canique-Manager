import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox
from PIL import Image


class ClientManager:

    def __init__(self, parent):

        self.parent = parent

        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        self.creer_table()

        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("FMS Manager - Clients")
        self.fenetre.geometry("1600x900")
        self.fenetre.configure(fg_color="#464242")

        self.creer_interface()

        self.charger_clients()

    def creer_table(self):

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            type_client TEXT,
            nom TEXT,
            prenom TEXT,
            SIRET TEXT,
            telephone TEXT,
            telephone2 TEXT,
            email TEXT,
            adresse TEXT,
            code_postal TEXT,
            ville TEXT,
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
            text="Gestion des clients",
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
            width=420,
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
            text="Clients",
            font=("Arial", 22, "bold")
        ).pack(pady=(15, 10))

        self.recherche = ctk.CTkEntry(
            self.gauche,
            placeholder_text="Rechercher un client..."
        )
        self.recherche.pack(fill="x", padx=15, pady=(0, 10))
        self.recherche.bind("<KeyRelease>",
        self.rechercher_client)

        self.liste = ttk.Treeview(
            self.gauche,
            columns=("Nom", "Téléphone"),
            show="headings",
            height=22
        )

        self.liste.heading("Nom", text="Client")
        self.liste.heading("Téléphone", text="Téléphone")

        self.liste.column("Nom", width=240, anchor="w")
        self.liste.column("Téléphone", width=130, anchor="center")

        self.liste.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.liste.bind(
            "<<TreeviewSelect>>",
            self.selection_client
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
            text="Informations client",
            font=("Arial", 22, "bold")
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 20))

        # ==========================
        # TYPE DE CLIENT
        # ==========================

        ctk.CTkLabel(
            cadre_infos,
            text="Type de client"
        ).grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.type_client = ctk.StringVar(value="Particulier")

        ctk.CTkRadioButton(
            cadre_infos,
            text="Particulier",
            command=self.changer_type_client,
            variable=self.type_client,
            value="Particulier"
        ).grid(row=1, column=1, sticky="w")

        ctk.CTkRadioButton(
            cadre_infos,
            text="Professionnel",
            command=self.changer_type_client,
            variable=self.type_client,
            value="Professionnel"
        ).grid(row=1, column=2, sticky="w")

        self.labels = {}
        self.entrees = {}

        champs = [
            ("Nom", 2, 0),
            ("Prénom", 2, 2),
            ("SIRET",3, 0),
            ("Téléphone", 4, 0),
            ("Téléphone 2", 4, 2),
            ("Email", 5, 0),
            ("Adresse", 5, 2),
            ("Code postal", 6, 0),
            ("Ville", 6, 2),
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
            height=110
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
            pady=(10,10)
        )

        self.btn_nouveau = ctk.CTkButton(
            cadre_boutons,
            text="➕ Nouveau",
            width=100,
            height=40,
            corner_radius=10,
            font=("Arial",15, "bold"),
            command=self.nouveau_client,
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
            command=self.enregistrer,
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
            command=self.modifier_client,
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
            command=self.supprimer_client,
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
            command=self.charger_clients,
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
            text="🚗 Véhicules",
            fg_color="#D80606",
            hover_color="#B00505",
            width=130,
            height=40,
            corner_radius=10,
            text_color="white",
            command=self.voir_vehicules
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
            text_color="white",
            command=self.voir_vehicules
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

    def changer_type_client(self):
        print("Fonction appelée")
        print(self.type_client.get())
        if self.type_client.get() == "Professionnel":
            self.labels["Nom"].configure(text="Entreprise")
            self.labels["Prénom"].configure(text="Contact")
            self.labels["SIRET"].grid()
            self.entrees["SIRET"].grid()
        else:
            self.labels["Nom"].configure(text="Nom")
            self.labels["Prénom"].configure(text="Prénom")
            self.labels["SIRET"].grid_remove()
            self.entrees["SIRET"].grid_remove()

            print(self.type_client.get())


    # ==========================
    # NOUVEAU CLIENT
    # ==========================

    def nouveau_client(self):

        for entree in self.entrees.values():
            entree.delete(0, "end")

        self.observations.delete("1.0", "end")

        if self.liste.selection():
            self.liste.selection_remove(self.liste.selection())


    # ==========================
    # ENREGISTRER
    # ==========================

    def enregistrer(self):

        nom = self.entrees["Nom"].get().strip()
        type_client= self.type_client.get()

        print(type_client)

        if not nom:
            messagebox.showwarning(
                "Attention",
                "Le nom du client est obligatoire."
            )
            return

        self.cur.execute("""
            INSERT INTO clients(
                type_client,
                nom,
                prenom,
                SIRET,
                telephone,
                telephone2,
                email,
                adresse,
                code_postal,
                ville,
                observations
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """, (
            type_client,
            self.entrees["Nom"].get(),
            self.entrees["Prénom"].get(),
            self.entrees["SIRET"].get(),
            self.entrees["Téléphone"].get(),
            self.entrees["Téléphone 2"].get(),
            self.entrees["Email"].get(),
            self.entrees["Adresse"].get(),
            self.entrees["Code postal"].get(),
            self.entrees["Ville"].get(),
            self.observations.get("1.0", "end").strip()

        ))

        self.conn.commit()

        self.nouveau_client()

        self.charger_clients()

        messagebox.showinfo(
            "FMS Manager",
            "Client enregistré avec succès."
        )

    # ==========================
    # CHARGER LES CLIENTS
    # ==========================

    def charger_clients(self):

        for item in self.liste.get_children():
            self.liste.delete(item)

        self.cur.execute("""
            SELECT id, nom, prenom, telephone
            FROM clients
            ORDER BY nom, prenom
        """)

        for id_client, nom, prenom, telephone in self.cur.fetchall():

            self.liste.insert(
                "",
                "end",
                iid=str(id_client),
                values=(
                    f"{nom} {prenom}".strip(),
                    telephone
                )
            )


    # ==========================
    # SÉLECTION CLIENT
    # ==========================

    def selection_client(self, event=None):

        selection = self.liste.selection()

        if not selection:
            return

        id_client = selection[0]

        self.cur.execute("""
            SELECT
                type_client,
                nom,
                prenom,
                SIRET,
                telephone,
                telephone2,
                email,
                adresse,
                code_postal,
                ville,
                observations
            FROM clients
            WHERE id=?
        """, (id_client,))

        client = self.cur.fetchone()

        if client is None:
            return

        self.type_client.set(client[0])
        self.changer_type_client()

        champs = [
            "Nom",
            "Prénom",
            "SIRET",
            "Téléphone",
            "Téléphone 2",
            "Email",
            "Adresse",
            "Code postal",
            "Ville"
        ]

        for i, champ in enumerate(champs, start=1):
            self.entrees[champ].delete(0, "end")
            self.entrees[champ].insert(0, client[i] if client[i] else "")

        self.observations.delete("1.0", "end")
        self.observations.insert("1.0", client[10] if client[10] else "")

    def voir_vehicules(self):

        selection = self.liste.selection()

        if not selection:
            messagebox.showwarning(
                "Attention",
                "Sélectionnez un client."
            )
            return

        id_client = selection[0]

        from modules.vehicules import VehiculeManager

        VehiculeManager(self.parent, id_client=id_client)
  

    # ==========================
    # MODIFIER CLIENT
    # ==========================

    def modifier_client(self):

        selection = self.liste.selection()

        if not selection:
            messagebox.showwarning(
                "Attention",
                "Sélectionnez un client."
            )
            return

        id_client = selection[0]

        self.cur.execute("""
            UPDATE clients
            SET
                type_client=?,
                nom=?,
                prenom=?,
                SIRET=?,
                telephone=?,
                telephone2=?,
                email=?,
                adresse=?,
                code_postal=?,
                ville=?,
                observations=?
            WHERE id=?
        """, (
            self.type_client.get(),
            self.entrees["Nom"].get(),
            self.entrees["Prénom"].get(),
            self.entrees["SIRET"].get(),
            self.entrees["Téléphone"].get(),
            self.entrees["Téléphone 2"].get(),
            self.entrees["Email"].get(),
            self.entrees["Adresse"].get(),
            self.entrees["Code postal"].get(),
            self.entrees["Ville"].get(),
            self.observations.get("1.0", "end").strip(),
            id_client
        ))

        self.conn.commit()

        self.charger_clients()

        messagebox.showinfo(
            "FMS Manager",
            "Client modifié."
        )


    # ==========================
    # SUPPRIMER CLIENT
    # ==========================

    def supprimer_client(self):

        selection = self.liste.selection()

        if not selection:
            messagebox.showwarning(
                "Attention",
                "Sélectionnez un client."
            )
            return

        if not messagebox.askyesno(
            "Confirmation",
            "Supprimer ce client ?"
        ):
            return

        id_client = selection[0]

        self.cur.execute(
            "DELETE FROM clients WHERE id=?",
            (id_client,)
        )

        self.conn.commit()

        self.nouveau_client()
        self.charger_clients()

        messagebox.showinfo(
            "FMS Manager",
            "Client supprimé."
        )

    # ==========================
    # RECHERCHER CLIENT
    # ==========================

    def rechercher_client(self, event=None):

        recherche = self.recherche.get().lower()

        for item in self.liste.get_children():
            self.liste.delete(item)

        self.cur.execute("""
            SELECT id, nom, prenom, telephone
            FROM clients
            ORDER BY nom, prenom
        """)

        for id_client, nom, prenom, telephone in self.cur.fetchall():

            nom_complet = f"{nom} {prenom}".strip()

            if (
                recherche in nom_complet.lower()
                or recherche in (telephone or "").lower()
            ):

                self.liste.insert(
                    "",
                    "end",
                    iid=str(id_client),
                    values=(nom_complet, telephone)
                )
