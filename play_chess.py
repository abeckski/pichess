from stockfish import Stockfish
import asyncio
import random
import spidev
import numpy as np
import RPi.GPIO as GPIO
import time
import LCD2004

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 1350000

# Set GPIO output pins
pins = [17, 27, 22, 23]
sensor_mapping = [0,8,4,12,2,10,6,14,15,7,11,3,13,5,9,1]
letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
threshold = 0.2 #Volts

#Setup GPIO pins
GPIO.setmode(GPIO.BCM)
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
GPIO.setup(5, GPIO.IN)
GPIO.setup(6, GPIO.IN)

# Initialize LCD
LCD2004.init(0x27, 1)	# init(slave address, background light)

# Start a stockfish instance
stockfish = Stockfish("/usr/games/stockfish", depth=8)

starting_position = np.array([[-1,-1,-1,-1,-1,-1,-1,-1],
                             [-1,-1,-1,-1,-1,-1,-1,-1],
                             [ 0, 0, 0, 0, 0, 0, 0, 0],
                             [ 0, 0, 0, 0, 0, 0, 0, 0],
                             [ 0, 0, 0, 0, 0, 0, 0, 0],
                             [ 0, 0, 0, 0, 0, 0, 0, 0],
                             [ 1, 1, 1, 1, 1, 1, 1, 1],
                             [ 1, 1, 1, 1, 1, 1, 1, 1]])
user_indicators = ["Press when finished with move        -->", "<-- Press when done with move"]
indicators = ["                -->", "<--                "]

def button_press():
    while True:
        if GPIO.input(5):
            return 0
        elif GPIO.input(6):
            return 1
        time.sleep(0.1)

def lcd_display(message, row=0):
    if type(message) is not type('e'): 
        print('Wrong data type for LCD display :(')
        return
    i = 0
    while i < int(len(message)/20):
        LCD2004.write(0, i+row, message[i*20:(i+1)*20])
        i += 1
    len_remaining = len(message) - i*20
    if len_remaining > 0:
        LCD2004.write(int((20-len_remaining)/2), i+row, message[i*20:])

def evaluate_move(old_eval, new_eval):
    '''Print a roast or a compliment depending on how stockfish likes your move'''
    good_moves = ['Well Done!', 'Beast Mooooode', 'Okay Magnus', 'Youre going Kasparov Mode :O', 'ok i see u', '$wag Mone¥', 'Good Job!']
    okay_moves = ['Ight.', 'word', 'kinda mid but ok', 'dece', 'Ive seen worse', 'not bad']
    bad_moves = ['B-B-B-BLUNDERRRR', 'oh brother this guy stinks', 'get gud lmaooo', 'YEEESH', 'All Aboard the      BLUNDERBUS', 'oh lord...', 'Jesus save your soul']
    loss_moves = ['RIPPP', 'gg buddy', 'aaaand you lost lmao', 'Sold the game after all that work?']
    missed_win_moves = ['you let victory slipthrough your fingerslike the fine sand  of the Sahara', 'Im not mad Im just  disappointed', 'you missed the win  :(']
    if (new_eval['type'] == "cp") and (old_eval['type'] == 'cp'):
        diff = abs(float(old_eval['value']) - float(new_eval['value']))
        if diff < 30: lcd_display(random.choice(good_moves))
        elif diff < 140: lcd_display(random.choice(okay_moves))
        else: lcd_display(random.choice(bad_moves))
    if (new_eval['type'] == "mate") and (old_eval['type'] == "cp"):
        lcd_display(random.choice(loss_moves))
    if (new_eval['type'] == "cp") and (old_eval['type'] == "mate"):
        lcd_display(random.choice(missed_win_moves))
    if (new_eval['type'] == "mate") and (old_eval['type'] == "mate"):
        if abs(new_eval['value']) < abs(old_eval['value']): lcd_display(random.choice(good_moves))
        else: lcd_display(random.choice(okay_moves))

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
    '''Sweep the hall sensors to find the current location of each white and black piece'''
    position = np.zeros([8,8])
    
    # Set the GPIO pins to choose the multiplexer input
    for i in range(16):
        pin_values = binary(sensor_mapping[i])
        for p, pin in enumerate(pins):
            if pin_values[p]:
                GPIO.output(pin, GPIO.HIGH)
            else: GPIO.output(pin, GPIO.LOW)
    
        time.sleep(0.01)
        for j in range(4):
            value = convert_to_voltage(read_adc(j))
            position[i%8, int(i/8) + j*2] = (value > 2.5+threshold) - (value < 2.5-threshold)

    return position

