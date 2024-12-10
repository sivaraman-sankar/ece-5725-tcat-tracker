import React, { useState, useEffect } from 'react';
import './StopsViewer.css';
import NotificationButton from './NotificationButton';
import { Page, Toolbar, List, ListItem, Select } from 'react-onsenui';
import StopsViewerGraph from './StopsGraph';

const routes = [
  {value: '', label: 'Select Route' },
  {value: '30', label: 'Route 30' },
  {value: '81', label: 'Route 81' },
  {value: '90', label: 'Route 90' },
  {value: '10', label: 'Route 10' },
];

function StopsViewer() {
  const fetch_interval = 10000;
  const [stops, setStops] = useState([]);
  const [status, setStatus] = useState('Select a route');
  const [selectedRoute, setSelectedRoute] = useState('');

  const fetchStops = async (routeId) => {
    if (!routeId) return;

    setStatus('Fetching stops...');
    const apiUrl = `/api/v1/stops/${routeId}`;

    try {
      const response = await fetch(apiUrl);
      const result = await response.json();
      if (result.status === 'success') {
        if (!!!result.data.stops) {
          setStops([]);
          setStatus('No Running vehicles currently, select a different route');
        } else {
          setStops(result.data.stops);
          setStatus('Stops updated successfully.');
        }
      } else {
        setStatus('Error fetching stops.');
        console.error('API Error:', result);
      }
    } catch (error) {
      setStatus('Error fetching stops.');
      console.error('Fetch Error:', error);
    }
  };

  useEffect(() => {
    if (selectedRoute) {
      fetchStops(selectedRoute);

      const intervalId = setInterval(() => fetchStops(selectedRoute), fetch_interval);
      return () => clearInterval(intervalId);
    } else {
      setStops([]);
    }
  }, [selectedRoute]);

  const handleRouteChange = (event) => {
    setSelectedRoute(event.target.value);
  };

  const getClassName = (stop) => {
    if (!!!stop) { return 'hide' };
    return stop['is_incoming'] ? 'incoming' : 'not-incoming';

  };

  return (
    <Page>
      <Toolbar>
        <div className="center">TCAT Tracker</div>
      </Toolbar>

      {/* Main Content */}
      <div style={{ marginTop: '2rem', padding: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', gap: '2rem' }}>
          <Select
            value={selectedRoute}
            onChange={handleRouteChange}
            style={{ flex: 1, marginRight: '8px' }} // Flex-grow for Select and spacing
          >
            {routes.map((route) => (
              <option key={route.value} value={route.value}>
                {route.label}
              </option>
            ))}
          </Select>
          {/* Notify Button */}
          <NotificationButton></NotificationButton>
        </div>

        <p style={{ marginTop: '16px', textAlign: 'center' }}>{status}</p>


        <div>
          <StopsViewerGraph numPoints={stops.length} stops={stops} />
        </div>

        {/* Stops List */}
        <div style={{ height: '10vw', overflow: 'auto' }}>
          <List
            dataSource={stops}
            renderRow={(stop, index) => (
              <ListItem key={index} className={getClassName(stop)}>
                <span style={{ fontWeight: stop.is_incoming ? 'bold' : 'normal' }}>
                  {stop.stop_name}
                </span>
              </ListItem>
            )}
          >
            {stops.length === 0 && status === 'Select a route' && (
              <ListItem>Select a route for More Details</ListItem>
            )}
          </List>
        </div>

      </div>
    </Page>
  );
}

export default StopsViewer;