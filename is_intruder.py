import cv2
import face_recognition

def is_intruder(path_frame: str, path_reference: str, tolerance: float = 0.6) -> bool:
    """
    Path_frame: chemin vers l'image capturée.
    Path_reference: chemin vers l'image de référence.
    Tolerance: seuil de tolérance pour la comparaison des visages.
    Retourne True si c’est un intrus (autre personne ou aucun visage reconnu).
    """
    # Charger l'image de référence
    reference_image = face_recognition.load_image_file(path_reference)
    ref_encodings = face_recognition.face_encodings(reference_image)
    if not ref_encodings:
        raise ValueError("Aucun visage détecté dans l’image de référence.")
    reference_encoding = ref_encodings[0]

    # Charger l'image capturée
    frame_image = cv2.imread(path_frame)
    if frame_image is None:
        raise FileNotFoundError(f"Impossible de charger l'image {path_frame}")
    rgb_frame = cv2.cvtColor(frame_image, cv2.COLOR_BGR2RGB)

    # Extraire les visages détectés dans la frame
    face_encodings = face_recognition.face_encodings(rgb_frame)
    if not face_encodings:
        return False  # aucun visage => pas considéré comme intrus

    # Comparer le premier visage détecté
    match = face_recognition.compare_faces([reference_encoding], face_encodings[0], tolerance)[0]
    return not match  # True si c’est un intrus
