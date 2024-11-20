from google.transit import gtfs_realtime_pb2
import requests
import urllib3
import zipfile
import pandas as pd
from flask_cors import CORS

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with zipfile.ZipFile("../source/dataset.zip","r") as traffic_dataset_zip:
        traffic_dataset_zip.extractall()

stop_dataset_pd_Data = pd.read_csv("./tcat-ny-us/stops.txt")
stop_nparray = stop_dataset_pd_Data.to_numpy()
stop_id_list = stop_nparray[:,0].tolist()
stop_name_list = stop_nparray[:,2].tolist()
# print(f"Stop name list: {stop_name_list}")

def get_trip_updates():
    # Initialize feed message
    feed = gtfs_realtime_pb2.FeedMessage()
    
    # Make request to TCAT realtime API
    url = 'https://realtimetcatbus.availtec.com/InfoPoint/GTFS-Realtime.ashx?&Type=TripUpdate'
    response = requests.get(url, verify=False)
    
    # Parse the protobuf message
    feed.ParseFromString(response.content)
    
    # Process each trip update entity
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            trip = entity.trip_update.trip
            print(f"\nTrip ID: {trip.trip_id}")
            
            # Process stop time updates
            for stop_update in entity.trip_update.stop_time_update:
                print("Stop Sequence:", stop_update.stop_sequence)
                
                if stop_update.HasField('arrival'):
                    delay = stop_update.arrival.delay
                    print(f"Arrival Delay: {delay} seconds")
                
                if stop_update.HasField('departure'):
                    delay = stop_update.departure.delay
                    print(f"Departure Delay: {delay} seconds")
                
                print("------------------------")


def get_vehicle_positions():
    # Initialize feed message
    POPULAR_BUSES = ['10'];
    feed = gtfs_realtime_pb2.FeedMessage()
    
    # Make request to TCAT realtime API
    url = 'https://realtimetcatbus.availtec.com/InfoPoint/GTFS-Realtime.ashx?&Type=VehiclePosition&serverid=0'
    response = requests.get(url, verify=False)
    
    # Parse the protobuf message
    feed.ParseFromString(response.content)
    
    # Process each vehicle entity
    for entity in feed.entity:
        if entity.HasField('vehicle'): 
            vehicle = entity.vehicle
            if vehicle.trip.route_id in POPULAR_BUSES or True:
                print(f"Vehicle ID: {vehicle.vehicle.id}")
                print(f"Route ID: {vehicle.trip.route_id}")
                print(f"Latitude: {vehicle.position.latitude}")
                print(f"Longitude: {vehicle.position.longitude}")
                print(f"Speed: {vehicle.position.speed if vehicle.position.HasField('speed') else 'N/A'}")
                vehicle_stop_id = int(vehicle.stop_id)
                print(f"Incoming: {stop_name_list[stop_id_list.index(vehicle_stop_id)]}")
                print("------------------------")

if __name__ == "__main__":
    get_vehicle_positions()
    # get_trip_updates()