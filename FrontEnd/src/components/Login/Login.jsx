import React, { useState } from 'react'
import './Login.css'

const Login = ({ onLogin }) => {
  // State for form inputs
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault()
    if (email && password) {
      // Pass email to parent component
      if (onLogin) onLogin(email)
    }
  }

  // Toggle password visibility
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  return (
    <div className="login-container">
      {/* Top navigation bar */}
      <div className="top-bar">
        <div className="logo">🎙️ SpeakTeX</div>
        <div className="subtitle">Voice to LaTeX</div>
      </div>
      
      {/* Login form card */}
      <div className="login-card card">
        <h2 className="card-title">Welcome to SpeakTeX</h2>
        <div className="card-subtitle">
          <p>Convert spoken math to LaTeX</p>
          <p>Hands-free, just by speaking naturally!</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <div className="input-with-icon">
              <span className="input-icon">✉️</span>
              <input 
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                required
                className="input-field"
              />
            </div>
          </div>
          
          <div className="input-group">
            <div className="input-with-icon">
              <span className="input-icon">🔒</span>
              <input 
                type={showPassword ? "text" : "password"} 
                value={password} 
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                required
                className="input-field"
              />
              <button 
                type="button" 
                onClick={togglePasswordVisibility} 
                className="toggle-password"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "👁️" : "👁️‍🗨️"}
              </button>
            </div>
          </div>
          
          <div className="forgot-password">
            <a href="#forgot">Forgot password?</a>
          </div>
          
          <button type="submit" className="login-btn">
            Get Started
          </button>
        </form>
        
        <div className="divider">
          <span>Or sign in with</span>
        </div>
        
        <div className="social-login">
          <button className="social-btn google">
            <img src="icon/google-logo-icon.png" alt="Google" />
            <span>Log in with Google</span>
          </button>
        </div>
      </div>
      
      {/* Feature highlights */}
      <div className="login-features">
        <div className="feature-card card">
          <div className="feature-icon">🎤</div>
          <div className="feature-title">Voice Input</div>
          <div className="feature-desc">Speak math formulas directly</div>
        </div>
        
        <div className="feature-card card">
          <div className="feature-icon">📋</div>
          <div className="feature-title">LaTeX Conversion</div>
          <div className="feature-desc">Auto-generate LaTeX code</div>
        </div>
        
        <div className="feature-card card">
          <div className="feature-icon">👁️</div>
          <div className="feature-title">Real-time Preview</div>
          <div className="feature-desc">Instantly see rendered results</div>
        </div>
      </div>
    </div>
  )
}

export default Login