# This class to init connection with 
# the running cassandra container

from cassandra.cluster import Cluster

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

      return data
    except:
      return "Error in the cassandra query"
