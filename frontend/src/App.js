import logo from './logo.svg';
import './App.css';
import StopsViewer from './StopsViewer';
import 'onsenui/css/onsenui.css'; // Core CSS
import 'onsenui/css/onsen-css-components.css'; // Theme CSS (Material Design, iOS styles)
import { Page, Toolbar, Button } from 'react-onsenui'; // Import specific components
import StopsViewerGraph from './StopsGraph';

function App() {
  return (
    <div className="App">
      <StopsViewer/>
    </div>
  );
}

export default App;
