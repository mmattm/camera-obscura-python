import os
from dotenv import load_dotenv

import cv2

import pynput
from pynput import keyboard
import base64
import requests
import json

load_dotenv()


def on_release(key):
    if 'char' in dir(key):
        if key.char == "p":
            print("\nphoto")

            # Activation de la caméra
            cam = cv2.VideoCapture(0)
            ret, img = cam.read()

            if ret:
                # scale_percent = 60  # percent of original size
                # width = int(img.shape[1] * scale_percent / 100)
                # height = int(img.shape[0] * scale_percent / 100)
                # dim = (width, height)

                # resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

                # cv2.imshow("test", resized)
                # cv2.waitKey()
                # cv2.destroyAllWindows()

                # Transformer l'image en base 64
                retval, buffer = cv2.imencode('.jpg', img)
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                dataurl = f'data:image/jpg;base64,{jpg_as_text}'

                # Requète vers l'API
                # Laisser vide la question si juste description automatique de l'image
                question = "Is the person giving a thumbs up or down? answer:"

                resp = requests.post(
                    os.getenv('DOMAIN'),
                    json={"image": dataurl,
                          "visualQuestion": question},
                    headers={"Content-Type": "application/json"})
                answer = resp.json()

                output = answer["prediction"]["output"]
                print(output)

            cam.release()


# Evenements du clavier
with keyboard.Listener(
        # on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
