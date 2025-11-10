# 🌍 Creative Role-based Chatbot by Nayujeong
# Run this app: streamlit run app.py

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

# API Key input
api_key = st.sidebar.text_input("🔑 Enter your OpenAI API Key", type="password")

# API 발급 안내
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

    sample_outputs = {
        "🎬 Film Director": """
- Suggests using close-up shots for emotional impact.
- Recommends dynamic camera angles for action sequences.
- Emphasizes color grading to enhance mood.
- Advises pacing adjustments to maintain tension.
""",
        "💃 Dance Coach": """
- Focus on core stability and fluid arm movements.
- Suggests practicing counts with music to improve timing.
- Recommends stretching routines for flexibility.
- Gives tips for expressive facial gestures.
""",
        "👗 Fashion Stylist": """
- Pair pastel colors with neutral accessories.
- Suggests layering textures for depth in outfits.
- Advises choosing clothing to complement body shapes.
- Recommends seasonal wardrobe color palettes.
""",
        "🎨 Art Critic": """
- Notice the contrast between light and shadow in the composition.
- Analyze symbolism and hidden meanings in the work.
- Comment on balance and visual harmony of elements.
- Suggest improvements in color choices or perspective.
""",
        "🎹 Music Composer": """
- Try a minor chord progression to enhance tension.
- Suggests adding counter-melodies for richness.
- Emphasizes dynamics to create emotional impact.
- Recommends tempo changes for dramatic effect.
""",
        "📝 Creative Writer": """
- Suggests using vivid imagery to immerse the reader.
- Provides ideas for character development.
- Offers plot twists to heighten suspense.
- Gives feedback on narrative pacing and dialogue.
""",
        "📸 Photographer": """
- Advises shooting during golden hour for natural light.
- Suggests framing subjects with leading lines.
- Recommends experimenting with depth of field.
- Emphasizes capturing emotion and storytelling.
""",
        "🎭 Theatre Actor": """
- Recommends projecting voice to reach the audience.
- Suggests practicing gestures for authenticity.
- Advises on timing and pauses for dramatic effect.
- Focus on emotional connection with scene partners.
""",
        "🎥 Film Editor": """
- Suggests cutting scenes for better pacing.
- Recommends transitions that match the tone.
- Advises layering sound and visuals for impact.
- Emphasizes rhythm and continuity in sequences.
""",
        "🎤 Performance Coach": """
- Guides on voice modulation for clarity and emotion.
- Recommends body posture exercises to boost confidence.
- Provides tips for managing stage anxiety.
- Suggests engaging the audience through interaction.
"""
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
