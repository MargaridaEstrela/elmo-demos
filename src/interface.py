import sys
import cv2
import time
import threading
import random
import PySimpleGUI as sg

from server import ElmoServer
from emotions import Emotions

elmo = None
elmo_ip = None
emotions = None
window = None
debug_mode = False
connect_mode = False
random_mode_active = False
random_mode_stop_event = threading.Event()


def create_layout():
    """
    Creates the layout for the interface.

    Returns:
        list: The layout of the interface as a list of elements.
    """
    sg.theme("LightBlue3")

    general_layout = [
        [sg.Text("", size=(1, 1))],
        [
            sg.Text("", size=(8, 1)),
            sg.Button("Toggle Behaviour", size=(15, 1), button_color=("white", "red")),
            sg.Button("Toggle Motors", size=(15, 1), button_color=("white", "green")),
            sg.Text("", size=(9, 1)),
            sg.Text("Speakers", size=(10, 1)),
            sg.Text("", size=(13, 1)),
            sg.Button("Center Player", size=(15, 1)),
            sg.Text("", size=(8, 1)),
        ],
        [
            sg.Text("", size=(8, 1)),
            sg.Text("Pan", size=(3, 1)),
            sg.InputText(key="pan_value", size=(18, 1)),
            sg.Button("Set", key="SetPan", size=(8, 1)),
            sg.Text("", size=(9, 1)),
            sg.Button("⬆", size=(7, 1)),
            sg.Text("", size=(15, 1)),
            sg.Button("Default Screen", size=(15, 1)),
            sg.Text("", size=(8, 1)),
        ],
        [
            sg.Text("", size=(8, 1)),
            sg.Text("Tilt", size=(3, 1)),
            sg.InputText(key="tilt_value", size=(18, 1)),
            sg.Button("Set", key="SetTilt", size=(8, 1)),
            sg.Text("", size=(9, 1)),
            sg.Button("⬇", size=(7, 1)),
            sg.Text("", size=(15, 1)),
            sg.Button("Default Icon", size=(15, 1)),
            sg.Text("", size=(8, 1)),
        ],
        [
            sg.Text("", size=(8, 1)),
            sg.Button("Toggle Blush", size=(15, 1), button_color=("white", "red")),
            sg.Button("Check Speakers", size=(15, 1)),
            sg.Text("", size=(37, 1)),
            sg.Button("Close All", size=(15, 1)),
            sg.Text("", size=(8, 1)),
        ],
        [sg.Text("", size=(1, 2))],
        [
            sg.Text("", size=(2, 1)),
            sg.Image(filename="", key="image"),
            sg.Text("", size=(2, 1)),
        ],
        [sg.Text("", size=(1, 1))],
    ]

    modes_layout = [
        [sg.Text("", size=(1, 2))],
        [
            sg.Push(),
            sg.Button(image_data=sg.EMOJI_BASE64_HAPPY_STARE, key="Stare"),
            sg.Text("", size=(2, 1)),
            sg.Button(image_data=sg.EMOJI_BASE64_HAPPY_CONTENT, key="Blush"),
            sg.Text("", size=(2, 1)),
            sg.Button(image_data=sg.EMOJI_BASE64_HAPPY_JOY, key="Joy"),
            sg.Text("", size=(2, 1)),
            sg.Button(image_data=sg.EMOJI_BASE64_HAPPY_HEARTS, key="Love"),
            sg.Text("", size=(2, 1)),
            sg.Button(image_data=sg.EMOJI_BASE64_HAPPY_WINK, key="Blink"),
            sg.Push(),
        ],
        [sg.Text("", size=(1, 2))],
        [
            sg.Push(),
            sg.Button(image_data=sg.EMOJI_BASE64_SAD, key="Sad"),
            sg.Text("", size=(2, 1)),
            sg.Button(image_data=sg.EMOJI_BASE64_FRUSTRATED, key="Angry"),
            sg.Text("", size=(2, 1)),
            sg.Button(image_data=sg.EMOJI_BASE64_THINK, key="Think"),
            sg.Text("", size=(2, 1)),
            sg.Button(image_data=sg.EMOJI_BASE64_CRY, key="Cry"),
            sg.Text("", size=(2, 1)),
            sg.Button(image_data=sg.EMOJI_BASE64_SCREAM, key="Fear"),
            sg.Push(),
        ],
        [sg.Text("", size=(1, 2))],
        [
            sg.Push(),
            sg.Button("Orange", size=(15, 1)),
            sg.Text("", size=(2, 1)),
            sg.Button("Blue", size=(15, 1)),
            sg.Text("", size=(2, 1)),
            sg.Button("IDMind", size=(15, 1)),
            sg.Push(),
        ],
        [sg.Text("", size=(1, 1))],
        [
            sg.Push(),
            sg.Button("Fireworks", size=(15, 1)),
            sg.Text("", size=(2, 1)),
            sg.Button("Heart", size=(15, 1)),
            sg.Text("", size=(2, 1)),
            sg.Button("Heartbeat", size=(15, 1)),
            sg.Push(),
        ],
        [sg.Text("", size=(1, 2))],
        [
            sg.Push(),
            sg.Button("Random", size=(15, 1), button_color=("white", "green")),
            sg.Push(),
        ],
        [sg.Text("", size=(1, 2))],
    ]

    emotions_layout = [
        [sg.Text("", size=(1, 2))],
        [
            sg.Push(),
            sg.Button("Angry", size=(10, 1), key="angry"),
            sg.Text("", size=(1, 1)),
            sg.Button("Disgust", size=(10, 1), key="disgust"),
            sg.Text("", size=(1, 1)),
            sg.Button("Fear", size=(10, 1), key="fear"),
            sg.Text("", size=(1, 1)),
            sg.Button("Happy", size=(10, 1), key="happy"),
            sg.Push(),
        ],
        [
            sg.Push(),
            sg.Button("Sad", size=(10, 1), key="sad"),
            sg.Text("", size=(1, 1)),
            sg.Button("Surprise", size=(10, 1), key="surprise"),
            sg.Text("", size=(1, 1)),
            sg.Button("Neutral", size=(10, 1), key="neutral"),
            sg.Text("", size=(1, 1)),
            sg.Button("Record", size=(10, 1), button_color=("white", "red")),
            sg.Push(),
        ],
        [sg.Text("", size=(1, 2))],
        [
            sg.Push(),
            sg.Image(filename="", key="emotion_results"),
            sg.Push(),
        ],
        [sg.Text("", size=(1, 2))],
        [
            sg.Push(),
            sg.Text("", size=(60, 1), key="results"),
            sg.Push(),
        ],
        [sg.Text("", size=(1, 2))],
    ]

    layout = [
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab("General", general_layout),
                        sg.Tab("Modes", modes_layout),
                        sg.Tab("Emotions", emotions_layout),
                    ]
                ],
                key="-TAB GROUP-",
                expand_x=True,
                expand_y=True,
            ),
        ]
    ]

    return layout


