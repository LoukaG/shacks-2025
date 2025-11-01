from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame, QSpacerItem, QSizePolicy, QPushButton
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtCore import Qt, Signal

from app.ui.intrusion_report_window import IntrusionReportWindow
from ..utils.options import settings
from .reference_window import ReferenceWindow

class OptionsWindow(QWidget):
    reference_window_opened = Signal()
    reference_window_closed = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shacks 2025 - Options")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.resize(500, 400)
        
        self.reference_window = None
        self.intrusion_report_window = None
        
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
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f5f5f5;
                color: #000000;
                font-size: 13px;
                min-height: 25px;
            }
            QComboBox:hover {
                border: 2px solid #018849;
            }
            QComboBox:focus {
                border: 2px solid #016a37;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #000000;
                selection-background-color: #018849;
                selection-color: white;
            }
            QFrame#separator {
                background-color: #bdc3c7;
            }
            QLabel#status {
                color: #27ae60;
                font-size: 12px;
                font-style: italic;
                padding: 5px;
            }
            QPushButton {
                padding: 10px 20px;
                border: 2px solid #018849;
                border-radius: 5px;
                background-color: #f5f5f5;
                color: #018849;
                font-size: 13px;
                font-weight: bold;
                min-height: 25px;
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
        
        title_label = QLabel("Shacks 2025")
        title_label.setObjectName("title")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Système de sécurité intelligent")
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

        # Section Options
        options_layout = QVBoxLayout()
        options_layout.setSpacing(15)
        
        security_label = QLabel("Type de sécurité")
        security_label.setObjectName("section")
        options_layout.addWidget(security_label)

        security_desc = QLabel("Choisissez le mode de réaction en cas de détection d'intrus :")
        security_desc.setWordWrap(True)
        security_desc.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 5px;")
        options_layout.addWidget(security_desc)

        self.security_dropdown = QComboBox()
        self.security_dropdown.addItems(["Fermeture automatique", "Contre-espionnage"])
        options_layout.addWidget(self.security_dropdown)

        main_layout.addLayout(options_layout)
        
        # Section Image de référence
        reference_layout = QVBoxLayout()
        reference_layout.setSpacing(15)
        
        reference_label = QLabel("Image de référence")
        reference_label.setObjectName("section")
        reference_layout.addWidget(reference_label)

        reference_desc = QLabel("Définissez l'image de référence utilisée pour la détection d'intrus :")
        reference_desc.setWordWrap(True)
        reference_desc.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 5px;")
        reference_layout.addWidget(reference_desc)

        self.reference_button = QPushButton("Définir images de référence")
        self.reference_button.clicked.connect(self.on_set_reference)
        reference_layout.addWidget(self.reference_button)

        main_layout.addLayout(reference_layout)

        # Section Rapport d'intrusion
        reports_layout = QVBoxLayout()
        reports_layout.setSpacing(15)

        reports_label = QLabel("Rapports d'intrusion")
        reports_label.setObjectName("section")
        reports_layout.addWidget(reports_label)

        reports_desc = QLabel("Consultez les rapports d'intrusion générés :")
        reports_desc.setWordWrap(True)
        reports_desc.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 5px;")
        reports_layout.addWidget(reports_desc)

        self.reports_button = QPushButton("Voir les rapports")
        self.reports_button.clicked.connect(self.on_open_intrusion_report)
        reports_layout.addWidget(self.reports_button)

        main_layout.addLayout(reports_layout)
        
        # Espaceur pour pousser le contenu vers le haut
        main_layout.addStretch()

        self.setLayout(main_layout)

        # Charger les paramètres
        self.security_dropdown.setCurrentText(settings.get("security_mode"))

        self.security_dropdown.currentTextChanged.connect(self.on_change)

    def on_change(self, text):
        settings.set("security_mode", text)
    
    def on_set_reference(self):
        if self.reference_window is None or not self.reference_window.isVisible():
            self.reference_window = ReferenceWindow()
            self.reference_window.window_closed.connect(self.on_reference_window_closed)
            self.reference_window.showMaximized()
            self.reference_window_opened.emit()
        else:
            self.reference_window.activateWindow()
    def on_open_intrusion_report(self):
        if self.intrusion_report_window is None or not self.intrusion_report_window.isVisible():
            self.intrusion_report_window = IntrusionReportWindow()
            self.intrusion_report_window.showMaximized()
        else:
            self.intrusion_report_window.activateWindow()
    
    def on_reference_window_closed(self):
        self.reference_window_closed.emit()
        
