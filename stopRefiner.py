import pandas
import overpass
import time

api = overpass.API(timeout=600)
response = api.get('')

refined_data = []
for i in response["features"]:
    print(i)
    stop = []
    if "name" in i["properties"].keys():
        stop.append(i["properties"]["name"])
    else:
        stop.append("unknown name")
    stop.append(i["geometry"]["coordinates"][1])
    stop.append(i["geometry"]["coordinates"][0])
    refined_data.append(stop)

temp_df = pandas.DataFrame(refined_data, columns = ['stop_name' , 'stop_lat', 'stop_lon'])
temp_df.to_csv('OSM_data.csv')

