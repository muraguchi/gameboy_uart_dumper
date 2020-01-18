#! /usr/bin/python
import serial
import struct
import time 
import config

def hex2str(hex):
    #return (format(hex, '04b'))
    return (format(hex, '04b')).replace("0"," "*config.LOGO_SIZE_X).replace("1","@"*config.LOGO_SIZE_X)
def display_logo(cart_logo):
    print("")
    for i_y_block in range(2):
        for i_y_line in range(2):
            for i_hl in [1,0]:
                for i_size_y in range(config.LOGO_SIZE_Y):
                    for i_x_line in range(12):
                        if (i_x_line==11):
                            print (hex2str(cart_logo[i_y_block*24+2*i_x_line+i_y_line]>>(4*i_hl)  & 0xf ))
                        else:
                            print (hex2str(cart_logo[i_y_block*24+2*i_x_line+i_y_line]>>(4*i_hl)  & 0xf ),end="")
    print("")




ser = serial.Serial(config.SERIAL_DEVICE,
                    config.SERIAL_BAUDRATE,
                    timeout=config.SERIAL_TIMEOUT_SEC)

####################################################################################
# MMU01 ( MOMOCOL2 ) MBC has 2 stages for dumping 
####################################################################################
#
# step 0   : mmm01_step=0 and 1st rom dump.
# * power down and power up cart by hand.
# step 1   : mmu01_step=1 and 2nd rom dump. and add padding data ( 14 * 16KB empty data )
# * power down and power up cart by hand.
# step 2   : mmu01_step=2 and 3rd 32KB header.
#mmu01_step=0;
mmm01_step=0;
####################################################################################


####################################################################################
# logo check
####################################################################################
cart_logo=[0xff]*48
# get cart logo ( 48 bytes )
for addr in range(48):
    ser.write (("R1%04X" %( addr+0x104 )).encode())
    cart_logo[addr]=int(ser.read(2).decode(),16)

if(config.VERBOSITY>=1):
    display_logo(cart_logo)
# check logo
for addr in range(48):
    if ( cart_logo[addr] != config.LOGO_EXPECTED[addr] ):
        print("Logo check      : FAIL" )
        print("Logo check error at 0x%04X. expected value 0x%02X, read value 0x%02X" % (addr+0x104,config.LOGO_EXPECTED[addr],cart_logo[addr]))
        print("Check the cartridge contact failure.")
        quit()
print("Logo check      : PASS")

####################################################################################
# header checksum
####################################################################################

# get header checksum at 0x14d point
ser.write (("R1%04X" %( 0x14d )).encode())
header_hc=int(ser.read(2).decode(),16)

calc_hc = 0
for addr in range(0x134,0x14C+1):
    ser.write (("R1%04X" %( addr )).encode())
    calc_hc = ( calc_hc - ( int(ser.read(2).decode(),16) ) - 1 ) % 0x100

if (header_hc!=calc_hc):
    print("Header checksum : FAIL")
    print("Header checksum error. expected value 0x%02X, calculated value 0x%02X" % (header_hc,calc_hc))
    print("Check the cartridge contact failure.")
    quit()
else:
    print("Header checksum : PASS")

####################################################################################
# Play "Po-ling!" 
####################################################################################
if(config.VERBOSITY>=2):
    print ("Po-",end="",flush=True)
    time.sleep(0.5)
    print ("ling",end="",flush=True)
    time.sleep(0.1)
    for itr in range(5):
        print (".",end="",flush=True)
        time.sleep(0.1)
    print("!",flush=True)

####################################################################################
# Global checksum (prepare)
####################################################################################
ser.write (("R1%04X" %( 0x014E)).encode() )
header_gc = int(ser.read(2).decode(),16)<<8
ser.write (("R1%04X" %( 0x014F)).encode() )
header_gc |= int(ser.read(2).decode(),16)
#print("global checksum at header = %04X"%(header_gc))
calc_gc=0


####################################################################################
# get cart info
####################################################################################
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


