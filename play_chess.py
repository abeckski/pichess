from stockfish import Stockfish
import asyncio
import random
import spidev
import numpy as np
import RPi.GPIO as GPIO
import time

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 1350000

# Set GPIO output pins
#choose GPIO pins to use
pins = [17, 27, 22, 23]
sensor_mapping = [0,8,2,10,4,12,6,14,15,7,13,5,11,3,9,1]
letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
threshold = 0.1 #Volts

#Setup GPIO pins
GPIO.setmode(GPIO.BCM)
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

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

def binary(input):
    return [int(input/8), int((input%8)/4), int((input%4)/2), int(input%2)]

def read_adc(channel):
    if channel < 0 or channel > 7:
        raise ValueError("ADC channel must be between 0 and 7")
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def convert_to_voltage(adc_value, vref=3.3):
    return (adc_value / 1023.0) * vref

def find_current_position():
    position = np.zeros([8,8])
    
    # Set the GPIO pins to choose the multiplexer input
    for i in range(16):
        pin_values = binary(i)
        for p, pin in enumerate(pins):
            if pin_values[p]:
                GPIO.output(pin, GPIO.HIGH)
            else: GPIO.output(pin, GPIO.LOW)
    
        time.sleep(0.1)
        for j in range(4):
            value = convert_to_voltage(read_adc(j))
            position[i%8, int(i/8) + j*2] = (value > 2.5+threshold) - (value < 2.5-threshold)

    return position

def find_move(old_position):
    new_position = find_current_position()
    diff = old_position - new_position
    if abs(diff).sum() == 0:
        print("Try moving a piece next time...")
    

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

    # Use BCM numbering (the Broadcom SoC channel numbering)
    GPIO.setmode(GPIO.BCM)
    for i in range(4):
        GPIO.setup(pins[i], GPIO.OUT)
    
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
