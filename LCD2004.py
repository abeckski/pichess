#!/usr/bin/env python3

import time
import smbus2 as smbus

BUS = smbus.SMBus(1)

def write_word(addr, data):
    global BLEN
    temp = data
    if BLEN == 1:
        temp |= 0x08
    else:
        temp &= 0xF7
    BUS.write_byte(addr, temp)

def send_command(comm):
    buf = comm & 0xF0
    buf |= 0x04
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB
    write_word(LCD_ADDR, buf)

    buf = (comm & 0x0F) << 4
    buf |= 0x04
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB
    write_word(LCD_ADDR, buf)

def send_data(data):
    buf = data & 0xF0
    buf |= 0x05
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB
    write_word(LCD_ADDR, buf)

    buf = (data & 0x0F) << 4
    buf |= 0x05
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB
    write_word(LCD_ADDR, buf)

def init(addr, bl):
    global LCD_ADDR
    global BLEN
    LCD_ADDR = addr
    BLEN = bl
    try:
        send_command(0x33)
        time.sleep(0.005)
        send_command(0x32)
        time.sleep(0.005)
        send_command(0x28)
        time.sleep(0.005)
        send_command(0x0C)
        time.sleep(0.005)
        send_command(0x01)
        BUS.write_byte(LCD_ADDR, 0x08)
    except:
        return False
    else:
        return True

def clear():
    send_command(0x01)

def openlight():
    BUS.write_byte(0x27, 0x08)
    BUS.close()

def write(x, y, str):
    if x < 0:
        x = 0
    if x > 19:
        x = 19
    if y < 0:
        y = 0
    if y > 3:
        y = 3

    # Fixed row addresses
    row_offsets = [0x00, 0x40, 0x14, 0x54]
    addr = 0x80 + row_offsets[y] + x
    send_command(addr)

    for chr in str:
        send_data(ord(chr))

if __name__ == '__main__':
    init(0x27, 1)
    write(0, 0, "Hello, World!")
    write(0, 1, "I2C 2004 LCD")
    write(0, 2, "Line 3")
    write(0, 3, "Line 4")
