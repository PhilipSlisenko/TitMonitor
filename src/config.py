from dataclasses import dataclass


@dataclass
class Config:
    stream_url: str = 'rtsp://192.168.0.101:554/ch0_0.h264'
    root_dir_to_save_images: str = '/Users/pslisenk/Documents/projects/camera/images/'
    db_connection_string: str = ''
    model_path: str = ''


config = Config()
