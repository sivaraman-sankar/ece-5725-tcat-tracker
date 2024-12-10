import os
import pandas as pd
import datetime
import logging
from typing import List, Dict, Optional

class AppConfig:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not AppConfig._initialized:
            self.logger = self._setup_logger()
            self.base_path = os.path.join('tcat-ny-us')
            self.trips_df: Optional[pd.DataFrame] = None
            self.stop_times_df: Optional[pd.DataFrame] = None
            self.stops_df: Optional[pd.DataFrame] = None
            self._load_dataframes()
            AppConfig._initialized = True
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_dataframes(self) -> None:
        """Load all required dataframes."""
        try:
            self.trips_df = pd.read_csv(os.path.join(self.base_path, 'trips.txt'))
            self.stop_times_df = pd.read_csv(os.path.join(self.base_path, 'stop_times.txt'))
            self.stops_df = pd.read_csv(os.path.join(self.base_path, 'stops.txt'))
            self.logger.info("Successfully loaded all dataframes")
        except Exception as e:
            self.logger.error(f"Error loading dataframes: {str(e)}")
            raise
    
    def get_stops_by_trip_id(self, trip_id: str) -> List[Dict]:
        """
        Get stops information for a specific trip ID.
        
        Args:
            trip_id: The ID of the trip
            
        Returns:
            List of dictionaries containing stop information
        """
        try:
            trip_stop_times = self.stop_times_df[
                self.stop_times_df['trip_id'].astype(str) == str(trip_id)
            ]
            
            ordered_stops = (
                trip_stop_times
                .merge(self.stops_df, on='stop_id')
                .sort_values('stop_sequence')
                [['stop_name']]
                .drop_duplicates()
            )
            
            if ordered_stops.empty:
                self.logger.warning(f"No stops found for trip_id: {trip_id}")
                return []
                
            return ordered_stops.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"Error getting stops for trip_id {trip_id}: {str(e)}")
            return []
    
    def get_stops_by_route_id(self, route_id: str) -> List[Dict]:
        """
        Get stops information for a specific route ID.
        
        Args:
            route_id: The ID of the route
            
        Returns:
            List of dictionaries containing stop information
        """
        try:
            relevant_trips = self.trips_df[
                self.trips_df['route_id'].astype(str) == route_id
            ]
            self.logger.debug(f"Found relevant trips: {relevant_trips}")

            current_time = datetime.datetime.now()
            current_time_str = current_time.strftime('%H:%M:%S')
            self.logger.debug(f"Current time: {current_time_str}")

            # Get active trips for the current time
            relevant_stop_times = self.stop_times_df[
                self.stop_times_df['trip_id'].astype(str) == route_id
            ]
            active_trips = relevant_stop_times[
                (relevant_stop_times['departure_time'] <= current_time_str) & 
                (relevant_stop_times['arrival_time'] >= current_time_str)
            ]

            if active_trips.empty:
                self.logger.warning(f"No active trips found for route_id: {route_id}")
                return []

            # Get the first active trip_id
            active_trip_id = active_trips['trip_id'].iloc[0]
            self.logger.debug(f"Selected active trip ID: {active_trip_id}")

            ordered_stops = (
                self.stop_times_df[
                    self.stop_times_df['trip_id'] == active_trip_id
                ]
                .merge(self.stops_df, on='stop_id')
                .sort_values('stop_sequence')
                [['stop_name']]
                .drop_duplicates()
            )

            return ordered_stops.to_dict('records')

        except Exception as e:
            self.logger.error(f"Error getting stops for route_id {route_id}: {str(e)}")
            return []
