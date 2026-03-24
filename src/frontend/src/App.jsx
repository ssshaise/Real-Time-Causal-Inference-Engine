import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/landing';
import Dashboard from './pages/Dashboard'; 
import Architecture from './pages/Architecture';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/architecture" element={<Architecture />} />
      </Routes>
    </Router>
  );
}

export default App;