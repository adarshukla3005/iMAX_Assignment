import streamlit as st
import threading
import requests
from flask import Flask, request, jsonify
from config import llm  # ✅ Import your LLM setup
import speech_recognition as sr
import pyttsx3
import time

def interview_screening():
    """Runs the AI-powered interview screening inside Streamlit."""
    
    # ============== 🔥 FLASK SERVER ============== #
    flask_app = Flask(__name__)

    # Text-to-speech engine
    engine = pyttsx3.init()

    # Session storage
    interview_sessions = {}

    def generate_question(job_role, previous_answers):
        """Generate next question dynamically in Hinglish based on previous answers."""
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
        """Evaluate the candidate's response briefly in Hinglish."""
        prompt = f"""
        Tum ek AI interviewer ho jo {job_role} ke liye interview le raha hai.
        Candidate ne ye jawab diya:
        "{answer}"
        Evaluation sirf Hinglish me likhna hai (Hindi + English in Latin script).
        Tumhe candidate ke jawab ka short aur precise evaluation dena hai.
        """
        try:
            response = llm.invoke([
                {"role": "system", "content": "You are a strict but fair AI interviewer."},
                {"role": "user", "content": prompt}
            ])
            return response.strip() if isinstance(response, str) else response.get("content", "Error: No evaluation generated").strip()
        except Exception as e:
            return f"Error evaluating response: {str(e)}"

    @flask_app.route('/start', methods=['POST'])
    def start_interview():
        """Start a new interview session."""
        try:
            data = request.json
            job_role = data.get("job_role", "").strip()

            if not job_role:
                return jsonify({"error": "Job role is required"}), 400  

            session_id = len(interview_sessions) + 1
            interview_sessions[session_id] = {"job_role": job_role, "questions": [], "answers": []}

            question = generate_question(job_role, [])
            interview_sessions[session_id]["questions"].append(question)

            return jsonify({"session_id": session_id, "question": question})

        except Exception as e:
            print(f"❌ Error in /start: {e}")  
            return jsonify({"error": str(e)}), 500  

    @flask_app.route('/respond', methods=['POST'])
    def respond():
        """Process user answer and generate next question."""
        try:
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

        except Exception as e:
            print(f"❌ Error in /respond: {e}")  
            return jsonify({"error": str(e)}), 500  

    # ============== 🚀 RUN FLASK IN BACKGROUND THREAD ============== #
    def run_flask():
        print("🚀 Starting Flask server...")
        flask_app.run(port=5000, debug=False, use_reloader=False)

    threading.Thread(target=run_flask, daemon=True).start()
    time.sleep(2)  # ✅ Ensure Flask starts before sending requests

    # ============== 🌟 STREAMLIT UI ============== #
    st.title("🎙 AI-Powered Interviewer")

    job_roles = ["Software Engineer", "Data Scientist", "Machine Learning Engineer", "AI Researcher"]

    candidate_name = st.text_input("Enter Your Name:")
    selected_role = st.selectbox("Select Job Role:", job_roles)

    if st.button("Start Interview"):
        if candidate_name and selected_role:
            try:
                response = requests.post("http://127.0.0.1:5000/start", json={"job_role": selected_role})
                if response.status_code == 200:
                    response_data = response.json()
                    st.session_state["session_id"] = response_data.get("session_id")
                    st.session_state["questions"] = [response_data.get("question", "Error: No question received")]
                    st.session_state["answers"] = []
                    st.session_state["interview_started"] = True
                else:
                    st.error(f"❌ Server Error: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Failed to connect to server: {str(e)}")

    if st.session_state.get("interview_started"):
        for i, (question, answer) in enumerate(zip(st.session_state["questions"], st.session_state["answers"])):
            st.write(f"**Q{i+1}:** {question}")
            st.write(f"🗣 **Your Answer:** {answer}")

        def record_voice():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.write("🎤 Listening...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            try:
                return recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                return "❌ Could not understand the audio."
            except sr.RequestError:
                return "⚠️ Speech API not responding."

        if st.button("🎤 Speak Answer"):
            user_answer = record_voice()
            if "❌" not in user_answer and "⚠️" not in user_answer:
                try:
                    response = requests.post("http://127.0.0.1:5000/respond", json={
                        "session_id": st.session_state["session_id"],
                        "answer": user_answer
                    })
                    if response.status_code == 200:
                        response_data = response.json()
                        st.write(f"✅ **Evaluation:** {response_data.get('evaluation', 'Error')}")
                    else:
                        st.error(f"❌ Server Error: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Failed to connect to server: {str(e)}")