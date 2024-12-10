import { useState, useRef } from 'react';
import Keyboard from 'react-simple-keyboard';
import { Button } from 'react-onsenui';
import { Typeahead } from "react-bootstrap-typeahead";
import { ROUTE_NAMES } from './stops';
import 'react-simple-keyboard/build/css/index.css';
import "react-bootstrap-typeahead/css/Typeahead.css";

const NotificationForm = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    email: '',
    stop: '',
    route: '30'
  });
  const [activeInput, setActiveInput] = useState('');
  const keyboardRef = useRef(null);
  
  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleKeyboardInput = (button) => {
    if (!activeInput) return;
    if (button === '{bksp}') {
      handleInputChange(activeInput, formData[activeInput].slice(0, -1));
      return;
    }
    if (button === '{enter}') return;
    
    handleInputChange(activeInput, formData[activeInput] + button);
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch('/api/v1/notification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        alert('Notification set successfully!');
        onClose();
      } else {
        throw new Error('Failed to set notification');
      }
    } catch (error) {
      alert('Error setting notification');
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.content}>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => handleInputChange('email', e.target.value)}
          onFocus={() => setActiveInput('email')}
          placeholder="Enter your email"
          style={styles.input}
        />

        <Typeahead
          id="stop-selector"
          onChange={(selected) => handleInputChange('stop', selected[0])}
          options={ROUTE_NAMES}
          selected={formData.stop ? [formData.stop] : []}
          placeholder="Choose a stop name..."
          style={styles.input}
          minLength={1}
          renderMenu={(results, menuProps) => (
            <div {...menuProps} style={styles.dropdownMenu}>
              {results.map((result, index) => (
                <div
                  key={index}
                  role="option"
                  tabIndex={0}
                  onClick={() => handleInputChange('stop', result)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      handleInputChange('stop', result);
                    }
                  }}
                  style={styles.dropdownItem}
                >
                  {result}
                </div>
              ))}
            </div>
          )}
        />

        <select
          value={formData.route}
          onChange={(e) => handleInputChange('route', e.target.value)}
          style={styles.select}
        >
          {['30', '90', '10', '82'].map(route => (
            <option key={route} value={route}>Route {route}</option>
          ))}
        </select>

        <div style={styles.keyboard}>
          <Keyboard
            keyboardRef={ref => (keyboardRef.current = ref)}
            onKeyPress={handleKeyboardInput}
            layout={{
              default: [
                "1 2 3 4 5 6 7 8 9 0",
                "q w e r t y u i o p",
                "a s d f g h j k l",
                "z x c v b n m",
                "@ . {bksp}",
              ],
            }}
          />
        </div>

        <div style={styles.buttonContainer}>
          <Button onClick={handleSubmit}>Submit</Button>
          <Button onClick={onClose}>Cancel</Button>
        </div>
      </div>
    </div>
  );
};

const NotificationButton = () => {
  const [showModal, setShowModal] = useState(false);
  
  return (
    <>
      <Button
        modifier="large"
        onClick={() => setShowModal(true)}
        style={styles.mainButton}
      >
        Notify Me!
      </Button>
      
      {showModal && (
        <NotificationForm 
          onClose={() => setShowModal(false)}
          onSubmit={() => setShowModal(false)}
        />
      )}
    </>
  );
};

const styles = {
  mainButton: { 
    flexShrink: 0, 
    width: '40vw' 
  },
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  content: {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '8px',
    width: '80vw',
    maxWidth: '600px',
    maxHeight: '90vh',
    overflow: 'auto',
  },
  input: {
    width: '100%',
    marginBottom: '10px',
    padding: '8px',
  },
  select: {
    width: '100%',
    marginBottom: '10px',
    padding: '8px',
    height: '35px',
    borderRadius: '4px',
    border: '1px solid #ccc',
  },
  keyboard: {
    marginBottom: '20px'
  },
  buttonContainer: {
    display: 'flex',
    justifyContent: 'space-between'
  },
  dropdownMenu: {
    background: 'white',
    border: '1px solid #ccc',
    borderRadius: '4px',
    maxHeight: '200px',
    overflowY: 'auto',
    padding: '5px',
    zIndex: 2000,
    position: 'absolute',
    width: '100%'
  },
  dropdownItem: {
    padding: '10px',
    cursor: 'pointer',
    borderBottom: '1px solid #eee',
    '&:last-child': {
      borderBottom: 'none'
    }
  }
};

export default NotificationButton;