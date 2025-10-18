## 🎙️ SpeakTeX: From Voice to LaTeX

## 🚀 Project Overview
SpeakTeX is a web application that converts spoken mathematical expressions into LaTeX code. Simply speak into your microphone, and watch as your mathematical expressions are instantly rendered in beautiful LaTeX.

## 🎯 Our Project Goal: Audio → LaTeX
- A web application: Users speak mathematical expressions into a microphone. The application converts the speech to LaTeX code in real time and renders the mathematical expression.

## ⚙️ How It Works
1. User speaks mathematical expression into microphone
2. Audio sent to backend API
3. Gemini API processes audio/text and converts to LaTeX
4. Frontend renders LaTeX using MathJax
5. User can copy LaTeX code or save to history

## 👥 Team Roles
|   Team Member  | Responsibilities |
|----------------|------------------|
|   Yubin Li     | Frontend Development, UI/UX Design |
|   Zongze Wu    | Backend Development, Gemini API Integration |

## 🧩 Tech Stack
- **Frontend:** React, TypeScript, Vite, MathJax
- **Backend:** Flask, Python
- **AI Model:** Google Gemini 1.5 Flash
- **LaTeX Rendering:** MathJax
- **Tools:** Axios, Flask-CORS

## ✨ Key Features
- **Real-time Voice Input** - Record mathematical expressions with your microphone
- **Instant LaTeX Generation** - Powered by Google's Gemini API
- **Live Preview** - See your LaTeX rendered in real-time
- **One-Click Copy** - Copy generated LaTeX code directly to your clipboard
- **History Panel** - Access your previously generated expressions
- **High Accuracy** - Optimized prompts for mathematical expression recognition
- **Cross-Platform** - Works on desktop and mobile browsers

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.9+)
- Google Gemini API key

### Frontend Setup
```bash
cd FrontEnd
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
# Create a virtual environment
python -m venv venv
# Activate the virtual environment (Windows)
venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Create .env file with your Gemini API key
echo GEMINI_API_KEY=your_api_key_here > .env
# Run the server
python run.py
```