import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/Layout'
import RequireAuth from './components/RequireAuth'
import RequirePaid from './components/RequirePaid'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Discover from './pages/Discover'
import IdeaEngine from './pages/IdeaEngine'
import Pricing from './pages/Pricing'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Services from './pages/Services'
import Network from './pages/Network'
import Leads from './pages/Leads'
import Funding from './pages/Funding'
import Tools from './pages/Tools'
import Learn from './pages/Learn'
import Cart from './pages/Cart'
import Account from './pages/Account'
import Purchases from './pages/Purchases'
import Analytics from './pages/Analytics'
import AIRoadmap from './pages/AIRoadmap'
import AIMatch from './pages/AIMatch'
import ExpertMarketplace from './pages/ExpertMarketplace'
import About from './pages/About'
import Blog from './pages/Blog'
import Contact from './pages/Contact'
import Terms from './pages/Terms'
import Privacy from './pages/Privacy'
import BrainDashboard from './pages/brain/BrainDashboard'
import AuthCallback from './pages/AuthCallback'
import MagicLinkCallback from './pages/MagicLinkCallback'
import Saved from './pages/Saved'
import OpportunityDetail from './pages/OpportunityDetail'
import ReportStudio from './pages/build/ReportStudio'
import Marketplace from './pages/marketplace/Marketplace'
import LeadDetail from './pages/marketplace/LeadDetail'
import MarketplaceDashboard from './pages/marketplace/Dashboard'
import Inbox from './pages/network/Inbox'
import DeveloperPortal from './pages/developer/DeveloperPortal'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={isAuthenticated ? <Dashboard /> : <Home />} />
        <Route path="discover" element={<Discover />} />
        <Route path="idea-engine" element={<IdeaEngine />} />
        <Route path="services" element={<Services />} />
        <Route path="network" element={<Network />} />
        <Route path="pricing" element={<Pricing />} />
        <Route path="cart" element={<Cart />} />
        <Route path="marketplace" element={<Marketplace />} />
        <Route path="marketplace/lead/:id" element={<LeadDetail />} />
        <Route path="opportunity/:id" element={<OpportunityDetail />} />
        <Route path="login" element={<Login />} />
        <Route path="signup" element={<Signup />} />
        <Route
          path="leads"
          element={
            <RequireAuth>
              <Leads />
            </RequireAuth>
          }
        />
        <Route
          path="tools"
          element={
            <RequireAuth>
              <Tools />
            </RequireAuth>
          }
        />
        <Route
          path="funding"
          element={
            <RequirePaid>
              <Funding />
            </RequirePaid>
          }
        />
        <Route path="learn" element={<Learn />} />
        <Route path="ai-roadmap" element={<AIRoadmap />} />
        <Route path="ai-match" element={<AIMatch />} />
        <Route path="expert-marketplace" element={<ExpertMarketplace />} />
        <Route path="content" element={<Navigate to="/services" replace />} />
        <Route path="about" element={<About />} />
        <Route path="blog" element={<Blog />} />
        <Route path="contact" element={<Contact />} />
        <Route path="terms" element={<Terms />} />
        <Route path="privacy" element={<Privacy />} />
        <Route
          path="saved"
          element={
            <RequireAuth>
              <Saved />
            </RequireAuth>
          }
        />
        <Route
          path="dashboard"
          element={
            <RequireAuth>
              <Dashboard />
            </RequireAuth>
          }
        />
        <Route
          path="brain"
          element={
            <RequireAuth>
              <BrainDashboard />
            </RequireAuth>
          }
        />
        <Route
          path="account"
          element={
            <RequireAuth>
              <Account />
            </RequireAuth>
          }
        />
        <Route
          path="purchases"
          element={
            <RequireAuth>
              <Purchases />
            </RequireAuth>
          }
        />
        <Route
          path="analytics"
          element={
            <RequirePaid>
              <Analytics />
            </RequirePaid>
          }
        />
        <Route
          path="marketplace/dashboard"
          element={
            <RequireAuth>
              <MarketplaceDashboard />
            </RequireAuth>
          }
        />
        <Route
          path="network/inbox"
          element={
            <RequireAuth>
              <Inbox />
            </RequireAuth>
          }
        />
        <Route
          path="developer"
          element={
            <RequirePaid>
              <DeveloperPortal />
            </RequirePaid>
          }
        />
        <Route
          path="build/reports"
          element={
            <RequirePaid>
              <ReportStudio />
            </RequirePaid>
          }
        />
        <Route
          path="build/reports/:type"
          element={
            <RequirePaid>
              <ReportStudio />
            </RequirePaid>
          }
        />
        <Route
          path="build/business-plan"
          element={
            <RequirePaid>
              <ReportStudio />
            </RequirePaid>
          }
        />
        <Route
          path="build/financials"
          element={
            <RequirePaid>
              <ReportStudio />
            </RequirePaid>
          }
        />
        <Route
          path="build/pitch-deck"
          element={
            <RequirePaid>
              <ReportStudio />
            </RequirePaid>
          }
        />
        <Route path="auth/callback" element={<AuthCallback />} />
        <Route path="auth/magic" element={<MagicLinkCallback />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

export default App
