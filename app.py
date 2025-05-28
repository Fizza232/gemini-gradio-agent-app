# 1. Imports and environment variable loading
import gradio as gr
import os
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import uuid

load_dotenv()

# --- Global Variables for Chat Session Management ---
chat_sessions = {}
current_session_id = None

# 2. Gemini model initialization
try:
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file.")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key)
except ValueError as e:
    print(f"Error initializing Gemini model: {e}")
    print("Please ensure you have a valid GOOGLE_API_KEY in your .env file.")
    llm = None

# --- Helper Functions for Session Management ---

def create_new_chat_session():
    """Generates a new session ID and clears the chat."""
    global current_session_id, chat_sessions
    new_id = str(uuid.uuid4())
    chat_sessions[new_id] = []
    current_session_id = new_id
    print(f"Created new chat session: {new_id}")
    return (
        "",  # Clear the message input
        [],  # Clear the chatbot display
        gr.update(value="", placeholder="Type your message here..."), # Clear input placeholder
        update_chat_list() # Update the list of chat sessions in the sidebar
    )

def update_chat_list():
    """Generates a Gradio Radio component with chat session titles for the sidebar."""
    choices = []
    for session_id, history in chat_sessions.items():
        if history and history[0]["content"]:
            title = history[0]["content"][:30] + "..." if len(history[0]["content"]) > 30 else history[0]["content"]
        else:
            if session_id == current_session_id:
                 title = f"New Chat (Current)"
            else:
                 title = f"New Chat ({session_id[:8]})"
        choices.append((title, session_id))

    choices.sort(key=lambda x: x[1], reverse=True)

    selected_value = current_session_id if current_session_id in [c[1] for c in choices] else (choices[0][1] if choices else None)

    return gr.Radio(choices=choices, value=selected_value, label="Previous Chats", container=False)

def load_chat_session(session_id):
    """Loads a selected chat session into the chatbot display."""
    global current_session_id, chat_sessions

    if session_id and session_id in chat_sessions:
        current_session_id = session_id
        loaded_history = chat_sessions[session_id]
        print(f"Loaded chat session: {session_id}")
        return (
            "", # Clear message input
            loaded_history, # Set the chatbot history to the loaded session
            update_chat_list() # Re-render chat list to show active selection
        )
    return "", [], update_chat_list()

def clear_current_chat_display():
    """Clears the messages in the current chat display and empties its history in chat_sessions."""
    global current_session_id, chat_sessions
    if current_session_id and current_session_id in chat_sessions:
        chat_sessions[current_session_id] = [] # Empty the history for the current session
        print(f"Cleared chat display for session: {current_session_id}")
    return (
        "", # Clear message input
        [], # Clear the chatbot display
        gr.update(placeholder="Type your message here..."), # Reset input placeholder
        update_chat_list() # Update the list (title might change to "New Chat (Current)")
    )


# --- Chat Interface Logic ---

def chat_interface(user_message, history):
    """
    This function will be called when the user sends a message in the Gradio chat.
    It manages the conversation history and interacts with the Gemini agent (non-streaming).
    """
    global llm, chat_sessions, current_session_id

    if current_session_id is None:
        new_id = str(uuid.uuid4())
        chat_sessions[new_id] = []
        current_session_id = new_id
        print(f"DEBUG: Auto-created new session for first message: {current_session_id}")

    messages_for_gemini: list[BaseMessage] = []
    if history:
        for msg in history:
            if msg["role"] == "user":
                messages_for_gemini.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages_for_gemini.append(AIMessage(content=msg["content"]))
    messages_for_gemini.append(HumanMessage(content=user_message))

    gradio_history = history + [{"role": "user", "content": user_message}]
    chat_sessions[current_session_id] = gradio_history.copy()

    if llm is None:
        bot_message_content = "Gemini model is not initialized. Please check your GOOGLE_API_KEY in the .env file."
        gradio_history.append({"role": "assistant", "content": bot_message_content})
        chat_sessions[current_session_id] = gradio_history.copy()
        return "", gradio_history, update_chat_list()

    try:
        ai_response = llm.invoke(messages_for_gemini)
        bot_message_content = ai_response.content

        gradio_history.append({"role": "assistant", "content": bot_message_content})
        chat_sessions[current_session_id] = gradio_history.copy()

        return "", gradio_history, update_chat_list()

    except Exception as e:
        error_message = f"An error occurred during Gemini interaction: {e}. Please try again or check your API key/network connection."
        print(error_message)
        gradio_history.append({"role": "assistant", "content": error_message})
        chat_sessions[current_session_id] = gradio_history.copy()
        return "", gradio_history, update_chat_list()


