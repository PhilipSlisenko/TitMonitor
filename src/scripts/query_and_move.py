"""
clip: conseguetn series of frames

1. tool to get
"""

"""
query, put bb, move
"""

_reopen_conn_if_closed()
sql = """INSERT INTO images(image_id, timestamp, filename) VALUES(%s, %s, %s);"""
with conn:
    with conn.cursor() as cur:
        cur.execute(sql, (image_id, timestamp, filename))