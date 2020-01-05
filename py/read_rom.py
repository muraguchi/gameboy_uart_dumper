#! /usr/bin/python
import serial
import struct

ser = serial.Serial('/dev/ttyUSB0',460800,timeout=None)
outfile="NONAME.gb"

logo_expected = [0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B, 0x03, 0x73, 0x00, 0x83,
                 0x00, 0x0C, 0x00, 0x0D, 0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
                 0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99, 0xBB, 0xBB, 0x67, 0x63,
                 0x6E, 0x0E, 0xEC, 0xCC, 0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E]

# Logo check ( 48 bytes )
for addr in range(48):
    ser.write (("R1%04X" %( addr+0x104 )).encode())
    readdata=int(ser.read(2).decode(),16)
    if ( readdata != logo_expected[addr] ):
        print("Error logo verify at addr 0x%04X. expected value 0x%02X, read value 0x%02X" % (addr+0x104,logo_expected[addr],readdata))
        quit()
print("Logo verify done.")

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
    print("Cartrige type: ROM ONLY")
elif ( cart_type==0x01):
    print("Cartrige type: MBC1")
elif ( cart_type==0x02):
    print("Cartrige type: MBC1+RAM")
elif ( cart_type==0x03):
    print("Cartrige type: MBC1+RAM+BATTERY")
elif ( cart_type==0x05):
    print("Cartrige type: MBC2")
elif ( cart_type==0x06):
    print("Cartrige type: MBC2+BATTERY")
elif ( cart_type==0x0F):
    print("Cartrige type: MBC3+TIMER+BATTERY")
elif ( cart_type==0x10):
    print("Cartrige type: MBC3+TIMER+RAM+BATTERY")
elif ( cart_type==0x11):
    print("Cartrige type: MBC3")
elif ( cart_type==0x12):
    print("Cartrige type: MBC3+RAM")
elif ( cart_type==0x13):
    print("Cartrige type: MBC3+RAM+BATTERY")
elif ( cart_type==0x19):
    print("Cartrige type: MBC5")
elif ( cart_type==0x1A):
    print("Cartrige type: MBC5+RAM")
elif ( cart_type==0x1B):
    print("Cartrige type: MBC5+RAM+BATTERY")
elif ( cart_type==0x1C):
    print("Cartrige type: MBC5+RUMBLE")
elif ( cart_type==0x1D):
    print("Cartrige type: MBC5+RUMBLE+RAM")
elif ( cart_type==0x1E):
    print("Cartrige type: MBC5+RUMBLE+RAM+BATTERY")
elif ( cart_type==0x22):
    print("Cartrige type: MBC7+SENSOR+RAM+BATTERY")
elif ( cart_type==0xFD):
    print("Cartrige type: TAMA5")
elif ( cart_type==0xFE):
    print("Cartrige type: HuC3")
elif ( cart_type==0xFF):
    print("Cartrige type: HuC1")
else:
    print("Cartrige type: 0x%02X" % (cart_type))

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



outfile=title.replace('!',"_").replace(" ","_").replace('\x00','').replace('.','_').replace('/','_').replace("-","_").replace("\'",'_').replace('&','_')+".gb"
for i in range(16):
    outfile=outfile.replace("__","_")
outfile=outfile.replace("_.gb",".gb")
print(outfile)
gbf=open((outfile),"wb")

#NO ROM
if (cart_type==0x00):
    if(rom_size==0x00):
        for ra in range(0x8000):
           if(ra % 0x4000 == 0): 
               ser.write (("P1%02X" %( ra>>8 ) ).encode() )
           data = int(ser.read(2).decode(),16)
           gbf.write(struct.pack("B", data ))
           if (ra%16==0):
               print(("0x00 0x%04X: %02X " % (ra,data)) , end="")
           elif (ra%16==15):
               print("%02X" % data)
           else:
               print(("%02X " % data), end="")
