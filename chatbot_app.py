import streamlit as st
import requests

# 🔐 직접 API 키 입력
api_key = "66450566"
base_url = "https://api.perplexity.ai"  # 예시 엔드포인트

# -------------------------------
# 💬 Chat Interface
# -------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

prompt = st.chat_input("Ask or discuss something!")

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking creatively..."):
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "sonar-medium-chat",  # Perplexity API 사용 가능한 모델
                "messages": [
                    {"role": "system", "content": "You are a creative role-playing assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8
            }
            response = requests.post(f"{base_url}/chat/completions", headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            st.markdown(reply)

    st.session_state["messages"].append({"role": "assistant", "content": reply})
