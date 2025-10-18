import { useState } from 'react'
import './App.css'
import Login from './components/Login/login'

function App() {
  // Login state
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState('')

  // Handle login
  const handleLogin = (user) => {
    setIsLoggedIn(true)
    setUsername(user)
  }

  return (
    <div className="app-container">
      {!isLoggedIn ? (
        <Login onLogin={handleLogin} />
      ) : (
        <div className="main-content">
          <h1>Welcome, {username}!</h1>
          <p>Main app content will go here</p>
        </div>
      )}
    </div>
  )
}

export default App