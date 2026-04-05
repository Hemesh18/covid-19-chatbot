import tkinter as tk
from tkinter import scrolledtext
import requests
import pymongo
from datetime import datetime

# ==========================================
# 1. MongoDB Database Setup
# ==========================================
MONGO_URI = "mongodb://localhost:27017/"

try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.server_info() 
    db = client["covid_chatbot_db"]
    chat_logs = db["chat_history"]
    db_status = "✅ MongoDB Connected"
except Exception:
    chat_logs = None 
    db_status = "⚠️ MongoDB Not Connected (Logs won't save)"

# ==========================================
# 2. COVID-19 API Setup
# ==========================================
BASE_URL = "https://disease.sh/v3/covid-19"

def get_global_stats():
    try:
        response = requests.get(f"{BASE_URL}/all")
        if response.status_code == 200:
            data = response.json()
            return (f"🌍 Global COVID-19 Stats:\n"
                    f"🤧 Total Cases: {data['cases']:,}\n"
                    f"❤️ Recovered: {data['recovered']:,}\n"
                    f"💀 Deaths: {data['deaths']:,}\n")
        return "Sorry, I couldn't fetch global stats right now."
    except Exception as e:
        return f"API Error: {e}"

def get_country_stats(country):
    try:
        response = requests.get(f"{BASE_URL}/countries/{country}")
        if response.status_code == 200:
            data = response.json()
            return (f"📍 Stats for {data['country']}:\n"
                    f"🤧 Cases: {data['cases']:,} (+{data['todayCases']:,} today)\n"
                    f"❤️ Recovered: {data['recovered']:,}\n"
                    f"💀 Deaths: {data['deaths']:,} (+{data['todayDeaths']:,} today)\n"
                    f"🏥 Active Cases: {data['active']:,}\n")
        elif response.status_code == 404:
            return f"Sorry, I couldn't find data for '{country}'. Please check the spelling."
        return "Sorry, I encountered an error fetching the data."
    except Exception as e:
        return f"API Error: {e}"

# ==========================================
# 3. Chatbot Logic & Logging
# ==========================================
def log_interaction(user_input, bot_response):
    if chat_logs is not None:
        chat_logs.insert_one({
            "timestamp": datetime.now(),
            "user_input": user_input,
            "bot_response": bot_response
        })

def generate_response(user_input):
    text = user_input.lower().strip()
    
    if text in ['quit', 'exit', 'bye']:
        return "Stay safe! Goodbye! 👋 (You can close the window now)"
    elif "global" in text or "world" in text or "worldwide" in text:
        return get_global_stats()
    elif "in " in text:
        words = text.split()
        idx = words.index("in")
        country = " ".join(words[idx+1:])
        if country:
             return get_country_stats(country)
        else:
             return "Please specify a country name after 'in', like 'cases in Brazil'."
    elif text in ["hi", "hello", "hey", "help"]:
         return ("Hello! I am your COVID-19 Tracker Bot. 🩺\n"
                 "Ask me things like:\n"
                 "- 'Show me global stats'\n"
                 "- 'What are the cases in India?'")
    else:
        return "I didn't quite catch that. Try asking for 'global stats' or 'cases in [Country Name]'."

# ==========================================
# 4. GUI Setup (Tkinter)
# ==========================================
def send_message(event=None):
    """Handles the user pressing 'Send' or hitting Enter."""
    user_text = entry_box.get().strip()
    if not user_text:
        return
    
    # 1. Display User Message
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, "You: " + user_text + "\n", "user")
    
    # 2. Clear Input Box
    entry_box.delete(0, tk.END)
    
    # 3. Generate and Display Bot Response
    bot_reply = generate_response(user_text)
    chat_area.insert(tk.END, "Bot: " + bot_reply + "\n\n", "bot")
    
    # 4. Scroll to the bottom & Lock text area
    chat_area.yview(tk.END)
    chat_area.config(state=tk.DISABLED)
    
    # 5. Save to MongoDB
    log_interaction(user_text, bot_reply)

# Initialize main window
root = tk.Tk()
root.title("COVID-19 Tracker Chatbot")
root.geometry("450x600")
root.resizable(False, False)
root.configure(bg="#2C3E50")

# Header Label
header = tk.Label(root, text="COVID-19 Live Tracker", bg="#2980B9", fg="white", font=("Arial", 14, "bold"), pady=10)
header.pack(fill=tk.X)

# Status Label (Shows MongoDB connection status)
status_label = tk.Label(root, text=db_status, bg="#2C3E50", fg="#BDC3C7", font=("Arial", 9))
status_label.pack(pady=2)

# Chat History Area (Scrollable)
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#ECF0F1", fg="#2C3E50", font=("Arial", 11))
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Add color tags for user and bot messages
chat_area.tag_config("user", foreground="#2980B9", font=("Arial", 11, "bold"))
chat_area.tag_config("bot", foreground="#27AE60")

# Initial greeting
chat_area.insert(tk.END, "Bot: Hello! Type 'hi' or 'help' to see what I can do.\n\n", "bot")
chat_area.config(state=tk.DISABLED) # Lock it so user can't type directly in the chat history

# Bottom Frame for Input and Button
bottom_frame = tk.Frame(root, bg="#2C3E50")
bottom_frame.pack(padx=10, pady=10, fill=tk.X)

# Text Input Box
entry_box = tk.Entry(bottom_frame, font=("Arial", 12), bg="white")
entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
entry_box.bind("<Return>", send_message) # Allows hitting "Enter" to send

# Send Button
send_btn = tk.Button(bottom_frame, text="Send", font=("Arial", 11, "bold"), bg="#27AE60", fg="white", command=send_message)
send_btn.pack(side=tk.RIGHT, padx=5, ipadx=10, ipady=4)

# Run the application
root.mainloop()