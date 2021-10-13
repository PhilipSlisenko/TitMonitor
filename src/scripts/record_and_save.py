import argparse
from datetime import datetime

from src.config import config
from src.main import BufferlessVideoCapture, DiscWriter, DBWriter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--out', type=str, nargs='?',
                        default=f'recordings/{datetime.now().strftime("%Y-%m-%d--%H-%M-%S-%f")}',
                        help='Dir to save recording to. Will default to ./recording/<current timestamp>/')
    args = parser.parse_args()
    return args


def main():
    """
    Start video capture from the camera, save frames to the specified `out` dir.
    """
    args = parse_args()
    cap = BufferlessVideoCapture(config.stream_url)
    disc_writer = DiscWriter(args.out)
    db_writer = DBWriter(config.dbhost, config.dbname, config.dbuser, config.dbpassword)

    while True:
        frame = cap.read()
        now = datetime.now()
        image_id = now.strftime("%Y-%m-%d--%H-%M-%S-%f")
        image_filename = now.strftime("%Y-%m-%d--%H-%M-%S-%f") + '.jpg'
        disc_writer.save_image(frame, image_filename)
        db_writer.insert_image_metadata(image_id, now, image_filename)
