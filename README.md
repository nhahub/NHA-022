# PavementEye

<div align="center">
  <img 
  src="media/Gemini_Generated_Image_yldkbmyldkbmyldk.png" 
  alt="PavementEye Logo" 
  width="100"
  style="border-radius: 50%; object-fit: cover;"
  />
</div>

### What is PavementEye ?
##### Introduction
Roads  are  the  most  widely  used  transportation method  around  the  world  at  present.  One  of the causes  of accidents on the roads  is road  distresses [1]. 

If left untreated,  road  distresses  will  degrade  the  ride quality and safety of motorists. They will also require costly  maintenance  and  repairs,  which  can  restrict traffic flow  and cause congestion. Therefore, timely maintenance is  essential  to keep  highways safe  and durable. [2]

##### Problem

Roadsurface inspection is primarily based on visual observations by humans and quantitative analysis using expensive machines. Furthermore, it is timeconsuming. visual inspection tends to be inconsistent and unsustainable, which increases the risk associated with aging road infrastructure.[3]

##### Solution
We leverage our expertise in data science and data engineering to transform collected ideas and information into a comprehensive streaming data pipeline. This pipeline automatically collects images, processes them to detect cracks and classify their types using deep learning model, and performs data preprocessing. It enriches the analysis through integration with OpenStreetMap, enabling advanced geolocation insights. Images are stored in the cloud (data lake), while structured data is saved in a NoSQL database. All results are visualized in a unified dashboard, providing administrators with rapid, actionable insights. We called the application “Pavement Eye”.

<div align="center">
  <img 
  src="media/main.png" 
  alt="PavementEye Logo" 
  width="80%"/>
</div>

### Data Pipeline
<div align="center">
  <img 
  src="media/Flow Chart Whiteboard in Red Blue Basic Style.png" 
  alt="PavementEye Logo" 
  width="80%"
  />
</div>

##### Goals

Improve road quality by applying cheap, sustainable and in an automated and fast manner. Reducing direct and indirect accidents caused by distresses. Making traffic in Egypt(Alexandria) more resilient and reducing traffic congestion by eliminating distresses and cracks.


## Steps to run the code

### Running Docker containers (Kafka, PySaprk, Cassandra)

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

1. Download the trained Yolo v8 model from:
https://github.com/oracl4/RoadDamageDetection/tree/main/models

**Note:** Put the model in the right place: `models\yolo v8`

2. Download the required python libraries:
```powershell
pip install -r requirements.txt
```

3. Run the backend **(Ensure that you ran the docker containers first)**
```powershell
cd backend
python app.py
```

4. To access the dashboard to see the visualizations:
```powershell
cd streamlit
streamlit run "page 1.py"
```

## References
[1]: Huang, Y.-H., & Zhang, Q.-Y., “A review of the causes and
effects of pavement distresses”, Construction and Building
Materials, Vol. 112, No. 1, pp. 294-305, 2016.

[2]: Kulshreshtha, S., & Zhang, X., “Pavement distresses and
their impact on pavement performance”, Journal of
Transportation Engineering, Part B: Pavements, Vol. 143,
No. 1, pp. 1-10, 2017.

[3]: Road Damage Detection Using Deep Neural Networks with
Images Captured Through a Smartphone, 2 Related Works
2.1 Road Damage Detection, Page 2
