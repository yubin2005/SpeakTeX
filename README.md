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

- **Real-time Voice Input** -
- **Instant LaTeX Generation** -
- **Live Preview** -
- **One-Click Copy** - Copy generated LaTeX code directly to your clipboard
- **High Accuracy** -
- **Cross-Platform** -

## 👥 Team Roles

| Team Member | Contribution |
| ----------- | ------------ |
| Yubin Li    |              |
| Zongze Wu   |              |

## 🧩 Tech Stack

- **Frontend:** React
- **Backend:**
- **AI Model:**
- **LaTeX Rendering:**
- **Tools:**

## ⏱️ Development Timeline

AWS 应用:
Amazon Transcribe(直接语音转文字)

### 第 3–8 小时：核心功能开发

- 建网页界面：
  - 左边是录音按钮
  - 中间显示转录文字
  - 右边显示 LaTeX 源代码与渲染结果（用 MathJax）
- 用 JavaScript 调用后端 API（语音上传 -> 获取 LaTeX 文本）
- 前端页面：recording，transcript，latex code，latex code 所对应的公式，然后有 copy button

### 第 9–14 小时：连接前后端

- 前端录音功能（MediaRecorder API）录音 → 上传音频到后端
- 后端 Flask 接口：接收音频 → Gemini API 转文字 → Gemini API 转 LaTeX → 返回 LaTeX 字符串
- 在前端实时显示结果

### 第 15–18 小时：改进 & 美化

- 美化界面（浅色背景、流畅动画、公式渲染动画）
- 添加错误提示或语音历史记录

### 第 19-22 小时：历史记录 + 登录/注册页面

- 保存每个用户过去的语音转 LaTeX 结果
- 在前端界面中添加"历史记录"区域（例如右侧栏或独立页面）
- 用户可以点击历史条目重新渲染或复制 LaTeX 代码

### 最后阶段

- 插件，部署网站
- 星期天早上 7:30：打磨 demo & 准备展示
- 星期天早上 9:30：提交 & 展示准备
