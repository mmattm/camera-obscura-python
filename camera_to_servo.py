import os
from dotenv import load_dotenv

import cv2

import pynput
from pynput import keyboard
import base64
import requests
import json

import RPi.GPIO as GPIO
import pigpio
import time

# Configuration du servo
# Activer dans le terminal la 1ère fois: $ sudo pigpio
servo = 18
pwm = pigpio.pi()
pwm.set_mode(servo, pigpio.OUTPUT)
pwm.set_PWM_frequency(servo, 50)

# Eteindre le servo
# pwm.set_PWM_dutycycle(servo, 0)
# pwm.set_PWM_frequency(servo, 0)


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

                # Activer le servo plusieurs fois en fonction du résultat
                number_of_pulse = 2 if output == "up" else 1

                for _ in range(number_of_pulse):
                    print("0 deg")
                    pwm.set_servo_pulsewidth(servo, 500)
                    time.sleep(0.25)

                    print("90 deg")
                    pwm.set_servo_pulsewidth(servo, 1500)
                    time.sleep(0.25)

                pwm.set_PWM_dutycycle(servo, 0)

                # GPIO.cleanup()

            cam.release()


# Evenements du clavier
with keyboard.Listener(
        # on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
