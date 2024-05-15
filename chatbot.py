from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from streamlit_feedback import streamlit_feedback
import os
import google.generativeai as genai
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

model = genai.GenerativeModel("gemini-pro")
chat=model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

def clear_history():
    if "history" in st.session_state:
        st.session_state.history = []
        st.session_state.messages = []

def _submit_feedback(user_response, emoji=None):
    st.toast(f"Feedback submitted: {user_response}", icon=emoji)
    return user_response.update({"some metadata": 123})

def run_chatbot():
    with st.sidebar.title("Sidebar"):
        if st.button("Clear History"):
            clear_history()
    st.title("💬 Chatbot")

    if "messages" not in st.session_state:
        with st.spinner("Loading, Please wait... !!!"):
            st.session_state['chat_history'] = []
        st.session_state["messages"] = [{"role": "assistant", "content": "Ask me something?"}]
    messages = st.session_state.messages
    feedback_kwargs = {
        "feedback_type": "thumbs",
        "optional_text_label": "Please provide extra information",
        "on_submit": _submit_feedback,
    }

    for n, msg in enumerate(messages):
        st.chat_message(msg["role"]).write(msg["content"])

        if msg["role"] == "assistant" and n > 1:
            feedback_key = f"feedback_{int(n/2)}"

            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = None

            streamlit_feedback(
                **feedback_kwargs,
                key=feedback_key,
            )

    if "history" not in st.session_state:
        st.session_state.history = []
    input = st.chat_input()
    if input:
        st.chat_message("user").write(input)
        response = get_gemini_response(input)
        st.session_state.history.append(("user", input)) 
        if len(st.session_state.history) >= 20:
            st.session_state.history = st.session_state.history[1:]
        temp = ""
        for chunk in response:
            temp += chunk.text
        st.chat_message("assistant").write(temp)
        st.session_state.history.append(("assistant", temp))
        st.session_state.messages.append({"role": "user", "content": input})
        st.session_state.messages.append({"role": "assistant", "content": temp})
        feedback_key = f"feedback_{len(st.session_state.messages) - 1}"
        streamlit_feedback(
            **feedback_kwargs,
            key=feedback_key,
        )   

if __name__ == "__main__":
    run_chatbot()