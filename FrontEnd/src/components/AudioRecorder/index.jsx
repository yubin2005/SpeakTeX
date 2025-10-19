import React, { useState, useRef, useEffect } from 'react'
import './styles.css'

const AudioRecorder = ({ isRecording, isProcessing, onRecordingComplete, setIsRecording, error }) => {
  const [recordingTime, setRecordingTime] = useState(0)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const timerRef = useRef(null)

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.removeEventListener('dataavailable', handleDataAvailable)
        mediaRecorderRef.current.removeEventListener('stop', handleStop)
      }
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [])

  const handleDataAvailable = (event) => {
    if (event.data.size > 0) {
      audioChunksRef.current.push(event.data)
    }
  }

  const handleStop = async () => {
    const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
    audioChunksRef.current = []
    await sendAudioToBackend(audioBlob)
  }

  const sendAudioToBackend = async (audioBlob) => {
    try {
      console.log('Step 1: Getting presigned upload URL from Lambda...')
      
      const uploadUrlResponse = await fetch('http://localhost:5000/get-upload-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_extension: 'webm' })
      })

      if (!uploadUrlResponse.ok) {
        throw new Error(`Failed to get upload URL: ${uploadUrlResponse.status}`)
      }

      const uploadData = await uploadUrlResponse.json()
      
      if (!uploadData.success) {
        throw new Error(uploadData.error || 'Failed to generate upload URL')
      }

      console.log('Step 2: Uploading audio directly to S3...')
      console.log('File will be saved as:', uploadData.file_key)
      
      const s3Response = await fetch(uploadData.upload_url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'audio/webm'
        },
        body: audioBlob
      })

      if (!s3Response.ok) {
        throw new Error(`S3 upload failed: ${s3Response.status}`)
      }

      console.log('✓ Audio uploaded successfully to S3!')
      console.log('✓ File key:', uploadData.file_key)
      
      console.log('Step 3: Starting AWS Transcribe job...')
      
      const transcribeResponse = await fetch('http://localhost:5000/transcribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          s3_file_key: uploadData.file_key 
        })
      })

      if (!transcribeResponse.ok) {
        throw new Error(`Transcription failed: ${transcribeResponse.status}`)
      }

      const transcribeData = await transcribeResponse.json()
      
      if (!transcribeData.success) {
        throw new Error(transcribeData.error || 'Transcription failed')
      }

      console.log('✓ Transcription completed!')
      console.log('✓ Transcript:', transcribeData.transcript_text)
      console.log('✓ LaTeX:', transcribeData.latex_code)
      console.log('✓ Saved to:', transcribeData.filepath)
      
      onRecordingComplete({
        transcript: transcribeData.transcript_text,
        latex: transcribeData.latex_code
      })
      
    } catch (error) {
      console.error('Error in recording workflow:', error)
      throw error
    }
  }

  const startRecording = async () => {
    try {
      audioChunksRef.current = []
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorder.addEventListener('dataavailable', handleDataAvailable)
      mediaRecorder.addEventListener('stop', handleStop)
      
      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.start()
      
      mediaRecorder.addEventListener('start', () => {
        mediaRecorder.requestData();
      });
      
      let seconds = 0
      timerRef.current = setInterval(() => {
        seconds++
        setRecordingTime(seconds)
        
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          mediaRecorderRef.current.requestData();
        }
        
        if (seconds >= 30) {
          stopRecording()
        }
      }, 1000)
    } catch (err) {
      console.error('Error starting recording:', err)
      setIsRecording(false)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
    }
    
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    
    setRecordingTime(0)
  }

  const handleClick = () => {
    if (isProcessing) return
    
    if (isRecording) {
      setIsRecording(false)
      stopRecording()
    } else {
      setIsRecording(true)
      startRecording()
    }
  }

  const getStatusText = () => {
    if (isProcessing) return 'Processing...'
    if (isRecording) return `Recording... ${recordingTime}s (Click to stop)`
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