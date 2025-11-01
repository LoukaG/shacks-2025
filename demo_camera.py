import cv2
import face_recognition


REFERENCE_IMAGE = "old\photo_1.jpg"  # Votre photo de référence
TOLERANCE = 0.6  # Plus bas = plus strict (0.4-0.7)


print("Chargement de l'image de référence...")
reference_image = face_recognition.load_image_file(REFERENCE_IMAGE)
reference_encoding = face_recognition.face_encodings(reference_image)[0]
print("✓ Image chargée\n")


video_capture = cv2.VideoCapture(0)
print("📷 Caméra ouverte. Appuyez sur SPACE pour capturer, Q pour quitter.")

result = None

while True:
    ret, frame = video_capture.read()
    
    if not ret:
        break
    
    # Convertir et détecter les visages
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    
    # Vérifier chaque visage détecté
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Comparer avec la référence
        matches = face_recognition.compare_faces([reference_encoding], face_encoding, TOLERANCE)
        is_match = matches[0]
        
        # Dessiner un rectangle (vert = match, rouge = pas match)
        color = (0, 255, 0) if is_match else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        label = "MATCH" if is_match else "PAS MATCH"
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    cv2.imshow('Detection', frame)
    
    # Gestion des touches
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord(' '):
        # Capturer le résultat
        if len(face_encodings) > 0:
            matches = face_recognition.compare_faces([reference_encoding], face_encodings[0], TOLERANCE)
            result = matches[0]
            print(f"\n{'='*40}")
            print(f"RÉSULTAT: {result}")
            print(f"{'='*40}\n")
        else:
            result = False
            print("Aucun visage détecté")
        break

video_capture.release()
cv2.destroyAllWindows()

# ============================================
# RÉSULTAT FINAL
# ============================================
if result is not None:
    print(f"C'est moi: {result}")
else:
    print("Aucune capture effectuée")