import React, { useState, useEffect } from 'react'
import './styles.css'

const HistoryPanel = () => {
  const [history, setHistory] = useState([])

  useEffect(() => {
    // Load history from localStorage
    const savedHistory = localStorage.getItem('speaktex-history')
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory))
      } catch (err) {
        console.error('Failed to load history:', err)
      }
    }
  }, [])

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handleItemClick = (item) => {
    // TODO: Implement reload functionality
    console.log('Reload item:', item)
  }

  const clearHistory = () => {
    if (window.confirm('Are you sure you want to clear all history?')) {
      localStorage.removeItem('speaktex-history')
      setHistory([])
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

      {history.length > 0 ? (
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
