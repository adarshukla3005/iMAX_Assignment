import streamlit as st
import requests

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
