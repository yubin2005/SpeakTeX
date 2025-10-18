import { useState } from 'react'
import './App.css'
import AudioRecorder from './components/AudioRecorder'
import TranscriptDisplay from './components/TranscriptDisplay'
import LatexPreview from './components/LatexPreview'
import HistoryPanel from './components/HistoryPanel'
import UserProfile from './components/UserProfile'

function App() {
  const [transcript, setTranscript] = useState('')
  const [latex, setLatex] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState('')
  const [showHistory, setShowHistory] = useState(false)

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
    <div className="app-container">
      {/* Top Navigation Bar */}
      <header className="top-bar">
        <div className="logo">
          <span className="logo-icon">🎙️</span>
          <span className="logo-text">SpeakTeX</span>
        </div>
        <UserProfile />
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        <div className="content-grid">
          {/* Left Section - Recording Area */}
          <section className="card recording-card">
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
    </div>
  )
}

export default App