def handle_events():
    """
    Handle events from the GUI window.

    This function reads events from the GUI window and performs corresponding
    actions based on the event type.
    """
    global random_mode_active

    event, values = window.read(timeout=1)

    if not debug_mode and not connect_mode:
        img = elmo.grab_image()
        img_bytes = cv2.imencode(".png", img)[1].tobytes()
        window["image"].update(data=img_bytes)

    if event == sg.WIN_CLOSED or event == "Close All":
        elmo.close_all()
        window.close()
        random_mode_stop_event.set()

    if event and event != "__TIMEOUT__":
        random_mode_stop_event.set()  # Stop the random mode if any button is pressed

    button_actions = {
        "Toggle Behaviour": lambda: toggle_button(
            event, elmo.toggle_behaviour, elmo.get_control_behaviour, "Toggle Behaviour"
        ),
        "Toggle Motors": lambda: toggle_button(
            event, elmo.toggle_motors, elmo.get_control_motors, "Toggle Motors"
        ),
        "SetPan": lambda: set_pan_tilt(
            values["pan_value"], elmo.move_pan, elmo.set_pan
        ),
        "SetTilt": lambda: set_pan_tilt(
            values["tilt_value"], elmo.move_tilt, elmo.set_tilt
        ),
        "Toggle Blush": lambda: toggle_button(
            event, elmo.toggle_blush, elmo.get_control_blush, "Toggle Blush"
        ),
        "Check Speakers": lambda: elmo.play_sound("countdown.wav"),
        "⬆": lambda: elmo.increase_volume(),
        "⬇": lambda: elmo.decrease_volume(),
        "Center Player": lambda: emotions.center_player(),
        "Default Screen": lambda: elmo.set_image("stare.png"),
        "Default Icon": lambda: elmo.set_icon("elmo_idm.png"),
        "Random": toggle_random_mode,
    }

    if event in button_actions:
        if event != "Random":
            random_mode_active = False
            random_mode_stop_event.set()
        button_actions[event]()

    emoji_actions = {
        "Stare": lambda: set_emoji("stare.png"),
        "Joy": lambda: set_emoji("joy.png", "joy.wav"),
        "Love": lambda: set_emoji("love.png", "love.wav", "heartbeat.gif"),
        "Blush": lambda: set_emoji("blush.png", "love.wav"),
        "Blink": lambda: blink_emoji(),
        "Sad": lambda: set_emoji("sad.png"),
        "Cry": lambda: set_emoji("cry.png", "cry.wav"),
        "Think": lambda: set_emoji("thinking.png"),
        "Angry": lambda: set_emoji("angry.png", "angry.wav"),
        "Fear": lambda: set_emoji("fear.png", "fear.wav"),
    }

    if event in emoji_actions:
        emoji_actions[event]()

    icon_actions = {
        "Orange": lambda: elmo.set_icon("orange.png"),
        "Blue": lambda: elmo.set_icon("blue.png"),
        "IDMind": lambda: elmo.set_icon("elmo_idm.png"),
        "Fireworks": lambda: elmo.set_icon("fireworks.gif"),
        "Heart": lambda: elmo.set_icon("heart.png"),
        "Heartbeat": lambda: elmo.set_icon("heartbeat.gif"),
    }

    if event in icon_actions:
        icon_actions[event]()

    emotion_buttons = [
        "angry",
        "disgust",
        "fear",
        "happy",
        "sad",
        "surprise",
        "neutral",
    ]
    if event in emotion_buttons or event == "Record":
        frame, results = emotions.analyse_emotion()
        if results:
            image = emotions.draw_results(frame, results)
            window["emotion_results"].update(data=image)
            res = format_emotion_results(results[0]["proba_list"])
            window["results"].update(res)
            if event != "Record":
                emotions.give_feedback(event)
            else:
                emotions.give_feedback()


