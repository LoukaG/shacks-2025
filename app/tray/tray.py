from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer
from ..ui.options_window import OptionsWindow
from ..camera.camera_capture import CameraCapture
from ..camera.intruder import Intruder
from pathlib import Path

class SystemTray(QSystemTrayIcon):
    def __init__(self, app):
        super().__init__(QIcon("assets/icon.png"), parent=None)
        self.app = app
        self.setToolTip("Shacks 2025 - Sécurité")

        menu = QMenu()
        options_action = QAction("Options", self)
        options_action.triggered.connect(self.open_options)
        menu.addAction(options_action)

        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.setVisible(True)
        self.show()

        self.windows = []
        self.camera = CameraCapture()
        
        # Construire l'array des images de référence
        reference_dir = Path("captures/reference")
        reference_images = []
        
        # Vérifier reference_1.jpg (obligatoire)
        ref1 = reference_dir / "reference_1.jpg"
        if ref1.exists():
            reference_images.append(str(ref1))
        
        # Vérifier reference_2.jpg (optionnel)
        ref2 = reference_dir / "reference_2.jpg"
        if ref2.exists():
            reference_images.append(str(ref2))
        
        # Vérifier reference_3.jpg (optionnel)
        ref3 = reference_dir / "reference_3.jpg"
        if ref3.exists():
            reference_images.append(str(ref3))
        
        # Créer le détecteur avec les images trouvées (minimum 1)
        if reference_images:
            self.intruder_detector = Intruder(reference_paths=reference_images)
            print(f"[Intruder] {len(reference_images)} image(s) de référence chargée(s) : {reference_images}")
        else:
            print("[Intruder] ATTENTION : Aucune image de référence trouvée !")
            self.intruder_detector = None

        # Compteur de détections consécutives
        self.intruder_count = 0
        self.threshold = 3  # marge de 3 détections

        # Timer toutes les 3 secondes
        self.timer = QTimer()
        self.timer.timeout.connect(self.tache_periodique)
        self.timer.start(1000)

    def open_options(self):
        win = OptionsWindow()
        win.reference_window_opened.connect(self.stop_monitoring)
        win.reference_window_closed.connect(self.start_monitoring)
        win.show()
        self.windows.append(win)

    def tache_periodique(self):
        try:
            # Vérifier si le détecteur est initialisé
            if self.intruder_detector is None:
                print("[Intruder] Pas de détecteur - aucune image de référence")
                return
            
            self.camera.capture_image()
            is_intruder_detected = self.intruder_detector.is_intruder(
                path_frame="captures/last_capture.jpg",
                tolerance=0.6
            )

            if is_intruder_detected:
                self.intruder_count += 1
                print(f"[Intruder] Détection {self.intruder_count}/{self.threshold}")
            else:
                self.intruder_count = 0  # reset si visage légitime détecté
                print("[Intruder] Visage reconnu, compteur réinitialisé.")

            # Action seulement après 3 détections consécutives
            if self.intruder_count >= self.threshold:
                self.trigger_intrusion_alert()
                self.intruder_count = 0  # reset après alerte

        except Exception as e:
            print(f"Erreur capture caméra : {e}")

    def trigger_intrusion_alert(self):
        """Action à exécuter après plusieurs détections."""
        self.showMessage(
            "Alerte Intrusion",
            "Un intrus a été détecté à plusieurs reprises !",
            QSystemTrayIcon.Critical
        )
        print("[Intruder] Alerte envoyée.")
    
    def stop_monitoring(self):
        """Arrête la surveillance et libère la caméra"""
        print("[Tray] Arrêt de la surveillance...")
        self.timer.stop()
        self.camera.release()
    
    def start_monitoring(self):
        """Redémarre la surveillance"""
        print("[Tray] Redémarrage de la surveillance...")
        self.camera = CameraCapture()
        
        # Recharger les images de référence
        reference_dir = Path("captures/reference")
        reference_images = []
        
        for i in range(1, 4):
            ref = reference_dir / f"reference_{i}.jpg"
            if ref.exists():
                reference_images.append(str(ref))
        
        if reference_images:
            self.intruder_detector = Intruder(reference_paths=reference_images)
            print(f"[Intruder] {len(reference_images)} image(s) de référence rechargée(s)")
        else:
            print("[Intruder] ATTENTION : Aucune image de référence trouvée !")
            self.intruder_detector = None
        
        self.timer.start(3000)

    def quit_app(self):
        self.timer.stop()
        self.camera.release()
        self.camera.delete_last_image()
        self.app.quit()
