// Gemini API service for speech-to-latex conversion

const GEMINI_API_KEY = 'AIzaSyDM0wa6jUmfv9mW9MZsJ2LB94nhR0KHbqo'
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'

const geminiService = {
  /**
   * Convert spoken mathematical expression to LaTeX code
   * @param {string} spokenText - The transcribed speech text
   * @returns {Promise<string>} - The LaTeX code with delimiters
   */
  async convertToLatex(spokenText) {
    const prompt = `Convert this spoken mathematical expression into complete LaTeX code.

IMPORTANT FORMATTING RULES:
- For display equations (centered, large), wrap in $$...$$ (double dollar signs)
- For inline equations (small, in text), wrap in $...$ (single dollar signs)
- Use \\begin{} and \\end{} for matrices, aligned equations, cases, etc.
- Choose the most appropriate LaTeX format based on the expression complexity
- Include ALL necessary LaTeX delimiters in your output
- Return ONLY the LaTeX code, no explanations or markdown

Spoken expression: ${spokenText}`

    const requestBody = {
      contents: [{
        parts: [{
          text: prompt
        }]
      }],
      generationConfig: {
        temperature: 0.1,
        maxOutputTokens: 2048
      }
    }

    try {
      const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(`Gemini API error: ${response.status} - ${JSON.stringify(errorData)}`)
      }

      const data = await response.json()
      
      // Extract LaTeX from response
      const latexCode = data.candidates?.[0]?.content?.parts?.[0]?.text

      if (!latexCode) {
        throw new Error('No LaTeX code returned from Gemini API')
      }

      // Clean up the response - remove markdown code blocks if present
      let cleanedLatex = latexCode.trim()
      
      // Remove markdown code blocks (```latex ... ``` or ``` ... ```)
      cleanedLatex = cleanedLatex.replace(/```latex\s*/g, '').replace(/```\s*/g, '')
      
      // Trim whitespace
      cleanedLatex = cleanedLatex.trim()

      return cleanedLatex
    } catch (error) {
      console.error('Error calling Gemini API:', error)
      throw error
    }
  }
}

export default geminiService
