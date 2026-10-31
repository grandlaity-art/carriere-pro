import os
import base64
from io import BytesIO
from datetime import datetime

from flask import Flask, render_template, request, flash, send_file, redirect
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from pypdf import PdfReader
from PIL import Image

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from xml.sax.saxutils import escape


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

app = Flask(__name__, static_folder="statique")

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "carriere-pro-cle-secrete-a-changer"
)


# --------------------------------------------------
# MODÈLES DE CV
# --------------------------------------------------

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


# --------------------------------------------------
# FONCTION IA
# --------------------------------------------------

def generer_avec_ia(instructions, donnees):
    cle_api = os.environ.get("OPENAI_API_KEY")

    if not cle_api:
        raise ValueError(
            "La clé API OpenAI n'est pas encore configurée."
        )

    client = OpenAI(api_key=cle_api)

    modele_ia = os.environ.get(
        "OPENAI_MODEL",
        "gpt-4.1-mini"
    )

    reponse = client.responses.create(
        model=modele_ia,
        instructions=instructions,
        input=donnees
    )

    return reponse.output_text.strip()


# --------------------------------------------------
# ACCUEIL
# --------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------
# CRÉER UN CV
# --------------------------------------------------

@app.route("/cv", methods=["GET", "POST"])
def cv():
    if request.method == "GET":
        return render_template("cv.html")

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
        flash("Veuillez renseigner votre nom et le poste recherché.")
        return render_template("cv.html")

    instructions = """
Tu es un expert en recrutement et en rédaction de CV.
Rédige un CV professionnel en français à partir des informations fournies.
Corrige les fautes et améliore la formulation.
N'invente aucune information, expérience, formation ou compétence.
Organise le CV avec des rubriques claires.
Retourne uniquement le contenu du CV.
"""

    try:
        contenu = generer_avec_ia(instructions, str(donnees))

        return render_template(
            "resultat.html",
            titre="Votre CV professionnel",
            document={"contenu": contenu},
            date=datetime.now().strftime("%d/%m/%Y"),
            modele=modele
        )

    except OpenAIError:
        app.logger.exception("Erreur OpenAI lors de la création du CV")
        flash("Le service IA rencontre un problème. Réessayez plus tard.")

    except Exception as erreur:
        app.logger.exception("Erreur lors de la création du CV")
        flash(str(erreur))

    return render_template("cv.html")


# --------------------------------------------------
# METTRE À JOUR UN ANCIEN CV
# --------------------------------------------------

@app.route("/mettre-a-jour-cv", methods=["POST"])
def mettre_a_jour_cv():
    fichier = request.files.get("ancien_cv")

    if not fichier or not fichier.filename:
        flash("Veuillez sélectionner votre ancien CV.")
        return render_template("cv.html")

    nom_fichier = secure_filename(fichier.filename)
    extension = os.path.splitext(nom_fichier)[1].lower()

    extensions_autorisees = [
        ".pdf", ".jpg", ".jpeg", ".png", ".webp"
    ]

    if extension not in extensions_autorisees:
        flash("Format non accepté. Utilisez PDF, JPG, PNG ou WEBP.")
        return render_template("cv.html")

    fichier_bytes = fichier.read()

    if not fichier_bytes:
        flash("Le fichier sélectionné est vide.")
        return render_template("cv.html")

    if len(fichier_bytes) > 10 * 1024 * 1024:
        flash("Le fichier ne doit pas dépasser 10 Mo.")
        return render_template("cv.html")

    modele = request.form.get("modele", "classique")

    if modele not in MODELES_CV:
        modele = "classique"

    cle_api = os.environ.get("OPENAI_API_KEY")

    if not cle_api:
        flash("La mise à jour automatique nécessite la clé API OpenAI.")
        return render_template("cv.html")

    client = OpenAI(api_key=cle_api)

    modele_ia = os.environ.get(
        "OPENAI_MODEL",
        "gpt-4.1-mini"
    )

    instructions = """
Tu es un expert en recrutement et en rédaction de CV.
Analyse le CV fourni et rédige une nouvelle version professionnelle
et bien structurée en français.
Corrige les fautes et améliore les formulations.
Conserve uniquement les informations réelles présentes dans le CV.
N'invente aucun diplôme, emploi, compétence ou coordonnée.
Si une information est illisible, ne la devine pas.
Retourne uniquement le CV amélioré.
"""

    try:
        if extension == ".pdf":
            lecteur = PdfReader(BytesIO(fichier_bytes))

            if lecteur.is_encrypted:
                flash("Ce PDF est protégé. Importez un PDF non protégé.")
                return render_template("cv.html")

            texte_original = "\n".join(
                page.extract_text() or ""
                for page in lecteur.pages
            )

            if not texte_original.strip():
                flash(
                    "Le texte de ce PDF n'est pas lisible. "
                    "Essayez une photo claire de votre CV."
                )
                return render_template("cv.html")

            reponse = client.responses.create(
                model=modele_ia,
                instructions=instructions,
                input=(
                    "Voici le contenu de mon ancien CV :\n\n"
                    + texte_original
                )
            )

        else:
            image = Image.open(BytesIO(fichier_bytes))
            image.verify()

            image = Image.open(
                BytesIO(fichier_bytes)
            ).convert("RGB")

            image_buffer = BytesIO()
            image.save(image_buffer, format="JPEG", quality=85)

            image_base64 = base64.b64encode(
                image_buffer.getvalue()
            ).decode("utf-8")

            reponse = client.responses.create(
                model=modele_ia,
                instructions=instructions,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "Lis ce CV photographié et améliore "
                                    "sa présentation sans inventer "
                                    "d'informations."
                                )
                            },
                            {
                                "type": "input_image",
                                "image_url": (
                                    "data:image/jpeg;base64,"
                                    + image_base64
                                ),
                                "detail": "high"
                            }
                        ]
                    }
                ]
            )

        contenu = reponse.output_text.strip()

        if not contenu:
            flash("L'analyse du CV n'a produit aucun résultat.")
            return render_template("cv.html")

        return render_template(
            "resultat.html",
            titre="Votre CV actualisé",
            document={"contenu": contenu},
            date=datetime.now().strftime("%d/%m/%Y"),
            modele=modele
        )

    except OpenAIError:
        app.logger.exception("Erreur API lors de la mise à jour du CV")
        flash("Erreur du service IA. Veuillez réessayer.")

    except Exception:
        app.logger.exception("Erreur lors du traitement de l'ancien CV")
        flash(
            "Impossible de lire ce fichier. "
            "Vérifiez qu'il s'agit d'un PDF ou d'une photo valide."
        )

    return render_template("cv.html")


