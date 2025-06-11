import streamlit as st
import requests
import json

# ========== CONFIG ==========
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-r1-0528:free"

# ========== PAGE SETUP ==========
st.set_page_config(page_title="Chat App", page_icon="💬")
st.title("💬 DeepSeek Chat with Real-time Streaming")

# ========== SESSION STATE ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Hello! 👋 How can I assist you today? Whether you have a question, need help with something, or just want to chat, I'm here for you! 😊"}
    ]


# ========== STREAMING FUNCTION ==========
def stream_response():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": st.session_state.messages,
        "stream": True
    }

    response = requests.post(API_URL, headers=headers, json=payload, stream=True)

    assistant_reply = ""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8").strip()

                if not decoded_line.startswith("data: "):
                    continue

                json_data = decoded_line[6:]

                if json_data.strip() == "[DONE]":
                    break

                try:
                    data = json.loads(json_data)
                    content = data["choices"][0]["delta"].get("content", "")
                    assistant_reply += content
                    message_placeholder.markdown(assistant_reply + "▌")
                except json.JSONDecodeError:
                    continue

        message_placeholder.markdown(assistant_reply)
    return assistant_reply


# ========== DISPLAY OLD MESSAGES ==========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ========== USER INPUT ==========
user_input = st.chat_input("Type your message here...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Stream assistant reply
    assistant_reply = stream_response()
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
