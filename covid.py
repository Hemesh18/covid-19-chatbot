import requests
import pymongo
from datetime import datetime

# ==========================================
# 1. MongoDB Database Setup
# ==========================================
# If you are using MongoDB Atlas, replace the URI string below with your connection string.
MONGO_URI = "mongodb://localhost:27017/"

try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Check connection
    client.server_info() 
    db = client["covid_chatbot_db"]
    chat_logs = db["chat_history"]
    print("✅ Successfully connected to MongoDB.")
except Exception as e:
    print(f"⚠️ Could not connect to MongoDB. Error: {e}")
    # Fallback to None so the bot can still run without logging if DB fails
    chat_logs = None 


# ==========================================
# 2. COVID-19 API Setup
# ==========================================
BASE_URL = "https://disease.sh/v3/covid-19"

def get_global_stats():
    """Fetches worldwide COVID-19 statistics."""
    try:
        response = requests.get(f"{BASE_URL}/all")
        if response.status_code == 200:
            data = response.json()
            return (f"🌍 **Global COVID-19 Stats:**\n"
                    f"🤧 Total Cases: {data['cases']:,}\n"
                    f"❤️ Recovered: {data['recovered']:,}\n"
                    f"💀 Deaths: {data['deaths']:,}\n"
                    f"📅 Last Updated: {datetime.fromtimestamp(data['updated']/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        return "Sorry, I couldn't fetch global stats right now."
    except Exception as e:
        return f"API Error: {e}"

def get_country_stats(country):
    """Fetches COVID-19 statistics for a specific country."""
    try:
        response = requests.get(f"{BASE_URL}/countries/{country}")
        if response.status_code == 200:
            data = response.json()
            return (f"📍 **Stats for {data['country']}:**\n"
                    f"🤧 Cases: {data['cases']:,} (+{data['todayCases']:,} today)\n"
                    f"❤️ Recovered: {data['recovered']:,}\n"
                    f"💀 Deaths: {data['deaths']:,} (+{data['todayDeaths']:,} today)\n"
                    f"🏥 Active Cases: {data['active']:,}")
        elif response.status_code == 404:
            return f"Sorry, I couldn't find data for '{country}'. Please check the spelling."
        return "Sorry, I encountered an error fetching the data."
    except Exception as e:
        return f"API Error: {e}"


# ==========================================
# 3. Chatbot Logic & Logging
# ==========================================
def log_interaction(user_input, bot_response):
    """Saves the conversation to MongoDB."""
    if chat_logs is not None:
        chat_logs.insert_one({
            "timestamp": datetime.now(),
            "user_input": user_input,
            "bot_response": bot_response
        })

def generate_response(user_input):
    """Basic Natural Language Processing to determine user intent."""
    text = user_input.lower().strip()
    
    if text in ['quit', 'exit', 'bye']:
        return "Stay safe! Goodbye! 👋"
    
    elif "global" in text or "world" in text or "worldwide" in text:
        return get_global_stats()
    
    # Simple extraction logic: "cases in Canada" -> Extracts "Canada"
    elif "in " in text:
        words = text.split()
        idx = words.index("in")
        # Join everything after the word "in" as the country name
        country = " ".join(words[idx+1:])
        if country:
             return get_country_stats(country)
        else:
             return "Please specify a country name after 'in', like 'cases in Brazil'."
             
    elif text in ["hi", "hello", "hey", "help"]:
         return ("Hello! I am your COVID-19 Tracker Bot. 🩺\n"
                 "You can ask me things like:\n"
                 "- 'Show me global stats'\n"
                 "- 'What are the cases in India?'\n"
                 "- 'status in UK'")
                 
    else:
        return "I didn't quite catch that. Try asking for 'global stats' or 'cases in [Country Name]'."


# ==========================================
# 4. Main Chat Loop
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*40)
    print("🤖 COVID-19 CLI Chatbot Initialized")
    print("Type 'quit' or 'exit' to stop.")
    print("="*40 + "\n")
    
    while True:
        user_msg = input("You: ")
        
        # Generate the reply based on input
        bot_reply = generate_response(user_msg)
        
        # Print the bot's response
        print(f"\nBot: {bot_reply}\n")
        
        # Save interaction to Database dynamically
        log_interaction(user_msg, bot_reply)
        
        # Break loop if user wants to exit
        if user_msg.lower() in ['quit', 'exit', 'bye']:
            break