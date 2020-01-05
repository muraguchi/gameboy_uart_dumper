all: compile upload
compile:
	avr-gcc -o main.elf main.c -mmcu=attiny2313 -Os -g0
	avr-objcopy -I elf32-avr -O ihex main.elf main.hex
	avr-size -C main.elf --mcu=attiny2313
upload:
	#firmware uploading command HERE for your environment. 
	#sudo avrdude -v -v -c arduino-ft232r -B 100 -P ft1 -p t2313  -U flash:w:main.hex	
        #
        # E:0xff, H:0xdf, L:0xff
	#sudo avrdude -V -c avrispmkII -p t2313 -U efuse:w:0xFF:m
        #sudo avrdude -V -c avrispmkII -p t2313 -U hfuse:w:0xDF:m
	#sudo avrdude -V -c avrispmkII -p t2313 -U lfuse:w:0xFF:m
	# 
	sudo avrdude -V -c avrispmkII -p t2313 -U flash:w:main.hex
	
clean:
	rm -rf main.elf main.hex 
