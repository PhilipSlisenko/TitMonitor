"""
- capture image
- run inference
- save image to disc
- put image info, detection info into db
"""
import copy
import os
import queue
import signal
import sys
import threading
from datetime import datetime

import cv2
import numpy as np
import psycopg2
import torch
from loguru import logger

from src.config import Config


class BufferlessVideoCapture:
    def __init__(self, stream_url: str):
        self.cap = cv2.VideoCapture(stream_url)
        if not self.cap.isOpened():
            raise Exception("Cannot connect to the stream.")
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get()

    def release(self):
        self.cap.release()


class DiscWriter:
    def __init__(self, save_images_to: str):
        self.save_images_to = save_images_to
        os.makedirs(save_images_to, exist_ok=True)

    def _thread_func(self, filename: str, image: np.ndarray):
        cv2.imwrite(os.path.join(self.save_images_to, filename), image)

    def save_image(self, image: np.ndarray, filename: str):
        t = threading.Thread(target=self._thread_func, args=(filename, image))
        t.start()


class Detector:
    def __init__(self, model_path: str):
        self.model = torch.hub.load('ultralytics/yolov5', 'custom',
                                    path=model_path)

    def detect(self, img: np.ndarray):
        """"
        :param img: image array as how it's read by cv2 imread: HxWxC in BGR
        """
        detection = self.model(img[:, :, ::-1])
        return detection

    def rename_detection_filename(self, detection, filename: str):
        """
        Renames filename inside detection object so that .save() method saves detection result with desired filename.
        """
        detection = copy.deepcopy(detection)
        detection.files[0] = filename
        return detection


class DBWriter:
    def __init__(self, dbhost: str, dbname: str, dbuser: str, dbpassword: str):
        self.dbhost = dbhost
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpassword = dbpassword
        self._open_connection()

    def _open_connection(self):
        self.conn = psycopg2.connect(host=self.dbhost,
                                     database=self.dbname,
                                     user=self.dbuser,
                                     password=self.dbpassword)

    def _reopen_conn_if_closed(self):
        if self.conn.closed:
            self._open_connection()

    def insert_image_metadata(self, image_id: str, timestamp: datetime, filename: str):
        self._reopen_conn_if_closed()
        sql = """INSERT INTO images(image_id, timestamp, filename) VALUES(%s, %s, %s);"""
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(sql, (image_id, timestamp, filename))

    def insert_detection(self, detection_id: str, coords: datetime, class_: str, conf: float, image_id: str):
        self._reopen_conn_if_closed()
        sql = """INSERT INTO detections(detection_id, coords, class, conf, image_id) VALUES(%s, %s, %s, %s, %s);"""
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(sql, (detection_id, coords, class_, conf, image_id))


class Operator:
    def __init__(self, config: Config):
        logger.info('Initing operator')
        self.cap = BufferlessVideoCapture(config.stream_url)
        self.disc_writer = DiscWriter(config.root_dir_to_save_images)
        self.db_writer = DBWriter(config.dbhost, config.dbname, config.dbuser, config.dbpassword)
        self.detector = Detector(config.model_path)

        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):
        self.cap.release()
        print('You pressed Ctrl+C!')
        sys.exit(0)

    def start_recording(self):
        """
        - capture
        - disc_writer
        - db_writer
        - detector

        - init everyone
        - capture -> inference -> save image (thread) -> write to db (thread)
        """
        model = torch.hub.load('ultralytics/yolov5', 'custom',
                               path='/Users/pslisenk/Documents/projects/camera/models/best.pt')
        while True:
            frame = self.cap.read()
            now = datetime.now()
            # timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")
            image_filename = now.strftime("%Y-%m-%d--%H-%M-%S-%f") + '.jpg'
            det = model(frame[:, :, ::-1])
            det.files[0] = image_filename  # so that det.save() saved with desired filename
            det.save('/Users/pslisenk/Documents/projects/camera/images/1/')
            # self.disc_writer.save_image(frame, image_filename)
            # self.dbwriter.insert_image(timestamp, image_filename)


def main():
    operator = Operator(config)
    operator.start_recording()
