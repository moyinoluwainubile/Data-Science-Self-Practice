import random       # 1. This line imports the random module, which allows us to generate random numbers.

def play_round(round_number, players_list):
    print(f"\n=======================")
    print(f"      ROUND {round_number}      ")
    print(f"=======================")

    secret = random.randint(1, 30)  # 2. This line generates a random integer between 1 and 30 (inclusive) and assigns it to the variable 'secret'. This
    guesses_taken = 0

    # Scale max attempts so each player gets exactly 3 turns
    turns_per_player = 3
    max_attempts = len(players_list) * turns_per_player  

    player_index = 0  # 3. This variable keeps track of the current player. It starts at 0, which corresponds to "Player 1".

    while guesses_taken < max_attempts:
        current_player = players_list[player_index]

        print(f"\n--- {current_player}'s Turn ---")
        guess = int(input(f"{current_player}, Guess the secret number between 1 and 30: "))
        guesses_taken += 1

        if guess == secret:
            print(f"Correct! {current_player} wins this round! 🎉")
            print(f"You guessed the secret number in {guesses_taken} attempts.")
            return current_player  # 4. This line returns the name of the player who guessed the secret number correctly, indicating that they won the round.
        
        elif guess > secret:
            if guesses_taken < max_attempts:
                print("Too high! Passing to the next player...")
            else:
                print(f"Too high! {current_player} is out of attempts.")
        else:
            if guesses_taken < max_attempts:
                print("Too low! Passing to the next player...")
            else:
                print(f"Too low! {current_player} is out of attempts.")

        # Rotates smoothly through 2, 3, 4, or more players
        player_index = (player_index + 1) % len(players_list)
    else:
        print(f"\nRound Over! Everyone ran out of attempts. The secret number was {secret}.")
        return None  # 3. This line returns None, indicating that the round ended without a winner.

# --- Main Game Setup ---
print("🏆 WELCOME TO THE NUMBER GUESSING GAME 🏆\n")

# 1. Determine number of players dynamically
num_players = int(input("How many players want to play? "))
players = []
scores = {}

# 2. Collect names and initialize the scoreboard dictionary
for i in range(num_players):
    name = input(f"Enter name for Player {i + 1}: ").strip()
    # Fallback to default name if left blank
    if not name:
        name = f"Player {i + 1}"
    players.append(name)
    scores[name] = 0

current_round = 1

# --- Main Game Loop Control ---
while True:
    winner = play_round(current_round, players)
    
    # 3. Update scores using the player name keys
    if winner in scores:
        scores[winner] += 1
        
    print("\n🏆 CURRENT LEADERBOARD:")
    for player, score in scores.items():
        print(f" {player}: {score} victories")
    
    play_again = input("\nDo you want to play another round? (yes/no): ").strip().lower()
    if play_again != "yes" and play_again != "y":
        print("\nThanks for playing! FINAL SCORE:")
        for player, score in scores.items():
            print(f" {player}: {score} victories")
        print("Goodbye!")
        break
        
    current_round += 1