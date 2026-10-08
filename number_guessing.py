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

# 1. Connect safely to the central cloud storage database
@st.cache_resource
def get_db():
    try:
        # Load the configuration keys from your local folder file
        creds = service_account.Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"])
        )
        return firestore.Client(credentials=creds, project=creds.project_id)
    except Exception as e:
        st.error(f"Firebase error: {e}")
        return None
db = get_db()

st.title("🏆 Live Number Guessing Game")

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
                # The Host initializes the shared memory state parameters
                secret = random.randint(1, 50)
                room_ref.set({
                    "players": [my_name],
                    "scores": {my_name: 0},
                    "secret_number": secret,
                    "guesses_taken": 0,
                    "max_attempts": 6, # Will scale when players join
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
                # The Joiner attaches their profile to the existing database keys
                if room_data.exists:
                    data = room_data.to_dict()
                    if my_name in data["players"]:
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

    # Sidebar details
    st.sidebar.markdown(f"### 📍 Room Code: **{st.session_state.room_code}**")
    st.sidebar.markdown(f"**Your Profile Name:** {st.session_state.my_name}")
    latest_room_data = room_ref.get().to_dict()
    st.sidebar.write("Connected Players:", ", ".join(room_data["players"]))
    
    if st.sidebar.button("Leave Room 🏠"):
        del st.session_state.room_active
        st.rerun()

    # --- REAL-TIME GAME INTERFACE CONTAINER ---
    # We wrap the entire status and turn view inside ONE fragment function.
    # This ensures only this container redraws every 3 seconds, leaving buttons fully clickable.

    @st.fragment(run_every=3)
    def render_game_lobby():
        # Pull fresh server data from Firestore
        live_data = room_ref.get().to_dict()

        if not live_data:
            st.stop()

        st.write("DEBUG PLAYERS:", live_data["players"])
        st.write("DEBUG STATUS:", live_data["status"])
        st.write("DEBUG MY NAME:", st.session_state.my_name)

        # -----------------------------
        # LOBBY
        # -----------------------------
        if live_data["status"] == "lobby":

            st.info("⌛ Waiting for the Host to lock the room and start the match...")

            # Only the host can start the game
            if live_data["players"][0] == st.session_state.my_name:

                if st.button("Lock Room & Start Game 🎮", type="primary"):
                    room_ref.update({"status": "playing"})
                    st.rerun()

        # -----------------------------
        # GAME
        # -----------------------------
        elif live_data["status"] == "playing":

            st.subheader(f"🎮 Round {live_data['round_number']}")

            st.write(f"Players: {', '.join(live_data['players'])}")

            st.divider()

            current_player = live_data["players"][live_data["player_index"]]

            if current_player == st.session_state.my_name:

                st.success("🎯 It is your turn!")

                st.write("Guess a number between **1 and 50**.")

                guess = st.number_input(
                    "Your Guess",
                    min_value=1,
                    max_value=50,
                    step=1,
                    key="current_guess"
                )

                if st.button("Submit Guess 🎯", type="primary"):

                    secret_number = live_data["secret_number"]

                    if guess == secret_number:

                        st.success("🎉 Correct! You guessed the number!")

                        room_ref.update({
                            "feedback": f"{st.session_state.my_name} guessed the number correctly!",
                            "status": "finished"
                        })

                        st.rerun()

                    elif guess < secret_number:

                        st.info("📈 Too low!")

                        room_ref.update({
                            "feedback": f"{st.session_state.my_name} guessed too low.",
                            "guesses_taken": live_data["guesses_taken"] + 1
                        })

                        st.rerun()

                    else:

                        st.info("📉 Too high!")

                        room_ref.update({
                            "feedback": f"{st.session_state.my_name} guessed too high.",
                            "guesses_taken": live_data["guesses_taken"] + 1
                        })

                        st.rerun()

            else:

                st.warning(
                    f"⏳ Waiting for **{current_player}** to make their guess..."
                )

            # Display latest game feedback
            if live_data.get("feedback"):
                st.info(f"💬 {live_data['feedback']}")

        # -----------------------------
        # GAME FINISHED
        # -----------------------------
        elif live_data["status"] == "finished":

            st.subheader("🏆 Game Finished!")

            st.success(live_data.get("feedback", "The game has ended."))

            st.write("### Scores")

            for player, score in live_data["scores"].items():
                st.write(f"**{player}:** {score}")

    # Execute the fragment container safely
    render_game_lobby()