const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'

const geminiService = {
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
      
      const latexCode = data.candidates?.[0]?.content?.parts?.[0]?.text

      if (!latexCode) {
        throw new Error('No LaTeX code returned from Gemini API')
      }

      let cleanedLatex = latexCode.trim()
      cleanedLatex = cleanedLatex.replace(/```latex\s*/g, '').replace(/```\s*/g, '')
      cleanedLatex = cleanedLatex.trim()

      return cleanedLatex
    } catch (error) {
      console.error('Error calling Gemini API:', error)
      throw error
    }
  }
}

export default geminiService
