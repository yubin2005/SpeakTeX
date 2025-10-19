import React, { useState, useEffect } from 'react'
import { getUserHistory, deleteHistoryRecord, deleteAllHistory } from '../../services/historyService'
import './styles.css'

const HistoryPanel = () => {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Default user ID - in a real app, this would come from authentication
  const userId = localStorage.getItem('userId') || 'anonymous'

  useEffect(() => {
    // Fetch history from backend API
    const fetchHistory = async () => {
      try {
        setLoading(true)
        setError(null)
        const result = await getUserHistory(userId)
        
        if (result.success && result.records) {
          setHistory(result.records)
        } else {
          throw new Error(result.error || 'Failed to fetch history')
        }
      } catch (err) {
        console.error('Failed to load history:', err)
        setError('Failed to load history. Please try again later.')
        
        // Fall back to localStorage if API fails
        const savedHistory = localStorage.getItem('speaktex-history')
        if (savedHistory) {
          try {
            setHistory(JSON.parse(savedHistory))
          } catch (parseErr) {
            console.error('Failed to parse local history:', parseErr)
          }
        }
      } finally {
        setLoading(false)
      }
    }

    fetchHistory()
  }, [userId])

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  }

  const handleItemClick = (item) => {
    // Dispatch event to parent component to reload this item
    const event = new CustomEvent('reload-latex', { 
      detail: { 
        transcript: item.transcript,
        latex: item.latex
      }
    })
    window.dispatchEvent(event)
  }
  
  const handleDeleteItem = async (item, e) => {
    // Stop propagation to prevent triggering the parent click handler
    e.stopPropagation()
    
    if (window.confirm('Are you sure you want to delete this item?')) {
      try {
        const result = await deleteHistoryRecord(userId, item.timestamp)
        
        if (result.success) {
          // Update local state
          setHistory(history.filter(h => h.timestamp !== item.timestamp))
        } else {
          throw new Error(result.error || 'Failed to delete record')
        }
      } catch (err) {
        console.error('Failed to delete history item:', err)
        alert('Failed to delete item. Please try again later.')
      }
    }
  }

  const clearHistory = async () => {
    if (window.confirm('Are you sure you want to clear all history?')) {
      try {
        // Use the batch delete endpoint
        const result = await deleteAllHistory(userId)
        
        if (result.success) {
          setHistory([])
          console.log(`Cleared ${result.deleted_count} history records`)
        } else {
          throw new Error(result.error || 'Unknown error')
        }
      } catch (err) {
        console.error('Failed to clear history:', err)
        alert('Failed to clear history. Please try again later.')
      }
    }
  }

  return (
    <div className="history-panel">
      <div className="history-header">
        <h3 className="history-title">Recent Conversions</h3>
        {history.length > 0 && (
          <button 
            className="clear-history-button"
            onClick={clearHistory}
            aria-label="Clear history"
          >
            Clear All
          </button>
        )}
      </div>

      {loading ? (
        <div className="history-loading">
          <span className="loading-spinner"></span>
          <p>Loading history...</p>
        </div>
      ) : error ? (
        <div className="history-error">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
        </div>
      ) : history.length > 0 ? (
        <div className="history-list">
          {history.map((item, index) => (
            <div 
              key={item.id || index}
              className="history-item"
              onClick={() => handleItemClick(item)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleItemClick(item)}
            >
              <div className="history-item-header">
                <span className="history-timestamp">
                  {formatTimestamp(item.timestamp)}
                </span>
                <button 
                  className="delete-item-button"
                  onClick={(e) => handleDeleteItem(item, e)}
                  aria-label="Delete item"
                >
                  ×
                </button>
              </div>
              <div className="history-item-content">
                <p className="history-transcript">
                  <strong>Transcript:</strong> {item.transcript}
                </p>
                <p className="history-latex">
                  <strong>LaTeX:</strong> <code>{item.latex}</code>
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="history-empty">
          <span className="empty-icon">📋</span>
          <p className="empty-text">No history yet. Start recording to see your conversions here!</p>
        </div>
      )}
    </div>
  )
}

export default HistoryPanel