def toggle_random_mode():
    """
    Toggles the random mode.
    """
    global random_mode_active
    random_mode_active = not random_mode_active
    if random_mode_active:
        random_mode_stop_event.clear()
        random_thread = threading.Thread(target=run_random_mode)
        random_thread.start()
    else:
        random_mode_stop_event.set()


def run_random_mode():
    """
    Runs the random mode, cycling through all modes randomly.
    """
    global random_mode_active
    modes = [
        "Stare",
        "Joy",
        "Love",
        "Blush",
        "Blink",
        "Sad",
        "Cry",
        "Think",
        "Angry",
        "Fear",
    ]
    while random_mode_active:
        random.shuffle(modes)  # Shuffle the modes each time the loop starts
        for mode in modes:
            if random_mode_stop_event.is_set():
                return
            set_emoji_mode(mode)
            time.sleep(5)  # Adjust the delay as needed


def set_emoji_mode(mode):
    emoji_actions = {
        "Stare": lambda: set_emoji("stare.png"),
        "Joy": lambda: set_emoji("joy.png", "joy.wav"),
        "Love": lambda: set_emoji("love.png", "love.wav", "heartbeat.gif"),
        "Blush": lambda: set_emoji("blush.png", "love.wav"),
        "Blink": lambda: blink_emoji(),
        "Sad": lambda: set_emoji("sad.png"),
        "Cry": lambda: set_emoji("cry.png", "cry.wav"),
        "Think": lambda: set_emoji("thinking.png"),
        "Angry": lambda: set_emoji("angry.png", "angry.wav"),
        "Fear": lambda: set_emoji("fear.png", "fear.wav"),
    }

    if mode in emoji_actions:
        emoji_actions[mode]()


