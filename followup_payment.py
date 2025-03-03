import streamlit as st
import requests
import json
import os

def save_payment_data(data):
    """Save payment follow-up details into a JSON file."""
    file_path = "payment_followup.json"

    # Load existing data if file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Append new payment details
    existing_data.append(data)

    # Save back to file
    with open(file_path, "w") as f:
        json.dump(existing_data, f, indent=4)

def payment_followup(st, speak):
    st.subheader("💰 Payment Follow-Up")

    name = st.text_input("Enter Customer Name:")
    contact = st.text_input("Enter Contact Number:")
    amount = st.text_input("Enter Pending Amount:")
    email = st.text_input("Enter Customer Email:")

    if st.button("Send Payment Reminder"):
        payment_details = {
            "name": name,
            "contact": contact,
            "amount": amount,
            "email": email,
        }

        # Save data locally
        save_payment_data(payment_details)

        # Send request to Flask backend
        response = requests.post("http://127.0.0.1:5000/payment_followup", json=payment_details)

        if response.status_code == 200:
            st.success(response.json().get("message", "Payment reminder sent!"))
            speak("Payment reminder successfully sent!")  # Speak confirmation
        else:
            try:
                response_data = response.json()
                st.error(response_data.get("error", "An error occurred!"))
            except requests.exceptions.JSONDecodeError:
                st.error(f"Failed to decode JSON. Response: {response.text}")

# Run Streamlit app
if __name__ == "__main__":
    st.title("📧 Automated Payment Reminder System")
    payment_followup(st, lambda msg: print(msg))  # Replace print with actual TTS function if needed