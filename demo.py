import logging
import os

import cv2
import torch
from mivolo.predictor import Predictor
from timm.utils import setup_default_logging

_logger = logging.getLogger("inference")


def main():
    config = {
        'output_dir' : 'output/',
        'img' : 'Untitled.png',
        'detector-weights' : 'models\yolov8x_person_face.pt',
        'checkpoint' : 'models\model_imdb_cross_person_4.22_99.46.pth.tar',
        'with-persons' : False,
        'disable-faces' : False,
        'draw' : False,
        'device' : 'cpu'
    }
    setup_default_logging()

    if torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
    
    os.makedirs(config['output_dir'], exist_ok=True)

    predictor = Predictor(config, verbose=True)
    img = cv2.imread(config['img'])
    print(img.shape)
    detected_objects, out_im = predictor.recognize(img)

    if config['draw']:
        bname = os.path.splitext(os.path.basename(config['img']))[0]
        filename = os.path.join(config['output_dir'], f"out_{bname}.jpg")
        cv2.imwrite(filename, out_im)
        _logger.info(f"Saved result to {filename}")


if __name__ == "__main__":
    main()
