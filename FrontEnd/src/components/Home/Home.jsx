import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import AudioRecorder from '../AudioRecorder'
import TranscriptDisplay from '../TranscriptDisplay'
import LatexPreview from '../LatexPreview'
import HistoryPanel from '../HistoryPanel'
import UserProfile from '../UserProfile'
import geminiService from '../../services/geminiService'
import './Home.css'

const Home = ({ isLoggedIn, username, handleLogout }) => {
  const [transcript, setTranscript] = useState('')
  const [latex, setLatex] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const [processingTime, setProcessingTime] = useState(null)
  const [successMessage, setSuccessMessage] = useState('')

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

  // Handle recording completion
  const handleRecordingComplete = async (transcriptText) => {
    if (transcriptText) {
      setTranscript(transcriptText)
    } else {
      setError('Failed to transcribe audio')
    }
  }

  // Handle manual submission (Generate LaTeX button)
  const handleGenerateLatex = async (transcriptText) => {
    setIsProcessing(true)
    setError('')
    setSuccessMessage('')
    setProcessingTime(null)
    
    const startTime = performance.now()
    
    try {
      // Call Gemini API to convert text to LaTeX
      const latexText = await geminiService.convertToLatex(transcriptText)
      
      setLatex(latexText)
      // Remove processing time and success message display
      setProcessingTime(null)
      setSuccessMessage('')
    } catch (err) {
      console.error('Error converting to LaTeX:', err)
      
      // Determine error type and provide user-friendly message
      let errorMessage = 'Failed to convert to LaTeX'
      
      if (err.message.includes('Failed to fetch') || err.message.includes('Network')) {
        errorMessage = '❌ Network error: Failed to connect to Gemini API'
      } else if (err.message.includes('timeout') || err.message.includes('timed out')) {
        errorMessage = '❌ Request timed out, please try again'
      } else if (err.message.includes('API error')) {
        errorMessage = `❌ Gemini API error: ${err.message}`
      } else {
        errorMessage = `❌ Error: ${err.message}`
      }
      
      setError(errorMessage)
      
      // Clear error message after 8 seconds
      setTimeout(() => {
        setError('')
      }, 8000)
    } finally {
      setIsProcessing(false)
    }
  }

  // Handle transcript change (user editing)
  const handleTranscriptChange = (newTranscript) => {
    setTranscript(newTranscript)
    // Clear success message when user edits
    if (successMessage) {
      setSuccessMessage('')
    }
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
            <TranscriptDisplay 
              transcript={transcript}
              onTranscriptChange={handleTranscriptChange}
              onSubmit={handleGenerateLatex}
              isProcessing={isProcessing}
            />
            {error && <div className="status-message error-message">{error}</div>}
            {successMessage && <div className="status-message success-message">{successMessage}</div>}
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

      {/* End of main content */}
    </div>
  )
}

export default Home