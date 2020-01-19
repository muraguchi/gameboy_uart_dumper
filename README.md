# gameboy_uart_dumper
Game Boy / Game Boy Color dumper with AVR attiny2313 and FT232R.

## Schematic

https://github.com/muraguchi/gameboy_uart_dumper/blob/master/kicad/gameboy_uart_dumper.pdf

## Firmware

https://github.com/muraguchi/gameboy_uart_dumper/tree/master/src

## Host programs

https://github.com/muraguchi/gameboy_uart_dumper/tree/master/py

## Configuration

Modify "config.py" as you like.

## Usage

run "read_rom.py" and then it dumps title named rom image.

## Supported ROM types

This dumper supports following types of cartridges.
It covers almost all commercially avairable cartridges.

* NO MBC <br> Tetris, Dr Mario, Alley way, Othello... This type is often seen in the early released cartidges. 
* MBC1 <br> Super Mario Land, Baseball, Pokemon red and many cartridges use this type. 
* MBC2 <br> Golf, F1RACE, Kirby's pinball and so on. MBC2 has SRAM on itself.
* MBC3 <br> Pokemon Yello, Pokemon Gold, Pokemon Silver, Bokujou GB and so on.
* MBC5 <br> DQ12, DQ3, Zelda Yume wo mirushima DX, Mr.Driller, Bokujou GB2, Pokemon de panepon and so on. This type is often seen in the later released cartridges. 
* MBC7 <br> Korokoro Kirby. It has a 2-axis accelerometer in the cart.
* HuC-1 <br> Pokemon Card GB, Super B-daman and so on. This type of cart has a infrared port on the top.
* HuC-3 <br> Robot ponkkotu sun/star/moon version and so on. It is similar to HuC-1. HuC-3 has a infrared port as well as HuC-1. HuC-3 has RTC function.
* TAMA5 <br> Tamagocchi3. Only Tamagocchi3 uses this type. This dumper supports ROM dumping with correct checksum.
* MMM01 <br> Momotarou collection 2 and so on. This type has multiple images in 1 cartridge. Multiple dumping (each title and title selection program) will be required to dump it out. In this dumper version global checksum fails. but it dumped images works on mgba emulator.
* PocketCamera <br> same with MBC3.

#### "Bomberman Quest" special patch

"Bomberman Quest" MBC1 cart has a wrong global checksum on the header. Because the global checksum of "Bomberman Quest" was calculated bank 0x20 as bank 0. This dumper has a special patch for "Bomberman Quest". It regards bank 20 as bank 0 for the correct global checksum.

## run log ( sample )

    $ ./read_rom.py 
    
    @@   @@ @@                             @@       
    @@@  @@ @@        @@                   @@       
    @@@  @@          @@@@                  @@       
    @@ @ @@ @@ @@ @@  @@  @@@@  @@ @@   @@@@@  @@@@ 
    @@ @ @@ @@ @@@ @@ @@ @@  @@ @@@ @@ @@  @@ @@  @@
    @@  @@@ @@ @@  @@ @@ @@@@@@ @@  @@ @@  @@ @@  @@
    @@  @@@ @@ @@  @@ @@ @@     @@  @@ @@  @@ @@  @@
    @@   @@ @@ @@  @@ @@  @@@@@ @@  @@  @@@@@  @@@@ 
    
    Logo check      : PASS
    Header checksum : PASS
    Title           : SUPER_MARIOLAND
    CGB flag        : Game Boy
    Cartridge type  : MBC1
    ROM size        : 64 KBytes / 4 banks
    RAM size        : 2 KBytes
    
    Bank 3/3 100.0 % 
    
    Global checksum : PASS
