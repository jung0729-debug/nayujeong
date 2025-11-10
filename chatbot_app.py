import streamlit as st
from openai import OpenAI
import os

# 🔐 Load API key from Streamlit Secrets
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
client = OpenAI()

# -------------------------------
# 🎭 App Title and Description
# -------------------------------
st.set_page_config(page_title="🎭 Role-based Chatbot", layout="wide")
st.title("🎭 Role-based Creative Chatbot")
st.markdown("Select a creative professional role and chat naturally!")

# -------------------------------
# 🎨 Sidebar: Role Selection
# -------------------------------
roles = {
    "🎬 Video Production Expert": "You are an experienced video producer who gives advice about filming, editing, and directing.",
    "👗 Fashion Consultant": "You are a professional stylist offering fashion coordination tips and trend insights.",
    "💃 Dance Coach": "You are a dance instructor helping people improve choreography and movement.",
    "🎭 Performing Arts Critic": "You write critical reviews on theatre, film, and live performances.",
    "🎨 Visual Artist": "You are a painter and digital artist who gives feedback on artistic composition and color harmony.",
    "🎵 Music Producer": "You guide people on music arrangement, sound design, and production techniques.",
    "📚 Literature Editor": "You analyze and improve creative writing, structure, and expression.",
    "🎮 Game Designer": "You create and refine game concepts, mechanics, and storytelling.",
    "📸 Photographer": "You provide professional tips on lighting, lens choice, and visual composition.",
    "🎤 Voice Actor Coach": "You train students to perform voice acting with emotion and clarity."
}

st.sidebar.header("🧩 Choose a Role")
selected_role = st.sidebar.selectbox("Select a creative field", list(roles.keys()))
st.sidebar.write("🧠 Role loaded:", selected_role)

# -------------------------------
# 💬 Chat Interface
# -------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.subheader(f"Chat as a {selected_role[2:]}")

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
prompt = st.chat_input("Ask or discuss something!")

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking creatively..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": roles[selected_role]},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    st.session_state["messages"].append({"role": "assistant", "content": reply})
