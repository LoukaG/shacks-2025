import os
import json
from datetime import datetime, timezone
from huggingface_hub import InferenceClient

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from app.utils.const import TOKEN_HUGGINGFACE
pdfmetrics.registerFont(TTFont("DejaVu", "assets/DejaVuSans.ttf"))


def generate_intrusion_report(input_json_path: str, output_folder: str = "reports", model_name: str = "openai/gpt-oss-120b", hf_token: str = TOKEN_HUGGINGFACE) -> dict:

    os.makedirs(output_folder, exist_ok=True)
    outputs_folder = os.path.join(output_folder, "outputs")
    os.makedirs(outputs_folder, exist_ok=True)

    with open(input_json_path, "r", encoding="utf-8") as f:
        logs = json.load(f)

    person = {
        "name": "Suspect inconnu",
        "image_local_path": "/home/ubuntu/shacks-2025/ror.jpg"
    }

    table_data = [["Heure (UTC)", "Action", "Détails"]]
    logs_text = ""
    timestamps = []

    for entry in logs:
        ts = entry.get("timestamp", 0)
        timestamps.append(ts)
        dt = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        action = entry.get("type", "")
        details = {k: v for k, v in entry.items() if k not in ["timestamp", "type"]}
        details_str = ", ".join([f"{k}:{v}" for k, v in details.items()]) or "—"

        logs_text += f"{dt} | {action} | {details_str}\n"
        table_data.append([dt, action, details_str])

    start_time = datetime.fromtimestamp(min(timestamps), timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    end_time   = datetime.fromtimestamp(max(timestamps), timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    prompt = f"""
    Tu es un assistant d’analyse de sécurité informatique.

    Voici les journaux d’activité détectés :
    {logs_text}

    Rédige un paragraphe fluide  pour expliquer d'une manière simple et claire
    ce qu’a fait l’intrus, et d'une manière simpleles risques,le texte doit etre compréhensible par un utilisateur non technique
   . Période : {start_time} -> {end_time}.
    """

    client = InferenceClient(api_key=hf_token)
    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700
    )
    summary_paragraph = completion.choices[0].message.content.strip()
    if not summary_paragraph.endswith('.'):
        summary_paragraph += '.'
    

    intrusion_duration_seconds = max(timestamps) - min(timestamps)
    intrusion_duration = str(datetime.utcfromtimestamp(intrusion_duration_seconds).strftime("%H:%M:%S"))

    summary_json = {
    "total_actions": len(table_data) - 1,  # retirer la ligne d'entête
    "intrusion_start": start_time,
    "intrusion_duration": intrusion_duration 
    }  

    summary_json_path = os.path.join(outputs_folder, "intrusion_summary.json")
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=4, ensure_ascii=False)


    styles = getSampleStyleSheet()
    alert_style = ParagraphStyle("Alert", parent=styles["Title"],
                                 fontName="DejaVu", textColor=colors.red,
                                 fontSize=20, leading=24)
    section_style = ParagraphStyle("Section", parent=styles["Heading2"],
                                   fontName="DejaVu", textColor=colors.darkblue,
                                   spaceAfter=8)
    body_style = ParagraphStyle("Body", parent=styles["BodyText"],
                                fontName="DejaVu", fontSize=11, spaceAfter=12)

    pdf_path = os.path.join(outputs_folder, "intrusion_report.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    elements = []
    elements.append(Paragraph("ALERTE - INTRUSION DÉTECTÉE", alert_style))
    elements.append(Spacer(1,20))
    elements.append(Paragraph(f"Suspect : {person['name']}", body_style))
    elements.append(Paragraph(f"Période : {start_time} -> {end_time}", body_style))
    elements.append(Spacer(1,20))

    if os.path.isfile(person["image_local_path"]):
        img = Image(person["image_local_path"], width=2.5*inch, height=2.5*inch)
        img.hAlign = "CENTER"
        elements.append(img)

    elements.append(Paragraph("1. Résumé des activités", section_style))
    elements.append(Spacer(1,6))
    elements.append(Paragraph(summary_paragraph, body_style))
    elements.append(Spacer(1,16))

    elements.append(Paragraph("2. Tableau des activités clés", section_style))
    elements.append(Spacer(1,6))

    table = Table(table_data, colWidths=[4*cm, 7*cm, 6*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.black),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "DejaVu"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    elements.append(table)
    elements.append(Spacer(1,16))

    doc.build(elements)

    print(f" PDF généré ➜ {pdf_path}")
    print(f" Résumé JSON généré ➜ {summary_json_path}")

    return pdf_path, summary_json_path