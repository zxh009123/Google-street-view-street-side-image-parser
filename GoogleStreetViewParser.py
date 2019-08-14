import pandas
import streetview
import google_streetview.helpers
import math
import utm
import googlemaps
import numpy as np
from api import CustomeAPI
import json
import progressbar


class GoogleStreetViewParser:
    def __init__(self, setting_file):
        settings_file = open(setting_file)
        settings = json.load(settings_file)

        try:
            self.GOOGLE_KEY = settings["GOOGLE_KEY"]
            self.DISTANCES = settings["DISTANCES"]
            self.FILE = settings["FILE"]
            self.ROOT_FOLDER = settings["ROOT_FOLDER"]
        except:
            print("please config settings correctly")
            exit(-1)

        self.gmaps = googlemaps.Client(key = self.GOOGLE_KEY)

        self.stops = self.read_csv(self.FILE)

        self.stop_name_to_index = []

    def ConvertToUTM(self, lat, lon):
        east, north, zoneLetter, zoneNumber = utm.from_latlon(lat, lon)
        return [east, north], zoneLetter, zoneNumber

    def CovertToLatLon(self, east, north, zoneNumber, zoneLetter):
        lat, lon = utm.to_latlon(east, north, zoneNumber, zoneLetter)
        return [lat, lon]

    def read_csv(self, csv_file):
        df = pandas.read_csv(csv_file)
        df_lan_lon = df[["stop_name", "stop_lat", "stop_lon"]]
        # return df_lan_lon.head(10)
        # return df_lan_lon.loc[100:102]
        return df_lan_lon

    def getNearestRoad(self, lat, lon):
        geocode_result = self.gmaps.nearest_roads((lat, lon))
        return geocode_result

    def angleBetweenTwoUTM(self, east_car, north_car, east_stop, north_stop):
        x = east_stop - east_car
        y = north_stop - north_car
        vector = np.array([x, y]) / np.linalg.norm(np.array([x, y]))
        angle = np.arccos(np.clip(np.dot(vector, np.array([0,1])), -1.0, 1.0))
        angle = angle * 180.0 / math.pi
        if x < 0:
            angle = 360.0 - angle
        return angle

    def getCarTrace(self, stop_pos, car_pos, distance_list):
        stop_pos = np.array(stop_pos)
        car_pos = np.array(car_pos)

        vector = [stop_pos[0] - car_pos[0], stop_pos[1] - car_pos[1]]

        normal_vector_clockwise = np.array([vector[1], -vector[0]])
        normal_vector_clockwise = normal_vector_clockwise / np.linalg.norm(normal_vector_clockwise)

        result_pos = []

        for d in distance_list:
            result_pos.append(car_pos + d * normal_vector_clockwise)
            result_pos.append(car_pos + (-d) * normal_vector_clockwise)

        result_pos.append(car_pos)

        return result_pos

    def parseData(self):
        with progressbar.ProgressBar(max_value = self.stops.shape[0]) as bar:
            for index, row in self.stops.iterrows():
                bar.update(index)

                name = str(index).zfill((len(str(self.stops.shape[0]))))

                self.stop_name_to_index.append([name, row['stop_name']])

                point = [row['stop_lat'],row['stop_lon']]

                road_point = self.getNearestRoad(point[0], point[1])

                if len(road_point) != 0:
                    near_lat, near_lon = road_point[0]['location']['latitude'], road_point[0]['location']['longitude']
                else:
                    print("no such point")
                    continue
                pointUTM, zoneLetter, zoneNumber = self.ConvertToUTM(point[0], point[1])
                roadUTM, zoneLetter, zoneNumber = self.ConvertToUTM(near_lat, near_lon)
                trace = self.getCarTrace(pointUTM, roadUTM, self.DISTANCES)
                point_dict = {
                    'size': '640x640', # max 640x640 pixels
                    'location': " ",
                    'heading': '180',
                    'key': self.GOOGLE_KEY,
                    'source' : 'outdoor'
                    }
                params = []
                for i in trace:
                    pointLatLon = self.CovertToLatLon(i[0], i[1],zoneLetter, zoneNumber)
                    latitude, longitude = pointLatLon[0], pointLatLon[1]
                    point = point_dict.copy()
                    point["location"] = str(latitude) + ',' + str(longitude)
                    params.append(point)

                results = CustomeAPI(params)

                new_lat_lon_list = results.get_lat_lon()


                new_UTMs = list(map(lambda x : self.ConvertToUTM(x[0], x[1]), new_lat_lon_list))


                new_headings = list(map(lambda x : self.angleBetweenTwoUTM(x[0][0], x[0][1], pointUTM[0], pointUTM[1]), new_UTMs))

                results.set_heading(new_headings)

                folder = self.ROOT_FOLDER + str(name)
                results.download_links(folder, name)

            stop_to_index = pandas.DataFrame(self.stop_name_to_index, columns =['index', 'name'])

            stop_to_index.to_csv(path_or_buf = self.ROOT_FOLDER + 'stop_name_to_index.csv')

if __name__ == "__main__":
    parser = GoogleStreetViewParser("sample_settings.json")
    parser.parseData()