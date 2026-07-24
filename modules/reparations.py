import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox
from modules import factures

class ReparationManager:

    def __init__(self, parent):
        self.parent = parent
        self.conn = sqlite3.connect("fms_manager.db")
        self.cur = self.conn.cursor()

        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("Ordres de réparation")
        self.fenetre.geometry("1400x800")

        # Cadre gauche
        frame_gauche = ctk.CTkFrame(self.fenetre)
        frame_gauche.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(frame_gauche, text="N° OR").pack(anchor="w", padx=10, pady=(10,0))
        self.entry_numero = ctk.CTkEntry(frame_gauche, width=250)
        self.entry_numero.pack(padx=10, pady=5)

        ctk.CTkLabel(frame_gauche, text="Date").pack(anchor="w", padx=10)
        self.entry_date = ctk.CTkEntry(frame_gauche, width=250)
        self.entry_date.pack(padx=10, pady=5)

        ctk.CTkLabel(frame_gauche, text="Client").pack(anchor="w", padx=10)
        self.entry_client = ctk.CTkEntry(frame_gauche, width=250)
        self.entry_client.pack(padx=10, pady=5)

        ctk.CTkLabel(frame_gauche, text="Immatriculation").pack(anchor="w", padx=10)
        self.entry_immat = ctk.CTkEntry(frame_gauche, width=250)
        self.entry_immat.pack(padx=10, pady=5)

        ctk.CTkLabel(frame_gauche, text="Kilométrage").pack(anchor="w", padx=10)
        self.entry_km = ctk.CTkEntry(frame_gauche, width=250)
        self.entry_km.pack(padx=10, pady=5)

        ctk.CTkLabel(frame_gauche, text="Ordres de réparation").pack(
        anchor="w",
        padx=10,
        pady=(10, 0)
        )

        self.table_or = ttk.Treeview(
        frame_gauche,
        columns=("numero", "date", "client"),
        show="headings",
        height=8
        )

        self.table_or.heading("numero", text="N° OR")
        self.table_or.heading("date", text="Date")
        self.table_or.heading("client", text="Client")

        self.table_or.pack(fill="both", expand=True, padx=10, pady=5)



        # Cadre droit
        frame_droit = ctk.CTkFrame(self.fenetre)
        frame_droit.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame_droit, text="Travaux prévus").pack(anchor="w", padx=10, pady=(10,0))
        self.txt_travaux_prevus = ctk.CTkTextbox(frame_droit, height=120)
        self.txt_travaux_prevus.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame_droit, text="Travaux effectués").pack(anchor="w", padx=10)
        self.txt_travaux_effectues = ctk.CTkTextbox(frame_droit, height=120)
        self.txt_travaux_effectues.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame_droit, text="Temps de main-d'œuvre (heures)").pack(anchor="w", padx=10)
        self.entry_temps = ctk.CTkEntry(frame_droit)
        self.entry_temps.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame_droit, text="Observations").pack(anchor="w", padx=10)
        self.txt_observations = ctk.CTkTextbox(frame_droit, height=100)
        self.txt_observations.pack(fill="both", expand=True, padx=10, pady=5)

        frame_boutons = ctk.CTkFrame(frame_droit)
        frame_boutons.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            frame_boutons,
            text="💾 Enregistrer",
            command=self.enregistrer
         ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_boutons,
            text="🧾 Créer la facture",
            command=self.creer_facture
         ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_boutons,
            text="❌ Fermer",
            command=self.fenetre.destroy
         ).pack(side="right", padx=5)


        self.fenetre.lift()
        self.fenetre.focus_force()
        self.fenetre.grab_set()
        self.charger_ordres()
        self.table_or.bind("<<TreeviewSelect>>",self.selectionner_or)

    def generer_numero_or(self):
        self.cur.execute("SELECT COUNT(*) FROM reparations")
        nb = self.cur.fetchone()[0] + 1
        return f"OR-2026-{nb:04d}"

    def charger_devis(self, numero, client, immatriculation, prestations):
        self.entry_numero.delete(0, "end")
        self.entry_numero.insert(0,
        self.generer_numero_or())

        self.entry_client.delete(0, "end")
        self.entry_client.insert(0, client)

        self.entry_immat.delete(0, "end")
        self.entry_immat.insert(0, immatriculation)

        self.txt_travaux_prevus.delete("1.0", "end")

        for ligne in prestations:
            designation = ligne[1]
            quantite = ligne[2]
            self.txt_travaux_prevus.insert(
                "end",
                f"- {designation} x{quantite}\n"
            )

    def charger_ordres(self):

        for item in self.table_or.get_children():
            self.table_or.delete(item)

        self.cur.execute("""
            SELECT numero, date, client
            FROM ordres_reparation
            ORDER BY id DESC
        """)

        for ligne in self.cur.fetchall():
            self.table_or.insert("", "end", values=ligne)

    def selectionner_or(self, event):

        selection = self.table_or.selection()

        if not selection:
            return

        numero = self.table_or.item(selection[0])["values"][0]

        self.cur.execute("""
            SELECT *
            FROM ordres_reparation
            WHERE numero=?
        """, (numero,))

        or_data = self.cur.fetchone()

        if not or_data:
            return
        self.entry_numero.delete(0, "end")
        self.entry_numero.insert(0, or_data[1])

        self.entry_date.delete(0, "end")
        self.entry_date.insert(0, or_data[2])

        self.entry_client.delete(0, "end")
        self.entry_client.insert(0, or_data[3])

        self.entry_immat.delete(0, "end")
        self.entry_immat.insert(0, or_data[4])

        self.entry_km.delete(0, "end")
        self.entry_km.insert(0, or_data[5])

        self.txt_travaux_prevus.delete("1.0", "end")
        self.txt_travaux_prevus.insert("1.0", or_data[6])

        self.txt_travaux_effectues.delete("1.0", "end")
        self.txt_travaux_effectues.insert("1.0", or_data[7])

        self.entry_temps.delete(0, "end")
        self.entry_temps.insert(0, or_data[8])

        self.txt_observations.delete("1.0", "end")
        self.txt_observations.insert("1.0", or_data[9])




    def enregistrer(self):

        self.cur.execute("""
            INSERT INTO ordres_reparation(
                numero,
                date,
                client,
                immatriculation,
                kilometrage,
                travaux_prevus,
                travaux_effectues,
                temps_mo,
                observations,
                statut
            )
            VALUES(?,?,?,?,?,?,?,?,?,?)
        """, (
            self.entry_numero.get(),
            self.entry_date.get(),
            self.entry_client.get(),
            self.entry_immat.get(),
            self.entry_km.get(),
            self.txt_travaux_prevus.get("1.0", "end").strip(),
            self.txt_travaux_effectues.get("1.0", "end").strip(),
            self.entry_temps.get(),
            self.txt_observations.get("1.0", "end").strip(),
            "En attente"
        ))

        self.conn.commit()
        self.charger_ordres()

        messagebox.showinfo(
            "Succès",
            "Ordre de réparation enregistré."
        )

    def creer_facture(self):
        facture = factures.ouvrir(self.parent)
        print("facture=",facture)
        if facture is None:
            print("ERREUR/ ouvrir()retourne None")
            return

        facture.charger_depuis_or(
            self.entry_numero.get(),
            self.entry_client.get(),
            self.entry_immat.get(),
            self.txt_travaux_effectues.get("1.0", "end"),
            self.entry_temps.get()
        )


def ouvrir(parent):
    return(
    ReparationManager(parent))
