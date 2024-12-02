from flask import Flask, jsonify
from google.transit import gtfs_realtime_pb2
import requests
import urllib3
from flask_cors import CORS; 
import os 
import pandas as pd
import datetime

app = Flask(__name__)

CORS(app); 


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_stop_data():
    basedir = os.path.abspath('.')
    path = os.path.join(basedir, "tcat-ny-us", "stops.txt")
    stop_dataset = pd.read_csv(path)
    stop_data = stop_dataset.to_numpy()
    return {
        'stop_ids': stop_data[:,0].tolist(),
        'stop_names': stop_data[:,2].tolist()
    }

STOP_DATA = load_stop_data()

class AppConfig:

    def __init__(self):
        self.base_path = None; 
        self.trips_df = None; 
        self.stop_times_df = None;
        self.stops_df = None; 
        self.load_dataframes();
    

    def load_dataframes(self):
        base_path = os.path.join('tcat-ny-us')
        self.trips_df = pd.read_csv(os.path.join(base_path, 'trips.txt'))
        self.stop_times_df = pd.read_csv(os.path.join(base_path, 'stop_times.txt'))
        self.stops_df = pd.read_csv(os.path.join(base_path, 'stops.txt'))

    def get_stops_by_trip_id(self, trip_id):
        try:
            trip_stop_times = self.stop_times_df[self.stop_times_df['trip_id'].astype(str) == str(trip_id)]
            
            ordered_stops = (trip_stop_times
                            .merge(self.stops_df, on='stop_id')
                            .sort_values('stop_sequence')
                            [['stop_name']]
                            .drop_duplicates())
            
            if ordered_stops.empty:
                print(f"No stops found for trip_id: {trip_id}")
                return []
                
            return ordered_stops.to_dict('records')
            
        except Exception as e:
            print(f"Error getting stops for trip_id {trip_id}: {str(e)}")
            return []
    
    def get_stops_by_route_id(self, route_id):
        relevant_trips = self.trips_df[self.trips_df['route_id'].astype(str) == route_id]
        print(f"[DEBUG] RT: {relevant_trips}")

        relevant_stop_times = self.stop_times_df[self.stop_times_df['trip_id'].astype(str) == route_id]

        print(f"[DEBUG] RST: {relevant_trips}")


        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime('%H:%M:%S')
        print(f"[DEBUG]: Current time: {current_time_str}");

        # Get active trips for the current time
        active_trips = (relevant_stop_times[
            (relevant_stop_times['departure_time'] <= current_time_str) & 
            (relevant_stop_times['arrival_time'] >= current_time_str)
        ])

        # Get the first active trip_id
        active_trip_id = active_trips['trip_id'].iloc[0]
        print(f"[DEBUG]: selected active trip ID: {active_trip_id}");
        print(f"[DEBUG]: All active trip ID: {active_trips['trip_id']}");

        relevant_stop_times = self.stop_times_df[self.stop_times_df['trip_id'].isin(relevant_trips['trip_id'])]

        ordered_stops = (relevant_stop_times[relevant_stop_times['trip_id'] == active_trip_id]
                        .merge(self.stops_df, on='stop_id')
                        .sort_values('stop_sequence')
                        [['stop_name']]
                        .drop_duplicates())

        print(ordered_stops)
        return ordered_stops.to_dict('records')

config = AppConfig();

class TCATBusAPI:
    @staticmethod
    def get_vehicle_positions(route_id):
        feed = gtfs_realtime_pb2.FeedMessage()
        
        url = 'https://realtimetcatbus.availtec.com/InfoPoint/GTFS-Realtime.ashx?&Type=VehiclePosition&serverid=0'
        response = requests.get(url, verify=False)
        
        feed.ParseFromString(response.content)
        
        vehicles = []
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                vehicle = entity.vehicle
                if int(vehicle.trip.route_id) == int(route_id):
                    vehicle_stop_id = int(vehicle.stop_id)
                    try:
                        stop_index = STOP_DATA['stop_ids'].index(vehicle_stop_id)
                        incoming_stop = STOP_DATA['stop_names'][stop_index]
                    except ValueError:
                        incoming_stop = "Unknown"
                    
                    vehicles.append({
                        'vehicle_id': vehicle.vehicle.id,
                        'route_id': vehicle.trip.route_id,
                        'latitude': vehicle.position.latitude,
                        'longitude': vehicle.position.longitude,
                        'speed': vehicle.position.speed if vehicle.position.HasField('speed') else None,
                        'incoming_stop': incoming_stop,
                        'trip_id': vehicle.trip.trip_id
                    })
        
        return vehicles

    @staticmethod
    def get_trip_updates():
        feed = gtfs_realtime_pb2.FeedMessage()
        
        url = 'https://realtimetcatbus.availtec.com/InfoPoint/GTFS-Realtime.ashx?&Type=TripUpdate'
        response = requests.get(url, verify=False)
        
        feed.ParseFromString(response.content)
        
        updates = []
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip = entity.trip_update.trip
                stop_updates = []
                
                for stop_update in entity.trip_update.stop_time_update:
                    update = {
                        'stop_sequence': stop_update.stop_sequence,
                        'arrival_delay': stop_update.arrival.delay if stop_update.HasField('arrival') else None,
                        'departure_delay': stop_update.departure.delay if stop_update.HasField('departure') else None
                    }
                    stop_updates.append(update)
                
                updates.append({
                    'trip_id': trip.trip_id,
                    'stop_updates': stop_updates
                })
        
        return updates



# API Routes
@app.route('/api/vehicles/<route_id>', methods=['GET'])
def get_vehicles(route_id):
    try:
        vehicles = TCATBusAPI.get_vehicle_positions(route_id)
        return jsonify({
            'status': 'success',
            'data': vehicles
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/trips', methods=['GET'])
def get_trips():
    try:
        trips = TCATBusAPI.get_trip_updates()
        return jsonify({
            'status': 'success',
            'data': trips
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/v2/stops/<route_id>', methods=['GET'])
def get_stops2(route_id):
    print(f"extracting stops for :{route_id}");
    vehicles = TCATBusAPI.get_vehicle_positions(route_id)
    
    ans = config.get_stops_by_trip_id(vehicles[0]['trip_id'])
    
    incoming_stops = [v['incoming_stop'] for v in vehicles]
    res = []
    for stop in ans: 
        res.append({
            "stop_name": stop['stop_name'],
            "is_incoming": stop['stop_name'] in incoming_stops
        }); 
    
    return jsonify({
            'status': 'success',
            'data': {
                'stops': res,
            },
            'vehicles': vehicles
    })


@app.route('/api/stops/<route_id>', methods=['GET'])
def get_stops(route_id):
    try:
        # Get vehicle positions from TCATBusAPI
        vehicles = TCATBusAPI.get_vehicle_positions(route_id)
        
        # Get list of incoming stops from vehicles
        incoming_stops = [v['incoming_stop'] for v in vehicles]
        
        # Get unique vehicle IDs for active buses count
        active_buses = len({v['vehicle_id'] for v in vehicles})

        # Read and process stops
        stops_file = os.path.join('tcat-ny-us', f'route_{route_id}.txt')
        with open(stops_file, 'r') as file:
            stops = []
            for line in file:
                stop_name = line.strip()
                stops.append({
                    'name': stop_name,
                    'is_incoming': stop_name in incoming_stops
                })

        return jsonify({
            'status': 'success',
            'data': {
                'vehicles': vehicles,
                'stops': stops,
                'active_buses': active_buses
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Resource not found'
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(debug=True)