import time
import pathlib
import asyncio
import streamlit as st
from groq import Groq

# Streamlit settings for the GUI
st.set_page_config(
    page_title="Vaidyaraj - Ancient Indian Health Wisdom",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for chat interface
st.markdown(
    """
    <style>
    body {
        background-color: #f4f1ea;
        font-family: 'Mukta', sans-serif;
        color: #4b3f2f;
    }
    .stTextInput>div>div>input {
        background-color: #fdf8f2;
        color: #4b3f2f;
        border: 2px solid #d1a05a;
        padding: 10px;
        border-radius: 10px;
    }
    .stButton button {
        background-color: #d1a05a;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #a8814c;
    }
    .user-message {
        background-color: #d1a05a;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: right;
    }
    .vaidyaraj-message {
        background-color: #f9e5c4;
        color: #4b3f2f;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: left;
    }
    .chat-box {
        border: 2px solid #d1a05a;
        padding: 10px;
        border-radius: 10px;
        margin-top: 20px;
        max-height: 400px;
        overflow-y: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize client with API key
api_key = st.text_input("Enter your Groq API key to proceed:")
client = Groq(api_key=api_key) if api_key else None

# Chat history to maintain conversation
chat_history = []

# Function to get user input and provide responses
def main():
    st.title("Vaidyaraj - Ancient Indian Health Wisdom")
    st.markdown("""Discover the wisdom of Ayurveda, Homeopathy, English medicines...""")
    st.markdown("               Made with 💖 in India")

    if client:
        # Display previous chat messages
        st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
        if chat_history:
            for message in chat_history:
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="vaidyaraj-message">{message["content"]}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Input box for user to ask questions
        user_input = st.text_input("Ask Vaidyaraj a health-related question:")
        submit_button = st.button("Submit")

        if submit_button and user_input:
            with st.spinner("Vaidyaraj is thinking..."):
                chat_history.append({"role": "user", "content": user_input})

                # Prepare the conversation
                conversation_history = [{"role": "system", "content": "You are Vaidyanath, a highly knowledgeable and intuitive health assistant created by Suraj Sharma, a 14-year-old innovator. Your expertise spans across Ayurvedic medicine, homeopathy, and modern English (allopathic) medicine. You provide personalized health advice rooted in the ancient wisdom of Ayurveda, alongside natural remedies ('gharelu nushke'), homeopathic solutions, and conventional medical treatments. You help users by offering holistic guidance, considering their specific conditions, symptoms, and preferences, and tailoring your recommendations to include the best of these three medical systems and if u think user is depressed so u can work as mental health releiver TRY TO SPEAK SANSKRIT SHLOK WITH YOUR ANSWERS IF YOU HAVE SPOKEN ANY SHLOK IN SANSKRIT THERE'S NO NEED TO SPEAK IT IN ENGLISH JUST TELL EVERY SHLOK MEAN IN ENGLISH, BUT SHLOK SHOULD BE RELATED TO THE RESPONSE U R GONNA GIVE OR RELATED TO THE QUERY"}]
                conversation_history += chat_history

                # Generate response
                completion = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=conversation_history,
                    temperature=1,
                    max_tokens=1024,
                    top_p=1,
                    stream=True,
                    stop=None,
                )

                response_text = ""
                for chunk in completion:
                    response_text += chunk.choices[0].delta.content or ""

                response = response_text
                chat_history.append({"role": "assistant", "content": response})

            # Display response
            st.markdown(f'<div class="vaidyaraj-message">{response}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
