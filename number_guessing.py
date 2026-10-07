import streamlit as st
import random
import time
from google.cloud import firestore
from google.oauth2 import service_account

# Configure mobile viewport settings
st.set_page_config(page_title="Number Guessing Game", page_icon="🎮", layout="centered")

# --- CUSTOM CSS VISUAL MAKEOVER ---
st.markdown("""
    <style>
    /* Global App Background */
    .stApp {
        background-color: #f7f9fc;
    }
    
    /* Sleek Application Title Banner */
    .app-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px;
        border-radius: 16px;
        color: white !important;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(30, 60, 114, 0.2);
    }
    .app-header h1, .app-header p {
        color: white !important;
    }
    
    /* LIGHT MODE: Clean Visual Containers */
    .game-container {
        background-color: white !important;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #e1e8ed;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
    }
    
    /* DARK MODE ADAPTIVE STYLE: Fixes mobile phone visibility bugs */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #0e1117 !important;
        }
        .game-container {
            background-color: #1a1c23 !important;
            border: 1px solid #2d3139 !important;
        }
        /* Forces all text items to adapt to solid high-visibility white */
        .stMarkdown, p, label, span, h3, div {
            color: #ffffff !important;
        }
    }
    
    /* Alert Style Turn Boxes */
    .your-turn-banner {
        background-color: #e6f4ea;
        border-left: 5px solid #34a853;
        padding: 15px;
        border-radius: 8px;
        color: #137333 !important;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .waiting-banner {
        background-color: #fef7e0;
        border-left: 5px solid #fbbc04;
        padding: 15px;
        border-radius: 8px;
        color: #b06000 !important;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    /* Full-Width responsive buttons for easier mobile tapping */
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 8px;
        height: 45px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Connect safely to the central cloud storage database
@st.cache_resource
def get_db():
    try:
        creds = service_account.Credentials.from_service_account_file("firebase_credentials.json")
        return firestore.Client(credentials=creds)
    except Exception as e:
        st.error("Missing firebase_credentials.json file in your folder structure.")
        return None

db = get_db()

# Render the Beautiful Styled Banner Header
st.markdown("""
    <div class="app-header">
        <h1 style='margin:0; font-size:26px;'>🏆 Number Guessing Game Online</h1>
        <p style='margin:5px 0 0 0; opacity:0.8; font-size:14px;'>Real-Time Cross-Device Match</p>
    </div>
""", unsafe_allow_html=True)

# --- INITIAL SETUP SCREEN ---
if "room_active" not in st.session_state:
    st.markdown('<div class="game-container">', unsafe_allow_html=True)
    st.subheader("🏠 Multi-Device Matchmaking Room")
    
    room_code = st.text_input("Enter 4-Digit Room Code (e.g., A7B9):", value="1234").upper().strip()
    my_name = st.text_input("Your Player Name:", value="Player").strip()
    
    choice = st.radio("Choose Action:", ["Create New Game Room (Host)", "Join Existing Game Room"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Connect to Lobby 🚀", type="primary"):
        if not room_code or not my_name:
            st.warning("Please fill in both fields.")
        else:
            room_ref = db.collection("guessing_rooms").document(room_code)
            room_data = room_ref.get()
            
            if choice == "Create New Game Room (Host)":
                secret = random.randint(1, 50)
                room_ref.set({
                    "players": [my_name],
                    "scores": {my_name: 0},
                    "secret_number": secret,
                    "guesses_taken": 0,
                    "max_attempts": 3,  # Scales up dynamically by 3 per player
                    "player_index": 0,
                    "feedback": "Room created. Waiting for players to join...",
                    "round_number": 1,
                    "status": "lobby"
                })
                st.session_state.room_code = room_code
                st.session_state.my_name = my_name
                st.session_state.room_active = True
                st.rerun()
                
            else:
                if room_data.exists:
                    data = room_data.to_dict()
                    
                    if len(data["players"]) >= 6:
                        st.error("This room is full! Maximum limit is 6 players.")
                    elif my_name in data["players"]:
                        st.error("That name is already taken in this room!")
                    else:
                        data["players"].append(my_name)
                        data["scores"][my_name] = 0
                        data["max_attempts"] = len(data["players"]) * 3
                        room_ref.update({
                            "players": data["players"],
                            "scores": data["scores"],
                            "max_attempts": data["max_attempts"]
                        })
                        st.session_state.room_code = room_code
                        st.session_state.my_name = my_name
                        st.session_state.room_active = True
                        st.rerun()
                else:
                    st.error("Room code not found! Check with the host.")

# --- ACTIVE REAL-TIME GAMEPLAY SCREEN ---
else:
    room_ref = db.collection("guessing_rooms").document(st.session_state.room_code)
    room_data = room_ref.get().to_dict()
    
    if not room_data:
        st.error("Room was disconnected by the host.")
        if st.button("Back to Setup"):
            del st.session_state.room_active
            st.rerun()
        st.stop()

    st.sidebar.markdown(f"### 📍 Room Code: **{st.session_state.room_code}**")
    st.sidebar.markdown(f"**Your Profile Name:** {st.session_state.my_name}")
    st.sidebar.write(f"Connected Players ({len(room_data['players'])}/6):", ", ".join(room_data["players"]))
    
    if room_data["status"] == "lobby":
        st.markdown('<div class="game-container" style="text-align:center;">', unsafe_allow_html=True)
        st.info("⌛ Waiting for the Host to lock the room and start the match...")
        
        # Check if current user is the host (first player in the list)
        is_host = room_data["players"][0] == st.session_state.my_name
        
        if is_host:
            st.write("⭐ You are the Host of this room.")
            if st.button("Lock Room & Start Game 🎮", type="primary"):
                room_ref.update({"status": "playing"})
                st.rerun()
        else:
            st.write("Waiting for the host to start the game...")
            
        st.write("---")
        if st.button("🔄 Refresh Lobby"):
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        current_turn_player = room_data["players"][room_data["player_index"]]
        
        st.markdown('<div class="game-container">', unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin:0 0 15px 0; color:#2a5298;'>✨ Round {room_data['round_number']}</h3>", unsafe_allow_html=True)
        
        cols = st.columns(len(room_data["players"]))
        for idx, name in enumerate(room_data["players"]):
            cols[idx].metric(label=name, value=f"{room_data['scores'].get(name, 0)} wins")
            
        st.write(f"📊 Attempts remaining in round: {room_data['max_attempts'] - room_data['guesses_taken']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if room_data["feedback"]:
            st.code(room_data["feedback"])
            
        st.markdown('<div class="game-container">', unsafe_allow_html=True)
        if current_turn_player == st.session_state.my_name:
            st.markdown('<div class="your-turn-banner">👉 It is YOUR turn to guess!</div>', unsafe_allow_html=True)
            
            with st.form(key="live_guess_form", clear_on_submit=True):
                guess = st.number_input("Guess the number (1-50):", min_value=1, max_value=50, step=1)
                submit = st.form_submit_button("Submit Guess 🎲")
                
            if submit:
                new_guesses = room_data["guesses_taken"] + 1
                
                if guess == room_data["secret_number"]:
                    room_data["scores"][st.session_state.my_name] += 1
                    room_ref.update({
                        f"scores.{st.session_state.my_name}": room_data["scores"][st.session_state.my_name],
                        "secret_number": random.randint(1, 50),
                        "guesses_taken": 0,
                        "player_index": 0,
                        "round_number": room_data["round_number"] + 1,
                        "feedback": f"🎉 {st.session_state.my_name} won Round {room_data['round_number']}! The number was {guess}."
                    })
                elif new_guesses >= room_data["max_attempts"]:
                    room_ref.update({
                        "secret_number": random.randint(1, 50),
                        "guesses_taken": 0,
                        "player_index": 0,
                        "round_number": room_data["round_number"] + 1,
                        "feedback": f"💥 Round Over! Out of attempts. The number was {room_data['secret_number']}."
                    })
                else:
                    hint = "Wrong!" if guess > room_data["secret_number"] else "Wrong!"
                    next_index = (room_data["player_index"] + 1) % len(room_data["players"])
                    
                    feedback_str = f"❌ {st.session_state.my_name} guessed {guess} — {hint}"
                    room_ref.update({
                        "guesses_taken": new_guesses,
                        "player_index": next_index,
                        "feedback": feedback_str
                    })
                st.rerun()
        else:
            waiting_msg = f"⏳ Waiting for {current_turn_player} to guess..."
            st.markdown(f'<div class="waiting-banner">{waiting_msg}</div>', unsafe_allow_html=True)
            time.sleep(3)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if st.sidebar.button("Leave Room 🏠"):
        del st.session_state.room_active
        st.rerun()