# --------------------------------------------------
# LETTRE DE MOTIVATION
# --------------------------------------------------

@app.route("/lettre", methods=["GET", "POST"])
def lettre():
    if request.method == "GET":
        return render_template("lettre.html")

    donnees = {
        "nom": request.form.get("nom", "").strip(),
        "entreprise": request.form.get("entreprise", "").strip(),
        "poste": request.form.get("poste", "").strip(),
        "formation": request.form.get("formation", "").strip(),
        "experience": request.form.get("experience", "").strip(),
        "motivation": request.form.get("motivation", "").strip()
    }

    instructions = """
Rédige une lettre de motivation professionnelle en français.
Utilise uniquement les informations fournies.
N'invente pas d'expérience ni de diplôme.
Retourne uniquement la lettre.
"""

    try:
        contenu = generer_avec_ia(instructions, str(donnees))

        return render_template(
            "resultat.html",
            titre="Votre lettre de motivation",
            document={"contenu": contenu},
            date=datetime.now().strftime("%d/%m/%Y"),
            modele="classique"
        )

    except Exception:
        app.logger.exception("Erreur lors de la création de la lettre")
        flash("Impossible de générer la lettre pour le moment.")
        return render_template("lettre.html")


# --------------------------------------------------
# DEMANDE D'EMPLOI
# --------------------------------------------------

@app.route("/demande", methods=["GET", "POST"])
def demande():
    if request.method == "GET":
        return render_template("demande.html")

    donnees = {
        "nom": request.form.get("nom", "").strip(),
        "entreprise": request.form.get("entreprise", "").strip(),
        "poste": request.form.get("poste", "").strip(),
        "message": request.form.get("message", "").strip()
    }

    instructions = """
Rédige une demande d'emploi professionnelle en français.
Utilise uniquement les informations fournies.
Retourne uniquement la demande.
"""

    try:
        contenu = generer_avec_ia(instructions, str(donnees))

        return render_template(
            "resultat.html",
            titre="Votre demande d'emploi",
            document={"contenu": contenu},
            date=datetime.now().strftime("%d/%m/%Y"),
            modele="classique"
        )

    except Exception:
        app.logger.exception("Erreur lors de la création de la demande")
        flash("Impossible de générer la demande pour le moment.")
        return render_template("demande.html")


# --------------------------------------------------
# TÉLÉCHARGER EN PDF
# --------------------------------------------------

@app.route("/telecharger-pdf", methods=["POST"])
def telecharger_pdf():
    contenu = request.form.get("contenu", "").strip()
    titre = request.form.get("titre", "Document professionnel")
    modele = request.form.get("modele", "classique")

    if not contenu:
        flash("Aucun contenu à télécharger.")
        return redirect("/")

    if modele not in MODELES_CV:
        modele = "classique"

    palette = MODELES_CV[modele]

    fichier = BytesIO()

    document_pdf = SimpleDocTemplate(
        fichier,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()

    style_titre = ParagraphStyle(
        "TitreDocument",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor(palette["principal"]),
        alignment=TA_CENTER,
        spaceAfter=15
    )

    style_contenu = ParagraphStyle(
        "ContenuDocument",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        spaceAfter=8
    )

    elements = [
        Paragraph(escape(titre), style_titre),
        Spacer(1, 10)
    ]

    for ligne in contenu.splitlines():
        ligne = ligne.strip()

        if ligne:
            elements.append(
                Paragraph(escape(ligne), style_contenu)
            )
        else:
            elements.append(Spacer(1, 6))

    document_pdf.build(elements)

    fichier.seek(0)

    return send_file(
        fichier,
        as_attachment=True,
        download_name="document_carriere_pro.pdf",
        mimetype="application/pdf"
    )


# --------------------------------------------------
# TARIFS
# --------------------------------------------------

@app.route("/tarifs")
def tarifs():
    return render_template("tarifs.html")


# --------------------------------------------------
# VÉRIFICATION DU SERVEUR
# --------------------------------------------------

@app.route("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# LANCEMENT LOCAL
# --------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