title=title.replace('!',"_").replace(" ","_").replace('\x00','').replace('.','_').replace('/','_').replace("-","_").replace("\'",'_').replace('&','_')
for i in range(16):
    title=title.replace("__","_").lstrip("_").rstrip("_")
outfile=title+".gb"
print("Title           : %s" % (title))


if (config.VERBOSITY>=1):
    if ( cgb_flag==0x80 ):
        print("CGB flag        : Game Boy / Game Boy Color")
    elif ( cgb_flag==0xC0 ):
        print("CGB flag        : Game Boy Color")
    else:
        print("CGB flag        : Game Boy")
        
    if ( cart_type==0x00):
        print("Cartridge type  : ROM ONLY")
    elif ( cart_type==0x01):
        print("Cartridge type  : MBC1")
    elif ( cart_type==0x02):
        print("Cartridge type  : MBC1+RAM")
    elif ( cart_type==0x03):
        print("Cartridge type  : MBC1+RAM+BATTERY")
    elif ( cart_type==0x05):
        print("Cartridge type  : MBC2")
    elif ( cart_type==0x06):
        print("Cartridge type  : MBC2+BATTERY")
    elif ( cart_type==0x0D):
        print("Cartridge type  : MMM01")
    elif ( cart_type==0x0F):
        print("Cartridge type  : MBC3+TIMER+BATTERY")
    elif ( cart_type==0x10):
        print("Cartridge type  : MBC3+TIMER+RAM+BATTERY")
    elif ( cart_type==0x11):
        print("Cartridge type  : MBC3")
    elif ( cart_type==0x12):
        print("Cartridge type  : MBC3+RAM")
    elif ( cart_type==0x13):
        print("Cartridge type  : MBC3+RAM+BATTERY")
    elif ( cart_type==0x19):
        print("Cartridge type  : MBC5")
    elif ( cart_type==0x1A):
        print("Cartridge type  : MBC5+RAM")
    elif ( cart_type==0x1B):
        print("Cartridge type  : MBC5+RAM+BATTERY")
    elif ( cart_type==0x1C):
        print("Cartridge type  : MBC5+RUMBLE")
    elif ( cart_type==0x1D):
        print("Cartridge type  : MBC5+RUMBLE+RAM")
    elif ( cart_type==0x1E):
        print("Cartridge type  : MBC5+RUMBLE+RAM+BATTERY")
    elif ( cart_type==0x22):
        print("Cartridge type  : MBC7+SENSOR+RAM+BATTERY")
    elif ( cart_type==0xFC):
        print("Cartridge type  : Pocket Camera")
    elif ( cart_type==0xFD):
        print("Cartridge type  : TAMA5")
    elif ( cart_type==0xFE):
        print("Cartridge type  : HuC3")
    elif ( cart_type==0xFF):
        print("Cartridge type  : HuC1")
    else:
        print("Cartridge type  : Unknown 0x%02X" % (cart_type))

    if (rom_size==0x00):
        print("ROM size        : 32 KBytes")
    elif (rom_size==0x01):
        print("ROM size        : 64 KBytes / 4 banks")
    elif (rom_size==0x02):
        print("ROM size        : 128 KBytes / 8 banks")
    elif (rom_size==0x03):
        print("ROM size        : 256 KBytes / 16 banks")
    elif (rom_size==0x04):
        print("ROM size        : 512 KBytes / 32 banks")
    elif (rom_size==0x05):
        print("ROM size        : 1 MBytes / 64 banks")
    elif (rom_size==0x06):
        print("ROM size        : 2 MBytes / 128 banks")
    elif (rom_size==0x07):
        print("ROM size        : 4 MBytes / 256 banks")
    elif (rom_size==0x08):
        print("ROM size        : 8 MBytes / 512 banks")
    elif (rom_size==0x52):
        print("ROM size        : 1.1 MBytes / 72 banks")
    elif (rom_size==0x53):
        print("ROM size        : 1.2 MBytes / 80 banks")
    elif (rom_size==0x54):
        print("ROM size        : 1.5 MBytes / 96 banks")
    else: 
        print("ROM size        : Unknown 0x%02X" %(rom_size))

    if (ram_size==0x00):
        print("RAM size        : None")
    elif (ram_size==0x01):
        print("RAM size        : 2 KBytes")
    elif (ram_size==0x02):
        print("RAM size        : 8 KBytes")
    elif (ram_size==0x03):
        print("RAM size        : 32 KBytes / 4 banks")
    elif (ram_size==0x04):
        print("RAM size        : 64 KBytes / 8 banks")
    elif (ram_size==0x05):
        print("RAM size        : 128 KBytes / 16 banks")
    elif (ram_size==0x06):
        print("RAM size        : 256 KBytes / 32 banks")
    elif (ram_size==0x07):
        print("RAM size        : 512 KBytes / 64 banks")
    else:
        print("RAM size        : Unknown 0x%02X" %(ram_size))

