# gameboy_uart_dumper
Game Boy / Game Boy Color dumper with AVR attiny2313 and FT232R.

# Dumper schematic

https://github.com/muraguchi/gameboy_uart_dumper/blob/master/kicad/gameboy_uart_dumper.pdf

# Dumper firmware

https://github.com/muraguchi/gameboy_uart_dumper/tree/master/src

# Dumper host programs

https://github.com/muraguchi/gameboy_uart_dumper/tree/master/py

# Configuration

Modify "config.py" as you like.

# Usage

run "read_rom.py" and then it dumps title named rom image.

# Supported ROM types

This dumper supports following types of cartridges.
It covers almost all commercially avairable cartridges.

* NO MBC  Tetris, Dr Mario, Alley way, Othello... This type is often seen in the early released cartidges. 
* MBC1  Super Mario Land, Baseball, Pokemon red and many cartridges uses this types. 
* MBC2  Golf, F1RACE, Kirby's pinball and so on. MBC2 has SRAM on itself.
* MBC3  Pokemon Yello, Pokemon Gold, Pokemon Silver, Bokujou GB and so on.
* MBC5  DQ12, DQ3, Zelda Yume wo mirushima DX, Mr.Driller, Bokujou GB2, Pokemon de panepon and so on. This type is often seen in the later released cartridges. 
* MBC7  Korokoro Kirby.
* HuC-1 Pokemon Card GB, Super B-daman and so on. This type of cart has a infrared port on the top.
* HuC-3 Robot ponkkotu sun, start and so on.
* TAMA5  Tamagocchi3. TAMA5 is designated for Tamagocchi3. This dumper supports ROM dumping with correct checksum.
* MMM01  Momotarou collection 2 and so on. This type has multiple images in 1 cartridge. Multiple dumping (each title and title selection program) will be required to dump it out. In this dumper version global checksum fails. but it dumped images works on mgba emulator.
* PocketCamera  It is same with MBC3.

# MBC1 "Bomberman Quest" special patch

MBC1 "Bomberman Quest" cart has wrong global checksum. Because the global checksum of "Bomberman Quest" was calculated bank 0x20 as bank 0. This dumper has special patch for "Bomberman Quest". It dumps bank 0 data as both of bank 0 and 0x20 for the correct global checksum.
