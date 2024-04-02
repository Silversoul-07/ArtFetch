from PIL import Image
import numpy as np
from keras import load_model
import os

class Grouper:
    def __init__(self) -> None:
        self.model = load_model('model.keras')

    def predict(self, image_path):
        pass
        
    def start(self):
        '''Models classifies the images and sorts them into respective folders'''   
        for image in os.listdir('images'):
            image_path = os.path.join('images', image)
            prediction = self.predict(image_path)
            if prediction == 0:
                os.rename(image_path, os.path.join('images', 'like', image))
            else:
                os.rename(image_path, os.path.join('images', 'dislike', image))