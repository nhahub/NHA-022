# you should have installed containers and python requirements
# you should have windows (Powershell)
# containers -> spark stream (parallel terminal) -> backend(parallel terminal) -> streamlit

Write-Host "Starting PavementEye services..." -ForegroundColor Green


# 1. running existing docker compose
Write-Host "Starting containers..." -ForegroundColor Green
# go to PavementEye root directory
cd ../

# run all containers
docker-compose up -d

Write-Host "wait 15s untill containers fully run ..." -ForegroundColor Yellow
Start-Sleep -Seconds 15 # some time untill all containers run

Write-Host "Cleaning old Spark checkpoints..." -ForegroundColor Yellow
docker exec pyspark-notebook bash -c "rm -rf /tmp/checkpoint*"

# running spark script
# 2. Start Spark in NEW PowerShell window
Write-Host "Starting Spark Streaming in new window..." -ForegroundColor Green
Start-Process powershell -ArgumentList @"
cd $PWD
docker exec pyspark-notebook spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 /home/jovyan/scripts/spark.py
"@

Start-Sleep -Seconds 1

# run backend
Write-Host "Starting bcakend new window..." -ForegroundColor Green
Start-Process powershell -ArgumentList @"
cd $PWD\backend
python app.py
"@

# open streamlit (runs in the same terminal)
# will bock every thing after
cd streamlit
streamlit run "page 1.py"


