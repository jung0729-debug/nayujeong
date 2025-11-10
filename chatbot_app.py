# 🌍 Creative Role-based Chatbot Homepage
# Run: streamlit run app.py

import streamlit as st
import openai

# --- PAGE SETUP ---
st.set_page_config(
    page_title="🎭 Role-based Chatbot by Nayujeong",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HEADER / HOME PAGE ---
st.markdown("""
<div style="text-align:center; background-color:#f7f0f5; padding:20px; border-radius:15px;">
    <h1 style="color:#6a1b9a;">🎭 Creative Role-based Chatbot</h1>
    <p style="font-size:18px; color:#333;">Chat with AI that thinks like a creative professional. Choose your role and start exploring!</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("⚙️ Settings")

api_key = st.sidebar.text_input("🔑 Enter your OpenAI API Key", type="password")

st.sidebar.markdown("### 🔗 How to get your API Key")
st.sidebar.markdown("""
- **OpenAI (ChatGPT/GPT API)**: [Get API Key](https://platform.openai.com/account/api-keys)  
- **Perplexity AI**: [Get API Key](https://www.perplexity.ai/)  
- **Gemma / Google Gemini**: [Get API Key](https://developers.generativeai.google/)
""")

# --- ROLE SELECTION ---
roles = {
    "🎬 Film Director": "Visionary director; cinematography, camera angles, storytelling.",
    "💃 Dance Coach": "Passionate dance instructor; rhythm, balance, expression.",
    "👗 Fashion Stylist": "Creative fashion consultant; color harmony, textures, body types.",
    "🎨 Art Critic": "Analyzes artworks; symbolism, composition, emotion.",
    "🎹 Music Composer": "Creates melodies; music theory, harmonies, mood design.",
    "📝 Creative Writer": "Writes stories and poems; style, imagery, characters.",
    "📸 Photographer": "Advice on lighting, composition, storytelling through lenses.",
    "🎭 Theatre Actor": "Stage performance, drama, emotion.",
    "🎥 Film Editor": "Focus on cuts, sequences, pacing, visual rhythm.",
    "🎤 Performance Coach": "Voice, emotion, and public performance guidance."
}

role = st.sidebar.selectbox("🎭 Choose a Role", list(roles.keys()))
st.sidebar.info(roles[role])

# --- MAIN PAGE LAYOUT ---
col1, col2 = st.columns([2,1])

with col1:
    st.markdown("### 💬 Chat with your AI professional")
    if api_key:
        openai.api_key = api_key
        user_input = st.text_area("Ask something:", height=100)
        if st.button("✨ Generate Response"):
            if user_input.strip():
                with st.spinner("Thinking like a pro..."):
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
        st.info("Follow the links in the sidebar if you don't have an API key yet.")

with col2:
    st.markdown("### 🎨 Role Gallery / Sample Outputs")
    st.info(f"Sample outputs for **{role}**:")
    # 예시 샘플 출력 (실제 API로 생성하면 더 동적 가능)
    sample_outputs = {
        "🎬 Film Director": "Suggests using close-up shots for emotional impact.",
        "💃 Dance Coach": "Focus on core stability and fluid arm movements.",
        "👗 Fashion Stylist": "Pair pastel colors with neutral accessories.",
        "🎨 Art Critic": "Notice the contrast between light and shadow in the composition.",
        "🎹 Music Composer": "Try a minor chord progression to enhance tension."
    }
    st.write(sample_outputs.get(role, "Sample outputs not available."))

# --- USAGE GUIDE SECTION ---
st.markdown("---")
st.markdown("### 📝 How to Use")
st.markdown("""
1. Enter your OpenAI API Key in the sidebar.
2. Select a role from the sidebar dropdown.
3. Type your question or prompt and click 'Generate Response'.
4. Explore sample outputs and learn how each role thinks!
""")

# --- FOOTER ---
st.markdown("---")
st.markdown("Made by **Nayujeong** | Powered by **OpenAI API + Streamlit** 🎨")
