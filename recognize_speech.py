import streamlit as st
import requests
import speech_recognition as sr
import re
import io
from gtts import gTTS
from deep_translator import GoogleTranslator
from pydub import AudioSegment
from pydub.playback import play

# Translator for Hinglish to Hindi conversion
translator = GoogleTranslator(source="auto", target="hi")

# Function to recognize speech from microphone
def recognize_speech():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        st.write("🎤 Listening... Speak now!")
        
        # Reduce background noise dynamically
        recognizer.adjust_for_ambient_noise(source, duration=1)  

        try:
            audio = recognizer.listen(source, timeout=None)  # Wait for speech
            text = recognizer.recognize_google(audio, language="en-IN")  # Recognize speech
            return text
        except sr.WaitTimeoutError:
            return "No speech detected. Please try again."
        except sr.UnknownValueError:
            return "Sorry, mujhe samajh nahi aaya."
        except sr.RequestError:
            return "Speech Recognition service filhaal uplabdh nahi hai."
        except Exception as e:
            return f"Error: {e}"

# Function to clean text (removes special characters)
def clean_text(text):
    text = re.sub(r'[“”":,\'!@#$%^&*()_+=\[\]{}<>?/|\\]', '', text)  # Remove unwanted symbols
    text = text.replace('\n', ' ')  # Replace newlines with space
    return text

# Function to Convert Hinglish Text to Hindi Speech
def speak(text):
    try:
        text = clean_text(text)  # Clean input text
        hindi_text = translator.translate(text)  # Translate to Hindi

        # Generate Hindi Speech using gTTS
        tts = gTTS(text=hindi_text, lang="hi")

        # Save to buffer instead of a file
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        # Play the audio directly
        audio = AudioSegment.from_file(audio_buffer, format="mp3")
        play(audio)

    except Exception as e:
        st.error(f"Error in speech synthesis: {e}")

# Streamlit UI
st.title("🗣️ AI Voice Assistant")

# Speech Input Button
if st.button("🎙️ Speak"):
    user_input = recognize_speech()
    st.write(f"**Recognized:** {user_input}")
else:
    user_input = st.text_input("Enter Message:")

# Send message to AI and get response
if st.button("Send"):
    response = requests.post("http://127.0.0.1:5000/chat", json={"message": user_input})

    if response.status_code == 200:
        ai_response = response.json().get("response", "No response from AI.")
    else:
        ai_response = f"Error: {response.json().get('error', 'Unknown error')}"

    st.write("🤖 **AI Response:**", ai_response)
    speak(ai_response)  # Speak AI Response in Hindi