print("")

####################################################################################
# MMU001
####################################################################################
if( (cart_type==0x0d) and (mmm01_step>0) and (title=="MOMOCOL2")):
    gbf=open((outfile),"ab")
else:
    gbf=open((outfile),"wb")

if (cart_type==0x0d and mmm01_step==0 and title=="MOMOCOL2"):
    ser.write (("W13FFF%02X" % ( 0x00 ) ).encode())
    data = int(ser.read(2).decode(),16)
    ser.write (("W15FFF%02X" % ( 0x01 ) ).encode())
    data = int(ser.read(2).decode(),16)
    ser.write (("W17FFF%02X" % ( 0x01 ) ).encode())
    data = int(ser.read(2).decode(),16)
    ser.write (("W11FFF%02X" % ( 0x3A ) ).encode())
    data = int(ser.read(2).decode(),16)
    ser.write (("W11FFF%02X" % ( 0x7A ) ).encode())
    data = int(ser.read(2).decode(),16)
    ser.write (("R1%04X" %( 0x0148)).encode() )
    rom_size = int(ser.read(2).decode(),16)
elif (cart_type==0x0d and mmm01_step==1 and title=="MOMOCOL2"):    
    ser.write (("W13FFF%02X" % ( 0x20 ) ).encode())
    data = int(ser.read(2).decode(),16)
    ser.write (("W15FFF%02X" % ( 0x40 ) ).encode())
    data = int(ser.read(2).decode(),16)
    ser.write (("W17FFF%02X" % ( 0x21 ) ).encode())
    data = int(ser.read(2).decode(),16)
    ser.write (("W11FFF%02X" % ( 0x3A ) ).encode())
    data = int(ser.read(2).decode(),16)
    ser.write (("W11FFF%02X" % ( 0x7A ) ).encode())
    data = int(ser.read(2).decode(),16)
    ser.write (("R1%04X" %( 0x0148)).encode() )
    rom_size = int(ser.read(2).decode(),16)

