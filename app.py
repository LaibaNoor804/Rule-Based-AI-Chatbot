"""
app.py
======
Browser interface for RuleBot. Run with:
    streamlit run app.py
"""

import streamlit as st

from core.engine import ChatEngine

st.set_page_config(page_title="RuleBot Pro", page_icon="🤖", layout="centered")

st.title("🤖 RuleBot Pro")
st.caption("A rule-based chatbot with fuzzy matching, memory, and live customization.")


@st.cache_resource
def load_engine():
    return ChatEngine()


engine = load_engine()

# --- Sidebar: about + teach panel -----------------------------------
with st.sidebar:
    st.header("About RuleBot")
    st.write(
        "RuleBot matches your message against a knowledge base using "
        "typo-tolerant fuzzy matching, so 'helo' still triggers a greeting."
    )
    st.write(f"**Known topics:** {len(engine.intents)}")

    st.divider()
    st.subheader("🎓 Teach RuleBot")
    st.caption("Add your own custom question & answer.")
    new_question = st.text_input("Question", placeholder="e.g. what is your favorite color")
    new_answer = st.text_input("Answer", placeholder="e.g. I like binary: 0 and 1")
    if st.button("Save this response"):
        if new_question and new_answer:
            reply = engine._handle_teach(f"{new_question} => {new_answer}")
            st.success(reply)
        else:
            st.warning("Please fill in both fields.")

    st.divider()
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        engine.reset_history()
        st.rerun()

# --- Chat state -------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm RuleBot. Type 'help' to see what I know."}
    ]

# --- Render existing conversation -------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- Chat input ---------------------------------------------------------
user_input = st.chat_input("Type a message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    turn = engine.get_response(user_input)

    st.session_state.messages.append({"role": "assistant", "content": turn.bot_reply})
    with st.chat_message("assistant"):
        st.write(turn.bot_reply)
        if turn.matched_tag:
            st.caption(f"matched topic: `{turn.matched_tag}`")
