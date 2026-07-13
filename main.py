import customtkinter as ctk
import database

# Modules
from modules import clients
from modules import vehicules
from modules import devis_v2 as devis
# -----------------------------
# Configuration
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

database.creer_base()

# -----------------------------
# Fenêtre principale
# -----------------------------
app = ctk.CTk()
app.title("FMS Manager V2")
app.geometry("1400x800")
app.minsize(1200, 700)

# -----------------------------
# Couleurs
# -----------------------------
COULEUR_MENU = "#161616"
COULEUR_FOND = "#202020"
COULEUR_BOUTON = "#d10000"
COULEUR_HOVER = "#990000"

# -----------------------------
# Menu gauche
# -----------------------------
menu = ctk.CTkFrame(
    app,
    width=250,
    fg_color=COULEUR_MENU,
    corner_radius=0
)

menu.pack(side="left", fill="y")

logo = ctk.CTkLabel(
    menu,
    text="FMS\nMANAGER",
    font=("Arial", 30, "bold"),
    text_color="#ff3030"
)

logo.pack(pady=30)

# -----------------------------
# Zone principale
# -----------------------------
contenu = ctk.CTkFrame(
    app,
    fg_color=COULEUR_FOND
)

contenu.pack(side="right", fill="both", expand=True)

titre = ctk.CTkLabel(
    contenu,
    text="Tableau de bord",
    font=("Arial", 34, "bold")
)

titre.pack(pady=25)

description = ctk.CTkLabel(
    contenu,
    text="Bienvenue dans FMS Manager V2",
    font=("Arial", 18)
)

description.pack()

# -----------------------------
# Fonctions
# -----------------------------
def ouvrir_clients():
    clients.ouvrir(app)

def ouvrir_vehicules():
    vehicules.ouvrir(app)

def ouvrir_devis():
    devis.ouvrir(app)
# -----------------------------
# Boutons du menu
# -----------------------------
boutons = [
    ("🏠 Tableau de bord", None),
    ("👤 Clients", ouvrir_clients),
    ("🚗 Véhicules", ouvrir_vehicules),
    ("📝 Devis", ouvrir_devis),
    ("💶 Factures", None),
    ("🔧 Réparations", None),
    ("📦 Stock", None),
    ("📅 Agenda", None),
    ("⚙ Paramètres", None)
]

for texte, commande in boutons:

    bouton = ctk.CTkButton(
        menu,
        text=texte,
        width=200,
        height=40,
        fg_color=COULEUR_BOUTON,
        hover_color=COULEUR_HOVER,
        command=commande
    )

    bouton.pack(pady=8)

app.mainloop()
