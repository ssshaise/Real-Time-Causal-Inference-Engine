// src/frontend/src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/landing';
import Dashboard from './pages/Dashboard'; // Assuming you saved your dashboard code here
import Architecture from './pages/Architecture';
import Login from './pages/Login';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/login" element={<Login />} />
        <Route path="/architecture" element={<Architecture />} />
      </Routes>
    </Router>
  );
}

export default App;