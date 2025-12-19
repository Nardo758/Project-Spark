import './App.css'
import { Navigate, Route, Routes } from 'react-router-dom'
import { Nav } from './components/Nav'
import { Home } from './pages/Home'
import { Pricing } from './pages/Pricing'
import { Admin } from './pages/Admin'
import { AuthCallback } from './pages/AuthCallback'
import { Validations } from './pages/Validations'

function App() {
  return (
    <>
      <Nav />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/validations" element={<Validations />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default App
