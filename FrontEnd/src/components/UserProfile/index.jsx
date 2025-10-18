import React, { useState, useEffect } from 'react'
import './styles.css'

const UserProfile = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)

  // Load login state from localStorage
  useEffect(() => {
    const savedUser = localStorage.getItem('speaktex-user')
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser)
        setIsLoggedIn(true)
      } catch (err) {
        console.error('Failed to load user data:', err)
      }
    }
  }, [])

  const handleAvatarClick = () => {
    console.log('Avatar clicked! Current expanded state:', isExpanded)
    setIsExpanded(!isExpanded)
    console.log('New expanded state:', !isExpanded)
  }

  const handleLogin = () => {
    // TODO: Navigate to login page (to be implemented by another team member)
    console.log('Navigate to login page')
    
    // For demo purposes, simulate login after clicking
    // Remove this when actual login page is implemented
    const userData = {
      username: 'User',
      email: 'user@example.com'
    }
    localStorage.setItem('speaktex-user', JSON.stringify(userData))
    setIsLoggedIn(true)
    setIsExpanded(false)
  }

  const handleLogout = () => {
    localStorage.removeItem('speaktex-user')
    setIsLoggedIn(false)
    setIsExpanded(false)
  }

  return (
    <div className="user-profile">
      <div className={`profile-container ${isExpanded ? 'expanded' : ''}`}>
        <button
          className="avatar-button"
          onClick={handleAvatarClick}
          aria-label={isExpanded ? 'Close profile menu' : 'Open profile menu'}
          aria-expanded={isExpanded}
        >
          <span className="avatar-icon" role="img" aria-hidden="true">
            👤
          </span>
        </button>

        <button
          className={`action-button ${isExpanded ? 'visible' : ''}`}
          onClick={isLoggedIn ? handleLogout : handleLogin}
          aria-label={isLoggedIn ? 'Log out' : 'Log in'}
        >
          {isLoggedIn ? 'Log Out' : 'Log In'}
        </button>
      </div>
    </div>
  )
}

export default UserProfile

