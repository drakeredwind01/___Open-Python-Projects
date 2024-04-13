import cv2
import numpy as np
from grabscreen import grab_screen

# Define the function to detect the face and emotions
def detect_face_emotions(screen):
    # Load the face detector model
    prototxt_path = "path/to/face_detector/deploy.prototxt"
    model_path = "path/to/face_detector/res10_300x300_ssd_iter_140000.caffemodel"
    face_detector = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

    # Load the emotion recognition model
    model_path = "path/to/emotion_recognition/model.hdf5"
    emotion_detector = load_model(model_path)

    # Define the emotion labels
    EMOTIONS = ["Angry", "Disgust", "Fear", "Happy", "Neutral", "Sad", "Surprise"]

    # Detect the face in the image
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    face_detector.setInput(blob)
    detections = face_detector.forward()

    # Process each detected face
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            # Get the face coordinates and draw a box around the face
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)

            # Extract the face ROI and preprocess it for emotion recognition
            face = image[startY:endY, startX:endX]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            face = cv2.resize(face, (48, 48))
            face = face.astype("float") / 255.0
            face = img_to_array(face)
            face = np.expand_dims(face, axis=0)

            # Make the emotion prediction and display the emotion bars on the left side of the face
            preds = emotion_detector.predict(face)[0]
            emotion_bar_width = 40
            emotion_bar_height = (endY - startY) // len(EMOTIONS)
            for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
                bar_width = int(prob * emotion_bar_width)
                cv2.rectangle(image, (startX - emotion_bar_width, startY + i * emotion_bar_height),
                              (startX - emotion_bar_width + bar_width, startY + (i + 1) * emotion_bar_height),
                              (255, 0, 0), -1)
            # Display the age and ethnicity information
            age = "23"
            ethnicity = "Asian"
            cv2.putText(image, f"{age}, {ethnicity}", (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    return image

# Load the image and detect the face and emotions
screen = grab_screen(region=mon)
mon = (0, 40, 800, 640)

# image_path = "path/to/image.jpg"
# image = cv2.imread(image_path)
output
