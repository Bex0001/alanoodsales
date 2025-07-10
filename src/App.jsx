import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import EmployeeManagement from './components/EmployeeManagement'
import ProjectManagement from './components/ProjectManagement'
import ReportsCenter from './components/ReportsCenter'
import AdminPanel from './components/AdminPanel'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import { ThemeProvider } from './contexts/ThemeContext'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import './App.css'

function AppContent() {
  const { user, token, login, logout } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // التحقق من وجود رمز مصادقة محفوظ عند تحميل التطبيق
  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('user_data')
    
    if (savedToken && savedUser) {
      try {
        const userData = JSON.parse(savedUser)
        login(userData, savedToken)
      } catch (error) {
        console.error('خطأ في تحليل بيانات المستخدم المحفوظة:', error)
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_data')
      }
    }
  }, [login])

  if (!user || !token) {
    return <Login onLogin={login} />
  }

  return (
    <Router>
      <div className="flex h-screen bg-background" dir="rtl">
        <Sidebar 
          isOpen={sidebarOpen} 
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          user={user}
        />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header 
            user={user} 
            onLogout={logout}
            onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          />
          
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-background p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/employees" element={<EmployeeManagement />} />
              <Route path="/projects" element={<ProjectManagement />} />
              <Route path="/reports" element={<ReportsCenter />} />
              {(user.role === 'admin' || user.role === 'sales_manager') && (
                <Route path="/admin" element={<AdminPanel />} />
              )}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App

