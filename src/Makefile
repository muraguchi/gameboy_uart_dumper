all: compile upload
compile:
	avr-gcc -o main.elf main.c -mmcu=attiny2313 -Os -g0
	avr-objcopy -I elf32-avr -O ihex main.elf main.hex
	avr-size -C main.elf --mcu=attiny2313
upload:
	#firmware uploading command HERE for your environment. 
	#sudo avrdude -v -v -c arduino-ft232r -B 10000  -P ft1 -p t2313  -U flash:w:main.hex	
	#sudo avrdude -V -B 1000 -c avrispmkII -p t2313 -U flash:w:main.hex
	
clean:
	rm -rf main.elf main.hex 
