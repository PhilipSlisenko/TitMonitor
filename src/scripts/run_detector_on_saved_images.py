# flake8: noqa
# pytype: skip-file
import json
import os
import uuid
from glob import glob
from datetime import datetime

import cv2
from tqdm import tqdm

from src.config import config
from src.main import DBWriter, Detector


def main():
    """
    Run predictor on every n images that were taken between timestamps, save detections to db.
    """
    # args = parse_args()
    db_writer = DBWriter(config.dbhost, config.dbname, config.dbuser, config.dbpassword)
    detector = Detector(config.model_path)

    rows = db_writer.select_images_between_timestamps(datetime(2021, 10, 13, 13, 25, 29), datetime(2021, 10, 13, 16, 00), False)

    for row in tqdm(rows[::10]):
        img = cv2.imread(os.path.join(config.root_dir_to_save_images, row['filename']))
        if img is None:
            continue
        dets = detector.detect(img).pandas()
        for box in dets.xyxyn[0].itertuples():
            box = box._asdict()
            detection_id = str(uuid.uuid4())
            coords_dict = {
                'xmin': box['xmin'],
                'ymin': box['ymin'],
                'xmax': box['xmax'],
                'ymax': box['ymax']
            }
            # print(detection_id, json.dumps(coords_dict), box['name'], box['confidence'],
            #                                 row['image_id'])
            db_writer.insert_detection(detection_id, json.dumps(coords_dict), box['name'], box['confidence'],
                                            row['image_id'])
        db_writer.update_detector_ran_status_of_image(row['image_id'], True)