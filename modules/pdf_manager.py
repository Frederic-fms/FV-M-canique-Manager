from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os


def creer_pdf(
    numero,
    date,
    client,
    immatriculation,
    travaux,
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

    pdf.rect(40, hauteur - 250, 515, 90)

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, hauteur - 180, "CLIENT")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, hauteur - 200, f"Nom : {client}")
    pdf.drawString(50, hauteur - 220, f"Immatriculation : {immatriculation}")

    # =====================================
    # TABLEAU DES PRESTATIONS
    # =====================================

    y = hauteur - 300

    pdf.setFont("Helvetica-Bold", 10)

    pdf.rect(40, y, 515, 20)

    pdf.drawString(50, y + 6, "Désignation")
    pdf.drawCentredString(340, y + 6, "Qté")
    pdf.drawCentredString(430, y + 6, "Prix")
    pdf.drawRightString(545, y + 6, "Total")

    # Ligne de prestation

    pdf.setFont("Helvetica", 10)

    pdf.rect(40, y - 25, 515, 25)

    pdf.drawString(50, y - 17, travaux)
    pdf.drawCentredString(340, y - 17, "1")
    pdf.drawCentredString(430, y - 17, f"{montant_ttc:.2f} €")
    pdf.drawRightString(545, y - 17, f"{montant_ttc:.2f} €")
    # =====================================
    # TOTAL
    # =====================================

    pdf.setFont("Helvetica-Bold", 12)

    pdf.drawRightString(
        470,
        170,
        "TOTAL :"
    )

    pdf.drawRightString(
        545,
        170,
        f"{montant_ttc:.2f} €"
    )

    # =====================================
    # MENTION LÉGALE
    # =====================================

    pdf.setFont("Helvetica", 9)

    pdf.drawString(
        40,
        110,
        "TVA non applicable - art. 293 B du CGI"
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



