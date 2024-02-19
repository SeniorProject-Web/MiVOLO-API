from typing import Optional, Tuple

import numpy as np
from mivolo.model.mi_volo import MiVOLO
from mivolo.model.yolo_detector import Detector
from mivolo.structures import PersonAndFaceResult


class Predictor:
    def __init__(self, config, verbose: bool = False):
        self.detector = Detector(config['detector-weights'], config['device'], verbose=verbose)
        self.age_gender_model = MiVOLO(
            config['checkpoint'],
            config['device'],
            half=True,
            use_persons=True,
            disable_faces=False,
            verbose=verbose,
        )
        self.draw = config['draw']

    def recognize(self, image: np.ndarray) -> Tuple[PersonAndFaceResult, Optional[np.ndarray]]:
        detected_objects: PersonAndFaceResult = self.detector.predict(image)
        self.age_gender_model.predict(image, detected_objects)

        out_im = None
        if self.draw:
            # plot results on image
            out_im = detected_objects.plot()

        return detected_objects, out_im

