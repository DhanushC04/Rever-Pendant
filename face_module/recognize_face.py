import cv2
import os
import numpy as np

def load_faces(data_dir="faces"):
    faces = []
    labels = []
    label_map = {}
    current_label = 0
    for person_name in os.listdir(data_dir):
        person_dir = os.path.join(data_dir, person_name)
        if not os.path.isdir(person_dir):
            continue
        label_map[current_label] = person_name
        for img_name in os.listdir(person_dir):
            img_path = os.path.join(person_dir, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                faces.append(img)
                labels.append(current_label)
        current_label += 1
    return faces, labels, label_map

def recognize_face(data_dir="faces"):
    faces, labels, label_map = load_faces(data_dir)
    if len(faces) == 0:
        print("⚠️ No faces found. Please register faces first.")
        return "Unknown"
    
    # Create and train the recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)
    print("📸 Looking for faces... Press 'q' to quit.")

    detected_name = "Unknown"

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_rects = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces_rects:
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (200, 200))
            label, confidence = recognizer.predict(face_img)
            name = label_map.get(label, "Unknown")
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, f"{name} ({confidence:.0f})", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

            # If we got a valid name, save and break
            if name != "Unknown" and confidence < 80:  # confidence threshold
                detected_name = name
                break

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or detected_name != "Unknown":
            break

    cap.release()
    cv2.destroyAllWindows()
    return detected_name

if __name__ == "__main__":
    name = recognize_face()
    print(f"✅ Detected Person: {name}")


