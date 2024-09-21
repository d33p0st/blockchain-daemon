from PIL import Image, ImageTk
from tkinter import Tk
from io import BytesIO
import requests
import os


class Icon:
    def __init__(self):
        self.url = "https://github.com/d33p0st/blockchain-daemon/raw/main/assets/blockchain.png"
    
    def set(self, master: Tk):
        if requests.get("https://www.google.com").status_code == 200:
            response = requests.get(self.url)
            img_data = BytesIO(response.content)
        else:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon-dat.py'), 'rb+') as ref:
                img_data = ref.read()
        
        image = Image.open(img_data)
        photo = ImageTk.PhotoImage(image)
        master.iconphoto(False, photo)
