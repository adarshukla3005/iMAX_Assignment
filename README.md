# Hinglish Cold Calling AI  

This is an AI-powered cold-calling assistant that helps with **demo scheduling, interview screening, and payment follow-ups**. It supports **voice interactions, Hinglish conversation processing, Google Calendar integration for meeting scheduling, and Gmail automation for follow-ups**.  

![Screenshot 2025-03-03 222903](https://github.com/user-attachments/assets/88a054ab-6e3a-45b9-8ee2-009d5f0a743a)

## Features  

- **AI-Powered Conversations**: Uses Google Gemini AI for natural conversations in Hinglish.  
- **Voice Interaction**: Speech-to-text input and AI-generated voice responses.  
- **Demo Scheduling**: Uses Google Calendar API to schedule meetings.  
- **Interview Screening**: AI conducts interviews with sequential questions and evaluates responses.  
- **Payment Follow-ups**: Sends polite email reminders for pending payments.  
- **Data Storage**: Stores scheduled meetings, interview responses, and follow-up details in JSON files.  
- **Streamlit UI**: Interactive web-based interface for user interaction.  
- **Flask API Backend**: Handles AI logic and integrates with external services.  

## Project Structure  

```bash
│── 📂 pycache/  
│── 📂 myenv/  
│── 📄 .env  
│── 📄 calendar_credentials.json  
│── 📄 .gitignore  
│── 📄 app.py 
│── 📄 demo_scheduling.py
│── 📄 followup_payment.py
│── 📄 interview_screening.py 
│── 📄 interview_data.json  
│── 📄 meetings.json
│── 📄 payment_followup.json
│── 📄 send_email.py  
│── 📄 config.py
│── 📄 requirements.txt
│── 📄 structure.md
```

## Installation and Setup  

Follow these steps to set up and run the Hinglish Cold Calling AI:  

### 1. Clone the Repository  

```bash
git clone https://github.com/your-username/hinglish-cold-calling-ai.git
cd hinglish-cold-calling-ai
```

### 2. Create Virtual Environment

```bash
python -m venv myenv
source myenv/bin/activate  # On macOS/Linux
myenv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Configure API Keys

Create a .env file in the project directory and add your API keys:

```ini
GOOGLE_API_KEY=your_google_gemini_api_key
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password  # Use an App Password, not your main password.
```

### 5. Set Up Google Calendar API
If you want to enable demo scheduling:

Go to Google Cloud Console
Enable the [Google Cloud Console](https://console.cloud.google.com/welcome?pli=1&project=llm-langchain-449320)
Download credentials.json and place it in the project folder as calendar_credentials.json.

### 6. Run the Streamlit Frontend
In a new terminal window:

```bash
streamlit run app.py
```
This will open the web UI in your browser and start the Flask server on http://127.0.0.1:5000/.

## API Endpoints

| Endpoint               | Method | Description |
|------------------------|--------|--------------------------------------------------------------|
| `/chat`               | POST   | Processes user messages and generates AI responses. |
| `/schedule`          | POST   | Schedules a demo meeting via Google Calendar. |
| `/payment_followup`   | POST   | Sends a payment reminder email. |
| `/send_demo_schedule` | POST   | Sends meeting details via email. |
| `/start`              | POST   | Starts an AI-driven interview session. |
| `/respond`            | POST   | Handles user responses during an interview. |

##  Usage  

1. **Select a Scenario:** Choose between `Demo Scheduling`, `Interview Screening`, or `Payment Follow-up`.  
2. **Speak or Type:** Click the "Speak" button for voice input or manually enter text.  
3. **AI Response:** The AI will assist based on the selected scenario.  
4. **Schedule a Meeting:** Provide details to book a demo via Google Calendar.  
5. **Follow Up on Payments:** Enter customer details to send an email reminder.  
6. **Conduct Interviews:** The AI sequentially asks job-related questions and evaluates responses.

## Troubleshooting
1. If the AI does not respond, check if the Flask server is running.
2. Ensure API keys and .env variables are correctly set up.
3. If speech recognition fails, enable your microphone.
4. For email errors, verify Gmail settings (use App Password if needed).

## Author
Adarsh Shukla
IIT Roorkee
📧 Email: adarshukla3005@gmail.com
📞 Contact: +91-8707446780




