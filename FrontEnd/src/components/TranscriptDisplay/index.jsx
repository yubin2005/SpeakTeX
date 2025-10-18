import React from 'react'
import './styles.css'

const TranscriptDisplay = ({ transcript }) => {
  return (
    <div className="transcript-display">
      {transcript ? (
        <div className="transcript-content">
          <p className="transcript-text">{transcript}</p>
        </div>
      ) : (
        <div className="transcript-placeholder">
          <span className="placeholder-icon">💬</span>
          <p className="placeholder-text">Your speech will appear here...</p>
        </div>
      )}
    </div>
  )
}

export default TranscriptDisplay
