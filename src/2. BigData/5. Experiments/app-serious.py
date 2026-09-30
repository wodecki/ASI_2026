import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file (local development)
load_dotenv()

# Get API key from environment (NEVER hardcode!)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("⚠️ OPENAI_API_KEY not found! Please set it in .env file or environment variables.")
    st.stop()

st.title("🎓 Academic Assistant")
st.caption("Professional academic support in scholarly style")

client = OpenAI(api_key=OPENAI_API_KEY)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": "You are a professional academic assistant. Answer questions in a polite, scholarly style with proper citations and formal language."
    }]

# Display chat history (skip system messages)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
