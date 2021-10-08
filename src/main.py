"""
- capture image
- run inference
- save image to disc
- put image info, detection info into db
"""
import os
import queue
import signal
import sys
import threading
from datetime import datetime

import cv2
import numpy as np
import torch
from loguru import logger

from src.config import Config, config


# bufferless VideoCapture
class MyVideoCapture:
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


class Operator:
    def __init__(self, config: Config):
        logger.info('Initing operator')
        self.cap = MyVideoCapture(config.stream_url)
        self.disc_writer = DiscWriter(config.root_dir_to_save_images)
        # self.db_writer = DBWriter(config.db_connection_string)
        # self.detector = Detector(config.model_path)

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
