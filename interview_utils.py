import streamlit as st
import threading
import requests
import json
from flask import Flask, request, jsonify
from config import llm  # ✅ Import your LLM setup
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import time
import os

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
    """Evaluate the candidate's response (stored in JSON but not displayed)."""
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
        response = llm.invoke([{"role": "user", "content": prompt}])
        return response.strip() if isinstance(response, str) else response.get("content", "Error: No evaluation generated").strip()
    except Exception as e:
        return f"Error evaluating response: {str(e)}"

def speak_text(text):
    """Generate and play TTS audio."""
    temp_audio_path = "tts_audio.mp3"
    tts = gTTS(text=text, lang="en")
    tts.save(temp_audio_path)

    audio = AudioSegment.from_file(temp_audio_path, format="mp3")
    play(audio)

    os.remove(temp_audio_path)

def save_interview_data():
    """Save session questions and answers to a JSON file."""
    data = {
        "name": st.session_state["candidate_name"],
        "role": st.session_state["selected_role"],
        "questions": st.session_state["questions"],
        "answers": st.session_state["answers"],
        "evaluations": st.session_state["evaluations"]  # ✅ Hidden but stored
    }
    with open("interview_data.json", "w") as f:
        json.dump(data, f, indent=4)

def interview_screening():
    # ============== 🌟 STREAMLIT UI ============== #
    st.title("🎙 AI-Powered Interviewer")

    job_roles = [
        "Software Engineer", "Data Scientist", "Machine Learning Engineer",
        "AI Researcher", "Cybersecurity Analyst", "DevOps Engineer"
    ]

    candidate_name = st.text_input("Enter Your Name:", key="candidate_name")
    selected_role = st.selectbox("Select Job Role:", job_roles, key="selected_role")

    if st.button("Start Interview", key="start_interview"):
        if candidate_name and selected_role:
            st.session_state["session_id"] = f"{candidate_name}-{selected_role}"
            st.session_state["questions"] = []
            st.session_state["answers"] = []
            st.session_state["evaluations"] = []
            st.session_state["interview_started"] = True

            # ✅ Start with Greeting + Introduction Request
            greeting = f"Namustey {candidate_name}! Please give a short introduction about yourself."
            st.session_state["questions"].append(greeting)
            st.session_state["current_question"] = greeting

            speak_text(greeting)

        else:
            st.warning("Please enter your name and select a role to proceed.")

    if st.session_state.get("interview_started"):
        # ✅ Show conversation history
        for i, (question, answer) in enumerate(zip(st.session_state["questions"], st.session_state["answers"])):
            st.write(f"**Q{i+1}:** {question}")
            st.write(f"🗣 **Your Answer:** {answer}")

        # ✅ Show the current question
        st.write(f"**Q{len(st.session_state['questions'])}:** {st.session_state['current_question']}")

        def record_voice():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.write("🎤 Listening... Speak now!")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            try:
                return recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                return "❌ Could not understand the audio, please try again."
            except sr.RequestError:
                return "⚠️ Google Speech API not responding."

        if st.button("🎤 Speak Answer"):
            user_answer = record_voice()

            if "❌" in user_answer or "⚠️" in user_answer:
                st.warning(user_answer)
            else:
                # ✅ Store response
                st.session_state["answers"].append(user_answer)

                if len(st.session_state["questions"]) == 1:
                    # ✅ After introduction, ask job-related questions
                    next_question = generate_question(st.session_state["selected_role"], [user_answer])
                else:
                    # ✅ Continue with logical next question
                    next_question = generate_question(st.session_state["selected_role"], st.session_state["answers"])

                # ✅ Store evaluation but don't show it
                evaluation = evaluate_response(st.session_state["selected_role"], user_answer)
                st.session_state["evaluations"].append(evaluation)

                if next_question:
                    st.session_state["questions"].append(next_question)
                    st.session_state["current_question"] = next_question
                    speak_text(next_question)
                else:
                    st.write("🎉 **Interview Completed!**")
                    save_interview_data()

if __name__ == "__main__":
    interview_screening()