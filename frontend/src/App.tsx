import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/Layout'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Discover from './pages/Discover'
import IdeaEngine from './pages/IdeaEngine'
import Pricing from './pages/Pricing'
import Login from './pages/Login'
import Signup from './pages/Signup'
import BrainDashboard from './pages/brain/BrainDashboard'
import AuthCallback from './pages/AuthCallback'
import MagicLinkCallback from './pages/MagicLinkCallback'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={isAuthenticated ? <Dashboard /> : <Home />} />
        <Route path="discover" element={<Discover />} />
        <Route path="idea-engine" element={<IdeaEngine />} />
        <Route path="pricing" element={<Pricing />} />
        <Route path="login" element={<Login />} />
        <Route path="signup" element={<Signup />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="brain" element={<BrainDashboard />} />
        <Route path="auth/callback" element={<AuthCallback />} />
        <Route path="auth/magic" element={<MagicLinkCallback />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

export default App
