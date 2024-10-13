import time
import pathlib
import edge_tts
import pygame
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

class EdgeTTS:
    """
    Text-to-speech provider using the Edge TTS API.
    """
    cache_dir = pathlib.Path("./audio_cache")

    def __init__(self, timeout: int = 20):
        """Initializes the Edge TTS client and clears the audio cache."""
        self.timeout = timeout
        pygame.mixer.init()

        # Clear the audio cache on startup
        self.clear_audio_cache()

        # Create separate channels for background music and TTS audio
        self.background_channel = pygame.mixer.Channel(0)
        self.tts_channel = pygame.mixer.Channel(1)
        self.last_audio_file = None  # To keep track of the last audio file

    def clear_audio_cache(self):
        """Clears all audio files from the audio cache."""
        if self.cache_dir.exists():
            for audio_file in self.cache_dir.glob("*.mp3"):
                try:
                    audio_file.unlink()  # Delete the file
                except Exception as e:
                    print(f"Error deleting {audio_file}: {e}")
        else:
            self.cache_dir.mkdir(parents=True, exist_ok=True)  # Create cache directory if not exists

    def tts(self, text: str, voice: str = "hi-IN-MadhurNeural") -> str:
        """
        Converts text to speech using the Edge TTS API and saves it to a file.
        Deletes the previous audio file if it exists.
        """
        # Create the filename with a timestamp
        filename = self.cache_dir / f"{int(time.time())}.mp3"

        try:
            # Create the audio_cache directory if it doesn't exist
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # If there is a previous audio file, delete it
            if self.last_audio_file and self.last_audio_file.exists():
                self.last_audio_file.unlink()

            # Generate new speech and save it
            asyncio.run(self._save_audio(text, voice, filename))

            # Update the last_audio_file to the current one
            self.last_audio_file = filename

            return str(filename.resolve())

        except Exception as e:
            raise RuntimeError(f"Failed to perform the operation: {e}")

    async def _save_audio(self, text: str, voice: str, filename: pathlib.Path):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)

    def play_audio(self, filename: str):
        """
        Plays an audio file using pygame on the TTS channel, ensuring no overlap with background music.
        """
        try:
            self.tts_channel.play(pygame.mixer.Sound(filename))
            while self.tts_channel.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            raise RuntimeError(f"Error playing audio: {e}")

    def play_background_music(self, music_path: str, volume: float = 0.1):
        """
        Plays background music continuously in a loop using pygame, with a specified volume.
        The volume value should be between 0.0 and 1.0.
        """
        try:
            if not self.background_channel.get_busy():  # Check if background music is already playing
                sound = pygame.mixer.Sound(music_path)
                sound.set_volume(volume)  # Set the volume (e.g., 0.1 for low volume)
                self.background_channel.play(sound, loops=-1)  # Loop indefinitely
        except Exception as e:
            raise RuntimeError(f"Error playing background music: {e}")


# Initialize client with API key
api_key = st.text_input("Enter your Groq API key to proceed:")
client = Groq(api_key=api_key) if api_key else None

# Initialize the TTS engine
tts_engine = EdgeTTS()

# Path to the background music file
background_music_path = "DRUMS.mp3"

# Function to speak the assistant's responses
def speak_response(text: str, voice: str = "hi-IN-MadhurNeural"):
    # Generate and play the response audio
    audio_file = tts_engine.tts(text, voice)
    tts_engine.play_audio(audio_file)

# Chat history to maintain conversation
chat_history = []

# Function to get user input and provide responses
def main():
    st.title("Vaidyaraj - Ancient Indian Health Wisdom")
    st.markdown("""Discover the wisdom of Ayurveda, Homeopathy, English medicines...""")
    st.markdown("               Made with 💖 in India")

    # Play background music with a lower volume (e.g., 20% of the full volume)
    if background_music_path:
        tts_engine.play_background_music(background_music_path, volume=0.1)  # Adjust volume as needed


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
                conversation_history = [{"role": "system", "content": "You are Vaidyaraj, an ancient Indian doctor..."}]
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

            # Display response and play TTS
            st.markdown(f'<div class="vaidyaraj-message">{response}</div>', unsafe_allow_html=True)
            speak_response(response)

if __name__ == "__main__":
    main()
