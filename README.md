## 🎙️ SpeakTeX: From Voice to LaTeX

## 🚀 Project Overview

- SpeakTeX is a web application that transforms spoken mathematical expressions into LaTeX code and renders them in real time. Hands-free, just by speaking naturally!

## 🎯 Our Project Goal: Audio → LaTeX

- A web application: Users speak mathematical expressions into a microphone. The application converts the speech to LaTeX code in real time and renders the mathematical expression.

## ⚙️ How It Works

1. User speaks mathematical expression into microphone
2. Audio uploaded to AWS S3 for storage
3. AWS Lambda processes audio and invokes Gemini API
4. Gemini API converts speech to LaTeX code
5. Frontend renders LaTeX using MathJax in real-time
6. User can copy LaTeX code or save to history

## ✨ Key Features

- **Real-time Voice Input** - Record mathematical expressions using your microphone
- **Instant LaTeX Generation** - Powered by Gemini AI for accurate speech-to-LaTeX conversion
- **Live Preview** - Real-time mathematical rendering using MathJax
- **One-Click Copy** - Copy generated LaTeX code directly to your clipboard
- **High Accuracy** - Using Gemini-2.5 Flash to understand mathematical terminology
- **Cross-Platform** - Works on any modern web browser with microphone support

## 👥 Team Roles

| Team Member | Contribution                                                                                        |
| ----------- | --------------------------------------------------------------------------------------------------- |
| Yubin Li    | Frontend Login System, Audio Recording & Processing, UI/UX Optimization, Backend History Management |
| Zongze Wu   | AWS Architecture, Lambda Functions, S3/DynamoDB Integration, Gemini API Integration                 |

## 🧩 Tech Stack

- **Frontend:** React + Vite
- **Backend:** AWS Lambda + Flask API + AWS S3 + DynamoDB
- **AI Model:** Google Gemini 1.5 Flash API
- **LaTeX Rendering:** MathJax
- **Tools:** AWS Transcribe, Axios, MediaRecorder API
