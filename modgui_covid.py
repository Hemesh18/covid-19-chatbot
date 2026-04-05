import streamlit as st
import requests
import pymongo
from datetime import datetime

# ==========================================
# 1. Page Configuration & UI Setup
# ==========================================
st.set_page_config(page_title="COVID-19 AI Tracker", page_icon="🦠", layout="centered")
st.title("🦠 Live COVID-19 Tracker")
st.caption("A dynamic chatbot powered by Disease.sh and MongoDB")

# ==========================================
# 2. Database Connection (Cached)
# ==========================================
# @st.cache_resource ensures we only connect to the database once!
@st.cache_resource
def init_connection():
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info() # trigger connection
        db = client["covid_chatbot_db"]
        return db["chat_history"]
    except Exception:
        return None

chat_logs = init_connection()

# Show a small status indicator in the sidebar
with st.sidebar:
    st.header("System Status")
    if chat_logs is not None:
        st.success("✅ MongoDB Connected")
        st.info(f"Total Logs Saved: {chat_logs.count_documents({})}")
    else:
        st.warning("⚠️ MongoDB Not Connected (Logs won't save)")

# ==========================================
# 3. API & Chat Logic
# ==========================================
BASE_URL = "https://disease.sh/v3/covid-19"

def get_global_stats():
    try:
        response = requests.get(f"{BASE_URL}/all")
        if response.status_code == 200:
            data = response.json()
            return (f"### 🌍 Global Stats\n"
                    f"- **🤧 Cases:** {data['cases']:,}\n"
                    f"- **❤️ Recovered:** {data['recovered']:,}\n"
                    f"- **💀 Deaths:** {data['deaths']:,}")
        return "Sorry, I couldn't fetch global stats."
    except Exception as e:
        return f"API Error: {e}"

def get_country_stats(country):
    try:
        response = requests.get(f"{BASE_URL}/countries/{country}")
        if response.status_code == 200:
            data = response.json()
            return (f"### 📍 Stats for {data['country']}\n"
                    f"- **🤧 Cases:** {data['cases']:,} `(+{data['todayCases']:,} today)`\n"
                    f"- **❤️ Recovered:** {data['recovered']:,}\n"
                    f"- **💀 Deaths:** {data['deaths']:,} `(+{data['todayDeaths']:,} today)`\n"
                    f"- **🏥 Active:** {data['active']:,}")
        elif response.status_code == 404:
            return f"I couldn't find data for '{country}'. Please check the spelling."
        return "Sorry, I encountered an error fetching the data."
    except Exception as e:
        return f"API Error: {e}"

def generate_response(user_input):
    text = user_input.lower().strip()
    if "global" in text or "world" in text:
        return get_global_stats()
    elif "in " in text:
        words = text.split()
        idx = words.index("in")
        country = " ".join(words[idx+1:])
        return get_country_stats(country) if country else "Please specify a country after 'in'."
    elif text in ["hi", "hello", "help"]:
         return "Hello! 👋 Ask me for **global stats** or **cases in [Country]**."
    else:
        return "I didn't quite catch that. Try 'global stats' or 'cases in Brazil'."

# ==========================================
# 4. Streamlit Chat Interface
# ==========================================
# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your COVID-19 Tracker. How can I help you today?"}]

# Display all previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# React to user input
if user_input := st.chat_input("Type your question here..."):
    
    # 1. Display User Message instantly
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. Get and Display Bot Response
    bot_reply = generate_response(user_input)
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    
    # 3. Log to MongoDB behind the scenes
    if chat_logs is not None:
        chat_logs.insert_one({
            "timestamp": datetime.now(),
            "user_input": user_input,
            "bot_response": bot_reply
        })