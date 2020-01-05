#! /usr/bin/python
import sys

if (len(sys.argv)<=1):
    print ("Usage: %s gameboy_romfile.gb" % sys.argv[0] )
    exit()
else:
    fgb = open (sys.argv[1],"rb")
    print ("Verify %s" % sys.argv[1])

    ###########################################################################
    # compare header checksum
    ###########################################################################
    # get header checksum at 0x14d point
    fgb.seek(0x14d)
    header_hc=int.from_bytes(fgb.read(1),'little')
    calc_hc = 0
    for addr in range(0x134,0x14C+1):
        fgb.seek(addr)
        calc_hc = ( calc_hc - (int.from_bytes(fgb.read(1),'little')) - 1 ) % 0x100
    if (calc_hc==header_hc):
        print ("HEADER CHECKSUM COMPARE RESULT : OK")
    else:
        print ("HEADER CHECKSUM COMPARE RESULT : ERROR")
        print ("Header Checksum at 0x14d : 0x%02X" % header_hc)
        print ("Header Checksum calculated : 0x%02X" % calc_hc)

    ###########################################################################
    # compare glocal checksum
    ###########################################################################

    # get filesize
    fgb.seek(0,2)
    last_addr = fgb.tell()

    # get global checksum
    fgb.seek(0x14e)
    header_gc = int.from_bytes(fgb.read(2),'big')
    calc_gc=0

    # seek head
    fgb.seek(0)   

    for addr in range(0,last_addr+1):        
        if(addr==0x14e or addr==0x14f):
            fgb.read(1)
        else:
            calc_gc = ( (calc_gc + int.from_bytes(fgb.read(1),'little')) % 0x10000)
    if (calc_gc==header_gc):
        print ("GLOBAL CHECKSUM COMPARE RESULT : OK")
    else:
        print ("GLOBAL CHECKSUM COMPARE RESULT : ERROR")
        print ("Global Checksum at 0x14E:0x14F 0x%04X" % header_gc)
        print ("Global Checksum calculated : 0x%04X" % calc_gc)
