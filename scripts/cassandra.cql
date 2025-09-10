-- This is the database
CREATE KEYSPACE IF NOT EXISTS pavementeye
WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'datacenter1': 3
};

ALTER KEYSPACE pavementeye
WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'datacenter1': 1
};

describe pavementeye;

-- use the database
USE pavementeye;

-- main table that will hold the cracks
CREATE TABLE IF NOT EXISTS crack (
  id uuid,
  road_index int,
  timestamp timestamp,
  label text,
  confidence float,
  image text,
  lon double,
  lat double,
  PRIMARY KEY ((road_index), timestamp, id)
) WITH CLUSTERING ORDER BY (timestamp DESC);

describe tables;

describe crack;

INSERT INTO pavementeye.crack (
    id,
    road_index,
    timestamp,
    label,
    confidence,
    image,
    lon,
    lat
) VALUES (
    uuid(),
    101,
    toTimestamp(now()),
    'crack',
    0.92,
    'image_001.jpg',
    45.764043,
    4.835659
);