import os
from io import BytesIO
from datetime import datetime

from flask import Flask, render_template, request, flash, send_file
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable
)
from xml.sax.saxutils import escape


# ==================================================
# CONFIGURATION
# ==================================================

load_dotenv()

app = Flask(__name__, static_folder="statique")

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "carriere-pro-cle-secrete-a-changer"
)


# ==================================================
# MODÈLES DE CV
# ==================================================

MODELES_CV = {
    "classique": {
        "nom": "Classique",
        "principal": "#102544",
        "accent": "#D4AA48",
        "fond": "#F1F4F8",
        "alignement": TA_CENTER
    },
    "moderne": {
        "nom": "Moderne",
        "principal": "#176B87",
        "accent": "#36A6A0",
        "fond": "#EAF5F6",
        "alignement": TA_LEFT
    },
    "elegant": {
        "nom": "Élégant",
        "principal": "#333333",
        "accent": "#B69A62",
        "fond": "#F5F1E8",
        "alignement": TA_CENTER
    },
    "creatif": {
        "nom": "Créatif",
        "principal": "#593A80",
        "accent": "#E17B68",
        "fond": "#F4EFF9",
        "alignement": TA_LEFT
    },
    "cadre": {
        "nom": "Cadre",
        "principal": "#142D4E",
        "accent": "#C49A45",
        "fond": "#EEF1F5",
        "alignement": TA_LEFT
    },
    "debutant": {
        "nom": "Débutant",
        "principal": "#26734D",
        "accent": "#76A88A",
        "fond": "#EDF6F0",
        "alignement": TA_LEFT
    }
}


# ==================================================
# INTELLIGENCE ARTIFICIELLE
# ==================================================

def generer_avec_ia(instructions, donnees):

    cle_api = os.environ.get("OPENAI_API_KEY")

    if not cle_api:
        raise ValueError("La clé API OpenAI est introuvable.")

    client = OpenAI(api_key=cle_api)

    modele_ia = os.environ.get("OPENAI_MODEL", "gpt-6-luna")

    reponse = client.responses.create(
        model=modele_ia,
        instructions=instructions,
        input=donnees
    )

    return reponse.output_text.strip()


# ==================================================
# PAGE D'ACCUEIL
# ==================================================

@app.route("/")
def index():
    return render_template("index.html")


# ==================================================
# CRÉATION DE CV
# ==================================================

@app.route("/cv", methods=["GET", "POST"])
def cv():

    if request.method == "POST":

        donnees = {
            "nom": request.form.get("nom", "").strip(),
            "telephone": request.form.get("telephone", "").strip(),
            "email": request.form.get("email", "").strip(),
            "adresse": request.form.get("adresse", "").strip(),
            "poste": request.form.get("poste", "").strip(),
            "profil": request.form.get("profil", "").strip(),
            "formation": request.form.get("formation", "").strip(),
            "experience": request.form.get("experience", "").strip(),
            "competences": request.form.get("competences", "").strip(),
            "langues": request.form.get("langues", "").strip(),
            "interets": request.form.get("interets", "").strip()
        }

        modele = request.form.get("modele", "classique")

        if modele not in MODELES_CV:
            modele = "classique"

        if not donnees["nom"] or not donnees["poste"]:
            flash("Veuillez remplir votre nom et le poste recherché.")
            return render_template("cv.html")

        instructions = """
Tu es un expert en recrutement et en rédaction de CV professionnels.

Rédige un CV professionnel, clair, élégant et bien organisé en français.

Respecte strictement les informations fournies.
N'invente aucun diplôme, aucune expérience, aucune compétence
et aucune coordonnée.

Organise le CV avec les rubriques suivantes :

IDENTITÉ ET COORDONNÉES
PROFIL PROFESSIONNEL
FORMATION
EXPÉRIENCES PROFESSIONNELLES
COMPÉTENCES
LANGUES
CENTRES D'INTÉRÊT

Améliore la formulation et la présentation.
Si une information est absente, ne l'invente pas.

Retourne uniquement le contenu du CV.
"""

        try:

            contenu = generer_avec_ia(
                instructions,
                str(donnees)
            )

            return render_template(
                "resultat.html",
                titre="Votre CV professionnel",
                document={"contenu": contenu},
                date=datetime.now().strftime("%d/%m/%Y"),
                modele=modele
            )

        except OpenAIError:

            app.logger.exception("Erreur API OpenAI")
            flash("Le service IA rencontre un problème. Réessayez.")
            return render_template("cv.html")

        except Exception:

            app.logger.exception("Erreur lors de la création du CV")
            flash("Impossible de créer le CV. Vérifiez la configuration.")
            return render_template("cv.html")

    return render_template("cv.html")


