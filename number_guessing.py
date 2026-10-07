import streamlit as st
import random
import time
from google.cloud import firestore
from google.oauth2 import service_account

# Configure mobile viewport settings
st.set_page_config(page_title="Number Guessing Game", page_icon="🎮", layout="centered")

# 1. Connect safely to the central cloud storage database
@st.cache_resource
def get_db():
    try:
        # Load the configuration keys from your local folder file
        creds = service_account.Credentials.from_service_account_file("firebase_credentials.json")
        return firestore.Client(credentials=creds)
    except Exception as e:
        st.error("Missing firebase_credentials.json file in your folder structure.")
        return None

db = get_db()

# Your updated official title
st.title("🏆 Number Guessing Game Online")

# --- INITIAL SETUP SCREEN ---
if "room_active" not in st.session_state:
    st.subheader("🏠 Multi-Device Matchmaking Room")
    
    room_code = st.text_input("Enter 4-Digit Room Code (e.g., A7B9):", value="1234").upper().strip()
    my_name = st.text_input("Your Player Name:", value="Player").strip()
    
    choice = st.radio("Choose Action:", ["Create New Game Room (Host)", "Join Existing Game Room"])
    
    if st.button("Connect to Lobby 🚀", type="primary"):
        if not room_code or not my_name:
            st.warning("Please fill in both fields.")
        else:
            room_ref = db.collection("guessing_rooms").document(room_code)
            room_data = room_ref.get()
            
            if choice == "Create New Game Room (Host)":
                # Host initializes the room. Range changed to 1 - 50.
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
                # The Joiner checks the lobby restrictions
                if room_data.exists:
                    data = room_data.to_dict()
                    
                    # 6 Players Max Enforcement Rule
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

    # Display game settings and current active players
    st.sidebar.markdown(f"### 📍 Room Code: **{st.session_state.room_code}**")
    st.sidebar.markdown(f"**Your Profile Name:** {st.session_state.my_name}")
    st.sidebar.write(f"Connected Players ({len(room_data['players'])}/6):", ", ".join(room_data["players"]))
    
    if room_data["status"] == "lobby":
        st.info("⌛ Waiting for the Host to lock the room and start the match...")
        
        # Only allow the creator/host to click the start game trigger
        if room_data["players"][0] == st.session_state.my_name:
            if st.button("Lock Room & Start Game 🎮", type="primary"):
                room_ref.update({"status": "playing"})
                st.rerun()
        
        time.sleep(2)
        st.rerun()
        
    else:
        current_turn_player = room_data["players"][room_data["player_index"]]
        st.subheader(f"✨ Round {room_data['round_number']}")
        
        # Real-time leaderboard across devices
        cols = st.columns(len(room_data["players"]))
        for idx, name in enumerate(room_data["players"]):
            cols[idx].metric(label=name, value=f"{room_data['scores'].get(name, 0)} wins")
            
        st.write(f"📊 Attempts remaining in round: {room_data['max_attempts'] - room_data['guesses_taken']}")
        st.divider()
        
        if room_data["feedback"]:
            st.code(room_data["feedback"])
            
        # Isolate interface interactions based on turn index rules
        if current_turn_player == st.session_state.my_name:
            st.success("👉 **It is YOUR turn to guess!**")
            
            with st.form(key="live_guess_form", clear_on_submit=True):
                # Target range modified to 50 parameters maximum limits
                guess = st.number_input("Guess the number (1-50):", min_value=1, max_value=50, step=1)
                submit = st.form_submit_button("Submit Guess 🎲")
                
            if submit:
                new_guesses = room_data["guesses_taken"] + 1
                
                # Win Condition Match
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
                # Out of Attempts / Lose Condition Match
                elif new_guesses >= room_data["max_attempts"]:
                    room_ref.update({
                        "secret_number": random.randint(1, 50),
                        "guesses_taken": 0,
                        "player_index": 0,
                        "round_number": room_data["round_number"] + 1,
                        "feedback": f"💥 Round Over! Out of attempts. The number was {room_data['secret_number']}."
                    })
                # High / Low Direction Hints
                else:
                    hint = "Too High!" if guess > room_data["secret_number"] else "Too Low!"
                    next_index = (room_data["player_index"] + 1) % len(room_data["players"])
                    room_ref.update({
                        "guesses_taken": new_guesses,
                        "player_index": next_index,
                        "feedback": f"❌ {st.session_state.my_name} guessed {guess} — {hint}"
                    })
                st.rerun()
        else:
            st.warning(f"⏳ Waiting for **{current_turn_player}** to guess...")
            time.sleep(3)
            st.rerun()

    if st.sidebar.button("Leave Room 🏠"):
        del st.session_state.room_active
        st.rerun()
