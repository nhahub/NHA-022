from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import functions as F
import geopandas as gpd
import shutil
import os

checkpoint_path = '/tmp/checkpoint1'

# Check if the directory exists before trying to delete it
if os.path.exists(checkpoint_path):
    try:
        shutil.rmtree(checkpoint_path)
        print(f"Successfully deleted checkpoint directory: {checkpoint_path}")
    except OSError as e:
        print(f"Error: {e.strerror}. Failed to delete checkpoint directory: {checkpoint_path}")
else:
    print(f"Checkpoint directory does not exist: {checkpoint_path}")

spark = SparkSession.builder \
    .appName("PavementEye Stream") \
    .config("spark.cassandra.connection.host", "cassandra")\
    .config("spark.cassandra.connection.port", "9042")\
    .getOrCreate()

# kafka parameters
kafka_bootstrap_servers = 'kafka:9092'  # kafka:9092 as we are inside the docker network
kafka_topic = 'test' # Can be changed later

# read data from Kafka
kafka_stream_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic) \
    .option("startingOffsets", "latest")\
    .load()

# To be able to see the right parsed value of the message
parse_kafka_stream = kafka_stream_df.selectExpr('CAST(value as STRING) as json_value')

# Define schema for the incoming JSON messages
schema = StructType([
    StructField("lon", DoubleType()),
    StructField("lat", DoubleType()),
    StructField("time", StringType()),
    StructField("ppm", DoubleType()),
    StructField("image", StringType()),
    StructField("labels", ArrayType(
        StructType([
            StructField("label", StringType()),
            StructField("confidence", DoubleType()),
            StructField("x1", DoubleType()),
            StructField("x2", DoubleType()),
            StructField("y1", DoubleType()),
            StructField("y2", DoubleType())
        ])
    ))
])

#Parse JSON string into a structured DataFrame
json_df = parse_kafka_stream.select(from_json(col("json_value"), schema).alias("data"))

#Explode the labels array so each detected object becomes one row
exploded_df = json_df.select(
    col("data.lon"),
    col("data.lat"),
    col("data.time"),
    col("data.ppm"),
    col("data.image"),
    explode(col("data.labels")).alias("label_struct")
).select(
    col("lon"),
    col("lat"),
    col("image"),
    col("time").alias("timestamp"),
    col("ppm"),
    col("label_struct.label").alias("label"),
    col("label_struct.confidence").alias("confidence"),
    col("label_struct.x1").alias("x1"),
    col("label_struct.x2").alias("x2"),
    col("label_struct.y1").alias("y1"),
    col("label_struct.y2").alias("y2")
)

#Remove empty values
df_no_nulls = exploded_df.na.drop()

# Convert 'time' column from string to timestamp
df_no_nulls = df_no_nulls.withColumn("timestamp", F.col("timestamp").cast(TimestampType()))

# Now deduplicate only on the last 1 minutes
cleaned_df = df_no_nulls \
    .withWatermark("timestamp", "5 minute") \
    .dropDuplicates(["lon", "lat", "label", "x1", "y1", "x2", "y2", "timestamp"])

#Verify the correctness of the coordinates
df_valid_coords = cleaned_df.filter(
    (col("x1") < col("x2")) &
    (col("y1") < col("y2")) &
    (col("lon") >= -180) & (col("lon") <= 180) &  # التأكد من حدود longitude
    (col("lat") >= -90) & (col("lat") <= 90)      # التأكد من حدود latitude
)

# inster the id (identifier for the crack)
df_valid_coords = df_valid_coords.withColumn("id", expr("uuid()"))

# load roads dataset
roads_df = gpd.read_file('../data/egypt/geo.geojson').to_crs(epsg=4326)
roads_df = roads_df.drop(['index'], axis=1)
roads_broadcast = spark.sparkContext.broadcast(roads_df)

def join_roads(lon, lat):
    # Import necessary libraries inside the UDF for execution on workers
    import geopandas as gpd
    from shapely.geometry import Point
    
    # Access the broadcasted roads data
    roads_df_local = roads_broadcast.value

    location = Point(lon, lat)
    stream_geo_df = gpd.GeoDataFrame(geometry=[location], crs="EPSG:4326")

    # Perform the nearest-neighbor spatial join
    joined_data = gpd.sjoin_nearest(stream_geo_df, roads_df_local, how='inner', max_distance=20)

    if not joined_data.empty:
        # Return the index of the nearest road (scalar)
        return int(joined_data.iloc[0]['index_right'])
    else:
        # Return a default value when no match is found
        return -1

join_roads = udf(join_roads, IntegerType())

def get_dist(lon, lat):
    # Import necessary libraries inside the UDF for execution on workers
    import geopandas as gpd
    from shapely.geometry import Point
    
    # Access the broadcasted roads data
    roads_df_local = roads_broadcast.value

    location = Point(lon, lat)
    stream_geo_df = gpd.GeoDataFrame(geometry=[location], crs="EPSG:4326")

    # Perform the nearest-neighbor spatial join
    joined_data = gpd.sjoin_nearest(stream_geo_df, roads_df_local, how='inner', max_distance=20)

    if not joined_data.empty:
        # Return the index of the nearest road (scalar)
        return joined_data.iloc[0]['ADM2_EN']
    else:
        # Return a default value when no match is found
        return "Unkown"

get_dist = udf(get_dist, StringType())

df_with_roads = df_valid_coords\
    .withColumn("road_index", join_roads(col("lon"), col("lat")))\
    .withColumn("dist", get_dist(col("lon"), col("lat")))

# To insert the stream into cassandra database
df_with_roads.writeStream\
    .outputMode("append")\
    .format("org.apache.spark.sql.cassandra")\
    .options(table="crack", keyspace="pavementeye")\
    .option('checkpointLocation', checkpoint_path)\
    .start()\
    .awaitTermination()