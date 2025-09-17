# This class to init connection with 
# the running cassandra container

from cassandra.cluster import Cluster
import geopandas as gpd
import pandas as pd

class Cassandra:
  def __init__(self, CASSANDRA_HOST='localhost', CASSANDRA_PORT=9042):
    try:
      print(f"Connecting to cassandra on host = {CASSANDRA_HOST}, port = {CASSANDRA_PORT} ...")

      # Connect to the cluster
      self.cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)

      # Create a session
      self.session = self.cluster.connect()

      # use our keyspace database
      self.session.set_keyspace('pavementeye')

      self.data = None
      
      print("Cassnadra connected successfully !")
    except:
      return "Error in cassandra connection"

  def exec(self, query):
    try:
      rows = self.session.execute(query)

      # parse data to be as normal python lists and dic
      data = []
      for row in rows:
        row_dict = dict(row._asdict())
        data.append(row_dict)

      self.data = pd.DataFrame(data)

      return self.data
    except:
      return "Error in the cassandra query"
    
  def join_roads(self):
    roads_df = gpd.read_file('../data/egypt/alex_roads.geojson').to_crs(epsg=4326)

    roads_df = roads_df\
      .drop(['osm_id', 'code', 'ref'], axis=1)

    roads_df['road_index'] = roads_df.index
    joined = roads_df\
      .merge(self.data, how='right', left_on='road_index', right_on='road_index')

    self.data = joined

    return self.data