# --- Custom CSS for Styling ---
custom_css = """
/* Styling for the Send button */
#send_button {
    min-width: 0 !important;
    width: 40px !important;
    height: 40px !important;
    padding: 0 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    border-radius: 50% !important;
    margin-left: 5px; /* Space to the left of the button */
}

#send_button .gradio-button-icon {
    margin: 0 !important;
    font-size: 1.2em !important;
}
#send_button span.lg {
    display: none !important; /* Hide the text label for the send button */
}

/* Styling for New Chat Button */
#new_chat_button {
    min-width: unset !important;
    width: 100%;
    height: 40px;
    margin-bottom: 10px;
}

/* General Chatbot and Radio list styling */
#chatbot {
    overflow-y: scroll;
    height: 400px;
}
.gradio-radio-input {
    margin-top: 5px;
}
.gradio-radio label {
    display: flex;
    align-items: center;
    padding: 8px;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.2s ease-in-out;
}
.gradio-radio label:hover {
    background-color: var(--color-primary-100);
}
.gradio-radio input[type="radio"]:checked + span {
    color: var(--color-text-primary);
    font-weight: bold;
    background-color: var(--color-primary-200);
}
"""

# --- Gradio UI Definition ---

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("# Gemini Gradio Agent Chat")
    gr.Markdown("Type your message below and chat with the Gemini-powered agent.")

    with gr.Row():
        with gr.Column(scale=1): # Left column for chat list
            new_chat_button = gr.Button("➕ New Chat", elem_id="new_chat_button")
            # Removed the delete_chat_button from here
            chat_list_radio = gr.Radio(
                choices=[],
                value=None,
                label="Previous Chats",
                interactive=True,
                container=False,
                elem_id="chat_list_radio"
            )


        with gr.Column(scale=4): # Right column for main chat interface
            chatbot = gr.Chatbot(height=400, type="messages", elem_id="chatbot")
            with gr.Row(): # Wrap message input and buttons in a Row for layout
                message_input = gr.Textbox(
                    label="Your Message",
                    placeholder="Type your message here...",
                    lines=2,
                    scale=4
                )
                # Send Button (Arrow Icon)
                send_button = gr.Button(
                    value="Send", # Text label (hidden by CSS)
                    icon="arrow-right",
                    scale=0,
                    elem_id="send_button"
                )
                # Clear Current Chat Button (Text Label, no icon)
                clear_button = gr.Button(
                    value="Clear Current Chat", # Text label is visible
                    scale=0, # Keep it compact
                    min_width=100, # Give it enough width for text
                    elem_id="clear_button" # Add elem_id for potential specific styling
                )

    # --- Event Handling ---

    demo.load(
        create_new_chat_session,
        inputs=None,
        outputs=[message_input, chatbot, message_input, chat_list_radio]
    )

    new_chat_button.click(
        create_new_chat_session,
        inputs=None,
        outputs=[message_input, chatbot, message_input, chat_list_radio]
    )

    chat_list_radio.change(
        load_chat_session,
        inputs=[chat_list_radio],
        outputs=[message_input, chatbot, chat_list_radio]
    )

    message_input.submit(
        chat_interface,
        inputs=[message_input, chatbot],
        outputs=[message_input, chatbot, chat_list_radio],
        queue=False
    )

    send_button.click(
        chat_interface,
        inputs=[message_input, chatbot],
        outputs=[message_input, chatbot, chat_list_radio],
        queue=False
    )

    # Bind the new clear_button to the clear_current_chat_display function
    clear_button.click(
        clear_current_chat_display,
        inputs=None,
        outputs=[message_input, chatbot, message_input, chat_list_radio], # Ensure all relevant components are updated
        queue=False
    )

    # The delete_chat_button and its binding are completely removed for this simplified version.


if __name__ == "__main__":
    if llm is None:
        print("\n*** WARNING: Gemini model not initialized. Chat functionality might be limited. ***\n")
    demo.launch(debug=True)