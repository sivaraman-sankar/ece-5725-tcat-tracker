from flask import Flask, jsonify, render_template, request, make_response
from google.transit import gtfs_realtime_pb2
import requests
import urllib3
import zipfile
import pandas as pd
from werkzeug.datastructures import Headers
from flask_cors import CORS; 

app = Flask(__name__)

CORS(app); 


# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load and process stop data
def load_stop_data():
    with zipfile.ZipFile("/workspaces/ece-5725-tcat-tracker/api/api/dataset.zip","r") as traffic_dataset_zip:
        traffic_dataset_zip.extractall()

    stop_dataset = pd.read_csv("./tcat-ny-us/stops.txt")
    stop_data = stop_dataset.to_numpy()
    return {
        'stop_ids': stop_data[:,0].tolist(),
        'stop_names': stop_data[:,2].tolist()
    }

# Initialize stop data
STOP_DATA = load_stop_data()

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
                        'incoming_stop': incoming_stop
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


# Webpage routes
@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/api/stops/<route_id>', methods=['GET'])
def get_stops(route_id):
    try:
        # Get vehicle positions from TCATBusAPI
        vehicles = TCATBusAPI.get_vehicle_positions(route_id)

        # Read the file containing stop names
        stops_file = './tcat-ny-us/route_'+route_id+'.txt';  

        with open(stops_file, 'r') as file:
            stops = [line.strip() for line in file.readlines()]

        # Return the combined data
        return jsonify({
            'status': 'success',
            'data': {
                'vehicles': vehicles,
                'stops': stops
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