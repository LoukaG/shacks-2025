from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
	QGridLayout, QSizePolicy, QPushButton
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QEvent
from pathlib import Path

class IntrusionReportWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Shacks 2025 - Rapports d'intrusion")
		self.setWindowIcon(QIcon("assets/icon.png"))
		self.resize(900, 650)

		self.setStyleSheet("""
			QWidget {
				background-color: #f5f5f5;
				font-family: 'Segoe UI', Arial, sans-serif;
			}
			QLabel#title {
				color: #2c3e50;
				font-size: 24px;
				font-weight: bold;
			}
			QLabel#subtitle {
				color: #7f8c8d;
				font-size: 12px;
			}
			QLabel#section {
				color: #34495e;
				font-size: 14px;
				font-weight: bold;
				margin-top: 10px;
			}
			QFrame#separator {
				background-color: #bdc3c7;
			}
			/* Carte de rapport */
			QFrame#card {
				background-color: #ffffff;
				border: 1px solid #e0e0e0;
				border-radius: 10px;
			}
			QLabel#cardTitle {
				color: #2c3e50;
				font-size: 14px;
				font-weight: bold;
			}
			QLabel#cardMeta {
				color: #7f8c8d;
				font-size: 12px;
			}
			QLabel#thumb {
				background-color: #ecf0f1;
				border: 1px solid #bdc3c7;
				border-radius: 5px;
			}
			QPushButton {
				padding: 8px 16px;
				border: 2px solid #018849;
				border-radius: 5px;
				background-color: #f5f5f5;
				color: #018849;
				font-size: 12px;
				font-weight: bold;
			}
			QPushButton:hover {
				background-color: #f0f9f5;
				border: 2px solid #016a37;
				color: #016a37;
			}
			QPushButton:pressed {
				background-color: #e0f2ea;
				border: 2px solid #014d28;
				color: #014d28;
			}
		""")

		main_layout = QVBoxLayout()
		main_layout.setContentsMargins(30, 30, 30, 30)
		main_layout.setSpacing(20)

		# En-tête avec icône et titre
		header_layout = QHBoxLayout()
		header_layout.setSpacing(15)

		icon_label = QLabel()
		icon_label.setPixmap(QPixmap("assets/icon.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
		icon_label.setFixedSize(64, 64)
		header_layout.addWidget(icon_label)

		title_layout = QVBoxLayout()
		title_layout.setSpacing(5)

		title_label = QLabel("Rapports d'intrusion")
		title_label.setObjectName("title")
		title_layout.addWidget(title_label)

		subtitle_label = QLabel("Historique des événements et éléments visuels")
		subtitle_label.setObjectName("subtitle")
		title_layout.addWidget(subtitle_label)

		header_layout.addLayout(title_layout)
		header_layout.addStretch()

		main_layout.addLayout(header_layout)

		# Séparateur
		separator = QFrame()
		separator.setObjectName("separator")
		separator.setFrameShape(QFrame.HLine)
		separator.setFixedHeight(2)
		main_layout.addWidget(separator)

		# Section
		section_label = QLabel("Rapports")
		section_label.setObjectName("section")
		main_layout.addWidget(section_label)

		# Zone scrollable
		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		scroll.setFrameShape(QFrame.NoFrame)

		content = QWidget()
		grid = QGridLayout(content)
		grid.setContentsMargins(0, 0, 0, 0)
		grid.setHorizontalSpacing(16)
		grid.setVerticalSpacing(16)

		# Charger les images de référence actuelles (si présentes)
		self.reference_dir = Path("captures/reference")
		self.reference_images = []
		for i in range(1, 4):
			path = self.reference_dir / f"reference_{i}.jpg"
			if path.exists():
				self.reference_images.append(str(path))

		# Données fictives
		items = self._fake_reports(12)

		# Ajouter les cartes en grille (3 colonnes)
		columns = 3
		for idx, item in enumerate(items):
			row = idx // columns
			col = idx % columns
			card = self._create_card(item["name"], item["date"], self.reference_images)
			grid.addWidget(card, row, col)

		print(f"[IntrusionReportWindow] cartes créées: {len(items)}, images de référence: {len(self.reference_images)}")

		scroll.setWidget(content)
		main_layout.addWidget(scroll)

		self.setLayout(main_layout)

	def _fake_reports(self, n):
		data = []
		# Contenu fictif: noms et dates d'exemple
		for i in range(1, n + 1):
			data.append({
				"name": f"Intrusion #{i}",
				"date": f"01/11/2025 1{(i%10)}:{(i*7)%60:02d}",
			})
		return data

	def _create_card(self, name: str, date: str, image_paths: list[str]):
		card = QFrame()
		card.setObjectName("card")
		card_layout = QVBoxLayout(card)
		card_layout.setContentsMargins(12, 12, 12, 12)
		card_layout.setSpacing(10)

		# Image de couverture: une seule image de référence, taille fixe
		if image_paths:
			cover = QLabel()
			cover.setObjectName("thumb")
			cover.setAlignment(Qt.AlignCenter)
			cover.setFixedSize(260, 195)  # Taille fixe pour éviter les boucles de resize
			cover.setScaledContents(False)
			
			pix = QPixmap(image_paths[0])
			if not pix.isNull():
				# Redimensionner une seule fois à la taille fixe
				scaled = pix.scaled(260, 195, Qt.KeepAspectRatio, Qt.SmoothTransformation)
				cover.setPixmap(scaled)
			else:
				cover.setText("Image invalide")
				cover.setStyleSheet("color: #95a5a6; font-size: 12px;")
			card_layout.addWidget(cover)
		else:
			placeholder = QLabel("Aucune image de référence")
			placeholder.setAlignment(Qt.AlignCenter)
			placeholder.setStyleSheet("color: #95a5a6; font-size: 12px;")
			placeholder.setObjectName("thumb")
			placeholder.setFixedSize(260, 195)
			card_layout.addWidget(placeholder)

		# Infos (nom + date)
		name_label = QLabel(name)
		name_label.setObjectName("cardTitle")
		name_label.setStyleSheet("background-color: transparent;")
		date_label = QLabel(date)
		date_label.setObjectName("cardMeta")
		date_label.setStyleSheet("background-color: transparent;")

		card_layout.addWidget(name_label)
		card_layout.addWidget(date_label)

		# Bouton pour afficher le rapport complet
		btn = QPushButton("Afficher rapport complet")
		btn.clicked.connect(lambda: self.on_show_full_report(name))
		card_layout.addWidget(btn)

		# Forcer la carte à s'étirer correctement
		card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		return card

	def on_show_full_report(self, report_name: str):
		"""Action temporaire pour afficher le rapport complet."""
		print(f"[IntrusionReportWindow] Afficher rapport complet: {report_name}")

