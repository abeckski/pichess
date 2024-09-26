#!/usr/bin/env python3
import LCD2004
import time

def setup():
	LCD2004.init(0x27, 1)	# init(slave address, background light)
	LCD2004.write(4, 0, 'Blacks Turn')
	# LCD2004.write(0, 1, 'IIC/I2C LCD2004')
	# LCD2004.write(0, 2, '20 cols, 4 rows')
	LCD2004.write(0, 3, '<-- press when done')
	time.sleep(2)

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

def destroy():
	LCD2004.clear()

if __name__ == "__main__":
	try:
		LCD2004.init(0x27, 1)	# init(slave address, background light)
		while True:
			LCD2004.clear()
			message = input("Message?: ")
			row = int(input("Row?: "))
			lcd_display(message, row)
			input("press Enter to clear")
	except KeyboardInterrupt:
		destroy()