from stockfish import Stockfish
import asyncio
import random

def evaluate_move(old_eval, new_eval):
    good_moves = ['Well Done!', 'Beast Mooooode', 'Okay Magnus', 'Youre going Kasparov Mode :O', 'ok i see u', '$wag Mone¥', 'Good Job!']
    okay_moves = ['Ight.', 'word', 'kinda mid but ok', 'dece', 'Ive seen worse', 'not bad']
    bad_moves = ['B-B-B-BLUNDERRRR', 'oh brother this guy stinks', 'get gud lmaooo', 'YEEESH', 'All Aboard the BLUNDERBUS', 'oh lord...', 'Jesus save your soul']
    loss_moves = ['RIPPP', 'gg buddy', 'aaaand you lost lmao', 'Sold the game after all that work?']
    missed_win_moves = ['you let victory slip right through your fingers like the fine sand of the Sahara', 'Im not mad Im just disappointed', 'you missed the win :(']
    if (new_eval['type'] == "cp") and (old_eval['type'] == 'cp'):
        diff = abs(float(old_eval['value']) - float(new_eval['value']))
        if diff < 30: print(random.choice(good_moves))
        elif diff < 140: print(random.choice(okay_moves))
        else: print(random.choice(bad_moves))
    if (new_eval['type'] == "mate") and (old_eval['type'] == "cp"):
        print(random.choice(loss_moves))
    if (new_eval['type'] == "cp") and (old_eval['type'] == "mate"):
        print(random.choice(missed_win_moves))
    if (new_eval['type'] == "mate") and (old_eval['type'] == "mate"):
        if abs(new_eval['value']) < abs(old_eval['value']): print(random.choice(good_moves))
        else: print(random.choice(okay_moves))

def input_to_bool(input_string):
    if (input_string == 'y') | (input_string == 'Y') | (input_string == 'Yes') | (input_string == 'yes'):
        return True
    else: return False

def main():
    stockfish = Stockfish("/usr/games/stockfish", depth=8)
    pvc = input_to_bool(input("Play vs Computer? (y/n): "))
    user_offset = 0

    if pvc:
        stockfish.set_elo_rating(int(input("Input Stockfish ELO: ")))
        user_input = input("Play as White or Black? (w/b): ")
        if (user_input == 'b') | (user_input == 'B'):
            user_offset = 1
    commentary = input_to_bool(input("Can I judge your moves? (y/n):"))
    moves = []
    colors = ["White","Black"]
    stockfish.set_position(moves)
    evalutation = stockfish.get_evaluation()
    move_num = 0
    
    while True: #Keep playing until there are no moves available
        #make a move
        print(stockfish.get_board_visual(not bool(user_offset)))
        while True:
            if (move_num%2!=user_offset) & (pvc):
                #print("Stockfish says: " + stockfish.get_best_move())
                moves.append(stockfish.get_best_move())
            else:
                moves.append(input(colors[move_num%2] + 's turn to move, please input a legal move: '))
            try:
                stockfish.set_position(moves)
                break
            except:
                print("That's not a legal move you dunce. Try again")
                moves.pop()
        new_eval = stockfish.get_evaluation()
        if commentary and not ((move_num%2!=user_offset) & (pvc)):
            evaluate_move(evalutation, new_eval)
            evalutation = new_eval
        
        if type(stockfish.get_best_move())!=type('string'):
            print('GAME OVER')
            if (new_eval['type'] == 'mate') & (move_num%2==0):
                print('WHITE WINS!!!')
            elif (new_eval['type'] == 'mate') & (move_num%2==1):
                print('BLACK WINS!!!')
            else:
                print('STALEMATE :/')
            print(stockfish.get_board_visual(not bool(user_offset)))
            return
        else:
            move_num += 1


if __name__ == "__main__":
    main()
