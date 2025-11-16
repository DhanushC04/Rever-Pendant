import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Home, History as HistoryIcon, MessageSquare } from 'lucide-react';
import Dashboard from './components/Dashboard';
import History from './components/History';
import ConversationDetail from './components/ConversationDetail';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <Router>
      <div className="App">
        {/* Navigation */}
        <nav className="bg-slate-900 border-b border-white/10">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg"></div>
                <span className="text-white font-bold text-xl">AI Pendant</span>
              </div>
              
              <div className="flex gap-4">
                <Link 
                  to="/"
                  className="flex items-center gap-2 text-gray-300 hover:text-white px-4 py-2 rounded-lg hover:bg-white/10 transition-all"
                >
                  <Home className="w-5 h-5" />
                  Dashboard
                </Link>
                <Link 
                  to="/history"
                  className="flex items-center gap-2 text-gray-300 hover:text-white px-4 py-2 rounded-lg hover:bg-white/10 transition-all"
                >
                  <HistoryIcon className="w-5 h-5" />
                  History
                </Link>
                <Link 
                  to="/chat"
                  className="flex items-center gap-2 text-gray-300 hover:text-white px-4 py-2 rounded-lg hover:bg-white/10 transition-all"
                >
                  <MessageSquare className="w-5 h-5" />
                  Chat
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
          <Route path="/conversation/:id" element={<ConversationDetail />} />
          <Route path="/chat" element={<ChatInterface />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;