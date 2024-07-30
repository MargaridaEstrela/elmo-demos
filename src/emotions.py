from rmn import RMN
from PIL import Image
import io
import cv2
import time
import random

# Load the Haar Cascade model
face_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


class Emotions:
    def __init__(self, elmo):
        self.rmn = RMN()
        self.elmo = elmo
        self.emotions = {
            "angry": 0,
            "disgust": 1,
            "fear": 2,
            "happy": 3,
            "sad": 4,
            "surprise": 5,
            "neutral": 6,
        }
        self.detected_emotion = ""
        self.accuracy = 0

    def get_detected_emotion(self):
        return self.detected_emotion

    def get_accuracy(self):
        return self.accuracy

    def generate_emotion(self):
        """
        Generates a random emotion for the player.
        """
        return random.choice(list(self.emotions.keys()))

    def center_player(self):
        """
        Centers the player's face in the frame by adjusting the robot's pan and
        tilt angles. If no faces detected, returns and continues the game.
        """
        frame = self.elmo.grab_image()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))

        if len(faces) == 0:
            print("Cannot center player. No faces detected.")
            return

        # Get frame center and dimensions
        frame_width, frame_height = frame.shape[1], frame.shape[0]
        frame_center_x = frame_width / 2
        frame_center_y = frame_height / 2

        # Extract face bounding box
        x, y, w, h = faces[0]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Calculate adjustments
        horizontal_adjustment = (frame_center_x - (x + w / 2)) // 4
        vertical_adjustment = (frame_center_y - (y + h / 2)) // 8

        # Get pan and tilt angles
        pan = self.elmo.get_pan()
        tilt = self.elmo.get_tilt()

        new_pan_angle = pan + int(horizontal_adjustment / 3)
        new_tilt_angle = tilt - int(vertical_adjustment / 3)

        # Check if values are within bounds
        new_pan_angle = self.elmo.check_pan_angle(new_pan_angle)
        new_tilt_angle = self.elmo.check_tilt_angle(new_tilt_angle)

        # Update default values
        self.elmo.set_pan(new_pan_angle)
        self.elmo.set_tilt(new_tilt_angle)

        self.elmo.move_pan(new_pan_angle)
        time.sleep(2)
        self.elmo.move_tilt(new_tilt_angle)

        print(f"Horizontal adjustment: {int(horizontal_adjustment/3)}")
        print(f"Vertical adjustment: {int(vertical_adjustment/3)}")

    def take_picture(self):
        """
        Plays a sound, displays a countdown sequence of icons (3, 2, 1), and
        captures the image.
        """
        self.elmo.play_sound("countdown.wav")
        self.elmo.set_image("3.png")
        time.sleep(1)
        self.elmo.set_image("2.png")
        time.sleep(0.7)
        self.elmo.set_image("1.png")
        time.sleep(0.4)

        self.elmo.set_image("camera_v2.png")
        time.sleep(1)
        self.elmo.set_image("black.png")
        self.elmo.set_icon("loading.gif")

        return self.elmo.grab_image()

    def analyse_emotion(self):
        """
        Analyzes the emotion.
        """
        frame = self.take_picture()

        # RMN analysis
        try:
            results = self.rmn.detect_emotion_for_single_frame(frame)
            self.detected_emotion = results[0]["emo_label"]
            self.accuracy = round(results[0]["emo_proba"] * 100)

        except Exception as e:
            print(e)

        return frame, results

    def give_feedback(self, emotion=None):
        """
        Gives feedback based on the detected emotion.
        """
        feedback_mapping = {
            "angry": ("angry.png", "angry.wav", 3),
            "disgust": ("disgust.png", "disgust.wav", 4),
            "fear": ("surprise.png", "fear.wav", 5),
            "happy": ("blush.png", "love.wav", 7),
            "sad": ("cry.png", "cry.wav", 4),
            "surprise": ("surprise.png", "surprise.wav", 4),
            "neutral": ("stare.png", "elmo_idm.png", 2),
        }

        image, sound, delay = feedback_mapping[self.detected_emotion]

        time.sleep(2)

        if emotion:
            if self.detected_emotion == emotion:
                self.elmo.set_image("joy.png")
                self.elmo.play_sound("joy.wav")
                time.sleep(5)
                self.elmo.set_image("stare.png")
                self.elmo.set_icon("elmo_idm.png")
            else:
                self.elmo.set_image("stare.png")
                self.elmo.play_sound(f"bad_{emotion}.wav")
                time.sleep(6)

        else:
            if self.detected_emotion != "neutral":
                self.elmo.set_image(image)
                self.elmo.play_sound(sound)
                time.sleep(delay)

        self.elmo.set_image("stare.png")
        self.elmo.set_icon("elmo_idm.png")

    def numpy_to_data(self, image_array):
        """
        Convert numpy array to data that PySimpleGUI Image element can understand.
        """
        image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image_rgb)
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            data = output.getvalue()
        return data

    def draw_results(self, frame, results):
        return self.numpy_to_data(self.rmn.draw(frame, results))
