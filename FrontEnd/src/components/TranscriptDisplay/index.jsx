import React, { useState } from 'react'
import './styles.css'

const TranscriptDisplay = ({ transcript, onTranscriptChange, onSubmit, isProcessing }) => {
  const [localTranscript, setLocalTranscript] = useState(transcript || '')

  const handleChange = (e) => {
    const value = e.target.value
    setLocalTranscript(value)
    if (onTranscriptChange) {
      onTranscriptChange(value)
    }
  }

  const handleSubmit = () => {
    if (localTranscript.trim() && onSubmit && !isProcessing) {
      onSubmit(localTranscript.trim())
    }
  }

  // Update local state when transcript prop changes
  React.useEffect(() => {
    if (transcript !== undefined && transcript !== localTranscript) {
      setLocalTranscript(transcript)
    }
  }, [transcript])

  const isButtonDisabled = !localTranscript.trim() || isProcessing

  return (
    <div className="transcript-display">
      <div className="transcript-input-container">
        <textarea
          className="transcript-textarea"
          value={localTranscript}
          onChange={handleChange}
          placeholder="Speak or type your mathematical expression here..."
          disabled={isProcessing}
        />
      </div>
      
      <button
        className="generate-button"
        onClick={handleSubmit}
        disabled={isButtonDisabled}
        aria-label="Generate LaTeX"
      >
        <span className="generate-icon" role="img" aria-hidden="true">
          {isProcessing ? '⏳' : '✨'}
        </span>
        <span className="generate-text">
          {isProcessing ? 'Generating...' : 'Generate LaTeX'}
        </span>
      </button>
    </div>
  )
}

export default TranscriptDisplay