# ==================================================
# LETTRE DE MOTIVATION
# ==================================================

@app.route("/lettre", methods=["GET", "POST"])
def lettre():

    if request.method == "POST":

        donnees = {
            "nom": request.form.get("nom", "").strip(),
            "entreprise": request.form.get("entreprise", "").strip(),
            "poste": request.form.get("poste", "").strip(),
            "formation": request.form.get("formation", "").strip(),
            "experience": request.form.get("experience", "").strip(),
            "motivation": request.form.get("motivation", "").strip()
        }

        if not donnees["nom"] or not donnees["poste"]:
            flash("Veuillez remplir votre nom et le poste recherché.")
            return render_template("lettre.html")

        instructions = """
Tu es un spécialiste de la rédaction professionnelle
et des lettres de motivation.

Rédige une lettre de motivation convaincante,
personnalisée, professionnelle et naturelle en français.

Respecte les informations fournies.
N'invente aucune expérience, formation ou compétence.

La lettre doit comporter :
- Les coordonnées du candidat si elles sont fournies.
- Un objet précis.
- Une introduction professionnelle.
- La présentation du profil.
- Les motivations pour le poste.
- Une conclusion polie.
- Une formule de salutation.

Retourne uniquement la lettre finale.
"""

        try:

            contenu = generer_avec_ia(
                instructions,
                str(donnees)
            )

            return render_template(
                "resultat.html",
                titre="Votre lettre de motivation",
                document={"contenu": contenu},
                date=datetime.now().strftime("%d/%m/%Y"),
                modele="classique"
            )

        except OpenAIError:

            app.logger.exception("Erreur API OpenAI")
            flash("Le service IA rencontre un problème. Réessayez.")
            return render_template("lettre.html")

        except Exception:

            app.logger.exception("Erreur lors de la création de la lettre")
            flash("Impossible de créer la lettre. Vérifiez la configuration.")
            return render_template("lettre.html")

    return render_template("lettre.html")


# ==================================================
# DEMANDE D'EMPLOI
# ==================================================

@app.route("/demande", methods=["GET", "POST"])
def demande():

    if request.method == "POST":

        donnees = {
            "nom": request.form.get("nom", "").strip(),
            "entreprise": request.form.get("entreprise", "").strip(),
            "poste": request.form.get("poste", "").strip(),
            "message": request.form.get("message", "").strip()
        }

        if not donnees["nom"] or not donnees["poste"]:
            flash("Veuillez remplir votre nom et le poste demandé.")
            return render_template("demande.html")

        instructions = """
Tu es un expert en rédaction administrative et professionnelle.

Rédige une demande d'emploi formelle, claire,
respectueuse et convaincante en français.

Respecte les informations fournies.
N'invente aucune expérience ni qualification.

Présente :
- Le nom du candidat.
- L'objet de la demande.
- Une formule d'introduction.
- Le poste sollicité.
- La motivation du candidat.
- Une formule de politesse.
- La signature.

Retourne uniquement la demande d'emploi finale.
"""

        try:

            contenu = generer_avec_ia(
                instructions,
                str(donnees)
            )

            return render_template(
                "resultat.html",
                titre="Votre demande d'emploi",
                document={"contenu": contenu},
                date=datetime.now().strftime("%d/%m/%Y"),
                modele="classique"
            )

        except OpenAIError:

            app.logger.exception("Erreur API OpenAI")
            flash("Le service IA rencontre un problème. Réessayez.")
            return render_template("demande.html")

        except Exception:

            app.logger.exception("Erreur lors de la création de la demande")
            flash("Impossible de créer la demande. Vérifiez la configuration.")
            return render_template("demande.html")

    return render_template("demande.html")


# ==================================================
# TÉLÉCHARGEMENT PDF
# ==================================================

