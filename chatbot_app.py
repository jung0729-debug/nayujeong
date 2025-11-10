# 🌍 Role-based Chatbot by Nayujeong
# Run this app: streamlit run app.py

import streamlit as st
import openai

# --- PAGE SETUP ---
st.set_page_config(page_title="🎭 Role-based Chatbot by Nayujeong", layout="wide")

st.title("🎭 Role-based Chatbot")
st.markdown("**Choose a professional role and chat with an AI that thinks like a creative expert.**")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("⚙️ Settings")

# --- API KEY INPUT ---
api_key = st.sidebar.text_input("🔑 Enter your OpenAI API Key", type="password")

# --- API 발급 안내 링크 ---
st.sidebar.markdown("### 🔗 How to get your API Key")
st.sidebar.markdown("""
- **OpenAI (ChatGPT/GPT API)**: [Get API Key](https://platform.openai.com/account/api-keys)  
- **Perplexity AI**: [Get API Key](https://www.perplexity.ai/)  
- **Gemma / Google Gemini**: [Get API Key](https://developers.generativeai.google/)
""")

# --- ROLE SETTINGS ---
roles = {
    "🎬 Film Director": "You are a visionary film director who loves discussing cinematography, camera angles, and emotional storytelling.",
    "💃 Dance Coach": "You are a passionate dance instructor focusing on rhythm, balance, and expression.",
    "👗 Fashion Stylist": "You are a creative fashion consultant specializing in color harmony, textures, and body types.",
    "🎨 Art Critic": "You analyze artworks deeply, emphasizing symbolism, composition, and emotion.",
    "🎹 Music Composer": "You create melodies and harmonies, explaining music theory and mood design.",
    "📝 Creative Writer": "You write stories and poems, focusing on style, imagery, and character development.",
    "📸 Photographer": "You give advice on lighting, composition, and storytelling through lenses.",
    "🎭 Theatre Actor": "You speak with drama and emotion, helping others improve stage performance.",
    "🎥 Film Editor": "You think in cuts and sequences, focusing on pacing and visual rhythm.",
    "🎤 Performance Coach": "You guide voice, emotion, and confidence in public performances."
}

role = st.sidebar.selectbox("🎭 Choose a Role", list(roles.keys()))
st.sidebar.write("🧠 **About this role:**")
st.sidebar.info(roles[role])

# --- MAIN INTERFACE ---
if api_key:
    openai.api_key = api_key
    user_input = st.text_area("💬 Ask something to your AI professional:", height=100)
    if st.button("✨ Generate Response"):
        if user_input.strip():
            with st.spinner("Thinking like a professional..."):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": roles[role]},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.8
                )
                st.markdown("### 🧩 Response:")
                st.write(response["choices"][0]["message"]["content"])
        else:
            st.warning("Please type something first!")
else:
    st.warning("🔑 Please enter your API key in the sidebar to start chatting.")
    st.info("If you don't have an API key, follow the links above to get one.")

# --- FOOTER ---
st.markdown("---")
st.markdown("Made by **Nayujeong** | Powered by **OpenAI API + Streamlit** 🎨")
