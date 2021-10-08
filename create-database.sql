DROP DATABASE IF EXISTS camera;
CREATE DATABASE camera;
\c camera
CREATE TABLE images(
   image_id VARCHAR PRIMARY KEY,
   timestamp TIMESTAMP,
   filename VARCHAR
);
CREATE TABLE detections(
    detection_id VARCHAR PRIMARY KEY,
    coords json,
    class VARCHAR,
    conf NUMERIC(3, 2),
    image_id VARCHAR
);