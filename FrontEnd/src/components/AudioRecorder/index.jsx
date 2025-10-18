import React, { useState } from 'react'
import './styles.css'

const AudioRecorder = ({ isRecording, isProcessing, onRecordingComplete, setIsRecording, error }) => {
  const [recordingTime, setRecordingTime] = useState(0)

  const handleClick = () => {
    if (isProcessing) return
    
    if (isRecording) {
      // Stop recording
      setIsRecording(false)
      setRecordingTime(0)
      // TODO: Implement actual recording logic
      onRecordingComplete(null)
    } else {
      // Start recording
      setIsRecording(true)
      // TODO: Implement actual recording logic
    }
  }

  const getStatusText = () => {
    if (isProcessing) return 'Processing...'
    if (isRecording) return 'Recording... Click to stop'
    if (error) return error
    return 'Click to start recording'
  }

  const getButtonClass = () => {
    let classes = 'record-button'
    if (isRecording) classes += ' recording'
    if (isProcessing) classes += ' processing'
    if (error) classes += ' error'
    return classes
  }

  return (
    <div className="audio-recorder">
      <button
        className={getButtonClass()}
        onClick={handleClick}
        disabled={isProcessing}
        aria-label={isRecording ? 'Stop recording' : 'Start recording'}
      >
        <span className="record-icon" role="img" aria-hidden="true">
          {isProcessing ? '⏳' : isRecording ? '⏹️' : '🎤'}
        </span>
      </button>
      
      <p className="status-text">{getStatusText()}</p>
      
      {isRecording && (
        <div className="recording-indicator">
          <span className="pulse-dot"></span>
          <span className="recording-label">RECORDING</span>
        </div>
      )}
    </div>
  )
}

export default AudioRecorder
