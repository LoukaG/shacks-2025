import os
import json
from datetime import datetime, timezone, timedelta
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

current_dir = os.path.dirname(os.path.abspath(__file__))

font_path = os.path.join(current_dir, "..", "fonts", "DejaVuSans.ttf")
font_path = os.path.abspath(font_path)

# Enregistrement de la police (Déjà fait, mais s'assurer qu'il est en haut)
pdfmetrics.registerFont(TTFont("DejaVu", font_path))


def generate_intrusion_report(input_json_path: str,
                               output_folder: str = "reports",
                               model_name: str = "openai/gpt-oss-120b",
                               hf_token: str = None) -> dict:

    os.makedirs(output_folder, exist_ok=True)
    outputs_folder = os.path.join(output_folder, "outputs")
    os.makedirs(outputs_folder, exist_ok=True)

    with open(input_json_path, "r", encoding="utf-8") as f:
        logs = json.load(f)

    person = {
        "name": "Suspect inconnu",
        "image_local_path": "/home/ubuntu/shacks-2025/ror.jpg"
    }

    # ----------- PDF STYLES IMPROVED -----------
    styles = getSampleStyleSheet()

    # Style pour le corps de texte général
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="DejaVu", # Utilisation de la police enregistrée
        fontSize=11.5,
        leading=15,
        spaceAfter=10
    )

    # NOUVEAU STYLE pour les cellules du tableau
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["BodyText"],
        fontName="DejaVu",  
        fontSize=9,         
        leading=11,
        alignment=0, # Alignement à gauche
        spaceAfter=0
    )


    table_data = [
        [
            Paragraph("Heure (UTC)", cell_style),
            Paragraph("Action", cell_style),
            Paragraph("Détails", cell_style)
        ]
    ] 

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

       
        table_data.append([
            Paragraph(dt, cell_style),
            Paragraph(action, cell_style),
            Paragraph(details_str, cell_style)
        ])

    start_time = datetime.fromtimestamp(min(timestamps), timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    end_time   = datetime.fromtimestamp(max(timestamps), timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # ----------- SUMMARY WITH LLM ------------------------

    prompt = f"""
    Tu es un expert cybersécurité. Voici les actions détectées sur un ordinateur :

    {logs_text}

    Explique clairement en racontant ce que la personne a fait , pourquoi c'est suspect, quels risques pour l'ordinateur,
    et suggère des recommandations simples. Contexte non technique. 
    mets une paragraphe bien écrite,fluide et claire.
    ignore les screenshots,c'est nous qui ont fait les screenshot pour savoir ce qu'il a fait
    Période : {start_time} -> {end_time}.
    """

    client = InferenceClient(api_key=hf_token)
    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    summary_paragraph = completion.choices[0].message.content.strip()
    if not summary_paragraph.endswith('.'):
        summary_paragraph += '.'

    intrusion_duration_seconds = max(timestamps) - min(timestamps)
    duration_timedelta = timedelta(seconds=intrusion_duration_seconds)
    
    # Obtenir les secondes totales (en ignorant les microsecondes)
    total_seconds = int(duration_timedelta.total_seconds())

    # Calculer Jours, Heures, Minutes, Secondes
    days = total_seconds // (3600 * 24)
    hours = (total_seconds // 3600) % 24
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Formater la durée en HH:MM:SS ou Jours, HH:MM:SS si nécessaire
    if days > 0:
        intrusion_duration = f"{days} jour{'s' if days > 1 else ''}, {hours:02}:{minutes:02}:{seconds:02}"
    else:
        # Format standard HH:MM:SS
        intrusion_duration = f"{hours:02}:{minutes:02}:{seconds:02}" 

    summary_json = {
        "total_actions": len(logs), 
        "intrusion_start": start_time,
        "intrusion_duration": intrusion_duration
    }

    summary_json_path = os.path.join(outputs_folder, "intrusion_summary.json")
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=4, ensure_ascii=False)

   

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="DejaVu",
        fontSize=24,
        textColor=colors.HexColor("#D91E18"),
        alignment=1,  # center
        spaceAfter=20
    )

    header_style = ParagraphStyle(
        "Header",
        parent=styles["Heading2"],
        fontName="DejaVu",
        fontSize=15,
        textColor=colors.HexColor("#004C99"),
        spaceAfter=10
    )
    
    pdf_path = os.path.join(outputs_folder, "intrusion_report.pdf")
    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=1.8*cm, bottomMargin=2*cm
    )

    elements = []

    # Le contenu du résumé (summary_paragraph) est aussi encapsulé par Paragraph,
    # donc il utilisera correctement la police "DejaVu"
    elements.append(Paragraph("⚠️ RAPPORT D'INTRUSION INFORMATIQUE", title_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Suspect identifié : <b>{person['name']}</b>", body_style))
    elements.append(Paragraph(f"Période d'activité : <b>{start_time}</b> → <b>{end_time}</b>", body_style))
    elements.append(Paragraph(f"Durée : {intrusion_duration}", body_style))
    elements.append(Spacer(1, 10))

    if os.path.isfile(person["image_local_path"]):
        img = Image(person["image_local_path"], width=2.2*inch, height=2.2*inch)
        img.hAlign = "CENTER"
        elements.append(img)
        elements.append(Spacer(1, 14))

    elements.append(Paragraph("1️-Résumé des actions suspectes", header_style))
    elements.append(Paragraph(summary_paragraph, body_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("2️-Détails des activités détectées", header_style))

    # ----------- TABLEAU FINAL (Reste inchangé) -----------

    col_widths = [4*cm, 5*cm, 7*cm]

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "DejaVu"), # Entête utilise "DejaVu"
        # La ligne suivante n'est plus nécessaire car le contenu est déjà Paragraph(..., cell_style)
        # ("FONTNAME", (0,1), (-1,-1), "DejaVu"), 
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
        ("LEFTPADDING", (0,0), (-1,-1), 3),
        ("RIGHTPADDING", (0,0), (-1,-1), 3),
    ]))

    elements.append(table)

    doc.build(elements)

    print(f" PDF généré ➜ {pdf_path}")
    print(f"Résumé JSON généré ➜ {summary_json_path}")

    return pdf_path, summary_json_path



