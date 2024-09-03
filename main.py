import random
import time
import json
import os

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

            data = get_data()

            # Play the rounds
            player_win_count, computer_win_count, round_num = game_round(
                player_win_count, computer_win_count, round_num, data, rounds
            )

            # Determine and store the final winner and points
            if player_win_count == 2:
                print("You won the game!")
                game_winner = "player"
            else:
                print("Computer won the game!") 
                game_winner = "computer"   

            update_data(game_summary, game_winner, player_win_count, computer_win_count, data, rounds)

        else:
            print("Please type (s) to start and (q) to quit.")
        
        choice = input("Start Game (s) / Quit Game (q): ").lower()

def game_round(player_win_count, computer_win_count, round_num, data, rounds):
    while player_win_count < 2 and computer_win_count < 2:
        time.sleep(1)
        print(f"Round {round_num}: Type Rock, Paper, or Scissors!")

        moves = ["Rock", "Paper", "Scissors"]
        computer_move = get_computer_move(data)

        player_move = input().capitalize()  

        # Get the updated values from the round winner function
        player_win_count, computer_win_count, round_num = get_round_winner(
            player_move, moves, computer_move, player_win_count, computer_win_count, round_num, rounds
        )

    return player_win_count, computer_win_count, round_num

def get_computer_move(data):

    user_possibilities = {
        "Rock": 0,
        "Paper": 0,
        "Scissors": 0
    }

    if data:
        user_possibilities = calculate_user_possibilities(data, user_possibilities)
        total_possibility = sum(user_possibilities.values())

        # Weighted random choice based on user behavior
        if total_possibility > 0:
            r = random.uniform(0, total_possibility)
            cumulative = 0
            for move, count in user_possibilities.items():
                cumulative += count
                if r <= cumulative:
                    return ["Scissors", "Rock", "Paper"].index(move)
    else:
        return random.randrange(0, 3)

def get_round_winner(player_move, moves, computer_move, player_win_count, computer_win_count, round_num, rounds):
    if player_move in moves:
        player_move_index = moves.index(player_move)

        time.sleep(1)
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

        time.sleep(1)
        print(f"Computer {computer_win_count} | You {player_win_count}")

        # Store the round summary
        round_summary = { 
            "winner": round_winner,
            "computer": moves[computer_move],
            "player": player_move
        }
        rounds[f"round_{round_num}"] = round_summary
        round_num += 1
    else:
        print("Invalid input, please choose Rock, Paper, or Scissors.")

    # Return the updated counts and round number
    return player_win_count, computer_win_count, round_num

def get_data():
    # Check if the file exists and load existing data
    if os.path.exists("game_history.json"):
        with open("game_history.json", "r") as infile:
            return json.load(infile)
    else:
        return {}

def update_data(game_summary, game_winner, player_win_count, computer_win_count, data, rounds):
    # Add the overall game summary
    game_summary["winner"] = game_winner
    game_summary["player_points"] = player_win_count
    game_summary["computer_points"] = computer_win_count
    game_summary["rounds"] = rounds

    # Add the new game summary to the existing data
    game_id = f"game_{len(data) + 1}"  # Assign a new game ID
    data[game_id] = game_summary

    # Write the updated data back to the JSON file
    with open("game_history.json", "w") as outfile:
        json.dump(data, outfile, indent=4)

def calculate_user_possibilities(data, user_possibilities):
    for games in data:
        for game_data in data[games]:
            if game_data == "rounds":
                for rounds in data[games][game_data]:
                    move = data[games][game_data][rounds]["player"]
                    if move in user_possibilities:
                        user_possibilities[move] += 1
    return user_possibilities

start_game()
