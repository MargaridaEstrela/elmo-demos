import socket
import cv2
import numpy as np
import requests


class ElmoServer:
    """
    Represents the server for controlling Elmo.

    Args:
        elmo_ip (str): The IP address of the Elmo device.
        elmo_port (int): The port number for communication with the Elmo device.
        client_ip (str): The IP address of the client.
        debug (bool, optional): Specifies whether debug mode is enabled.
                                Defaults to False.
        connect_mode (bool, optional): Specifies whether the server is in
                                    connect mode. Defaults to False.

    Methods:
        set_pan(default_pan): Set the pan angle
        set_tilt(default_tilt): Set the tilt angle
        get_pan(): Get the pan angle
        get_tilt(): Get the tilt angle
        get_control_motors(): Get the status of the motor control
        get_control_behaviour(): Get the status of the behaviour control
        get_control_blush(): Get the status of the behaviour blush
        connect_elmo(): Connect to the Elmo robot
        send_message(message): Send a message to the Elmo robot
        send_request_command(command, **kwargs): Send a request command to the
                                                Elmo robot
        toggle_motors(): Toggle the motor control
        toggle_behaviour(): Toggle the behaviour control
        toggle_blush(): Toggle the blush control
        check_pan_angle(self, angle): Check if the pan angle is valid
        check_tilt_angle(self, angle): Check if the tilt angle is valid
        move_pan(angle): Pan move with a specific angle
        move_tilt(angle): Tilt move with a specific angle
        increase_volume(): Send message to increase the volume
        decrease_volume(): Send message to decrease the volume
        grab_image(): Capture an image
        set_image(image_name): Set the image
        set_icon(icon_name): Set the icon
        play_sound(sound): Play a sound
        play_video(video_name): Play a video
        close_all(): Close all connections

    """

    def __init__(self, elmo_ip, elmo_port, client_ip, debug=False, connect_mode=False):
        self.elmo_ip = elmo_ip
        self.elmo_port = elmo_port
        self.client_ip = client_ip
        self.elmo_socket = None

        self.connect_mode = connect_mode

        self.pan = 0
        self.tilt = 0

        self.send_request_command("enable_behaviour", name="look_around", control=False)
        self.send_request_command("enable_behaviour", name="blush", control=False)
        self.send_request_command("set_tilt_torque", control=True)
        self.send_request_command("set_pan_torque", control=True)

        self.control_motors = True
        self.control_behaviour = False
        self.control_blush = False

        if not debug:
            self.connect_elmo()
            self.debug = False
        else:
            self.debug = True

        self.set_image("stare.png")
        self.set_icon("elmo_idm.png")

    def set_pan(self, pan_angle):
        """
        Sets the pan angle.
        """
        self.pan = pan_angle

    def set_tilt(self, tilt_angle):
        """
        Sets the tilt angle.
        """
        self.tilt = tilt_angle

    def get_pan(self):
        """
        Returns the pan angle.

        """
        return self.pan

    def get_tilt(self):
        """
        Returns the tilt angle.
        """
        return self.tilt

    def get_control_motors(self):
        """
        Returns the control motors object.

        Returns:
            bool: The control motors object.
        """
        return self.control_motors

    def get_control_behaviour(self):
        """
        Returns the control behaviour object.

        Returns:
            bool: The control behaviour object.
        """
        return self.control_behaviour

    def get_control_blush(self):
        """
        Returns the control blush object.

        Returns:
            bool: The control blush object.
        """
        return self.control_blush

    def connect_elmo(self):
        """
        Connects to the Elmo robot.
        """
        self.elmo_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_message(self, message):
        """
        Sends a message to the Elmo robot.

        Args:
            message (str): The message to be sent.
        """
        print(message)

        if self.debug == True:
            return "debug"

        self.elmo_socket.sendto(message.encode("utf-8"), (self.elmo_ip, self.elmo_port))

    def send_request_command(self, command, **kwargs):
        """
        Sends a request command to the Elmo robot.
        """
        if not self.connect_mode:
            try:
                url = "http://" + self.elmo_ip + ":8001/command"
                kwargs["op"] = command
                res = requests.post(url, json=kwargs, timeout=1).json()
                if not res["success"]:
                    return
            except Exception as e:
                return

    def toggle_motors(self):
        """
        Toggles the control of the motors and send a message and request command.
        """
        self.control_motors = not self.control_motors
        self.send_message(f"motors::{self.control_motors}")
        self.send_request_command("set_tilt_torque", control=self.control_motors)
        self.send_request_command("set_pan_torque", control=self.control_motors)

    def toggle_behaviour(self):
        """
        Toggles the control behaviour and send a message and request command.
        """
        self.control_behaviour = not self.control_behaviour
        self.send_message(f"behaviour::{self.control_behaviour}")
        self.send_request_command(
            "enable_behaviour", name="look_around", control=self.control_behaviour
        )

    def toggle_blush(self):
        """
        Toggles the control blush and send a message and request command.
        """
        self.control_blush = not self.control_blush
        self.send_message(f"blush::{self.control_blush}")
        self.send_request_command(
            "enable_behaviour", name="blush", control=self.control_blush
        )

    def check_pan_angle(self, angle):
        """
        Checks if the pan angle is valid. If it is not valid then returns a
        valid angle.
        """
        if angle > 40:
            angle = 40
        elif angle < -40:
            angle = -40
        return angle

    def check_tilt_angle(self, angle):
        """
        Checks if the tilt angle is valid. If it is not valid then returns a
        valid angle.
        """
        if angle > 15:
            angle = 15
        elif angle < -15:
            angle = -15
        return angle

    def move_pan(self, angle):
        """
        Moves the pan with a specific angle.
        """
        self.send_message(f"pan::{angle}")

    def move_tilt(self, angle):
        """
        Moves the tilt with a specific angle.
        """
        self.send_message(f"tilt::{angle}")

    def increase_volume(self):
        """
        Sends a message to increase the volume.
        """
        self.send_message("speakers::increaseVolume")

    def decrease_volume(self):
        """
        Sends a message to decrease the volume.
        """
        self.send_message("speakers::decreaseVolume")

    def grab_image(self):
        """
        Captures an image.
        """
        if self.debug:
            return

        if self.connect_mode:
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                print("Failed to open camera")

            ret, frame = cap.read()  # Capture a frame

            if not ret:
                print("Failed to capture frame")
                cap.release()
                return np.full((480, 640, 3), 26, dtype=np.uint8)

            cap.release()

        else:
            url = f"http://{self.elmo_ip}:8080/stream.mjpg"
            response = requests.get(url, stream=True)

            if response.status_code == 200:  # Is a valid response
                stream = response.iter_content(chunk_size=1024)
                bytes_ = b""
                for chunk in stream:
                    bytes_ += chunk
                    a = bytes_.find(b"\xff\xd8")
                    b = bytes_.find(b"\xff\xd9")
                    if a != -1 and b != -1:
                        jpg = bytes_[a : b + 2]
                        bytes_ = bytes_[b + 2 :]
                        frame = cv2.imdecode(
                            np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR
                        )
                        break

        # Resize the image to 480x640
        frame = cv2.resize(frame, (640, 480))
        return frame

    def set_image(self, image_name):
        """
        Sets the image.
        """
        self.send_message(f"image::{image_name}")

    def play_video(self, video_name):
        """
        Play a video.
        """
        self.send_message(f"video::{video_name}")

    def set_icon(self, icon_name):
        """
        Sets the icon.
        """
        self.send_message(f"icon::{icon_name}")

    def play_sound(self, sound):
        """
        Plays the specified sound.
        """
        self.send_message(f"sound::{sound}")

    def close_all(self):
        """
        Closes all connections and shuts down the server.

        Sends a "game::off" message to the robot.
        If the debug flag is set to False, it also shuts down the Elmo socket.

        """
        if self.debug == False:
            self.elmo_socket.shutdown(socket.SHUT_RDWR)
            self.elmo_socket.close()
            return
        return
