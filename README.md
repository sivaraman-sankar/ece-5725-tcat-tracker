# TCAT Tracker

A real-time bus tracking system for TCAT (Tompkins Consolidated Area Transit) built with Flask and React.js.

## Features

- Real-time bus tracking
- Email notifications for bus arrivals
- Interactive route visualization
- Mobile-responsive design
- Kiosk mode support for PiTFT display

## Quick Start

### Demo Mode

```bash
cd /home/pi
./start_server.sh
./cmd.sh

# View logs
tail -f backend/output.log
```

## Development Setup

### Backend Setup

1. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Launch server

```bash
python app.py
# Server runs on port 5000
```

### Frontend Setup

1. Install Node.js and npm
2. Install dependencies and build

```bash
npm install
npm run build
```

## Display Modes

### PiTFT Kiosk Mode

The application supports a dedicated kiosk mode optimized for PiTFT displays, featuring:

- Touch-screen interface
- Responsive layout
- On-screen keyboard for notifications

### Multi-Device Support

- Responsive design that adapts to different screen sizes
- Optimized for both mobile and desktop views
- Support for various browser resolutions

## Features

### Notification System

- Email alerts for bus arrivals
- On-screen keyboard integration
- Real-time status updates

### Interactive Interface

- Live route visualization
- Stop selection with typeahead
- Real-time tracking updates

## Project Structure

```
├── backend/
│   ├── app.py                 # Main server entry point
│   ├── app_config.py          # Configuration management
│   ├── notification_manager.py # Email notification system
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── StopsViewer.js    # Route visualization
│   │   └── stops.js          # Stop data management
│   └── package.json          # Node.js dependencies
└── README.md                 # Project documentation
```

## Documentation

- [Demo Video 1](https://drive.google.com/file/d/1EexffGljyLN1diIFRaSe8hY7eQZBvfOS/view?usp=sharing) (Requires Cornell NetID)
- [Demo Video 2](https://drive.google.com/file/d/10gTdPnRN-oDLlZ8IlpzHvNlZ-8wBmv5t/view?usp=sharing) (Requires Cornell NetID)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
