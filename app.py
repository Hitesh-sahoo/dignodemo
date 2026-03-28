import streamlit as st
import requests
import os
import time 

st.set_page_config(page_title="🏥Diagnoverse_ai", page_icon="🤖", layout="wide")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #1f1c2c, #928dab); color: white; }
.main-container { max-width: 900px; margin: auto; padding: 20px; }
.chat-bubble-user { background: linear-gradient(90deg, #00c6ff, #0072ff); padding: 12px 16px; border-radius: 18px; margin: 8px; color: white; max-width: 70%; align-self: flex-end; }
.chat-bubble-bot { background: #2c2c3e; padding: 12px 16px; border-radius: 18px; margin: 8px; color: white; max-width: 70%; align-self: flex-start; }
.stButton>button { background: linear-gradient(90deg, #ff7e5f, #feb47b); border-radius: 12px; border: none; color: white; font-weight: bold; }
input { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
<h1 style='text-align:center;'>🏥 AI Hospital Assistant</h1>
<p style='text-align:center;'>Smart Appointment Booking System</p>
<hr>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Login", "🧍 Register"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("📧 Email", key="login_email")
        password = st.text_input("🔒 Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            res = requests.post(
                f"{API_URL}/login",
                data={"email": email.strip(), "password": password.strip()}
            )

            if res.status_code == 200:
                data = res.json()
                st.session_state.logged_in = True
                st.session_state.patient_id = data.get("patient_id")
                st.session_state.user_name = data.get("name")
                st.success("Login successful 🎉")
                st.rerun()
            else:
                st.error("Invalid credentials ❌")


    with tab2:
        st.subheader("Create Account")
        name = st.text_input("👤 Full Name", key="reg_name")
        reg_email = st.text_input("📧 Email", key="reg_email")
        reg_password = st.text_input("🔒 Password", type="password", key="reg_password")
        phone = st.text_input("📱 Phone Number", key="reg_phone")

        if st.button("Register", key="register_btn"):
            res = requests.post(
                f"{API_URL}/register",
                data={
                    "name": name.strip(),
                    "email": reg_email.strip(),
                    "password": reg_password.strip(),
                    "phone": phone.strip()
                }
            )

            if res.status_code == 200:
                st.success("Account created successfully 🎉 Now login!")
            else:
                st.error(res.json().get("message", "Registration failed"))

else:
    st.success(f"Welcome {st.session_state.user_name} 👋")

    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-bubble-user'>{msg['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-bot'>{msg['text']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Type your symptoms...")

    if user_input:
        st.session_state.messages.append({"role": "user", "text": user_input})
        with st.spinner("🤖 Analyzing your symptoms..."):
            time.sleep(1.5)
            res=requests.post(
                f"{API_URL}/chatbot",
                params={"symptoms": user_input, "patient_id": st.session_state.patient_id}
            )

        bot_reply = res.json().get("message", "Error")

        if "Booking Confirmed" in bot_reply:
            st.balloons()
        st.session_state.messages.append({"role": "bot", "text": bot_reply})
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚪 Logout", key="logout_btn"):
        st.session_state.clear()
        st.rerun()
