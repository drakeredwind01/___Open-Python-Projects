import cv2
import numpy as np
import tensorflow as tf
from grabscreen import grab_screen

# Load the face detector model
face_detector = cv2.CascadeClassifier("path/to/haarcascade_frontalface_default.xml")

# Load the emotion recognition model
emotion_detector = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, kernel_size=(3, 3), activation="relu", input_shape=(48, 48, 1)),
    tf.keras.layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
    tf.keras.layers.Dropout(0.25),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(7, activation="softmax")
])

# Load the weights for the emotion recognition model
emotion_detector.load_weights("path/to/emotion_recognition/weights.h5")

# Define the emotions
EMOTIONS = ["Angry", "Disgust", "Fear", "Happy", "Neutral", "Sad", "Surprise"]


def detect_face_emotions(screen):
    image = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_detector.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(screen, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Extract the face region of interest (ROI)
        face = image[y:y + h, x:x + w]
        face = cv2.resize(face, (48, 48))
        face = np.expand_dims(face, axis=-1)
        face = np.expand_dims(face, axis=0)

        # Predict the emotion
        preds = emotion_detector.predict(face)[0]
        emotion_bar_width = 40
        emotion_bar_height = h // len(EMOTIONS)
        for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
            bar_width = int(prob * emotion_bar_width)
            cv2.rectangle(screen, (x - emotion_bar_width, y + i * emotion_bar_height),
                          (x - emotion_bar_width + bar_width, y + (i + 1) * emotion_bar_height),
                          (255, 0, 0), -1)

        age = "23"
        ethnicity = "Asian"
        cv2.putText(screen, f"{age}, {ethnicity}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    return screen


# Define the region of the screen to capture
mon = (0, 40, 800, 640)

while True:
    screen = grab_screen(region=mon)
    screen = detect_face_emotions(screen)
    cv2.imshow("Screen", screen)

    if cv2.waitKey(25) & 0xFF == ord("q"):
        cv2.destroyAllWindows()
        break









'''

Collect or download a dataset of facial expression images. Some popular datasets include CK+, FER2013, and AffectNet. You can also create your own dataset by capturing images of faces with different expressions.



'''