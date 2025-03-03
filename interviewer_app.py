import streamlit as st
import threading
import requests
from flask import Flask, request, jsonify
from config import llm  # ✅ Import your LLM setup
import streamlit as st
import requests
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import time
import os

# ============== FLASK SERVER ============== #
flask_app = Flask(__name__)

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak_text(text):
    """Generate and play TTS audio without permission issues."""
    temp_audio_path = "tts_audio.mp3"  # ✅ Use a normal filename instead of tempfile
    tts = gTTS(text=text, lang="en")
    tts.save(temp_audio_path)
    
    audio = AudioSegment.from_file(temp_audio_path, format="mp3")
    play(audio)

    # ✅ Delete the file manually after playback (avoiding locked file issues)
    os.remove(temp_audio_path)

# Interview session storage
interview_sessions = {}

def generate_question(job_role, previous_answers):
    """Generate the next question dynamically in Hinglish based on previous answers."""
    context = "\n".join(previous_answers) if previous_answers else "No previous answers."
    prompt = f"""
    Tum ek AI interviewer ho jo {job_role} ke liye interview le raha hai.
    Ye candidate ke pehle ke answers hain:
    {context}
    Tumhe iske jawab ke basis par ek logical agla sawal puchna hai jo role se related ho.
    Sawal **Hinglish** (mix of Hindi and English in Latin script) me likhna hai.
    Bas ek sawal likho bina kisi explanation ke.
    """
    try:
        response = llm.invoke([{"role": "user", "content": prompt}])
        return response.strip() if isinstance(response, str) else response.get("content", "Error: No question generated").strip()
    except Exception as e:
        return f"Error generating question: {str(e)}"

def evaluate_response(job_role, answer):
    """Evaluate the candidate's response briefly, focusing on weaknesses."""
    prompt = f"""
    Tum ek AI interviewer ho jo {job_role} ke liye interview le raha hai.
    Candidate ne ye jawab diya:
    "{answer}"
    Evaluation sirf Hinglish me likhna hai (Hindi + English in Latin script).
    Tumhe candidate ke jawab ka short aur precise evaluation dena hai.
    Ye batao ki jawab kahan weak tha aur kya missing tha.
    Aur agar kuch acha jawab hain toh unhe bhi mention karo.
    two line me crisp response do. Extra explanation mat do.
    """
    try:
        response = llm.invoke([
            {"role": "system", "content": "You are a strict but fair AI interviewer."},
            {"role": "user", "content": prompt}
        ])
        if isinstance(response, str):  
            return response.strip()
        return response.get("content", "Error: No evaluation generated").strip()
    except Exception as e:
        return f"Error evaluating response: {str(e)}"

@flask_app.route('/start', methods=['POST'])
def start_interview():
    """Start a new interview session."""
    data = request.json
    job_role = data.get("job_role", "").strip()

    if not job_role:
        return jsonify({"error": "Job role is required"}), 400

    session_id = len(interview_sessions) + 1
    interview_sessions[session_id] = {"job_role": job_role, "questions": [], "answers": []}

    question = generate_question(job_role, [])
    interview_sessions[session_id]["questions"].append(question)

    return jsonify({"session_id": session_id, "question": question})

@flask_app.route('/respond', methods=['POST'])
def respond():
    """Process user answer and generate next question."""
    data = request.json
    session_id = data.get("session_id")
    answer = data.get("answer", "").strip()

    if not session_id or session_id not in interview_sessions:
        return jsonify({"error": "Invalid session"}), 400

    job_role = interview_sessions[session_id]["job_role"]
    interview_sessions[session_id]["answers"].append(answer)

    evaluation = evaluate_response(job_role, answer)

    if len(interview_sessions[session_id]["questions"]) < 8:
        next_question = generate_question(job_role, interview_sessions[session_id]["answers"])
        interview_sessions[session_id]["questions"].append(next_question)
    else:
        next_question = "Interview complete! ✅"

    return jsonify({"evaluation": evaluation, "next_question": next_question})

# ============== 🚀 RUN FLASK IN BACKGROUND THREAD ============== #
def run_flask():
    flask_app.run(port=5000, debug=False, use_reloader=False)

threading.Thread(target=run_flask, daemon=True).start()

# ============== 🌟 STREAMLIT UI ============== #
st.title("🎙 AI-Powered Interviewer")

# Predefined job roles
job_roles = [
    "Software Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Researcher",
    "Cybersecurity Analyst",
    "DevOps Engineer"
]

# Step 1: Ask for the candidate's name
candidate_name = st.text_input("Enter Your Name:", key="candidate_name")

# Step 2: Select Job Role from Dropdown
selected_role = st.selectbox("Select Job Role:", job_roles, key="selected_role")

# ================== 🌟 Interview Start ==================
if st.button("Start Interview", key="start_interview"):
    if candidate_name and selected_role:
        response = requests.post("http://127.0.0.1:5000/start", json={"job_role": selected_role}).json()
        
        st.session_state["session_id"] = response.get("session_id")
        first_question = response.get("question", "Error: No question received")
        
        st.session_state["questions"] = [first_question]
        st.session_state["answers"] = [""]  
        st.session_state["interview_started"] = True
        st.session_state["current_question"] = first_question

        # ✅ Play first question as voice
        temp_audio_path = "temp_audio.mp3"
        tts = gTTS(text=first_question, lang="en")
        tts.save(temp_audio_path)

        # ✅ Load and play audio (fixes Windows file lock issue)
        audio = AudioSegment.from_file(temp_audio_path, format="mp3")
        play(audio)

        # ✅ Cleanup temporary file
        os.remove(temp_audio_path)

    else:
        st.warning("Please enter your name and select a role to proceed.")

# ================== 🌟 Interview UI ==================
if st.session_state.get("interview_started"):
    # ✅ Show previous questions and answers
    for i, (question, answer) in enumerate(zip(st.session_state["questions"], st.session_state["answers"])):
        st.write(f"**Q{i+1}:** {question}")
        st.write(f"🗣 **Your Answer:** {answer}")

    # ✅ Show the current question
    st.write(f"**Q{len(st.session_state['questions'])}:** {st.session_state['current_question']}")

    # 🎤 ✅ Voice Input: Capture Speech
    def record_voice():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("🎤 Listening... Speak now!")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "❌ Could not understand the audio, please try again."
        except sr.RequestError:
            return "⚠️ Google Speech API not responding."

    # 🎤 ✅ Speak Answer Button (Voice Input Only)
    if st.button("🎤 Speak Answer"):
        user_answer = record_voice()

        if "❌" in user_answer or "⚠️" in user_answer:
            st.warning(user_answer)
        else:
            response = requests.post("http://127.0.0.1:5000/respond", json={
                "session_id": st.session_state["session_id"],
                "answer": user_answer
            }).json()

            evaluation = response.get("evaluation", "Error: No evaluation received")
            next_question = response.get("next_question", "Interview complete! ✅")

            # ✅ Store question and answer
            st.session_state["answers"].append(user_answer)
            st.write(f"✅ **Evaluation:** {evaluation}")

            if next_question != "Interview complete! ✅":
                st.session_state["questions"].append(next_question)
                st.session_state["current_question"] = next_question

                # ✅ Speak the next question
                temp_audio_path = "temp_audio.mp3"
                tts = gTTS(text=next_question, lang="en")
                tts.save(temp_audio_path)

                time.sleep(1)  # Ensure file is saved

                audio = AudioSegment.from_file(temp_audio_path, format="mp3")
                play(audio)

                os.remove(temp_audio_path)
            else:
                st.write("🎉 **Interview Completed!**")