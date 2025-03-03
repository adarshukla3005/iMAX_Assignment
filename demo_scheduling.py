import os
import json
import streamlit as st
import speech_recognition as sr
import requests
from datetime import datetime, timedelta
import dateparser
from google.oauth2 import service_account
from googleapiclient.discovery import build

MEETINGS_FILE = "meetings.json"

# Google Calendar API Configuration
SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "calendar_credentials.json"  # Replace with your actual file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)
CALENDAR_ID = "shukla305adarsh@gmail.com"  # Replace with your actual Calendar ID

# LLM API Endpoint
LLM_API_URL = "http://127.0.0.1:5000/chat"  # Flask server running for LLM correction

def load_meetings():
    """Loads existing meetings from JSON file."""
    if os.path.exists(MEETINGS_FILE):
        try:
            with open(MEETINGS_FILE, "r", encoding="utf-8") as file:
                return json.load(file)  # Load JSON data
        except (json.JSONDecodeError, FileNotFoundError):
            return []  # Return empty list if file is empty/corrupted
    return []

def save_meeting(meeting_details):
    """Saves a new meeting to the JSON file."""
    if not meeting_details:
        st.error("❌ Cannot save empty meeting details!")
        return

    meetings = load_meetings()  # Load existing data
    meetings.append(meeting_details)  # Append new data

    # Save updated data back to file
    with open(MEETINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(meetings, file, indent=4, ensure_ascii=False)

    st.success("✅ Meeting details saved successfully!")

# Transliteration API (Google Input Tools or Open-Source)
TRANSLIT_API_URL = "https://inputtools.google.com/request?itc=hi-t-i0-und&num=1&cp=0&cs=0&ie=utf-8&oe=utf-8"

def transliterate_hindi_to_english(hindi_text):
    """Converts Hindi script text to English (Romanized)."""
    try:
        response = requests.post(TRANSLIT_API_URL, json={"queries": [hindi_text]})
        if response.status_code == 200:
            translit_data = response.json()
            if translit_data[0] == "SUCCESS":
                return translit_data[1][0][1][0]  # Extract first transliteration suggestion
    except Exception as e:
        st.error(f"⚠️ Transliteration failed: {e}")
    return hindi_text  # Fallback: Return original text if transliteration fails

def recognize_speech(prompt):
    """Captures user speech and converts it to text."""
    st.write(prompt)
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for noise
        try:
            st.write("🎤 Listening... Speak now.")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            text = recognizer.recognize_google(audio, language="hi-IN")  # Hindi input
            return text.strip()
        except sr.WaitTimeoutError:
            return "⚠️ No speech detected, please try again."
        except sr.UnknownValueError:
            return "⚠️ Couldn't recognize speech, please speak clearly."
        except sr.RequestError:
            return "⚠️ Speech recognition service unavailable."
        except Exception as e:
            return f"⚠️ Error: {e}"

def parse_date_time(user_input):
    """Parses natural language date/time inputs like 'kal shaam'."""
    parsed_dt = dateparser.parse(user_input, settings={'PREFER_DATES_FROM': 'future'})
    
    if parsed_dt:
        return parsed_dt  # If dateparser works, return parsed date

    # If dateparser fails, send to LLM for correction
    try:
        response = requests.post(LLM_API_URL, json={"scenario": "demo_scheduling", "message": user_input})
        if response.status_code == 200:
            corrected_text = response.json().get("response", "").strip()
            return dateparser.parse(corrected_text, settings={'PREFER_DATES_FROM': 'future'})
    except Exception as e:
        st.error(f"⚠️ LLM Processing Failed: {e}")
    
    return None  # Return None if everything fails

def create_google_calendar_event(name, email, date, time):
    """Creates a Google Calendar event."""
    event_start = datetime.combine(date, time)
    event_end = event_start + timedelta(hours=1)  # Default: 1-hour meeting

    event = {
        "summary": f"Demo Meeting with {name}",
        "description": f"Email: {email}",
        "start": {"dateTime": event_start.isoformat(), "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": event_end.isoformat(), "timeZone": "Asia/Kolkata"},
    }

    try:
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        event_link = created_event.get("htmlLink")
        return event_link
    except Exception as e:
        st.error(f"❌ Failed to schedule event: {e}")
        return None
    

def send_email_notification(name, email, date, time, event_link):
    """Send the demo schedule to the user's email."""
    url = "http://127.0.0.1:5000/send_demo_schedule"  # Change if hosted on a server
    data = {
        "name": name,
        "email": email,
        "date": str(date),
        "time": str(time),
        "event_link": event_link
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            st.success(f"📩 Email sent successfully to {email}!")
        else:
            st.error("❌ Failed to send email!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# Google Calendar API Configuration
SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "calendar_credentials.json"  # Replace with your actual file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)
CALENDAR_ID = "shukla305adarsh@gmail.com"  # Replace with your actual Calendar ID

# LLM API Endpoint
LLM_API_URL = "http://127.0.0.1:5000/chat"  # Flask server running for LLM correction

def recognize_speech(prompt):
    """Captures user speech and converts it to text."""
    st.write(prompt)
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for noise
        try:
            st.write("🎤 Listening... Speak now.")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            text = recognizer.recognize_google(audio, language="hi-IN")  # Hindi input
            return text.strip()
        except sr.WaitTimeoutError:
            return "⚠️ No speech detected, please try again."
        except sr.UnknownValueError:
            return "⚠️ Couldn't recognize speech, please speak clearly."
        except sr.RequestError:
            return "⚠️ Speech recognition service unavailable."
        except Exception as e:
            return f"⚠️ Error: {e}"

def parse_date_time(user_input):
    """Parses natural language date/time inputs like 'kal shaam'."""
    parsed_dt = dateparser.parse(user_input, settings={'PREFER_DATES_FROM': 'future'})
    
    if parsed_dt:
        return parsed_dt  # If dateparser works, return parsed date

    # If dateparser fails, send to LLM for correction
    try:
        response = requests.post(LLM_API_URL, json={"scenario": "demo_scheduling", "message": user_input})
        if response.status_code == 200:
            corrected_text = response.json().get("response", "").strip()
            return dateparser.parse(corrected_text, settings={'PREFER_DATES_FROM': 'future'})
    except Exception as e:
        st.error(f"⚠️ LLM Processing Failed: {e}")
    
    return None  # Return None if everything fails


def demo_scheduling():
    """Main function to schedule meetings via voice or text."""
    st.subheader("📅 Schedule a ERP Demo Meeting")

    # Initialize session state variables if not already set
    if "name" not in st.session_state:
        st.session_state.name = ""
    if "date" not in st.session_state:
        st.session_state.date = None
    if "time" not in st.session_state:
        st.session_state.time = None
    if "email" not in st.session_state:
        st.session_state.email = ""

    # Choose Input Method
    input_method = st.radio("Choose Input Method:", ("Text", "Voice"), key="input_method")

    if input_method == "Text":
        st.session_state.name = st.text_input("👤 Enter Your Name:", value=st.session_state.name)
        st.session_state.date = st.date_input("📅 Select Date:", value=st.session_state.date if st.session_state.date else None)
        st.session_state.time = st.time_input("⏰ Select Time:", value=st.session_state.time if st.session_state.time else None)
        st.session_state.email = st.text_input("📧 Enter Email Address:", value=st.session_state.email)

    elif input_method == "Voice":
        if not st.session_state.name:
            hindi_name = recognize_speech("🗣️ Kripya apna naam bataiye:")
            if "⚠️" in hindi_name:
                st.error(hindi_name)
                return
            st.session_state.name = transliterate_hindi_to_english(hindi_name)  # Convert Hindi to English
            st.write(f"✅ Name: {st.session_state.name}")

        if not st.session_state.date:
            date_str = recognize_speech("📅 Kripya demo ka date bataiye (e.g., 2 March 2025 or 'kal shaam'):")
            if "⚠️" in date_str:
                st.error(date_str)
                return
            parsed_date = parse_date_time(date_str)
            if parsed_date:
                st.session_state.date = parsed_date.date()
                st.write(f"✅ Date: {st.session_state.date}")
            else:
                st.error("⚠️ Invalid date format, please try again.")
                return

        if not st.session_state.time:
            time_str = recognize_speech("⏰ Kripya samay bataiye (e.g., 10:30 AM or 'shaam 6 baje'):")
            if "⚠️" in time_str:
                st.error(time_str)
                return
            parsed_time = parse_date_time(time_str)
            if parsed_time:
                st.session_state.time = parsed_time.time()
                st.write(f"✅ Time: {st.session_state.time}")
            else:
                st.error("⚠️ Invalid time format, please try again.")
                return
            
        # Manual Email Input After Voice/Text Inputs
        email = st.text_input("📧 Enter Email Address Manually:", value=st.session_state.email)

        # Ensure session state updates with the entered email
        if email:
            st.session_state.email = email.strip()

    # Schedule Meeting Button
    if st.button("Schedule Meeting", key="schedule_btn"):
        if not st.session_state.name or "@" not in st.session_state.email:
            st.error("❌ Please enter valid details!")
            return

        # Ensure date and time are properly set
        if not st.session_state.date or not st.session_state.time:
            st.error("❌ Please provide a valid date and time before scheduling.")
            return

        event_link = create_google_calendar_event(
            st.session_state.name, st.session_state.email, st.session_state.date, st.session_state.time
        )
        if event_link:
            st.success(f"✅ Meeting scheduled successfully! [View Event]({event_link})")
            save_meeting({
                "name": st.session_state.name,
                "email": st.session_state.email,
                "date": str(st.session_state.date),
                "time": str(st.session_state.time),
                "event_link": event_link
            })

            # Send email confirmation
            send_email_notification(
                st.session_state.name,
                st.session_state.email,
                st.session_state.date,
                st.session_state.time,
                event_link
            )

        # Clear session state after scheduling
        st.session_state.name = ""
        st.session_state.date = None
        st.session_state.time = None
        st.session_state.email = ""

if __name__ == "__main__":
    demo_scheduling()