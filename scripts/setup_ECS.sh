git clone https://github.com/yahia997/PavementEye.git
cd PavementEye
wget -O "models/yolo v8/YOLOv8_Small_RDD.pt" "https://github.com/oracl4/RoadDamageDetection/raw/refs/heads/main/models/YOLOv8_Small_RDD.pt"
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install ca-certificates curl gnupg lsb-release -y
sudo mkdir -p /etc/apt/keyrings # done
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg # done
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null # done
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io -y
docker --version
sudo usermod -aG docker $USER
newgrp docker
sudo apt-get update
sudo apt-get install docker-compose-plugin -y
docker compose version