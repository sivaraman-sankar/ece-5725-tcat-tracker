from functools import wraps
import requests
import urllib3
import os 
from flask import Flask, jsonify, render_template, request
from google.transit import gtfs_realtime_pb2
from flask_cors import CORS; 
import pandas as pd
from flask_apscheduler import APScheduler
from dotenv import load_dotenv
import logging

from app_config import AppConfig
from notification_manager import NotificationManager

logger = logging.getLogger(__name__)

app = Flask(__name__,
    static_url_path='',
    static_folder='../frontend/build',
    template_folder='../frontend/build'
)

scheduler = APScheduler()

load_dotenv()

ROUTES = [30, 10, 90, 81]
NOTIFICATION_LOG_FILE = 'routes.csv'

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

config = AppConfig();
notification = NotificationManager(notification_file=NOTIFICATION_LOG_FILE);

def handle_api_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in API call: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    return wrapper

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
@app.route('/api/v1/vehicles/<route_id>', methods=['GET'])
@handle_api_errors
def get_vehicles(route_id):
    return jsonify({
        'status': 'success',
        'data': TCATBusAPI.get_vehicle_positions(route_id)
    })

@app.route('/api/v1/notification', methods=['POST'])
@handle_api_errors
def submit_notification():
    data = request.get_json()
        
    email = data.get('email')
    stop = data.get('stop')
    route = data.get('route')
        
    if not all([email, stop, route]):
        return jsonify({
            'error': 'Missing required fields'
        }), 400
            
    notification.save_route_notification(email, stop, route)

    return jsonify({
        'message': 'Notification settings saved successfully',
    }), 201

@app.route('/api/v1/stops/<route_id>', methods=['GET'])
@handle_api_errors
def get_stops2(route_id):
    logger.debug(f"Extracting stops for: {route_id}");
    vehicles = TCATBusAPI.get_vehicle_positions(route_id)

    if not vehicles:
        return jsonify ({
            'status': f'success',
            'data': [],
            'vehicles': []
        }); 

    res = []

    incoming_stops = [v['incoming_stop'] for v in vehicles]

    for stop in config.get_stops_by_trip_id(vehicles[0]['trip_id']): 
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

@scheduler.task('cron', id='read_csv_task', minute='*')
def scheduled_task():
    with app.app_context():
        for route in ROUTES:
            vehicles = TCATBusAPI.get_vehicle_positions(route);
            notification.process_notifications(vehicles)


@app.route('/')
def serve_react():
    return render_template("index.html")

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    logger.debug(error)
    return jsonify({
        'status': 'error',
        'message': 'Resource not found'
    }), 404

@app.errorhandler(500)
def server_error(error):
    logger.debug(error)
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='0.0.0.0',debug=True)