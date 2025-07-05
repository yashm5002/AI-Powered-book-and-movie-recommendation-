import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import re

# --- Gemini Setup ---
load_dotenv()
client = genai.Client()

# --- Enhanced CSS for Dark Theme and Card UI ---
st.markdown("""
<style>
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #a0a0a0;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .bot-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff !important;
        border-radius: 20px 20px 20px 5px;
        padding: 15px 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .user-message {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: #fff !important;
        border-radius: 20px 20px 5px 20px;
        padding: 15px 20px;
        margin: 10px 0;
        text-align: right;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .card {
        background: linear-gradient(135deg, #232526 0%, #414345 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        border-left: 5px solid #74b9ff;
        position: relative;
    }
    .card-title {
        color: #74b9ff !important;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 8px;
        font-weight: bold;
    }
    .desc {
        color: #ecf0f1 !important;
        line-height: 1.6;
        font-size: 1rem;
        margin-top: 8px;
    }
    .progress-container {
        background: #2c3e50;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        border: 1px solid #34495e;
    }
    .footer {
        text-align: center;
        color: #a0a0a0 !important;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 20px;
        border-top: 1px solid #34495e;
    }
    .stApp {
        background: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Questions & Options ---
QUESTIONS = [
    {
        "q": "Do you prefer 📚 books or 🎬 movies?",
        "type": "radio",
        "options": ["Books", "Movies", "Both equally"]
    },
    {
        "q": "Which genre speaks to your soul?",
        "type": "radio",
        "options": ["🚀 Sci-Fi", "🎭 Drama", "😱 Thriller", "😂 Comedy", "💕 Romance", "⚡ Action", "🧙 Fantasy", "🔍 Mystery"]
    },
    {
        "q": "What's your preferred story pace?",
        "type": "radio",
        "options": ["⚡ Fast-paced & exciting", "🐌 Slow & contemplative", "🎯 Balanced mix"]
    },
    {
        "q": "Do you lean towards classics or modern works?",
        "type": "radio",
        "options": ["📜 Timeless classics", "🆕 Modern masterpieces", "🎭 Mix of both"]
    },
    {
        "q": "What themes resonate with you most?",
        "type": "text",
        "placeholder": "e.g., adventure, self-discovery, family, technology..."
    },
    {
        "q": "How do you like your stories to end?",
        "type": "radio",
        "options": ["😊 Happy & satisfying", "🤔 Open-ended & thought-provoking", "😢 Bittersweet & realistic"]
    }
]

def build_prompt(answers):
    prompt = (
        "You are a passionate book and movie curator. Based on the user's preferences, "
        "recommend exactly 3 titles in this format:\n\n"
        "1. Title (Book/Movie, Genre, Year): Description.\n"
        "2. Title (Book/Movie, Genre, Year): Description.\n"
        "3. Title (Book/Movie, Genre, Year): Description.\n\n"
        "User Preferences:\n"
    )
    for i, ans in enumerate(answers):
        prompt += f"• {QUESTIONS[i]['q']} → {ans}\n"
    prompt += "\nProvide exactly 3 recommendations in the specified format."
    return prompt

def parse_gemini_recommendations(raw_text):
    # Parse Gemini output: "1. Title (Book/Movie, Genre, Year): Description"
    pattern = re.compile(
        r'\d+\.\s*([^\(]+)\(([^,]+),\s*([^,]+),\s*(\d{4}|N/A)\):\s*(.+?)(?=\n\d+\.|$)',
        re.DOTALL
    )
    icons = {"Book": "📚", "Movie": "🎬"}
    recs = []
    for match in pattern.finditer(raw_text):
        title = match.group(1).strip()
        format_type = match.group(2).strip()
        genre = match.group(3).strip()
        year = match.group(4).strip()
        desc = match.group(5).strip()
        icon = icons.get(format_type, "✨")
        recs.append({
            "title": title,
            "format": format_type,
            "genre": genre,
            "year": year,
            "desc": desc,
            "icon": icon
        })
    return recs

def display_recommendations(recs):
    st.markdown("### 🎯 Your Perfect Matches")
    for idx, rec in enumerate(recs, 1):
        with st.container():
            st.markdown(f"""
                <div class="card">
                    <div style="position:absolute;top:15px;right:20px;font-size:1.1rem;color:#fff;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;">{idx}</div>
                    <div class="card-title">{rec['icon']} {rec['title']}</div>
                    <div>
                        <span class="badge">{rec['format']}</span>
                        <span class="badge">{rec['genre']}</span>
                        <span class="badge">{rec['year']}</span>
                    </div>
                    <div class="desc">{rec['desc']}</div>
                </div>
            """, unsafe_allow_html=True)

# --- Main UI ---
st.set_page_config(
    page_title="Story Genie ✨", 
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown('<h1 class="main-title">✨ Story Genie</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your personal curator for amazing books & movies</p>', unsafe_allow_html=True)

if "question_idx" not in st.session_state:
    st.session_state.question_idx = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

# Progress
with st.container():
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    progress = st.session_state.question_idx / len(QUESTIONS)
    st.progress(progress, text=f"✨ Question {st.session_state.question_idx + 1} of {len(QUESTIONS)}")
    st.markdown('</div>', unsafe_allow_html=True)

# Chat history
for i in range(len(st.session_state.answers)):
    st.markdown(
        f'<div class="bot-message"><strong>🧞‍♂️ Genie:</strong> {QUESTIONS[i]["q"]}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="user-message"><strong>You:</strong> {st.session_state.answers[i]}</div>',
        unsafe_allow_html=True
    )

# Current question
if st.session_state.question_idx < len(QUESTIONS):
    q_obj = QUESTIONS[st.session_state.question_idx]
    st.markdown(
        f'<div class="bot-message"><strong>🧞‍♂️ Genie:</strong> {q_obj["q"]}</div>',
        unsafe_allow_html=True
    )
    answer = None
    if q_obj["type"] == "radio":
        answer = st.radio(
            "Choose your answer:",
            q_obj["options"],
            key=f"radio_q_{st.session_state.question_idx}",
            label_visibility="visible"
        )
    else:
        answer = st.text_input(
            "Your answer:",
            placeholder=q_obj.get("placeholder", "Type your answer here..."),
            key=f"text_q_{st.session_state.question_idx}",
            label_visibility="visible"
        )
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("✨ Next", key=f"next_btn_{st.session_state.question_idx}", use_container_width=True):
            if q_obj["type"] == "text" and answer.strip() == "":
                st.error("Please share your thoughts before continuing! 💭")
            else:
                st.session_state.answers.append(answer)
                st.session_state.question_idx += 1
                st.rerun()

# Generate recommendations
elif st.session_state.recommendations is None:
    with st.spinner("🔮 The Genie is consulting the mystical library..."):
        raw_recommendations = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=build_prompt(st.session_state.answers)
        ).text
        st.session_state.recommendations = raw_recommendations
    st.balloons()
    st.success("🎉 Your personalized recommendations are ready!")

# Display formatted recommendations
if st.session_state.recommendations:
    recs = parse_gemini_recommendations(st.session_state.recommendations)
    display_recommendations(recs)

# Footer with start over button
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("🔄 Start New Journey", key="start_new_journey_btn", use_container_width=True):
        st.session_state.question_idx = 0
        st.session_state.answers = []
        st.session_state.recommendations = None
        st.rerun()