#MBC
else :
    if (rom_size==0x01):
        num_banks=4
    elif (rom_size==0x02):
        num_banks=8
    elif (rom_size==0x03):
        num_banks=16
    elif (rom_size==0x04):
        num_banks=32
    elif (rom_size==0x05):
        num_banks=64
    elif (rom_size==0x06):
        num_banks=128
    elif (rom_size==0x07):
        num_banks=256
    elif (rom_size==0x08):
        num_banks=512
    for bank_index in range(num_banks):
        if (bank_index==0):
            for ra in range(0x4000):
                if(ra % 0x4000 == 0): 
                    ser.write (("P1%02X" %( ra>>8 ) ).encode() )
                #ser.write (("R1%04X" %( ra ) ).encode() )
                data = int(ser.read(2).decode(),16)
                gbf.write(struct.pack("B", data ))
                if (ra%16==0):
                    print(("0x000 0x%04X: %02X " % (ra,data)) , end="")
                elif (ra%16==15):
                    print("%02X" % data)
                else:
                    print(("%02X " % data), end="")
        else:
            # Change BANK
            # MBC1
            if (cart_type==0x01 or cart_type==0x02 or cart_type==0x03 ):
                # Upper 2bit
                ser.write (("W14100%02X" %((bank_index>>5)&0x3) ).encode())
                data = int(ser.read(2).decode(),16)
                # Lower 5bit
                ser.write (("W12100%02X" %(bank_index&0x1F) ).encode() )
                data = int(ser.read(2).decode(),16)
            # MBC2
            elif (cart_type==0x05 or cart_type==0x06):
                ser.write (("W12100%02X" %(bank_index&0xf) ).encode())
                data = int(ser.read(2).decode(),16)
            # MBC3
            elif  (cart_type==0x0f or cart_type==0x10 or cart_type==0x11 or cart_type==0x12 or cart_type==0x13 ):
                ser.write (("W12000%02X" %(bank_index) ).encode())
                data = int(ser.read(2).decode(),16)
            # MBC5 or MBC7
            elif(cart_type==0x19 or cart_type==0x1a or cart_type==0x1b or cart_type==0x1c or cart_type==0x1d or cart_type==0x1e or cart_type==0x22):
                # Upper 1bit
                ser.write (("W13100%02X" %((bank_index>>8)&0x1) ).encode())
                data = int(ser.read(2).decode(),16)
                # Lower 8bit
                ser.write (("W12100%02X" %(bank_index&0xff) ).encode())
                data = int(ser.read(2).decode(),16)
            # TAMA5
            elif(cart_type==0xfd):

                # Init 
                ser.write ( ("W0A0010A" ).encode() )
                data = int(ser.read(2).decode(),16)
                
                # Select lower nibble bank reg 
                ser.write (("W0A00100" ).encode() )
                data = int(ser.read(2).decode(),16)
                
                # Write lower nibble bank address
                ser.write (("W0A000%02X" % (bank_index&0xf) ).encode() )
                data = int(ser.read(2).decode(),16)

                # Select upper nibble bank reg 
                ser.write (("W0A00101" ).encode() )
                data = int(ser.read(2).decode(),16)
                
                # Write upper nibble bank address
                ser.write (("W0A000%02X" % ( (bank_index&0xf0)>>4) ).encode() )
                data = int(ser.read(2).decode(),16)
                
            # HuC1, HuC3
            elif(cart_type==0xfe or cart_type==0xff):
                #  6bit
                #print("W12100%02X" %(bank_index&0x3F))
                ser.write (("W12100%02X" %(bank_index&0x3F) ).encode() )
                data = int(ser.read(2).decode(),16)
            else:
                print("Error. No BANK procs...")
            print("Change Bank 0x%03X (%d) "%(bank_index,bank_index))
            for ra in range(0x4000,0x8000):
                if(ra % 0x4000 == 0): 
                    ser.write (("P1%02X" %( ra>>8 ) ).encode() )
                #ser.write (("R1%04X" %( ra ) ).encode() )
                data = int(ser.read(2).decode(),16)
                gbf.write(struct.pack("B", data ))
                if (ra%16==0):
                    print(("0x%03X 0x%04X: %02X " % (bank_index,ra,data)) , end="")
                elif (ra%16==15):
                    print("%02X" % data)
                else:
                    print(("%02X " % data), end="")



    
    