####################################################################################
# dump ROM
####################################################################################
#NO MBC
if (cart_type==0x00):
    if(rom_size==0x00):
        for ra in range(0x8000):
            if(ra % 0x4000 == 0): 
                ser.write (("P1%02X" %( ra>>8 ) ).encode() )
                if (ra==0):
                    print("\rBank %d/%d %0.1f %% "%(0,1,1/2*100.0),end="")
                else:
                    print("\rBank %d/%d %0.1f %% "%(1,1,2/2*100.0))
            data = int(ser.read(2).decode(),16)
            if(ra!=0x14e and ra!=0x14f):
                calc_gc = ( (calc_gc + data) % 0x10000)
            gbf.write(struct.pack("B", data ))
            if(config.VERBOSITY>=2):
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
            print("\rBank %d/%d %0.1f %% "%(bank_index,num_banks-1,(bank_index)/num_banks*100.0),end="")
            if (cart_type==0x0d and mmm01_step==2 and title=="MOMOCOL2"):
                for ra in range(0x8000):
                    if(ra % 0x4000 == 0): 
                        ser.write (("P1%02X" %( ra>>8 ) ).encode() )
                    data = int(ser.read(2).decode(),16)
                    gbf.write(struct.pack("B", data ))
                    if(config.VERBOSITY>=2):
                        if (ra%16==0):
                            print(("0x000 0x%04X: %02X " % (ra,data)) , end="")
                        elif (ra%16==15):
                            print("%02X" % data)
                        else:
                            print(("%02X " % data), end="")
                quit()
            else:
                for ra in range(0x4000):
                    if(ra % 0x4000 == 0): 
                        ser.write (("P1%02X" %( ra>>8 ) ).encode() )
                    #ser.write (("R1%04X" %( ra ) ).encode() )
                    data = int(ser.read(2).decode(),16)
                    if(ra!=0x14e and ra!=0x14f):
                        calc_gc = ( (calc_gc + data) % 0x10000)
                    gbf.write(struct.pack("B", data ))
                    if(config.VERBOSITY>=2):
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
                # Change Banking mode
                if (rom_size>4):
                    # 8KByte RAM, 2MB ROM mode
                    ser.write (("W1610001" ).encode())
                    data = int(ser.read(2).decode(),16)
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
            # MMM01
            elif (cart_type==0x0d):
                if((mmm01_step==0 or mmm01_step==1)and title=="MOMOCOL2"):
                    ser.write (("W12000%02X" %(bank_index) ).encode())
                    data = int(ser.read(2).decode(),16)
            # MBC3 or PocketCamera
            elif  (cart_type==0x0f or cart_type==0x10 or cart_type==0x11 or cart_type==0x12 or cart_type==0x13 or cart_type==0xfc):
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

            if(config.VERBOSITY>=1):
                if (bank_index==num_banks-1 or config.VERBOSITY>=2):
                    pend=""
                else:
                    pend=""
                print("\rBank %d/%d %0.1f %% "%(bank_index,num_banks-1,(bank_index)/(num_banks)*100.0),end=pend)
                    
            start_point = 0x4000
            # Start "BOMBERMAN QUEST" patch
            # "BOMBERMAN QUEST" has odd global check. it expects bank 0x20 is not bank 0x1 but bank 0x0.
            if ((title=="BOMBERMAN_QUEST") and (cart_type==0x03) and (bank_index==0x20)):
                start_point = 0x0000
            # End   "BOMBERMAN QUEST" patch
                
            for ra in range(start_point,start_point+0x4000):
                if(ra % 0x4000 == 0): 
                    ser.write (("P1%02X" %( ra>>8 ) ).encode() )
                #ser.write (("R1%04X" %( ra ) ).encode() )
                data = int(ser.read(2).decode(),16)
                calc_gc = ( (calc_gc + data) % 0x10000)
                gbf.write(struct.pack("B", data ))
                if(config.VERBOSITY>=2):
                    if (ra%16==0):
                        print(("0x%03X 0x%04X: %02X " % (bank_index,ra,data)) , end="")
                    elif (ra%16==15):
                        print("%02X" % data)
                    else:
                        print(("%02X " % data), end="")
            if (bank_index==num_banks-1):
                print("\rBank %d/%d %0.1f %% "%(bank_index,num_banks-1,(bank_index+1)/(num_banks)*100.0))
# Add padding data for MOMOCOL2
if(cart_type==0x0d and mmm01_step==1 and title=="MOMOCOL2"):
    for itr in range(14*(16*1024)):
        gbf.write(struct.pack("B", 0xFF ))

####################################################################################
# Global result
####################################################################################
print("")
if(header_gc!=calc_gc):
    print("Global checksum : FAIL")
    print("Global checksum error. expected value 0x%02X, calculated value 0x%02X" % (header_gc,calc_gc) )
    print("Check the cartridge contact failure.")
else:
    print("Global checksum : PASS")
