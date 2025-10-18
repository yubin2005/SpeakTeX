import React, { useState, useEffect } from 'react'
import './styles.css'

const LatexPreview = ({ latex }) => {
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    // Trigger MathJax to render when latex changes
    if (latex && window.MathJax) {
      window.MathJax.typesetPromise().catch((err) => console.error('MathJax error:', err))
    }
  }, [latex])

  const handleCopy = () => {
    if (!latex) return
    
    navigator.clipboard.writeText(latex).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }).catch((err) => {
      console.error('Failed to copy:', err)
    })
  }

  return (
    <div className="latex-preview">
      {latex ? (
        <>
          <div className="latex-code-section">
            <h3 className="section-label">LaTeX Code</h3>
            <div className="latex-code">
              <code>{latex}</code>
            </div>
          </div>
          
          <div className="latex-render-section">
            <h3 className="section-label">Preview</h3>
            <div className="latex-render">
              <div className="math-display">
                {`$$${latex}$$`}
              </div>
            </div>
          </div>

          <button 
            className="copy-button"
            onClick={handleCopy}
            aria-label="Copy LaTeX code"
          >
            <span className="copy-icon" role="img" aria-hidden="true">
              {copied ? '✓' : '📋'}
            </span>
            <span className="copy-text">{copied ? 'Copied!' : 'Copy Code'}</span>
          </button>
        </>
      ) : (
        <div className="latex-placeholder">
          <span className="placeholder-icon">✨</span>
          <p className="placeholder-text">LaTeX output will appear here...</p>
          <div className="example-preview">
            <p className="example-label">Example:</p>
            <div className="math-display example">
              {`$$x^2 + 2x + 1 = 0$$`}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default LatexPreview
