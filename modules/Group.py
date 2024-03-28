from PIL import Image
import numpy as np


def predict_image(model, image_path):
    img = Image.open(image_path)
    
    img = img.resize((180, 180)) 
    img_array = np.array(img)
    if img_array.shape[-1] == 4: 
        img_array = img_array[:, :, :3]
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    predictions = model.predict(img_array)
    return np.argmax(predictions)