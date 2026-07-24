from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from datetime import datetime, timedelta

def creer_pdf(
    numero,
    date,
    client,
    immatriculation,
    prenom,
    telephone,
    email,
    adresse,
    code_postal,
    ville,
    marque,
    modele,
    kilometrage,
    prestations,
    montant_ht,
    tva,
    montant_ttc
):

    dossier = "PDF"

    if not os.path.exists(dossier):
        os.makedirs(dossier)

    fichier = os.path.join(
        dossier,
        f"Devis_{numero}.pdf"
    )

    pdf = canvas.Canvas(
        fichier,
        pagesize=A4
    )

    largeur, hauteur = A4

    # =====================================
    # DATE DE VALIDITÉ
    # =====================================

    date_devis = datetime.strptime(date, "%d/%m/%Y")
    date_validite = date_devis + timedelta(days=30)

    validite = date_validite.strftime("%d/%m/%Y")

    # =====================================
    # LOGO
    # =====================================

    logo = ImageReader("assets/logo_fms.png")

    pdf.drawImage(
        logo,
        40,
        hauteur - 120,
        width=170,
        height=85,
        mask="auto"
    )

    # =====================================
    # TITRE
    # =====================================

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(
        largeur / 2,
        hauteur - 45,
        "DEVIS"
    )

    pdf.setFont("Helvetica", 11)

    pdf.drawCentredString(
        largeur / 2,
        hauteur - 65,
        f"N° {numero}"
    )

    pdf.drawCentredString(
        largeur / 2,
        hauteur - 82,
        f"Date : {date}"
    )

    pdf.drawCentredString(
        largeur / 2,
        hauteur - 99,
        f"Validité : {validite}"
    )
    # =====================================
    # ENTREPRISE
    # =====================================

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(360, hauteur - 40, "FRED.MECA.SERVICES")

    pdf.setFont("Helvetica", 9)

    pdf.drawString(360, hauteur - 58, "85 rue Paul Vaillant Couturier")
    pdf.drawString(360, hauteur - 72, "62540 Marles-les-Mines")
    pdf.drawString(360, hauteur - 86, "06 99 97 31 79")
    pdf.drawString(360, hauteur - 100, "fred.meca.services62@gmail.com")
    pdf.drawString(360, hauteur - 114, "TVA non applicable - art. 293 B du CGI")

    # Ligne de séparation
    pdf.line(40, hauteur - 135, 555, hauteur - 135)
    # =====================================
    # CLIENT
    # =====================================

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, hauteur - 180, "CLIENT")

    pdf.setFont("Helvetica", 10)

    pdf.drawString(50, hauteur - 200, f"Nom : {client} {prenom}")
    pdf.drawString(50, hauteur - 220, f"Adresse : {adresse}")
    pdf.drawString(50, hauteur - 240, f"{code_postal} {ville}")
    pdf.drawString(50, hauteur - 260, f"Téléphone : {telephone}")
    pdf.drawString(50, hauteur - 280, f"E-mail : {email}")

    pdf.drawString(300, hauteur - 200, f"Immatriculation : {immatriculation}")
    pdf.drawString(300, hauteur - 220, f"Marque : {marque}")
    pdf.drawString(300, hauteur - 240, f"Modèle : {modele}")
    pdf.drawString(300, hauteur - 260, f"Kilométrage : {kilometrage} km")


    # =====================================
    # TABLEAU DES PRESTATIONS
    # =====================================

    y = hauteur - 340

    pdf.setFont("Helvetica-Bold", 10)

    pdf.rect(40, y, 515, 20)

    pdf.drawString(50, y + 6, "Réf.")
    pdf.drawString(120, y + 6, "Désignation")
    pdf.drawCentredString(335, y + 6, "Qté")
    pdf.drawCentredString(410, y + 6, "PU HT")
    pdf.drawCentredString(480, y + 6, "TVA")
    pdf.drawRightString(545, y + 6, "Total")

    # Ligne de prestation

    pdf.setFont("Helvetica", 10)

    y -= 25

    for reference, designation, qte, pu, tva_ligne, total in prestations:
        qte= float(qte)
        pu=float(pu)
        tva_ligne=float(tva_ligne)
        total=float(total)

        pdf.rect(40, y, 515, 20)
        # Colonnes
        pdf.line(110, y, 110, y + 20)
        # Référence
        pdf.line(300, y, 300, y + 20)
        # Désignation
        pdf.line(370, y, 370, y + 20)
        # Qté
        pdf.line(440, y, 440, y + 20)
        # PU HT
        pdf.line(490, y, 490, y + 20)
        # TVA

        pdf.drawString(50, y + 5, str(reference))
        pdf.drawString(120, y + 5, designation)
        pdf.drawCentredString(335, y + 5, str(qte))
        pdf.drawCentredString(410, y + 5, f"{pu:.2f} €")
        pdf.drawCentredString(470, y + 5, f"{tva_ligne:.0f}%")
        pdf.drawRightString(545, y + 5, f"{total:.2f} €")

        y -= 20

    # =====================================
    # TOTAUX
    # =====================================

    pdf.setFont("Helvetica-Bold", 10)

    pdf.rect(360, 140, 195, 60)

    pdf.drawString(370, 185, "Total HT")
    pdf.drawRightString(545, 185, f"{montant_ht:.2f} €")

    pdf.drawString(370, 168, "TVA")
    pdf.drawRightString(545, 168, f"{tva:.2f} €")

    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(370, 150, "TOTAL TTC")
    pdf.drawRightString(545, 150, f"{montant_ttc:.2f} €")

    # =====================================
    # MENTION LÉGALE
    # =====================================

    pdf.setFont("Helvetica", 9)

    pdf.drawString(
        40,
        110,
        "TVA non applicable - art. 293 B du CGI"
    )
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(
        40,
        125,
        "Ce devis est valable 30 jours à compter de sa date d'émission."
    )
    # =====================================
    # SIGNATURES
    # =====================================

    pdf.line(60, 70, 220, 70)
    pdf.line(340, 70, 500, 70)

    pdf.setFont("Helvetica", 9)

    pdf.drawCentredString(
        140,
        55,
        "Signature du client"
    )

    pdf.drawCentredString(
        420,
        55,
        "FRED.MECA.SERVICES"
    )

    pdf.drawString(
        40,
        25,
        "Bon pour accord - Date et signature"
    )

    # =====================================
    # SAUVEGARDE
    # =====================================

    pdf.save()

    return fichier



