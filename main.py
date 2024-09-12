import random
import time
import json
import os
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

winner_list = {
    "computer": -1,
    "draw": 0,
    "player": 1
}

def one_hot_encode_move(move_index):
    encoding = [0, 0, 0]
    encoding[move_index] = 1
    return encoding

# Function to load data
def get_data():
    if os.path.exists("game_history.json"):
        with open("game_history.json", "r") as infile:
            return json.load(infile)
    else:
        return {}

# Process data into feature matrix and target vector
def process_data(data):
    player_moves = []
    computer_moves = []
    winners = []

    for games in data:
        for game_data in data[games]:
            if game_data == "rounds":
                for rounds in data[games][game_data]:
                    round_data = data[games][game_data][rounds]
                    player_move_encoded = round_data["player_move_encoded"]
                    computer_move_encoded = round_data["computer_move_encoded"]
                    winner = round_data["winner"]

                    player_moves.append(player_move_encoded)
                    computer_moves.append(computer_move_encoded)
                    winners.append(winner)

    X = np.array([p + c for p, c in zip(player_moves, computer_moves)])
    y = np.array(winners)
    return X, y

# Function to train or retrain the model
def train_model():
    data = get_data()
    X, y = process_data(data)
    
    if len(y) < 6:
        print("Less than 6 rounds in history. Switching to random mode.")
        return None

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)
    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy}")

    return model

# Function to predict the next move
def predict_next_move(model, player_move_encoded):
    if model:
        last_computer_move = random.randint(0, 2) 
        X_last_move = np.array(player_move_encoded + one_hot_encode_move(last_computer_move)).reshape(1, -1)
        predicted_outcome = model.predict(X_last_move)

        # Counter the predicted outcome (rock->paper, paper->scissors, scissors->rock)
        counter_move = (predicted_outcome[0] + 1) % 3
        return counter_move
    else:
        return random.randint(0, 2)

# Update the game data after each round
def update_data(game_summary, data, rounds):
    game_summary["rounds"] = {}

    for round_num, round_data in rounds.items():
        player_move_encoded = one_hot_encode_move(round_data["player"])
        computer_move_encoded = one_hot_encode_move(round_data["computer"])

        game_summary["rounds"][round_num] = {
            "winner": round_data["winner"],
            "player_move_encoded": player_move_encoded,
            "computer_move_encoded": computer_move_encoded
        }

    game_id = f"game_{len(data) + 1}"
    data[game_id] = game_summary

    with open("game_history.json", "w") as outfile:
        json.dump(data, outfile, indent=4)

# Start and manage the game loop
def start_game():
    print("This is an AI-powered Rock, Paper, Scissors game.")
    time.sleep(1)
    choice = input("Start Game (s) / Quit Game (q): ").lower()
    
    main(choice)
    
    print("Thanks for playing!")

def main(choice):
    while choice != 'q':  
        if choice == 's':
            player_win_count = 0
            computer_win_count = 0
            round_num = 1
            game_summary = {}
            rounds = {}

            time.sleep(1)
            print("Best of three wins!")

            model = train_model()

            player_win_count, computer_win_count, round_num = game_round(
                player_win_count, computer_win_count, round_num, model, rounds
            )

            if player_win_count == 2:
                print("You won the game!")
            else:
                print("Computer won the game!") 

            data = get_data()
            update_data(game_summary, data, rounds)
        else:
            print("Please type (s) to start and (q) to quit.")
        
        choice = input("Start Game (s) / Quit Game (q): ").lower()

def game_round(player_win_count, computer_win_count, round_num, model, rounds):
    while player_win_count < 2 and computer_win_count < 2:
        time.sleep(1)
        print(f"Round {round_num}: Type Rock, Paper, or Scissors!")

        moves = ["Rock", "Paper", "Scissors"]
        player_move = input().capitalize()

        if player_move in moves:
            player_move_index = moves.index(player_move)
            player_move_encoded = one_hot_encode_move(player_move_index)
            
            computer_move = predict_next_move(model, player_move_encoded)
            print(f"Computer chose {moves[computer_move]}.")

            if player_move_index == computer_move:
                print("It's a Draw!")
                round_winner = "draw"
            elif (player_move_index == 0 and computer_move == 2) or \
                (player_move_index == 1 and computer_move == 0) or \
                (player_move_index == 2 and computer_move == 1):
                print("You win this round!")
                player_win_count += 1
                round_winner = "player"
            else:
                computer_win_count += 1
                print("Computer wins this round!")
                round_winner = "computer"

            rounds[f"round_{round_num}"] = { 
                "winner": winner_list[round_winner],
                "computer": computer_move,
                "player": player_move_index
            }

            round_num += 1
        else:
            print("Invalid input, please choose Rock, Paper, or Scissors.")

    return player_win_count, computer_win_count, round_num

start_game()