def find_move(old_position):
    '''Determine the only legal move based on the current and previous position'''
    new_position = find_current_position()
    if np.array_equal(new_position, starting_position):
        return 'restart', new_position
    
    # Find the squares which have changed state since the last move
    diff = old_position - new_position
    # Castling totally breaks my system for finding moves so check for that first 
    if sum(sum(abs(diff))) > 3: # Castling causes more squares to change state than any other move
        if stockfish.is_move_correct('e1g1'): return 'e1g1', new_position
        elif stockfish.is_move_correct('e1c1'): return 'e1c1', new_position
        elif stockfish.is_move_correct('e8g8'): return 'e8g8', new_position
        elif stockfish.is_move_correct('e8c8'): return 'e8c8', new_position
        else: return 'toomany', None #return toomany to indicate that too many pieces have moved and something is wrong
    
    r, c = np.nonzero(diff) # indices of all the squares which have changed state
    zi = [] #zero indices
    for i in range(len(r)):
        if new_position[r[i], c[i]] == 0:
            zi.append(i)
    # This would be one line of code if it weren't for en passant...
    if sum(sum(abs(diff))) == 3: # If 3 squares changes, check for en passant
        # Crazy logic statement, if true then the move CANNOT be en passant and must be illegal
        if len(zi)!=2 or (r[zi[0]] != r[zi[1]]) or ((r[zi[0]] != 3) and (r[zi[0]] != 4)):
            return 'toomany', None 
    for i in range(len(c)):
        if new_position[r[i], c[i]] == 0:
            for j in range(len(c)):
                if new_position[r[j], c[j]] != 0:
                    move = letters[c[i]]+str(8-r[i])+letters[c[j]]+str(8-r[j])
                    if stockfish.is_move_correct(move):
                        return move, new_position
                    if stockfish.is_move_correct(move+'q'):
                        return move+'q', new_position
    return None, None

def chess_game(skill_level, pvc, commentary, user_offset):
    '''Play a game of chess, return when finished'''
    moves = []
    colors = ["White","Black"]
    stockfish.set_position(moves)
    evalutation = stockfish.get_evaluation()
    move_num = 0
    position = starting_position
    stockfish.set_skill_level(3*skill_level)
    lcd_display(colors[0] + 's Turn!')
    lcd_display(user_indicators[0], 2)
    
    while True: #Keep playing until there are no moves available
        #Display the computer's choice move if necessary
        if (move_num%2!=user_offset) & (pvc):
            row = 2 if move_num > 3 else 0
            lcd_display("Computer says:  " + random.choice(stockfish.get_top_moves(6 - skill_level))['Move'], row)

        while True: # Keep trying until User makes a legal move
                
            ### WAIT FOR BUTTON PRESS ###
            while move_num%2 != button_press():
                time.sleep(0.1)

            move, new_position = find_move(position)
            if move is not None:
                if move == 'restart':
                    return #End the game if the user sets pieces back to starting position
                if move == 'toomany': 
                    lcd_display('Somethings up, too  many pieces moved.  Try again')
                    continue
                moves.append(move)
                stockfish.set_position(moves)
                position = new_position
                break
            
            else:
                lcd_display("That's not a legal  move you dunce.     Try again")
        
        LCD2004.clear()
        # Check if the game is over
        if type(stockfish.get_best_move())!=type('string'):
            lcd_display('GAME OVER')
            if (new_eval['type'] == 'mate') & (move_num%2==0):
                lcd_display('WHITE WINS!!!', 2)
            elif (new_eval['type'] == 'mate') & (move_num%2==1):
                lcd_display('BLACK WINS!!!', 2)
            else:
                lcd_display('STALEMATE :/', 2)
            time.sleep(5)
            return
        else:
            move_num += 1

        # Reset the LCD display either with an evaluation of the previous move, or an indication
        # of whose turn it is
        if move_num < 4:
            lcd_display(user_indicators[move_num%2], 2)
        else: lcd_display(indicators[move_num%2], 3)
        new_eval = stockfish.get_evaluation()
        if commentary and not ((move_num%2==user_offset) & (pvc)) and move_num>3: #crazy logic statement lol
            evaluate_move(evalutation, new_eval)
        else:
            lcd_display(colors[move_num%2] + 's Turn!')
        evalutation = new_eval
        


def main():
    try:
        while True:
            LCD2004.clear()
            lcd_display("Welcome to Pichess!!")
            lcd_display("Play vs Computer?", 1)
            lcd_display("<-- Yes      No -->", 2)
            pvc = button_press() #Player vs Computer Boolean
            LCD2004.clear()
            user_offset = 0
            skill_level = 0

            if pvc:
                lcd_display("A Good or a Bad     Computer?")
                lcd_display("<-- Good     Bad -->", 2)
                if button_press():
                    LCD2004.clear()
                    lcd_display("How Good?")
                    lcd_display("<-- Expert  Hard -->", 2)
                    if button_press():
                        skill_level = 5
                    else: skill_level = 3
                else:
                    LCD2004.clear()
                    lcd_display("How Bad?")
                    lcd_display("<-- Intermediate            Beginner -->", 2)
                    if button_press():
                        skill_level = 1
                    else: skill_level = 0
                LCD2004.clear()
                lcd_display("Play as White or    Black?")
                lcd_display("<-- Black  White -->", 2)
                user_offset = button_press()

            LCD2004.clear()
            lcd_display("Can I judge your    moves??")
            lcd_display("<-- Yes      No -->", 2)
            commentary = button_press()
            LCD2004.clear()

            chess_game(skill_level, pvc, commentary, user_offset)
        
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        GPIO.cleanup()
        LCD2004.clear()


if __name__ == "__main__":
    main()
