# flake8: noqa
# pytype: skip-file
import os
import uuid
from glob import glob

import cv2
from tqdm import tqdm


def main(self, path: str):
    """
    Run predictor on images in directory, save results to db.
    - list files
    - load files
    - run predictor
    - save result to db
    """
    filenames = glob(os.path.join(path, '*.jpg'))
    for filename in tqdm(filenames):
        img = cv2.imread(filename)
        det = self.detector.detect(img).pandas()
        # image_id = str(uuid.uuid4())
        # print(image_id, None, filename)
        self.db_writer.insert_image_metadata(image_id, None, filename)
        for box in det.xyxyn[0].itertuples():
            box = box._asdict()
            detection_id = str(uuid.uuid4())
            coords_dict = {
                'xmin': box['xmin'],
                'ymin': box['ymin'],
                'xmax': box['xmax'],
                'ymax': box['ymax']
            }
            # print(detection_id, coords_dict, box['name'], box['confidence'], image_id)
            self.db_writer.insert_detection(detection_id, json.dumps(coords_dict), box['name'], box['confidence'],
                                            image_id)