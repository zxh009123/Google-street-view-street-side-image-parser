# Google street view street side image parser
This project provides easy way to parse images of objects on street side from google street view. Such as bus stops, stop signs, pedestrian signs and so on. 

## prerequisite
```
pandas
streetview
google_streetview
utm
googlemaps
numpy
json
progressbar
overpass (optional)
```

## Usage

1. Configuration API key

   In [sample_settings.json](./sample_settings.json), It is needed to fill your google street view API key in GOOGLE_KEY field. Detailed information about google street view API key can be found [here](https://developers.google.com/maps/documentation/streetview/intro).  The DISTANCES field means the distances between each viewing point to the object. [10, 20] means we have totally 5 points to that points each are the nearest point on the road to the object, two points 10 meters away from the nearest point to the object and two points 20 meters away from the nearest point to the object. The FILE field is the required .csv file directory which is detailed explained in data preparation. The ROOT_FOLDER is the directory to save all the parsed images.

2. Data preparation

   To successfully running the code, a .csv file containing all the coordinates must be provided in settings' FILE field. This file containing all the coordinates to be parsed from google street view. A sample format of a .csv file is provided and shown below.

   ```
   stop_name,         stop_lat,      stop_lon
   "Bird Ave",        37.325184,     -121.900520
   "BSan Carlos",     37.324215,     -121.900337
   "Diridon Station", 37.330338,     -121.902634
   "Santa Clara",     37.331902,     -121.899567
   ```

   If you do not have the coordinates yet. We also provided a simple script [stopRefiner.py](./stopRefiner.py) to use OpenStreetMap (OSM) overpass API to parse the data and generate a .csv file. Before running this script, make sure fill in line 6 in stopRefiner.py. this line require a Overpass QL request. For example ```node["highway"="bus_stop"](36.947831, -122.070237,37.007419, -121.916590)``` is request all the bus stop in Santa Cruz area. More information can be found [here](https://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide).

3. Running the parser 

   Make sure everything is done just simply running

   ```python3 GoogleStreetViewParser.py```

   After the progress bar completed, all the data can be found under /downloads. 