@app.route("/telecharger-pdf", methods=["POST"])
def telecharger_pdf():

    titre = request.form.get(
        "titre",
        "Document CARRIÈRE PRO"
    )

    date = request.form.get(
        "date",
        datetime.now().strftime("%d/%m/%Y")
    )

    modele = request.form.get("modele", "classique")

    if modele not in MODELES_CV:
        modele = "classique"

    theme = MODELES_CV[modele]

    couleur_principale = colors.HexColor(theme["principal"])
    couleur_accent = colors.HexColor(theme["accent"])
    couleur_fond = colors.HexColor(theme["fond"])

    fichier = BytesIO()

    pdf = SimpleDocTemplate(
        fichier,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.7 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()

    style_titre = ParagraphStyle(
        "TitreCarriere",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=25,
        textColor=couleur_principale,
        alignment=theme["alignement"],
        spaceAfter=12
    )

    style_normal = ParagraphStyle(
        "TexteCarriere",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        textColor=colors.HexColor("#263238"),
        spaceAfter=8
    )

    style_section = ParagraphStyle(
        "SectionCarriere",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=couleur_principale,
        spaceBefore=12,
        spaceAfter=6,
        borderPadding=4
    )

    elements = []

    elements.append(
        Paragraph(
            escape(titre),
            style_titre
        )
    )

    elements.append(
        HRFlowable(
            width="100%",
            thickness=2,
            color=couleur_accent
        )
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            f"Document préparé le {escape(date)}",
            style_normal
        )
    )

    elements.append(Spacer(1, 12))

    contenu = request.form.get("contenu", "").strip()

    rubriques = [
        "IDENTITÉ ET COORDONNÉES",
        "PROFIL PROFESSIONNEL",
        "FORMATION",
        "EXPÉRIENCES PROFESSIONNELLES",
        "COMPÉTENCES",
        "LANGUES",
        "CENTRES D'INTÉRÊT",
        "FORMATION ET DIPLÔMES",
        "EXPÉRIENCES PROFESSIONNELLES",
        "LANGUES PARLÉES"
    ]

    if contenu:

        for ligne in contenu.splitlines():

            texte_brut = ligne.strip()

            if not texte_brut:
                elements.append(Spacer(1, 6))
                continue

            texte = escape(texte_brut)

            est_titre = (
                texte_brut.upper() in rubriques
                or (
                    texte_brut.isupper()
                    and len(texte_brut) < 65
                    and len(texte_brut) > 2
                )
            )

            if est_titre:

                elements.append(
                    Paragraph(
                        texte,
                        style_section
                    )
                )

            else:

                elements.append(
                    Paragraph(
                        texte.replace("\n", "<br/>"),
                        style_normal
                    )
                )

    else:

        champs = [
            ("Nom et prénom", "nom"),
            ("Téléphone", "telephone"),
            ("Email", "email"),
            ("Adresse", "adresse"),
            ("Poste recherché", "poste"),
            ("Profil professionnel", "profil"),
            ("Formation et diplômes", "formation"),
            ("Expériences professionnelles", "experience"),
            ("Compétences", "competences"),
            ("Langues parlées", "langues"),
            ("Centres d'intérêt", "interets")
        ]

        for label, champ in champs:

            valeur = request.form.get(champ, "").strip()

            if valeur:

                elements.append(
                    Paragraph(
                        escape(label),
                        style_section
                    )
                )

                texte = escape(valeur).replace("\n", "<br/>")

                elements.append(
                    Paragraph(
                        texte,
                        style_normal
                    )
                )

    # EN-TÊTE ET PIED DE PAGE PERSONNALISÉS

    def pied_de_page(canvas, doc):

        canvas.saveState()

        largeur, hauteur = A4

        canvas.setFillColor(couleur_principale)

        canvas.rect(
            0,
            hauteur - 0.55 * cm,
            largeur,
            0.55 * cm,
            fill=1,
            stroke=0
        )

        canvas.setFillColor(couleur_accent)

        canvas.rect(
            0,
            hauteur - 0.65 * cm,
            largeur,
            0.10 * cm,
            fill=1,
            stroke=0
        )

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)

        canvas.drawCentredString(
            largeur / 2,
            1 * cm,
            f"CARRIÈRE PRO - Page {doc.page}"
        )

        canvas.restoreState()

    pdf.build(
        elements,
        onFirstPage=pied_de_page,
        onLaterPages=pied_de_page
    )

    fichier.seek(0)

    nom_fichier = "document_carriere_pro.pdf"

    if "CV" in titre.upper():
        nom_fichier = "CV_carriere_pro.pdf"
    elif "LETTRE" in titre.upper():
        nom_fichier = "lettre_motivation.pdf"
    elif "DEMANDE" in titre.upper():
        nom_fichier = "demande_emploi.pdf"

    return send_file(
        fichier,
        as_attachment=True,
        download_name=nom_fichier,
        mimetype="application/pdf"
    )


# ==================================================
# PAGE DES TARIFS
# ==================================================

@app.route("/tarifs")
def tarifs():
    return render_template("tarifs.html")


# ==================================================
# VÉRIFICATION DU SERVEUR
# ==================================================

@app.route("/health")
def health():
    return {"status": "ok"}


# ==================================================
# DÉMARRAGE DE L'APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
