from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    Image
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.utils import ImageReader

from datetime import datetime

import os
try:
    pdfmetrics.registerFont(
        TTFont(
            "Arial",
            "arial.ttf"
        )
    )
    POLICE = "Arial"
except:
    POLICE = "Helvetica"

DOSSIER = "PDF/Ordres_Reparation"

os.makedirs(
    DOSSIER,
    exist_ok=True
)

def creer_pdf_or(
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
          travaux_prevus,
          travaux_effectues,
          temps_prevu,
          temps_reel,
          observations
          ):
     fichier = os.path.join(
         DOSSIER,
         f"{numero}.pdf"
         )
     doc = SimpleDocTemplate(
         fichier,
         pagesize=(210 * mm, 297 * mm),
         leftMargin=12 * mm,
         rightMargin=12 * mm,
         topMargin=10 * mm,
         bottomMargin=10 * mm
         )
     styles = getSampleStyleSheet()

     story = []

    # =====================================
    # LOGO
    # =====================================

     logo = "assets/logo_fms.png"

     if os.path.exists(logo):
        from reportlab.platypus import Image

        img = Image(
            logo,
            width=42*mm,
            height=28*mm
        )
     else:
        img = Paragraph(
            "<b>FMS MANAGER</b>",
            styles["Heading1"]
        )

    # =====================================
    # TITRE
    # =====================================

     titre = Paragraph(
         f"ORDRE DE REPARATION N° {numero}",
        styles["Title"]
     )

    # =====================================
    # COORDONNÉES ENTREPRISE
    # =====================================

     entreprise = Paragraph(
         """
         <b>FRED.MECA.SERVICES</b><br/>
         Mécanicien automobile à domicile<br/>
         Tél : 06 99 97 31 79<br/>
         Mail : fred.meca.services@gmail.com
         """,
         styles["BodyText"]
         )

    # =====================================
    # # TABLEAU EN-TÊTE
    # =====================================

     entete = Table(
         [
             [img, titre, entreprise]
         ],
         colWidths=[
             45*mm,
             70*mm,
             65*mm
         ]
     )

     entete.setStyle(

         TableStyle(

             [

                 ("VALIGN",(0,0),(-1,-1),"TOP"),
                 ("TOPPADDING",(0,0),(-1,-1),0),
                 ("BOTTOMPADDING",(0,0),(-1,-1),2),
                 ("VALIGN",(0,0),(-1,-1),"MIDDLE"),

             ]

         )

     )

     story.append(entete)

     story.append(Spacer(1,5))

     infos = Table(

         [

             [

                 f"N° OR : {numero}",

                 f"Date : {date}"

             ],

             [

                 f"Client : {client}",

                 f"Téléphone : {telephone}"

             ],

             [

                 f"Immatriculation : {immatriculation}",

                 "Kilométrage à la réception : ___________km"

             ],

             [

                 f"Marque : {marque}",

                 f"Modèle : {modele}"

             ]

         ],

         colWidths=[90*mm,90*mm]

     )

     infos.setStyle(

         TableStyle(

             [

                 ("GRID",(0,0),(-1,-1),0.5,colors.grey),

                 ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#cc0000")),

                 ("TEXTCOLOR",(0,0),(-1,0),colors.white),

                 ("FONTNAME",(0,0),(-1,-1),POLICE),

                 ("FONTSIZE",(0,0),(-1,-1),10),

                 ("BOTTOMPADDING",(0,0),(-1,-1),3),

                 ("TOPPADDING",(0,0),(-1,-1),3),

             ]

         )

     )

     story.append(infos)

     story.append(Spacer(1,5))

     # =====================================
     # PRESTATIONS
     # =====================================

     story.append(
         Paragraph(
             "<b>PRESTATIONS</b>",
             styles["Heading2"]
         )
     )

     data = [
         [
             "Désignation",
             "Qté",
             "Temps",
             "PU HT",
             "Total HT"
         ]
     ]

     total_ht = 0

     for ligne in prestations:

         reference, designation, qte, temps, prix_ht, total = ligne

         total_ht += float(total)

         data.append([
             designation,
             str(qte),
             temps,
             f"{float(prix_ht):.2f} €",
             f"{float(total):.2f} €"
         ])

     table = Table(
         data,
         colWidths=[
             100*mm,
             15*mm,
             20*mm,
             25*mm,
             30*mm
         ]
     )

     table.setStyle(
         TableStyle([
             ("GRID",(0,0),(-1,-1),0.5,colors.grey),
             ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#cc0000")),
             ("TEXTCOLOR",(0,0),(-1,0),colors.white),
             ("FONTNAME",(0,0),(-1,-1),POLICE),
             ("FONTSIZE",(0,0),(-1,-1),9),
             ("ALIGN",(2,1),(-1,-1),"CENTER"),
             ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
             ("BOTTOMPADDING",(0,0),(-1,-1),6),
             ("TOPPADDING",(0,0),(-1,-1),6),
         ])
     )

     story.append(table)

     story.append(Spacer(1,5))

     temps = Table([
         ["Temps prévu", temps_prevu],
         ["Temps réel", temps_reel]
     ], colWidths=[50*mm,50*mm])

     temps.setStyle(
         TableStyle([
             ("GRID",(0,0),(-1,-1),0.5,colors.black),
             ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#eeeeee")),
             ("FONTNAME",(0,0),(-1,-1),POLICE),
             ("FONTSIZE",(0,0),(-1,-1),10),
         ])
     )

     story.append(temps)

     story.append(Spacer(1,5))

     # =====================================
     # TRAVAUX PREVUS
     # =====================================

     story.append(
         Paragraph(
             "<b>TRAVAUX PRÉVUS</b>",
             styles["Heading2"]
         )
     )

     travaux_prevus_table = Table(
         [
             [travaux_prevus if travaux_prevus else ""]
         ],
         colWidths=[180*mm],
         rowHeights=[18*mm]
     )

     travaux_prevus_table.setStyle(
         TableStyle([
             ("GRID",(0,0),(-1,-1),0.5,colors.black),
             ("VALIGN",(0,0),(-1,-1),"TOP"),
             ("LEFTPADDING",(0,0),(-1,-1),8),
             ("TOPPADDING",(0,0),(-1,-1),8),
             ("FONTNAME",(0,0),(-1,-1),POLICE),
             ("FONTSIZE",(0,0),(-1,-1),10),
         ])
     )

     story.append(travaux_prevus_table)

     story.append(Spacer(1,5))

     # =====================================
     # TRAVAUX EFFECTUÉS
     # =====================================

     story.append(
         Paragraph(
             "<b>TRAVAUX EFFECTUÉS</b>",
             styles["Heading2"]
         )
     )

     travaux_effectues_table = Table(
         [
             [travaux_effectues if travaux_effectues else ""]
         ],
         colWidths=[180*mm],
         rowHeights=[12*mm]
     )

     travaux_effectues_table.setStyle(
         TableStyle([
             ("GRID",(0,0),(-1,-1),0.5,colors.black),
             ("VALIGN",(0,0),(-1,-1),"TOP"),
             ("LEFTPADDING",(0,0),(-1,-1),8),
             ("TOPPADDING",(0,0),(-1,-1),8),
             ("FONTNAME",(0,0),(-1,-1),POLICE),
             ("FONTSIZE",(0,0),(-1,-1),10),
         ])
     )

     story.append(travaux_effectues_table)

     story.append(Spacer(1,5))

     # =====================================
     # OBSERVATIONS
     # =====================================

     story.append(
         Paragraph(
             "<b>OBSERVATIONS</b>",
             styles["Heading2"]
         )
     )

     observations_table = Table(
         [
             [observations if observations else ""]
         ],
         colWidths=[180*mm],
         rowHeights=[25*mm]
     )

     observations_table.setStyle(
         TableStyle([
             ("GRID",(0,0),(-1,-1),0.5,colors.black),
             ("VALIGN",(0,0),(-1,-1),"TOP"),
             ("LEFTPADDING",(0,0),(-1,-1),8),
             ("TOPPADDING",(0,0),(-1,-1),8),
             ("FONTNAME",(0,0),(-1,-1),POLICE),
             ("FONTSIZE",(0,0),(-1,-1),10),
         ])
     )

     story.append(observations_table)
     story.append(Spacer(1,5))
     doc.build(story)
     return fichier