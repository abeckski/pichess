import RPi.GPIO as GPIO
import time

#Setup GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)
GPIO.setup(6, GPIO.IN)

pin = int(input("which pin? (5 or 6): "))

try:
    while True:
         print(GPIO.input(pin))
         time.sleep(0.25)

except KeyboardInterrupt:
        print("Exiting program")
finally:
    GPIO.cleanup()
