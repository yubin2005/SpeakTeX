import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './styles.css'

const UserProfile = ({ isLoggedIn, username, onLogout }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const navigate = useNavigate()

  const handleAvatarClick = () => {
    setIsExpanded(!isExpanded)
  }

  const handleLogin = () => {
    navigate('/login')
    setIsExpanded(false)
  }

  const handleLogout = () => {
    onLogout()
    setIsExpanded(false)
  }

  return (
    <div className="user-profile">
      <div className={`profile-container ${isExpanded ? 'expanded' : ''}`}>
        {isLoggedIn ? (
          // Show username and avatar when logged in
          <>
            <span className="username-display">{username}</span>
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
              onClick={handleLogout}
              aria-label="Log out"
            >
              Log Out
            </button>
          </>
        ) : (
          // Show login button when not logged in
          <button
            className="login-button"
            onClick={handleLogin}
            aria-label="Log in"
          >
            Log In
          </button>
        )}
      </div>
    </div>
  )
}

export default UserProfile