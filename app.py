import os
from io import BytesIO
from datetime import datetime

from flask import (
    Flask, render_template, request,
    flash, send_file
)

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable
)
from xml.sax.saxutils import escape


# CHARGEMENT DES VARIABLES
load_dotenv()

app = Flask(__name__, static_folder="statique")

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "carriere-pro-cle-secrete-a-changer"
)


# CONFIGURATION DE L'INTELLIGENCE ARTIFICIELLE
def generer_avec_ia(instructions, donnees):
    cle_api = os.environ.get("OPENAI_API_KEY")

    if not cle_api:
        raise ValueError("La clé API OpenAI est introuvable.")

    client = OpenAI(api_key=cle_api)

    modele = os.environ.get("OPENAI_MODEL", "gpt-6-luna")

    reponse = client.responses.create(
        model=modele,
        instructions=instructions,
        input=donnees
    )

    return reponse.output_text.strip()


# PAGE D'ACCUEIL
@app.route("/")
def index():
    return render_template("index.html")


# CRÉATION DE CV
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
            contenu = generer_avec_ia(instructions, str(donnees))
            return render_template(
                "resultat.html",
                titre="Votre CV professionnel",
                document={"contenu": contenu},
                date=datetime.now().strftime("%d/%m/%Y")
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


# LETTRE DE MOTIVATION
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
            contenu = generer_avec_ia(instructions, str(donnees))
            return render_template(
                "resultat.html",
                titre="Votre lettre de motivation",
                document={"contenu": contenu},
                date=datetime.now().strftime("%d/%m/%Y")
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


# DEMANDE D'EMPLOI
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
            contenu = generer_avec_ia(instructions, str(donnees))
            return render_template(
                "resultat.html",
                titre="Votre demande d'emploi",
                document={"contenu": contenu},
                date=datetime.now().strftime("%d/%m/%Y")
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


# TÉLÉCHARGEMENT DU DOCUMENT EN PDF
@app.route("/telecharger-pdf", methods=["POST"])
def telecharger_pdf():
    titre = request.form.get("titre", "Document CARRIÈRE PRO")
    date = request.form.get(
        "date",
        datetime.now().strftime("%d/%m/%Y")
    )

    fichier = BytesIO()

    pdf = SimpleDocTemplate(
        fichier,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()

    style_titre = ParagraphStyle(
        "TitreCarriere",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=19,
        textColor=colors.HexColor("#102544"),
        alignment=TA_CENTER,
        spaceAfter=12
    )

    style_normal = ParagraphStyle(
        "TexteCarriere",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        spaceAfter=8
    )

    style_section = ParagraphStyle(
        "SectionCarriere",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#102544"),
        spaceBefore=12,
        spaceAfter=6
    )

    elements = [
        Paragraph("CARRIÈRE PRO", style_titre),
        Paragraph(escape(titre), style_titre),
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#D4AA48")
        ),
        Spacer(1, 12),
        Paragraph(
            f"Document préparé le {escape(date)}",
            style_normal
        ),
        Spacer(1, 12)
    ]

    contenu = request.form.get("contenu", "").strip()

    if contenu:
        for ligne in contenu.splitlines():
            texte = escape(ligne.strip())
            if texte:
                elements.append(Paragraph(texte, style_normal))
            else:
                elements.append(Spacer(1, 6))
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
                    Paragraph(escape(label), style_section)
                )
                texte = escape(valeur).replace("\n", "<br/>")
                elements.append(Paragraph(texte, style_normal))

    def pied_de_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(
            A4[0] / 2,
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

    return send_file(
        fichier,
        as_attachment=True,
        download_name="document_carriere_pro.pdf",
        mimetype="application/pdf"
    )


# PAGE DES TARIFS — UNE SEULE DÉCLARATION
@app.route("/tarifs")
def tarifs():
    return render_template("tarifs.html")


# VÉRIFICATION DU SERVEUR
@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
