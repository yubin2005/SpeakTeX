import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import './App.css'
import Login from './components/Login/login'
import Home from './components/Home/Home'

function App() {
  // Login state
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState('')

  // Check if user is already logged in
  useEffect(() => {
    const savedUser = localStorage.getItem('speaktex-user')
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser)
        setIsLoggedIn(true)
        setUsername(userData.username || 'User')
      } catch (err) {
        console.error('Failed to load user data:', err)
      }
    }
  }, [])

  // Handle login
  const handleLogin = (user) => {
    setIsLoggedIn(true)
    setUsername(user)
    
    // Save user data to localStorage
    const userData = {
      username: user,
      email: `${user}@example.com` // Placeholder email
    }
    localStorage.setItem('speaktex-user', JSON.stringify(userData))
  }

  // Handle logout
  const handleLogout = () => {
    setIsLoggedIn(false)
    setUsername('')
    localStorage.removeItem('speaktex-user')
  }

  // Login page wrapper with navigation
  const LoginPage = () => {
    const navigate = useNavigate()
    const location = useLocation()
    
    const handleLoginSuccess = (user) => {
      handleLogin(user)
      // Redirect to home page or the page user was trying to access
      const from = location.state?.from?.pathname || '/'
      navigate(from)
    }
    
    return <Login onLogin={handleLoginSuccess} />
  }

  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route 
            path="/login" 
            element={
              isLoggedIn ? 
                <Navigate to="/" /> : 
                <LoginPage />
            } 
          />
          <Route 
            path="/*" 
            element={
              <Home 
                isLoggedIn={isLoggedIn} 
                username={username} 
                handleLogout={handleLogout}
              />
            } 
          />
        </Routes>
      </div>
    </Router>
  )
}

export default App