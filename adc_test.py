import spidev
import time

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

try:
    while True:
        adc_value = read_adc(0)  # Read from channel 0
        voltage = convert_to_voltage(adc_value)
        print(f"ADC Value: {adc_value}, Voltage: {voltage:.2f}V")
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting program")
finally:
    spi.close()