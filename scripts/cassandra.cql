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
  dist text,
  PRIMARY KEY ((dist), timestamp, id)
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
  y2,
  ppm
) VALUES (
  uuid(),                  
  3693,                       
  1752144000000,  -- Replace with your millis value from Python
  'Alligator Crack',   
  0.89,                   
  'image_001.png',        
  29.9882,                
  31.25843,                
  125.4,                  
  98.2,                   
  200.6,                  
  130.8,                  
  200
);

select * from crack;