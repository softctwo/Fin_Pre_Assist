import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import Proposals from './pages/Proposals'
import ProposalCreate from './pages/ProposalCreate'
import ProposalDetail from './pages/ProposalDetail'
import Templates from './pages/Templates'
import Knowledge from './pages/Knowledge'
import { useAuthStore } from './store/authStore'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((state) => state.token)
  return token ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="documents" element={<Documents />} />
          <Route path="proposals" element={<Proposals />} />
          <Route path="proposals/create" element={<ProposalCreate />} />
          <Route path="proposals/:id" element={<ProposalDetail />} />
          <Route path="templates" element={<Templates />} />
          <Route path="knowledge" element={<Knowledge />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
