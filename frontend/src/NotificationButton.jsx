import { useState } from 'react';
import Keyboard from 'react-simple-keyboard';
import 'react-simple-keyboard/build/css/index.css';
import { Page, Toolbar, Button, List, ListItem, Select } from 'react-onsenui';

const NotificationButton = () => {
  const [showModal, setShowModal] = useState(false);
  const [email, setEmail] = useState('');
  const [stop, setStop] = useState('');
  const [route, setRoute] = useState('30'); // Default value
  const [activeInput, setActiveInput] = useState('');

  const routes = ['30', '90', '10', '82'];

  const onKeyPress = (button) => {
    if (button === '{enter}') {
      return;
    }
    
    if (button === '{bksp}') {
      switch(activeInput) {
        case 'email':
          setEmail(prev => prev.slice(0, -1));
          break;
        case 'stop':
          setStop(prev => prev.slice(0, -1));
          break;
      }
      return;
    }

    switch(activeInput) {
      case 'email':
        setEmail(prev => prev + button);
        break;
      case 'stop':
        setStop(prev => prev + button);
        break;
    }
  };

  const handleInputFocus = (inputName) => {
    setActiveInput(inputName);
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch('/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          stop,
          route
        })
      });
      
      if (response.ok) {
        alert('Notification set successfully!');
        setShowModal(false);
        setEmail('');
        setStop('');
        setRoute('30');
      } else {
        alert('Failed to set notification');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error setting notification');
    }
  };

  return (
    <div>
      <Button
        modifier="large"
        onClick={() => setShowModal(true)}
        style={{ flexShrink: 0, width: '40vw' }}
      >
        Notify Me!
      </Button>

      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            width: '80vw',
            maxWidth: '600px'
          }}>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onFocus={() => handleInputFocus('email')}
              placeholder="Enter your email"
              style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
            />
            <input
              type="text"
              value={stop}
              onChange={(e) => setStop(e.target.value)}
              onFocus={() => handleInputFocus('stop')}
              placeholder="Enter stop number"
              style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
            />
            <select
              value={route}
              onChange={(e) => setRoute(e.target.value)}
              style={{ 
                width: '100%', 
                marginBottom: '10px', 
                padding: '8px',
                height: '35px',
                borderRadius: '4px',
                border: '1px solid #ccc'
              }}
            >
              {routes.map(routeNumber => (
                <option key={routeNumber} value={routeNumber}>
                  Route {routeNumber}
                </option>
              ))}
            </select>
            <div style={{ marginBottom: '20px' }}>
              <Keyboard
                onKeyPress={onKeyPress}
                layout={{
                  default: [
                    "1 2 3 4 5 6 7 8 9 0",
                    "q w e r t y u i o p",
                    "a s d f g h j k l",
                    "z x c v b n m",
                    "@ . {bksp}"
                  ]
                }}
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button onClick={handleSubmit}>Submit</Button>
              <Button onClick={() => setShowModal(false)}>Cancel</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationButton;