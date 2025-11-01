import cv2
from deepface import DeepFace


# Constantes
REFERENCE_IMAGE = "photo_jas\photo_4.jpg"  # Votre photo de référence
THRESHOLD = 0.4  # Plus bas = plus strict (0.3-0.5 recommandé)

video_capture = cv2.VideoCapture(0)
print("📷 Caméra ouverte. Appuyez sur SPACE pour capturer, Q pour quitter.")

result = None

while True:
    ret, frame = video_capture.read()   # Ret : booléen, frame : image capturée
    
    if not ret:
        break
    
    # Sauvegarder temporairement la frame actuelle
    cv2.imwrite("temp_frame.jpg", frame)
    
    try:
        # Vérifier si c'est la même personne
        verification = DeepFace.verify(
            img1_path=REFERENCE_IMAGE,
            img2_path="temp_frame.jpg",
            model_name="VGG-Face",  # ou "Facenet", "OpenFace", "DeepFace"
            enforce_detection=False
        )
        
        is_match = verification["verified"]
        distance = verification["distance"]
        
        # Dessiner le résultat
        color = (0, 255, 0) if is_match else (0, 0, 255)
        label = f"MATCH (dist: {distance:.2f})" if is_match else f"PAS MATCH (dist: {distance:.2f})"
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
    except Exception as e:
        cv2.putText(frame, "Aucun visage detecte", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    cv2.imshow('Detection', frame)
    
    # Gestion des touches
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord(' '):
        # Capturer le résultat
        try:
            verification = DeepFace.verify(
                img1_path=REFERENCE_IMAGE,
                img2_path="temp_frame.jpg",
                model_name="VGG-Face",
                enforce_detection=False
            )
            result = verification["verified"]
            print(f"\n{'='*40}")
            print(f"RÉSULTAT: {result}")
            print(f"Distance: {verification['distance']:.3f}")
            print(f"{'='*40}\n")
        except Exception as e:
            result = False
            print(f"Erreur: {e}")
        break

video_capture.release()
cv2.destroyAllWindows()

# Nettoyer
import os
if os.path.exists("temp_frame.jpg"):
    os.remove("temp_frame.jpg")

# ============================================
# RÉSULTAT FINAL
# ============================================
if result is not None:
    print(f"C'est moi: {result}")
else:
    print("Aucune capture effectuée")