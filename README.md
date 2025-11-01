# shacks-2025
# 🛡️ GuardianPeek  
### Ne laissez plus votre écran devenir une histoire.

---

## 🚀 Présentation

**GuardianPeek** est une application de **surveillance intelligente** qui protège votre ordinateur quand vous l’oubliez ouvert.  
Grâce à la caméra et à la reconnaissance faciale, GuardianPeek détecte toute personne non autorisée devant l’écran et **active automatiquement un mode de protection** :

- 🔒 **Verrouillage / extinction immédiate**  
- 🕵️ **Mode espionnage** : enregistre toutes les actions effectuées sur l’ordinateur  
- 🧠 **Résumé automatique** : envoie les journaux dans un **LLM** qui crée un **PDF clair et structuré** de tout ce qui s’est passé  

> En clair : si quelqu’un touche à votre poste pendant votre absence, GuardianPeek le sait, le documente et vous le livre dans un rapport PDF.

---

## ✨ Fonctionnalités principales

- 🎥 **Surveillance temps réel** via la webcam  
- 👁️ **Reconnaissance de visage** (personnes « safe » vs intrus)  
- ⚙️ **Actions configurables** :
  - `lock` — Verrouille l’écran  
  - `shutdown` — Éteint le poste  
  - `collect` — Journalise toutes les actions locales  
  - `summarize` — Génère un rapport PDF avec résumé LLM  
- 📂 **Sauvegarde automatique** des incidents avec historique local  
- 🧾 **Génération de PDF** propre et lisible (avec captures optionnelles)  
- 🔐 **Confidentialité respectée** — tout peut rester 100 % local  

---

## 🧩 Architecture technique

| Composant | Technologie |
|------------|-------------|
| Détection visage | `face_recognition`, `OpenCV` |
| Agent local | Python (service ou CLI) |
| Résumé automatique | LLM local ou distant (configurable) |
| Génération PDF | `reportlab` / `weasyprint` |
| Interface | CLI + mini serveur web (FastAPI / Flask) |
| Sécurité | Chiffrement AES + TLS |

---

## ⚙️ Installation

```bash
# Cloner le projet
git clone https://github.com/votreorg/guardianpeek.git
cd guardianpeek

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # sous Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Copier et éditer la configuration
cp config.example.yaml config.yaml
# -> Ajoutez les visages autorisés, le modèle LLM, et vos préférences

# Lancer l'application
python guardianpeek/agent.py --config config.yaml
