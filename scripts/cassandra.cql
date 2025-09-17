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
  x1 double,
  y1 double,
  x2 double,
  y2 double,
  ppm double,
  PRIMARY KEY ((road_index), timestamp, id)
) WITH CLUSTERING ORDER BY (timestamp DESC);

describe tables;

describe crack;

INSERT INTO crack (
  id, 
  road_index, 
  timestamp, 
  label, 
  confidence, 
  image, 
  lon, 
  lat, 
  x1, 
  y1, 
  x2, 
  y2
) VALUES (
  uuid(),                  -- Unique ID (can use Python's uuid.uuid4())
  1,                       -- Example road index
  toTimestamp(now()),     -- Current timestamp
  'longitudinal_crack',   -- Label
  0.89,                   -- Confidence
  'image_001.png',        -- Image name or path
  77.5946,                -- Longitude
  12.9716,                -- Latitude
  125.4,                  -- x1
  98.2,                   -- y1
  200.6,                  -- x2
  130.8                   -- y2
);

select * from crack;