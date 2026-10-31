import os
import base64
from io import BytesIO
from datetime import datetime

from flask import (
    Flask, render_template, request,
    flash, send_file
)
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
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable
)
from xml.sax.saxutils import escape
