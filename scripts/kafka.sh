# This file contains scripts used to create
# and monitor Kafka topics, producers, or consumers
# Use the following command to open the shell in a docker container:


# -----------> docker exec -it <kakfa-container-id> bash


# Then copy and paste and command (command by command)
# Take care of order
# You can adjust commands such as topic name etc.

# Just for test
kafka-topics -create \
--bootstrap-server localhost:9092 \
--partitions 3 \
--replication-factor 3 \
--topic test

# List all topics
kafka-topics -list \
--bootstrap-server localhost:9092

# Details about specific topic
kafka-topics -describe \
--bootstrap-server localhost:9092 \
--topic test

# List all messages from specific topic
# If you want new messages only remove the last line
kafka-console-consumer \
--bootstrap-server localhost:9092 \
--topic test \
--from-beginning


