import spidev
import time
import numpy as np

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 1350000

def read_adc(channel):
    if channel < 0 or channel > 7:
        raise ValueError("ADC channel must be between 0 and 7")
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def convert_to_voltage(adc_value, vref=3.3):
    return (adc_value / 1023.0) * vref

def main():
    j = input("Which ADC input?")
    while True:
        print(convert_to_voltage(read_adc(j)))
        time.sleep(0.25)