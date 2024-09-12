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

GPIO.setmode(GPIO.BCM)
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

# def setup_gpio(pin):
#     """Export and set GPIO pin direction."""
#     with open("/sys/class/gpio/export", "w") as f:
#         f.write(str(pin))
#     with open(f"/sys/class/gpio/gpio{pin}/direction", "w") as f:
#         f.write("out")

# def set_gpio_value(pin, value):
#     """Set GPIO pin to high (1) or low (0)."""
#     with open(f"/sys/class/gpio/gpio{pin}/value", "w") as f:
#         f.write(str(value))

# def cleanup_gpio(pin):
#     """Unexport GPIO pin."""
#     with open("/sys/class/gpio/unexport", "w") as f:
#         f.write(str(pin))

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
            pin_values = binary(i)
            for p, pin in enumerate(pins):
                if pin_values[p]: GPIO.output(pin, GPIO.HIGH)
                else: GPIO.output(pin, GPIO.LOW)
            time.sleep(0.1)
            sensor_readings[i%8, int(i/8)] = convert_to_voltage(read_adc(0))
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