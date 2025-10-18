import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import AudioRecorder from '../AudioRecorder'
import TranscriptDisplay from '../TranscriptDisplay'
import LatexPreview from '../LatexPreview'
import HistoryPanel from '../HistoryPanel'
import UserProfile from '../UserProfile'
import './Home.css'

const Home = ({ isLoggedIn, username, handleLogout }) => {
  const [transcript, setTranscript] = useState('')
  const [latex, setLatex] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)

  // Handle scroll effects
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset
      if (scrollTop > 50) {
        setIsScrolled(true)
      } else {
        setIsScrolled(false)
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

  // Handle recording
  const handleRecordingComplete = async (audioBlob) => {
    setIsProcessing(true)
    setError('')
    
    // TODO: Implement API call to backend
    // Placeholder for now
    setTimeout(() => {
      setTranscript('x squared plus 2x plus 1 equals 0')
      setLatex('x^2 + 2x + 1 = 0')
      setIsProcessing(false)
    }, 2000)
  }

  return (
    <div className="home-container">
      {/* Top Navigation Bar */}
      <header className={`top-bar ${isScrolled ? 'scrolled' : ''}`}>
        <Link to="/" className="logo-link">
          <div className="logo">
            <span className="logo-icon">🎙️</span>
            <span className="logo-text">SpeakTeX</span>
          </div>
        </Link>
        <UserProfile isLoggedIn={isLoggedIn} username={username} onLogout={handleLogout} />
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        <h1 className="page-title" style={{ marginTop: '2rem' }}>Convert Your Voice to LaTeX</h1>
        <p className="page-description">Just speak naturally and get instant LaTeX code</p>
        <div className="content-grid">
          {/* Left Section - Recording Area */}
          <section className={`card recording-card ${isRecording ? 'recording-active' : ''}`}>
            <h2 className="card-title">Recording</h2>
            <AudioRecorder
              isRecording={isRecording}
              isProcessing={isProcessing}
              onRecordingComplete={handleRecordingComplete}
              setIsRecording={setIsRecording}
              error={error}
            />
          </section>

          {/* Middle Section - Transcript Display */}
          <section className="card transcript-card">
            <h2 className="card-title">Transcript</h2>
            <TranscriptDisplay transcript={transcript} />
          </section>

          {/* Right Section - LaTeX Preview */}
          <section className="card latex-card">
            <h2 className="card-title">LaTeX Output</h2>
            <LatexPreview latex={latex} />
          </section>
        </div>

        {/* Bottom Section - History Panel */}
        <section className="history-section">
          <button 
            className="history-toggle"
            onClick={() => setShowHistory(!showHistory)}
            aria-label="Toggle history panel"
          >
            {showHistory ? '▼' : '▲'} History
          </button>
          {showHistory && <HistoryPanel />}
        </section>
      </main>

      {/* Empty space at bottom for better spacing */}
      <div className="bottom-spacing"></div>
    </div>
  )
}

export default Home