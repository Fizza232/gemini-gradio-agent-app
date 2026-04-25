# Gemini Gradio Chat Agent

**Type:** Generative AI Project | **Tool:** Python + Gradio + Google Gemini

A multi-turn conversational AI chat agent powered by Google Gemini and built with Gradio, featuring persistent multi-session chat history and a clean interactive UI.

This project demonstrates practical implementation of LLM integration, session state management, and real-world AI application design.

## Objective

To build a fully functional AI chat interface that supports multiple independent chat sessions, maintains conversation history across turns, and delivers a smooth user experience through a clean Gradio-based UI.

## App Preview

> Add a screenshot here after launching the app

---

## Features

### Chat Interface
- Multi-turn conversation with full message history
- Real-time responses powered by Google Gemini (`gemini-1.5-flash`)
- Send messages via button click or Enter key

### Session Management
- Create multiple independent chat sessions
- Switch between previous chats via sidebar
- Clear current chat without affecting other sessions
- Auto-generates session titles from first message

### UI
- Two-column layout: sidebar for chat history, main panel for conversation
- Custom CSS styling for send button, chat list, and layout
- Responsive and clean Gradio Blocks interface

---

## Tools & Technologies

- **Python** — Core application logic
- **Gradio** — Web UI framework
- **LangChain** (`langchain-core`, `langchain-google-genai`) — LLM integration and message formatting
- **Google Gemini API** (`gemini-1.5-flash`) — AI language model
- **python-dotenv** — Environment variable management
- **UUID** — Unique session ID generation

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Fizza232/gemini-gradio-chat-agent.git
cd gemini-gradio-chat-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```
Get your free API key at https://aistudio.google.com

---

### 4. Run the app
```bash
python app.py
```
The app will launch in your browser at:
```
http://localhost:7860
```

---

## Project Structure

```
gemini-gradio-chat-agent/
├── app.py              # Main application (UI + logic + Gemini integration)
├── .env                # API keys (not committed)
├── .env.example        # Template for environment variables
├── requirements.txt    # Python dependencies
└── .gitignore          # Excludes sensitive/system files
```

---

## Key Implementation Details

- Session management is handled using a global `chat_sessions` dictionary keyed by UUID, ensuring each chat maintains independent history.
- LangChain converts Gradio chat history into `HumanMessage` and `AIMessage` formats before sending to Gemini.
- Robust error handling ensures smooth UX for API failures, missing keys, or runtime exceptions.

---

## Author

**Fizza Shabbir** — [LinkedIn](https://linkedin.com/in/fizzashabbir) | [GitHub](https://github.com/Fizza232)
