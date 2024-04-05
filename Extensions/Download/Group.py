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




from nudenet import NudeDetector
import os

detector = NudeDetector()

female = ['FEMALE_GENITALIA_COVERED', 'FACE_FEMALE', 'BUTTOCKS_EXPOSED', 'FEMALE_BREAST_EXPOSED', 'FEMALE_GENITALIA_EXPOSED', 'FEET_EXPOSED', 'BELLY_COVERED', 'FEET_COVERED', 'ARMPITS_COVERED', 'ARMPITS_EXPOSED', 'FEMALE_BREAST_COVERED', 'BUTTOCKS_COVERED', 'BELLY_EXPOSED ']  
male = ['MALE_BREAST_EXPOSED', 'ANUS_EXPOSED', 'FACE_MALE', 'MALE_GENITALIA_EXPOSED', 'ANUS_COVERED']

# sample output
# [{'class': 'FEMALE_BREAST_EXPOSED',
#   'score': 0.8520756959915161,
#   'box': [130, 849, 1690, 1596]},
#  {'class': 'FEMALE_BREAST_EXPOSED',
#   'score': 0.7964769601821899,
#   'box': [1624, 454, 1257, 1010]},
#  {'class': 'BELLY_EXPOSED',
#   'score': 0.6901438236236572,
#   'box': [1371, 2217, 1586, 1817]}]


def classify_gender(result):
    average = []
    for item in result:
        if item['class'] in male:
            average.append('male') 
        elif item['class'] in female:
            average.append('female')
    if average:
        return max(set(average), key = average.count)
    else:
        return None

# usage
for i in os.listdir('Downloads'):
    path = os.path.join('Downloads', i)
    
    try:
        result = detector.detect(path)
        gender = classify_gender(result)
        if gender is not None:
            os.rename(path, os.path.join(gender, i))  
    except:
        pass