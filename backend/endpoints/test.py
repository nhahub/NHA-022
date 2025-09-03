from kafka_producer import kafka_producer

def test():

  # Just for testing kafka is working
  kafka_producer.send('test', 'Message from Flask API !')
  kafka_producer.flush()


  return "App is working !"