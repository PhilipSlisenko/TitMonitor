import os
import statistics
import threading
import timeit
import random

import cv2

from src.config import config
from src.main import DBWriter

db_writer = DBWriter(config.dbhost, config.dbname, config.dbuser, config.dbpassword)

def insert_dummy():
    for i in list(range(1000)):
        sql = "INSERT INTO test VALUES (%s);"
        with db_writer.conn:
            with db_writer.conn.cursor() as cur:
                # x = threading.Thread(target=cur.execute, args=(sql, (i,)))
                # x.start()
                cur.execute(sql, (i,))

im = cv2.imread("/Users/pslisenk/Documents/projects/camera/dataset/fourth-try/15_41_38_709119.jpg")

def save_dummy():
    os.makedirs('test_write', exist_ok=True)
    def write_file():
        cv2.imwrite('test_write/{random.randint(1, 10000)}.jpg', im)

    for i in list(range(1000)):
        x = threading.Thread(target=write_file)
        x.start()
        # write_file()

times = timeit.repeat(save_dummy, repeat=5, number=1)
print(times)
print(statistics.mean(times))
print(statistics.stdev(times))

