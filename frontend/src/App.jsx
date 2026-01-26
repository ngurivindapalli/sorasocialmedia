import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './components/LandingPage'
import Login from './components/auth/Login'
import Signup from './components/auth/Signup'
import Dashboard from './pages/Dashboard'
import MarketingPost from './pages/MarketingPost'
// Hyperspell removed - using MemoryService (S3 + Mem0) directly
import SEOAEOTracker from './pages/SEOAEOTracker'
import TermsOfService from './pages/TermsOfService'
import PrivacyPolicy from './pages/PrivacyPolicy'
import ProtectedRoute from './components/ProtectedRoute'
import ContentCalendar from './pages/ContentCalendar'
import ContentCalendarView from './pages/ContentCalendarView'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        {/* Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/marketing-post" element={<ProtectedRoute><MarketingPost /></ProtectedRoute>} />
        <Route path="/seo-aeo" element={<ProtectedRoute><SEOAEOTracker /></ProtectedRoute>} />
        <Route path="/content-calendar" element={<ProtectedRoute><ContentCalendar /></ProtectedRoute>} />
        <Route path="/content-calendar/day/:day" element={<ProtectedRoute><ContentCalendarView /></ProtectedRoute>} />
        <Route path="/terms" element={<TermsOfService />} />
        <Route path="/privacy" element={<PrivacyPolicy />} />
        {/* Hyperspell route removed - using MemoryService (S3 + Mem0) directly */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