def enrich_logs_with_descriptions(
    input_json_path: str,
    model_name: str = "openai/gpt-oss-120b",
    hf_token: str = None
) -> list:
    """
    Prend un JSON de logs, et pour chaque entrée 'screenshot', ne parle pas pourquoi on a fait un screenshot,juste décris le screenshot qui se base
    sur le contexte des actions précédentes. Utilise un LLM pour cela. 
    génère une description basée sur les actions loggées juste avant, 
    en utilisant un LLM. Retourne un nouveau JSON enrichi.
    """
    
    with open(input_json_path, "r", encoding="utf-8") as f:
        logs = json.load(f)

    # Initialiser le client LLM une seule fois
    client = InferenceClient(api_key=hf_token)
    
    # Créer une copie pour le nouveau JSON
    enriched_logs = []
    
    # Buffer pour stocker les actions récentes (jusqu'à un certain point)
    context_buffer = []
    CONTEXT_SIZE = 10 # Nombre d'événements précédents à inclure dans le contexte

    for i, entry in enumerate(logs):
        new_entry = entry.copy()
        
        if entry["type"] == "screenshot":
            timestamp = entry.get("timestamp", 0)
            
            # 1. Déterminer les actions pertinentes PRÉCÉDANT ce screenshot
            # On prend les entrées depuis l'index (i - CONTEXT_SIZE) jusqu'à i-1
            
            start_index = max(0, i - CONTEXT_SIZE)
            relevant_logs = logs[start_index:i]
            
            # Formater le contexte pour le prompt
            context_text = ""
            for log in relevant_logs:
                ts = log.get("timestamp", 0)
                dt = datetime.fromtimestamp(ts, timezone.utc).strftime("%H:%M:%S.%f")[:-3]
                action = log.get("type", "")
                details = {k: v for k, v in log.items() if k not in ["timestamp", "type"]}
                details_str = ", ".join([f"{k}:{v}" for k, v in details.items()])
                context_text += f"[{dt}] {action}: {details_str}\n"

            window_title = entry.get("window_title", "Inconnue")
            
            prompt = f"""
            On a pris un screenshot à l'instant dans la fenêtre : "{window_title}".
            Basé UNIQUEMENT sur la séquence d'actions(et qui ne sont pas des logs type screenshot) JUSTE AVANT ce screenshot , rédige une 
            description CONCISE (maximum deux phrases courtes) de ce que l'utilisateur était 
            probablement en train de faire et ce que le screenshot capture.
            
            Séquence des actions précédentes (Format: [Heure_Relative] TypeAction: Détails):
            ---
            {context_text.strip()}
            ---
            
            Exemple de sortie attendue : "L'utilisateur était en train de fermer l'application Spotify après avoir cliqué sur la croix de fermeture de la fenêtre." 
            
            Ta description :
            """
            
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150 # Limiter la taille de la description
                )
                description = completion.choices[0].message.content.strip()
                
                # Optionnel : Nettoyer la sortie si le LLM répond de manière inattendue
                if description.startswith("Description :"):
                     description = description.replace("Description :", "").strip()

            except Exception as e:
                print(f"⚠️ Erreur LLM pour le screenshot {entry['file_path']}: {e}")
                description = "Description non disponible (Erreur LLM)."

            new_entry["description"] = description
            print(f"Description générée pour : {entry['file_path']}")

        enriched_logs.append(new_entry)
        
    return enriched_logs
