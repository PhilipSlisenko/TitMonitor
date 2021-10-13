from src.main import Operator, DBWriter, Detector
from src.config import config
from tqdm import tqdm
import datetime
import cv2
from src.scripts.run_detector_on_saved_images import main

# db_writer = DBWriter(config.dbhost, config.dbname, config.dbuser, config.dbpassword)

# rows = db_writer.select_high_conf_snapshots()
# detector = Detector(config.model_path)
#
# for row in tqdm(rows):
#     dets = detector.detect(cv2.imread(row['filename']))
#     dets.files[0] = row['filename']  # so that det.save() saved with desired filename
#     dets.save('runs/1/')

# res = db_writer.select_images_between_timestamps(datetime.datetime(2021, 10, 8), datetime.datetime.now(), False)


main()


