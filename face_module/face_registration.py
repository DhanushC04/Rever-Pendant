import cv2
import os
import numpy as np

def register_person(data_dir="faces"):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    name = input("Enter your name: ").strip()
    person_dir = os.path.join(data_dir, name)
    if not os.path.exists(person_dir):
        os.makedirs(person_dir)
    else:
        print("Person already registered. Adding more images.")

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    count = 0
    print("Look at the camera. Capturing 20 face samples...")

    while count < 20:
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (200, 200))
            file_path = os.path.join(person_dir, f"{count}.jpg")
            cv2.imwrite(file_path, face_img)
            count += 1
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, f"Samples: {count}/20", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            if count >= 20:
                break
        cv2.imshow("Register Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if count >= 20:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Registration complete for {name}.")

if __name__ == "__main__":
    register_person()
