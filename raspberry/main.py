from picamera import PiCamera
import requests

url = "https://cs270.buttercrab.net/upload-image"

while True:
    camera = PiCamera()
    camera.capture("image.jpg")
    files = {"file": open("image.jpg", "rb")}
    r = requests.post(url, files=files)
    print(r.text)
    camera.close()
