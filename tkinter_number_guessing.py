import tkinter as tk
from tkinter import messagebox
import random

class GuessingGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.geometry("400x550")
        
        # Game State Variables
        self.players = []
        self.scores = {}
        self.current_round = 1
        self.guesses_taken = 0
        self.max_attempts = 0
        self.player_index = 0
        self.secret_number = 0
        
        # Build the initial Setup Screen
        self.setup_frame = tk.Frame(root)
        self.setup_frame.pack(pady=20)
        
        tk.Label(self.setup_frame, text="🏆 NUMBER GUESSING GAME 🏆", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.setup_frame, text="How many players? (2-5):", font=("Arial", 11)).pack(pady=5)
        
        self.num_players_entry = tk.Entry(self.setup_frame, font=("Arial", 11), width=10)
        self.num_players_entry.pack(pady=5)
        self.num_players_entry.insert(0, "2") # Default value
        
        tk.Button(self.setup_frame, text="Next: Enter Names", command=self.create_name_fields, bg="blue", fg="white", font=("Arial", 10, "bold")).pack(pady=15)
        
        # Frames for later phases
        self.names_frame = tk.Frame(root)
        self.game_frame = tk.Frame(root)
        self.name_entries = []

    def create_name_fields(self):
        try:
            count = int(self.num_players_entry.get())
            if not (2 <= count <= 5):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of players between 2 and 5.")
            return
            
        self.setup_frame.pack_forget() # Hide setup screen
        self.names_frame.pack(pady=20)
        
        tk.Label(self.names_frame, text="Enter Player Names", font=("Arial", 12, "bold")).pack(pady=10)
        
        for i in range(count):
            tk.Label(self.names_frame, text=f"Player {i+1} Name:", font=("Arial", 10)).pack(pady=2)
            entry = tk.Entry(self.names_frame, font=("Arial", 10), width=25)
            entry.pack(pady=2)
            entry.insert(0, f"Player {i+1}")
            self.name_entries.append(entry)
            
        tk.Button(self.names_frame, text="Start Game 🎮", command=self.initialize_game, bg="green", fg="white", font=("Arial", 11, "bold")).pack(pady=20)

    def initialize_game(self):
        for i, entry in enumerate(self.name_entries):
            name = entry.value = entry.get().strip()
            if not name:
                name = f"Player {i+1}"
            self.players.append(name)
            self.scores[name] = 0
            
        self.names_frame.pack_forget() # Hide name entry screen
        self.game_frame.pack(pady=15, fill="both", expand=True)
        self.start_new_round()

    def start_new_round(self):
        self.secret_number = random.randint(0, 30)
        self.guesses_taken = 0
        self.player_index = 0
        self.max_attempts = len(self.players) * 3 # 3 turns per player
        
        # Re-build UI for the current round
        for widget in self.game_frame.winfo_children():
            widget.destroy()
            
        self.round_label = tk.Label(self.game_frame, text=f"--- ROUND {self.current_round} ---", font=("Arial", 14, "bold"), fg="purple")
        self.round_label.pack(pady=5)
        
        # Scoreboard
        score_text = " | ".join([f"{p}: {self.scores[p]}" for p in self.players])
        self.score_label = tk.Label(self.game_frame, text=f"Scores: {score_text}", font=("Arial", 10, "italic"))
        self.score_label.pack(pady=5)
        
        self.turn_label = tk.Label(self.game_frame, text=f"{self.players[self.player_index]}'s Turn", font=("Arial", 12, "bold"), fg="blue")
        self.turn_label.pack(pady=10)
        
        tk.Label(self.game_frame, text="Guess a number between 0 and 30:", font=("Arial", 11)).pack(pady=5)
        self.guess_entry = tk.Entry(self.game_frame, font=("Arial", 12), width=10, justify="center")
        self.guess_entry.pack(pady=5)
        
        tk.Button(self.game_frame, text="Submit Guess", command=self.process_guess, bg="orange", font=("Arial", 11, "bold")).pack(pady=10)
        
        self.feedback_label = tk.Label(self.game_frame, text="", font=("Arial", 11, "bold"))
        self.feedback_label.pack(pady=15)

    def process_guess(self):
        try:
            guess = int(self.guess_entry.get())
        except ValueError:
            messagebox.showwarning("Warning", "Please type a valid whole number.")
            return
            
        self.guesses_taken += 1
        current_player = self.players[self.player_index]
        
        if guess == self.secret_number:
            self.scores[current_player] += 1
            messagebox.showinfo("Round Over", f"🎉 Correct! {current_player} wins this round!\nIt took {self.guesses_taken} total guesses.")
            self.ask_next_round()
            return
            
        # Determine remaining attempts
        remaining = self.max_attempts - self.guesses_taken
        
        if remaining <= 0:
            messagebox.showinfo("Round Over", f"Game Over! Everyone ran out of attempts.\nThe secret number was {self.secret_number}.")
            self.ask_next_round()
            return
            
        # Provide relative high/low direction feedback
        if guess > self.secret_number:
            msg = "Wrong! Passing to next player..."
        else:
            msg = "Wrong! Passing to next player..."
            
        self.feedback_label.config(text=msg, fg="red")
        self.guess_entry.delete(0, tk.END)
        
        # Switch to the next active player configuration profile smoothly
        self.player_index = (self.player_index + 1) % len(self.players)
        self.turn_label.config(text=f"{self.players[self.player_index]}'s Turn")

    def ask_next_round(self):
        if messagebox.askyesno("Continue?", "Do you want to play another round?"):
            self.current_round += 1
            self.start_new_round()
        else:
            final_scores = "\n".join([f"{p}: {self.scores[p]} wins" for p in self.players])
            messagebox.showinfo("Final Results", f"Thanks for playing!\n\nFinal Standings:\n{final_scores}")
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = GuessingGameApp(root)
    root.mainloop()
