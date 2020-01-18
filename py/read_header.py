#! /usr/bin/python
import serial
import config




ser = serial.Serial(config.SERIAL_DEVICE,
                    config.SERIAL_BAUDRATE,
                    timeout=config.SERIAL_TIMEOUT_SEC)

# Get_cart_type
ser.write (("R1%04X" %( 0x0143)).encode() )
cgb_flag = int(ser.read(2).decode(),16)

# Get title
title_length=16
if (cgb_flag==0x80 or cgb_flag == 0xC0):
    title_length=15

title=""
for index in range(title_length):
    ser.write (("R1%04X" %( index+0x134)).encode() )
    title+=chr(int(ser.read(2).decode(),16))

    
# Get cart_type

ser.write (("R1%04X" %( 0x0147)).encode() )
cart_type = int(ser.read(2).decode(),16)

# Get ROM size

ser.write (("R1%04X" %( 0x0148)).encode() )
rom_size = int(ser.read(2).decode(),16)

# Get RAM size

ser.write (("R1%04X" %( 0x0148)).encode() )
ram_size = int(ser.read(2).decode(),16)


print("Title: %s" % (title))

if ( cgb_flag==0x80 ):
    print("CGB flag: Game Boy / Game Boy Color")
elif ( cgb_flag==0xC0 ):
    print("CGB flag: Game Boy Color")
else:
    print("CGB flag: Game Boy")

if ( cart_type==0x00):
    print("Cartridge type: ROM ONLY")
elif ( cart_type==0x01):
    print("Cartridge type: MBC1")
elif ( cart_type==0x02):
    print("Cartridge type: MBC1+RAM")
elif ( cart_type==0x03):
    print("Cartridge type: MBC1+RAM+BATTERY")
elif ( cart_type==0x05):
    print("Cartridge type: MBC2")
elif ( cart_type==0x06):
    print("Cartridge type: MBC2+BATTERY")
elif ( cart_type==0x0D):
    print("Cartridge type: MMM01")
elif ( cart_type==0x0F):
    print("Cartridge type: MBC3+TIMER+BATTERY")
elif ( cart_type==0x10):
    print("Cartridge type: MBC3+TIMER+RAM+BATTERY")
elif ( cart_type==0x11):
    print("Cartridge type: MBC3")
elif ( cart_type==0x12):
    print("Cartridge type: MBC3+RAM")
elif ( cart_type==0x13):
    print("Cartridge type: MBC3+RAM+BATTERY")
elif ( cart_type==0x19):
    print("Cartridge type: MBC5")
elif ( cart_type==0x1A):
    print("Cartridge type: MBC5+RAM")
elif ( cart_type==0x1B):
    print("Cartridge type: MBC5+RAM+BATTERY")
elif ( cart_type==0x1C):
    print("Cartridge type: MBC5+RUMBLE")
elif ( cart_type==0x1D):
    print("Cartridge type: MBC5+RUMBLE+RAM")
elif ( cart_type==0x1E):
    print("Cartridge type: MBC5+RUMBLE+RAM+BATTERY")
elif ( cart_type==0x22):
    print("Cartridge type: MBC7+SENSOR+RAM+BATTERY")
elif ( cart_type==0xFD):
    print("Cartridge type: TAMA5")
elif ( cart_type==0xFE):
    print("Cartridge type: HuC3")
elif ( cart_type==0xFF):
    print("Cartridge type: HuC1")
else:
    print("Cartridge type: 0x%02X" % (cart_type))
    
if (rom_size==0x00):
    print("ROM size: 32 KBytes")
elif (rom_size==0x01):
    print("ROM size: 64 KBytes / 4 banks")
elif (rom_size==0x02):
    print("ROM size: 128 KBytes / 8 banks")
elif (rom_size==0x03):
    print("ROM size: 256 KBytes / 16 banks")
elif (rom_size==0x04):
    print("ROM size: 512 KBytes / 32 banks")
elif (rom_size==0x05):
    print("ROM size: 1 MBytes / 64 banks")
elif (rom_size==0x06):
    print("ROM size: 2 MBytes / 128 banks")
elif (rom_size==0x07):
    print("ROM size: 4 MBytes / 256 banks")
elif (rom_size==0x08):
    print("ROM size: 8 MBytes / 512 banks")
elif (rom_size==0x52):
    print("ROM size: 1.1 MBytes / 72 banks")
elif (rom_size==0x53):
    print("ROM size: 1.2 MBytes / 80 banks")
elif (rom_size==0x54):
    print("ROM size: 1.5 MBytes / 96 banks")
else: 
    print("ROM size: 0x%02X" %(rom_size))

if (ram_size==0x00):
    print("RAM size: None")
elif (ram_size==0x01):
    print("RAM size: 2 Kbytes")
elif (ram_size==0x02):
    print("RAM size: 8 Kbytes")
elif (ram_size==0x03):
    print("RAM size: 32 Kbytes / 4 banks")
elif (ram_size==0x04):
    print("RAM size: 128 Kbytes / 16 banks")
elif (ram_size==0x05):
    print("RAM size: 64 Kbytes / 8 banks")
else:
    print("RAM size: 0x%02X" %(ram_size))



