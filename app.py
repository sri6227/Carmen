import streamlit as st
import openai
import requests
import time

# Setup OpenAI and Resemble
openai.api_key = st.secrets["OPENAI_API_KEY"]
RESEMBLE_API_KEY = st.secrets["RESEMBLE_API_KEY"]
VOICE_UUID = st.secrets["VOICE_UUID"]
PROJECT_UUID = st.secrets["PROJECT_UUID"]

# Page Setup
st.set_page_config(page_title="CARMEN Voice Assistant", layout="centered")
st.title("🎤 Talk to Carmen")
st.markdown("Ask Carmen anything and hear her reply in her voice!")

# Get user input
user_input = st.text_input("You:", placeholder="Type your message...")

# Process input
if user_input:
    with st.spinner("Carmen is thinking..."):
        # Call GPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Carmen, a warm, empathetic assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content
        st.write("**Carmen:**", reply)

        # Call Resemble
        headers = {
            "Authorization": f"Token {RESEMBLE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "voice": VOICE_UUID,
            "text": reply,
            "project_uuid": PROJECT_UUID,
            "output_format": "mp3"
        }
        r = requests.post(f"https://app.resemble.ai/api/v2/projects/{PROJECT_UUID}/clips", headers=headers, json=payload)
        clip = r.json()
        clip_id = clip["item"]["uuid"]

        # Poll until ready
        while True:
            check = requests.get(f"https://app.resemble.ai/api/v2/clips/{clip_id}", headers=headers).json()
            if check["item"]["is_public"]:
                audio_url = check["item"]["audio_src"]
                break
            time.sleep(2)

        # Audio playback
        st.audio(audio_url, format="audio/mp3")

