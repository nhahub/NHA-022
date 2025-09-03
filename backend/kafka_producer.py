from kafka import KafkaProducer

# Creating Kafka Producer to push messages to Kafka Topic ---------------------------------------------
kafka_producer = KafkaProducer(
  bootstrap_servers=['localhost:29092'],
  value_serializer=lambda v: v.encode('utf-8'), # must for encoding (will give error if removed)
  request_timeout_ms=5000,
  retries=3
)