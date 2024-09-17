import spidev
import time
import RPi.GPIO as GPIO
import numpy as np

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 1350000

#choose GPIO pins to use
pins = [17, 27, 22, 23]
sensor_mapping = [0,8,2,10,4,12,6,14,15,7,13,5,11,3,9,1]
threshold = 0.1

GPIO.setmode(GPIO.BCM)
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

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

try:

    while True:
        sensor_readings = np.zeros((8,2))
        for i in range(16):
            s = sensor_mapping[i]
            pin_values = binary(s)
            for p, pin in enumerate(pins):
                if pin_values[p]: GPIO.output(pin, GPIO.HIGH)
                else: GPIO.output(pin, GPIO.LOW)
            time.sleep(0.01)
            value = convert_to_voltage(read_adc(0))
            sensor_readings[i%8, int(i/8)] = (value > 2.5+threshold) - (value < 2.5-threshold)
        print(sensor_readings)
        time.sleep(2)
        # adc_value = read_adc(0)  # Read from channel 0
        # voltage = convert_to_voltage(adc_value)
        # print(f"ADC Value: {adc_value}, Voltage: {voltage:.2f}V")
        # time.sleep(1)
except KeyboardInterrupt:
    print("Exiting program")
finally:
    GPIO.cleanup()
    # for pin in pins:
    #     cleanup_gpio(pin)