def toggle_button(event, toggle_func, check_func, button_key):
    toggle_func()
    if check_func():
        window[button_key].update(button_color=("white", "green"))
    else:
        window[button_key].update(button_color=("white", "red"))


def set_pan_tilt(value, move_func, set_func):
    if value:
        move_func(value)
        set_func(int(value))


def set_emoji(image, sound=None, icon=None):
    elmo.set_image(image)
    if icon:
        elmo.set_icon(icon)
    else:
        elmo.set_icon("elmo_idm.png")
    if sound:
        elmo.play_sound(sound)


def blink_emoji():
    elmo.set_icon("elmo_idm.png")
    elmo.set_image("stare.png")
    time.sleep(0.75)
    elmo.set_image("blink.png")
    time.sleep(0.75)
    elmo.set_image("stare.png")


def format_emotion_results(proba_list):
    return (
        f'Angry: {round(proba_list[0]["angry"] * 100)}  '
        f'Disgust: {round(proba_list[1]["disgust"] * 100)}  '
        f'Fear: {round(proba_list[2]["fear"] * 100)}  '
        f'Happy: {round(proba_list[3]["happy"] * 100)}  '
        f'Sad: {round(proba_list[4]["sad"] * 100)}  '
        f'Surprise: {round(proba_list[5]["surprise"] * 100)}  '
        f'Neutral: {round(proba_list[6]["neutral"] * 100)}'
    )


def main():
    """
    This function parses command line arguments, initializes the logger, starts the server,
    creates the game window, and enters the event loop to handle user interactions.
    """
    global elmo, elmo_ip, emotions, window, debug_mode, connect_mode

    # Parse arguments
    if len(sys.argv) == 1:
        elmo_ip = ""
        elmo_port = 0
        client_ip = ""
        debug_mode = True  # Running in debug mode (just GUI)
    elif len(sys.argv) == 4:
        elmo_ip, elmo_port, client_ip = sys.argv[1:4]
        debug_mode = False
    elif len(sys.argv) == 5:
        elmo_ip, elmo_port, client_ip = sys.argv[1:4]
        if sys.argv[4] == "--connect":
            connect_mode = True
    else:
        print("Usage: python3 interface.py <elmo_ip> <elmo_port> <client_ip>")
        return

    # Start server
    elmo = ElmoServer(elmo_ip, int(elmo_port), client_ip, debug_mode, connect_mode)
    emotions = Emotions(elmo)

    layout = create_layout()

    # Create window
    title = "Elmo"
    if elmo_ip:
        title += f"  idmind@{elmo_ip}"
    window = sg.Window(title, layout, finalize=True)

    if not debug_mode and not connect_mode:
        # Initial image update
        img = elmo.grab_image()
        img_bytes = cv2.imencode(".png", img)[1].tobytes()
        window["image"].update(data=img_bytes)

    # Event loop
    while True:
        handle_events()


if __name__ == "__main__":
    main()
