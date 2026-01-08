import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import QueryInterface from './pages/QueryInterface';
import SiloManagement from './pages/SiloManagement';
import PrivacyCenter from './pages/PrivacyCenter';
import Analytics from './pages/Analytics';
import Documentation from './pages/Documentation';
import Demo from './pages/Demo';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="pb-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/query" element={<QueryInterface />} />
            <Route path="/silos" element={<SiloManagement />} />
            <Route path="/privacy" element={<PrivacyCenter />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/docs" element={<Documentation />} />
            <Route path="/demo" element={<Demo />} />
          </Routes>
        </main>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;