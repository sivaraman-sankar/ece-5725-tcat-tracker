# TCAT Tracker

## 1. Introduction
TCAT Tracker is a real-time bus tracking system for Tompkins Consolidated Area Transit, designed to run on a Raspberry Pi server. The system provides live bus location updates, route visualization, and email notifications.

### Tech Stack
- **Frontend**: React.js, onsenui
- **Backend**: Flask (Python)
- **Hardware**: Raspberry Pi 4 Model B
- **Display**: PiTFT 3.5" resistive touch screen
- **Email Service**: SendGrid API

### Key Features
- Real-time bus tracking using TCAT's public API
- Interactive route visualization with stop selection
- Email notifications for bus arrivals
- Mobile-responsive design
- Kiosk mode optimized for PiTFT display
- Server deployment on Raspberry Pi

## 2. Setup

### Backend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/sivaraman-sankar/ece-5725-tcat-tracker.git
   cd ece-5725-tcat-tracker
   ```

2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Launch the server:
    ```bash
    ./start_server.sh
    ```

5. Visit `http://<your_ip>:5000` to view the website

### Optional Setup

#### SendGrid Configuration
1. Create a SendGrid account
2. Generate API key from SendGrid dashboard
3. Create `.env` file:
   ```
   SENDGRID_API_KEY=your_api_key
   FROM_EMAIL=your_email
   ```

#### PiTFT Display Setup

1. Launch the website in kiosk mode:
   ```bash
   ./cmd.sh
   ```

### Frontend Setup
1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Build the application:
   ```bash
   npm run build
   ```

## 3. Demo
- [System Overview and Features](https://drive.google.com/file/d/1EexffGljyLN1diIFRaSe8hY7eQZBvfOS/view?usp=sharing)
- [PiTFT Integration Demo](https://drive.google.com/file/d/10gTdPnRN-oDLlZ8IlpzHvNlZ-8wBmv5t/view?usp=sharing)

## 4. Debugging

1. Server Issues:
   ```bash
   tail -f output.log
   ```

2. Permission Errors:
   ```bash
   chmod 644 start_server.sh
   chmod 644 cmd.sh
   ```

3. Display Issues:
   ```bash
   ls /dev/fb*
   sudo modprobe fb1
   ```

4. Email Configuration:
   - Verify SendGrid API key in .env
   - Check server logs for email errors
   - Verify FROM_EMAIL is authenticated

## 5. References

1. React.js - [React Documentation](https://reactjs.org/)
2. Flask - [Flask Documentation](https://flask.palletsprojects.com/)
3. SendGrid - [SendGrid API Documentation](https://docs.sendgrid.com/)
4. Raspberry Pi - [Official Documentation](https://www.raspberrypi.org/documentation/)
5. PiTFT Setup - [Adafruit PiTFT Guide](https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi)
6. Material-UI - [Official Documentation](https://material-ui.com/)
7. TCAT API - [TCAT Developer Resources](https://www.tcatbus.com/developers)
8. Python Virtual Environment - [Python venv](https://docs.python.org/3/library/venv.html)

## 6. License
This project is licensed under the MIT License. See the LICENSE file for details.

Feel free to use, modify, and distribute this software according to the terms of the MIT License.