if __name__ == "__main__":
    
    INPUT_JSON_PATH = "/home/ubuntu/shacks-2025/logs/json_final.json"
    OUTPUT_FOLDER = "/home/ubuntu/shacks-2025/my_reports"
    MODEL_NAME = "openai/gpt-oss-120b"
    HF_TOKEN = os.getenv("HF_API_TOKEN")
    
    try:
        # 1. ENRICHIR LE JSON AVEC LES DESCRIPTIONS
        print("1/2 - Enrichissement du JSON avec les descriptions des screenshots...")
        enriched_logs = enrich_logs_with_descriptions(
            input_json_path=INPUT_JSON_PATH,
            model_name=MODEL_NAME,
            hf_token=HF_TOKEN
        )
        
        # 2. SAUVEGARDER LE NOUVEAU JSON ENRICHI
        enriched_output_path = os.path.join(OUTPUT_FOLDER, "outputs", "enriched_logs.json")
        os.makedirs(os.path.dirname(enriched_output_path), exist_ok=True)
        with open(enriched_output_path, "w", encoding="utf-8") as f:
            json.dump(enriched_logs, f, indent=4, ensure_ascii=False)
        print(f"Nouveau JSON enrichi sauvegardé ➜ {enriched_output_path}")

        # 3. GÉNÉRER LE RAPPORT PDF (en utilisant le JSON original pour le résumé de l'activité globale)
        # Note: J'ai gardé l'appel à generate_intrusion_report tel quel pour la génération du PDF
        # car son prompt LLM était spécifiquement pour le *résumé global* et non pour les descriptions individuelles.
        print("2/2 - Génération du rapport PDF...")
        result = generate_intrusion_report(
            INPUT_JSON_PATH, # On utilise le JSON initial pour le résumé global (comme avant)
            output_folder=OUTPUT_FOLDER,
            model_name=MODEL_NAME,
            hf_token=HF_TOKEN
        )
        print("Rapport final généré.")
        print("Résultat du rapport PDF :", result)

     
        screenshot_example = next((log for log in enriched_logs if log['type'] == 'screenshot'), None)
        if screenshot_example:
            print("\n--- Exemple d'entrée 'screenshot' enrichie ---")
            print(json.dumps(screenshot_example, indent=4, ensure_ascii=False))
            print("--------------------------------------------")

    except Exception as e:
        print(f"Erreur lors du processus : {e}")
        print("Vérifiez le chemin vers 'DejaVuSans.ttf', la validité du HF_API_TOKEN, et que le JSON initial existe.")