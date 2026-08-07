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
    # BANDEAU HAUT
    # =====================================
    pdf.setFillColorRGB(0.08, 0.08, 0.08)
    pdf.rect(20, hauteur - 135, largeur - 40, 115, fill=1, stroke=0)

    # Retour à la couleur noire
    pdf.setFillColorRGB(0, 0, 0)

    # =====================================
    # CADRE ROUGE
    # =====================================
    pdf.setStrokeColorRGB(0.85, 0.0, 0.0) # Rouge FMS
    pdf.setLineWidth(2)
    pdf.rect(20, 20, largeur - 40, hauteur - 40)


    # =====================================
    # DATE DE VALIDITÉ
    # =====================================

    date_devis = datetime.strptime(date, "%d/%m/%Y")
    date_validite = date_devis + timedelta(days=30)

    validite = date_validite.strftime("%d/%m/%Y")

    # =====================================
    # EN-TÊTE
    # =====================================

    # Fond noir
    pdf.setFillColorRGB(0.08, 0.08, 0.08)
    pdf.rect(0, hauteur - 130, largeur, 130, fill=1, stroke=0)

    # Bordure rouge
    pdf.setStrokeColorRGB(0.85, 0.10, 0.10)
    pdf.setLineWidth(2)
    pdf.line(0, hauteur - 130, largeur, hauteur - 130)

    # =====================================
    # LOGO FMS
    # =====================================
    logo = ImageReader("assets/logo_fms.png")

    pdf.drawImage(
        logo,
        25, # Plus à gauche
        hauteur - 115, # Légèrement remonté
        width=185,
        height=95,
        mask="auto"
    )
    
    # =====================================
    # CARTOUCHE DEVIS
    # =====================================

    # Fond rouge
    pdf.setFillColorRGB(0.85, 0.05, 0.05)
    pdf.roundRect(220, hauteur - 112, 170, 80, 8, fill=1, stroke=0)

    # Texte blanc
    pdf.setFillColorRGB(1, 1, 1)

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(305, hauteur - 60, "DEVIS")

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(305, hauteur - 82, f"N° {numero}")

    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(305, hauteur - 97, f"Date : {date}")

    pdf.drawCentredString(305, hauteur - 110, f"Validité : {validite}")

    # Retour au noir
    pdf.setFillColorRGB(0, 0, 0)


    # =====================================
    # ENTREPRISE
    # =====================================

    # Texte blanc
    pdf.setFillColorRGB(1, 1, 1)

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawRightString(560, hauteur - 32, "FRED.MECA.SERVICES")

    pdf.setFont("Helvetica", 9)

    pdf.drawRightString(560, hauteur - 48, "85 rue Paul Vaillant Couturier")
    pdf.drawRightString(560, hauteur - 62, "62540 Marles-les-Mines")
    pdf.drawRightString(560, hauteur - 76, "06 99 97 31 79")
    pdf.drawRightString(560, hauteur - 90, "fred.meca.services@gmail.com")
    pdf.drawRightString(560, hauteur - 104, "SIRET : xxxxxxxxxxxxxx")
    pdf.drawRightString(560, hauteur - 118, "TVA non applicable - art. 293 B du CGI")

    # Retour au noir
    pdf.setFillColorRGB(0, 0, 0)

    # =====================================
    # BLOC CLIENT
    # =====================================

    # Cadre
    pdf.setStrokeColorRGB(0.85, 0.05, 0.05)
    pdf.setLineWidth(1.5)
    pdf.roundRect(35, hauteur - 300, 245, 125, 8)

    # Bandeau rouge
    pdf.setFillColorRGB(0.85, 0.05, 0.05)
    pdf.roundRect(35, hauteur - 195, 245, 20, 6, fill=1, stroke=0)

    # Titre
    pdf.setFillColorRGB(1,1,1)
    pdf.setFont("Helvetica-Bold",10)
    pdf.drawString(45, hauteur - 204, "CLIENT")

    # Texte
    pdf.setFillColorRGB(0,0,0)
    pdf.setFont("Helvetica",9)

    pdf.drawString(45, hauteur - 215, f"Nom : {client}")
    pdf.drawString(45, hauteur - 230, adresse)
    pdf.drawString(45, hauteur - 245, f"{code_postal} {ville}")
    pdf.drawString(45, hauteur - 260, telephone)
    pdf.drawString(45, hauteur - 275, email)


    # =====================================
    # BLOC VÉHICULE
    # =====================================

    pdf.setStrokeColorRGB(0.85, 0.05, 0.05)
    pdf.roundRect(305, hauteur - 300, 250, 125, 8)

    pdf.setFillColorRGB(0.85, 0.05, 0.05)
    pdf.roundRect(305, hauteur - 195, 250, 20, 6, fill=1, stroke=0)

    pdf.setFillColorRGB(1,1,1)
    pdf.setFont("Helvetica-Bold",10)
    pdf.drawString(315, hauteur - 204, "VÉHICULE")

    pdf.setFillColorRGB(0,0,0)
    pdf.setFont("Helvetica",9)

    pdf.drawString(315, hauteur - 215, f"Immatriculation : {immatriculation}")
    pdf.drawString(315, hauteur - 230, f"Marque : {marque}")
    pdf.drawString(315, hauteur - 245, f"Modèle : {modele}")
    pdf.drawString(315, hauteur - 260, f"Kilométrage : {kilometrage} km")

    # =====================================
    # TABLEAU DES PRESTATIONS
    # =====================================

    y = hauteur - 365

    # En-tête rouge
    pdf.setFillColorRGB(0.85, 0.05, 0.05)
    pdf.roundRect(35, y, 520, 22, 5, fill=1, stroke=0)

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 10)


    pdf.drawString(170, y + 7, "Désignation")
    pdf.drawCentredString(325, y + 7, "Qté")
    pdf.drawCentredString(390, y + 7, "PU HT")
    pdf.drawCentredString(455, y + 7, "TVA")
    pdf.drawRightString(525, y + 7, "Total")

    # Retour texte noir
    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", 10)

    # Première ligne
    y -= 25

    for _, designation, qte, pu, tva_ligne, total in prestations:

        qte = float(qte)
        pu = float(pu)
        tva_ligne = float(tva_ligne)
        total = float(total)

        # Cadre de la ligne
        pdf.setStrokeColorRGB(0.80, 0.80, 0.80)
        pdf.roundRect(35, y, 520, 20, 2)

        # Colonnes
        
        pdf.line(300, y, 300, y + 20)
        pdf.line(350, y, 350, y + 20)
        pdf.line(425, y, 425, y + 20)
        pdf.line(485, y, 485, y + 20)

        # Données
        pdf.drawString(50, y + 5, designation)

        pdf.drawCentredString(325, y + 5, str(int(qte)))

        pdf.drawRightString(410, y + 5, f"{pu:.2f} €")

        pdf.drawCentredString(455, y + 5, f"{tva_ligne:.0f}%")

        pdf.drawRightString(540, y + 5, f"{total:.2f} €")

        y -= 20
        pdf.line(40, y, 560, y)

    # =====================================
    # TOTAUX
    # =====================================

    pdf.setFont("Helvetica-Bold", 10)

    # =====================================
    # TOTAUX
    # =====================================

    pdf.setStrokeColorRGB(0.85, 0.05, 0.05)
    pdf.setFillColorRGB(0.97, 0.97, 0.97)

    pdf.roundRect(340, 145, 210, 70, 8, fill=1)

    pdf.setFillColorRGB(0, 0, 0)

    pdf.setFont("Helvetica", 10)
    pdf.drawString(355, 195, "Total HT")
    pdf.drawRightString(540, 195, f"{montant_ht:.2f} €")

    pdf.drawString(355, 178, "TVA")
    pdf.drawRightString(540, 178, f"{tva:.2f} €")

    pdf.setFont("Helvetica-Bold", 13)
    pdf.setFillColorRGB(0.85, 0.05, 0.05)

    pdf.drawString(355, 158, "TOTAL TTC")
    pdf.drawRightString(540, 158, f"{montant_ttc:.2f} €")

    pdf.setFillColorRGB(0, 0, 0)



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



