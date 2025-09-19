# PavementEye
![PavementEye Logo](/media/Gemini_Generated_Image_ap7b8eap7b8eap7b.png)
# Environemt Docker

### Running Docker containers (Kafka, PySaprk, Cassandra, Hadoop)

Clone the repository

```powershell
git clone https://github.com/yahia997/PavementEye.git
cd PavementEye
```

Then to install docker images and run **for the first time.**

```powershell
docker compose up
```

This will install and run the containers.

If it is your not your first time to run the containers

```powershell
docker compose start
```

To stop the containers without deteting them

```powershell
docker compose stop
```

### Running the Flask API

1. Clone the following repo:

```powershell
git clone https://github.com/TITAN-lab/Road-crack-detection.git
```

1. Rename the directory to `yolo v2` and copy it to `backend` directory.
2. Follow Download the trained Yolo v2 model from [https://drive.google.com/drive/folders/144Jlnt2xJSD3zuGG3mWtpkR0Gw1Xaxg1](https://drive.google.com/drive/folders/144Jlnt2xJSD3zuGG3mWtpkR0Gw1Xaxg1)
3. Put the files you downloaded from dirve it its right location to match the paths in `model.py`  file.

```powershell
pip install -r requirements.txt
cd backend
python app.py
```