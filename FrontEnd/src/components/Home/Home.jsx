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

  // Handle recording completion
  const handleRecordingComplete = async (transcriptText) => {
    setIsProcessing(true)
    setError('')
    
    if (transcriptText) {
      setTranscript(transcriptText)
      
      try {
        // For now, we'll use a simple conversion for LaTeX
        // In a real app, you would call another API endpoint to convert text to LaTeX
        const latexText = await convertToLatex(transcriptText)
        setLatex(latexText)
      } catch (err) {
        console.error('Error converting to LaTeX:', err)
        setError('Failed to convert to LaTeX')
      }
    } else {
      setError('Failed to transcribe audio')
    }
    
    setIsProcessing(false)
  }
  
  // Improved function to convert text to LaTeX
  const convertToLatex = async (text) => {
    // Convert word numbers to digits
    const wordToNumber = {
      'zero': '0',
      'one': '1',
      'two': '2',
      'three': '3',
      'four': '4',
      'five': '5',
      'six': '6',
      'seven': '7',
      'eight': '8',
      'nine': '9',
      'ten': '10'
    };
    
    // First convert word numbers to digits
    let processedText = text.toLowerCase();
    
    // Replace word numbers with digits
    Object.keys(wordToNumber).forEach(word => {
      const regex = new RegExp(`\\b${word}\\b`, 'gi');
      processedText = processedText.replace(regex, wordToNumber[word]);
    });
    
    // Now apply mathematical replacements
    let latexText = processedText
      // Basic operations
      .replace(/\bplus\b/g, "+")
      .replace(/\bminus\b/g, "-")
      .replace(/\btimes\b/g, "\\times ")
      .replace(/\bdivided by\b/g, "\\div ")
      .replace(/\bequal to\b/g, "=")
      .replace(/\bequals\b/g, "=")
      .replace(/\bis equal to\b/g, "=")
      
      // Powers
      .replace(/\bsquared\b/g, "^2")
      .replace(/\bcubed\b/g, "^3")
      .replace(/\bto the power of (\w+)\b/g, "^{$1}")
      .replace(/\bto the (\w+) power\b/g, "^{$1}")
      
      // Fractions
      .replace(/\bfraction\b/g, "\\frac")
      .replace(/(\d+) over (\d+)/g, "\\frac{$1}{$2}")
      
      // Calculus
      .replace(/\bintegral\b/g, "\\int ")
      .replace(/\bfrom (\w+) to (\w+)\b/g, "_{$1}^{$2}")
      .replace(/\bderivative of\b/g, "\\frac{d}{dx}")
      
      // Trigonometry
      .replace(/\bsine\b/g, "\\sin ")
      .replace(/\bcosine\b/g, "\\cos ")
      .replace(/\btangent\b/g, "\\tan ")
      .replace(/\bpi\b/g, "\\pi ")
      
      // Roots
      .replace(/\bsquare root of\b/g, "\\sqrt{")
      .replace(/\bcube root of\b/g, "\\sqrt[3]{")
      
      // Parentheses
      .replace(/\bleft parenthesis\b/g, "(")
      .replace(/\bright parenthesis\b/g, ")")
      
      // Clean up extra spaces
      .replace(/\s+/g, " ")
      .trim();
    
    // Add closing braces for square roots if needed
    const openSqrt = (latexText.match(/\\sqrt\{/g) || []).length + (latexText.match(/\\sqrt\[\d+\]\{/g) || []).length;
    const closeBraces = (latexText.match(/\}/g) || []).length;
    
    if (openSqrt > closeBraces) {
      latexText += "}".repeat(openSqrt - closeBraces);
    }
    
    return latexText;
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

      {/* End of main content */}
    </div>
  )
}

export default Home