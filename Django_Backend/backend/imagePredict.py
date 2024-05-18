import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models')))

import logging

import PIL
import torch
import numpy as np
from mivolo.predictor import Predictor
from timm.utils import setup_default_logging

_logger = logging.getLogger("inference")

def getImgtoModel(image_data):
    config = {
        'img' : image_data,
        # 'detector-weights' : '..\..\models\yolov8x_person_face.pt',
        # 'checkpoint' : '..\..\models\model_imdb_cross_person_4.22_99.46.pth.tar',
        'with-persons' : False,
        'disable-faces' : False,
        'draw' : False,
        'device' : 'cpu'
    }
    setup_default_logging()

    if torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
    
    predictor = Predictor(config, verbose=True)
    file = config['img']
    img = PIL.Image.open(file)
    img_rgb = img.convert("RGB")
    img_array = np.array(img_rgb)
    detected_objects, out_im = predictor.recognize(img_array)
    return detected_objects