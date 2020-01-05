/*
main.c

Copyright (c) 2020 muraguchi 

This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php
*/

// 
// Target device: ATTINY2313
//

//
// Fuse setting
// 
// LOW FUSE value : 0xFF 
//   - Disabled CKOUT
//   - Disabled CKDIV8 
//   - External crystal osc over 8MHz
//   - Start-up time:14 CK + 65ms
// HIGH FUSE value : 0xDF
//   - Disabled RSTDISBL
//   - Disabled DWEN
//   - Enabled SPIEN
//   - Disabled WDTON
//   - Disabled EESAVE
//   - Disabled Brownout detection
// EXTENT FUSE value : 0xFF
//   - Disabled SELFPRGEN
// LOCKBIT FUSE value : 0xFF
//   - No memory lock feature enabled 



// 18.432MHz
#define F_CPU 18432000UL

#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>

// UART baudrate : 460.8kbps
#define BAUDRATE 460800

// receive buffer 2^USART_RX_SZ_BITS = USART_RX_LEN
#define USART_RX_SZ_BITS 2 
#define USART_RX_LEN     4
// transmit buffer 2^USART_TX_SZ_BITS = USART_TX_LEN
#define USART_TX_SZ_BITS 2 
#define USART_TX_LEN     4


#define GB1_DDR     DDRB
#define GB2_DDR     DDRD
#define GB1_PORT    PORTB
#define GB2_PORT    PORTD
#define GB1_PIN     PINB
#define GB2_PIN     PIND
#define GB1_SI      PB0
#define GB1_WRB     PB1
#define GB1_PLB     PB2
#define GB1_CSB     PB3
#define GB1_SCK     PB4
#define GB1_RCK     PB5
#define GB1_OEB     PB6
#define GB1_SO      PB7
#define GB2_RDB     PD2
#define GB_WAIT_RD  3
#define GB_WAIT_WR  3

void GB_init();
void USART_init();
char USART_rx_pop(unsigned char *rd);
void USART_tx_push(unsigned char wr);
unsigned char hex_to_bin(unsigned char hex);
unsigned char nibble_to_hex(unsigned char bin);
void GB_msbfirst_shift(unsigned char data);
unsigned char GB_read(unsigned char addrh,unsigned char addrl);
void GB_write(unsigned char addrh,unsigned char addrl, unsigned char wr_data);

static volatile unsigned char USART_rx_wr_ptr;
static volatile unsigned char USART_rx_rd_ptr;
static volatile unsigned char USART_rx_b[USART_RX_LEN];
static volatile unsigned char USART_tx_wr_ptr;
static volatile unsigned char USART_tx_rd_ptr;
static volatile unsigned char USART_tx_b[USART_TX_LEN];
static volatile unsigned char chip_select;

ISR(USART_RX_vect){
  unsigned char next_rx_wr_ptr;
  next_rx_wr_ptr = ( USART_rx_wr_ptr + 1 ) & ( USART_RX_LEN - 1 );
  // If FIFO is full, discarded.
  if (next_rx_wr_ptr==USART_rx_rd_ptr)
    return;
  // else [Aread data and progress write pointer
  else {
    USART_rx_b[USART_rx_wr_ptr]=UDR;
    USART_rx_wr_ptr=next_rx_wr_ptr;
  }
}

ISR(USART_UDRE_vect){
  // If fifo is empty, disable UDR intrrupt
  if (USART_tx_wr_ptr==USART_tx_rd_ptr){
    //UCR = (1 << RXCIE) | (0<< TXCIE) | (0<<UDRIE) | (1<<RXEN) | (1<<TXEN) |(0<<CHR9) ;
    UCSRB = 1 << RXCIE | 0 << TXCIE | 0<<UDRIE | 1<< RXEN | 1<< TXEN | 0<<UCSZ2;
  }
  // pop tx data
  else {
    UDR = USART_tx_b[USART_tx_rd_ptr];
    USART_tx_rd_ptr = ( USART_tx_rd_ptr + 1 ) & ( USART_TX_LEN - 1 );
  }
}

void GB_init(){
  GB1_DDR  = 0 << GB1_SI | 1 << GB1_WRB | 1 << GB1_PLB | 1 << GB1_CSB | 1 << GB1_SCK | 1 << GB1_RCK | 1 << GB1_OEB | 1 << GB1_SO ;
  GB2_DDR  = 1 << GB2_RDB ;
  GB1_PORT =               1 << GB1_WRB | 1 << GB1_PLB | 1 << GB1_CSB | 0 << GB1_SCK | 0 << GB1_RCK | 1 << GB1_OEB | 1 << GB1_SO ;
  GB2_PORT = 1 << GB2_RDB ;
}

void USART_init(){
  // Stop Interrupt
  cli();

  // Init pointers
  USART_rx_wr_ptr=0;
  USART_rx_rd_ptr=0;
  USART_tx_wr_ptr=0;
  USART_tx_rd_ptr=0;
  // Init UBRR
  UBRRH = (unsigned char)((F_CPU/8/BAUDRATE-1)>>8);
  UBRRL = (unsigned char)((F_CPU/8/BAUDRATE-1)&0xff);
  UCSRA = 1 << U2X | 0<<MPCM;
  UCSRB = 1 << RXCIE | 0 << TXCIE | 0<<UDRIE | 1<< RXEN | 1<< TXEN | 0<<UCSZ2;
  UCSRC = 0 << UMSEL | 0 << UPM1  | 0<<UPM0  | 0<< USBS | 1<<UCSZ1|1<<UCSZ0|0<<UCPOL;

  // Enable Interrupt
  sei();  
}

// pop rxdata
char USART_rx_pop(unsigned char * rd)
{
  // If fifo is empty, return 0
  if (USART_rx_wr_ptr==USART_rx_rd_ptr){
    return 0;
  }
  // get read data and return 1
  else {
    *rd = USART_rx_b[USART_rx_rd_ptr];
    USART_rx_rd_ptr = ( USART_rx_rd_ptr + 1 ) & ( USART_RX_LEN - 1 );
    return 1;
  }
}

// push txdata
void USART_tx_push(unsigned char wr)
{
  unsigned char next_tx_wr_ptr;
  next_tx_wr_ptr = ( USART_tx_wr_ptr + 1 ) & ( USART_TX_LEN - 1 );
  // If FIFO is full,
  while (next_tx_wr_ptr==USART_tx_rd_ptr){;}

  USART_tx_b[USART_tx_wr_ptr]=wr;
  USART_tx_wr_ptr = next_tx_wr_ptr;
  // Enable empty interrupt
  //UCR = (1 << RXCIE) | (0<< TXCIE) | (1<<UDRIE) | (1<<RXEN) | (1<<TXEN) |(0<<CHR9) ;
  UCSRB = 1 << RXCIE | 0 << TXCIE | 1<<UDRIE | 1<< RXEN | 1<< TXEN | 0<<UCSZ2;
}

unsigned char hex_to_bin(unsigned char hex){
  if (hex>='0' && hex <='9')
    return hex - '0';
  else if (hex>='A' && hex <='F')
    return (hex - 'A') + 10;
  else if (hex>='a' && hex <='f')
    return (hex - 'a') + 10;
  else
    return 0;
}
unsigned char nibble_to_hex(unsigned char bin){
  if (bin<10)
    return '0'+bin;
  else if (bin<16)
    return 'A'-10+bin;
  else
    return 0;
}


void GB_msbfirst_shift(unsigned char data){
  unsigned char d;
  for (unsigned char l=0; l<8; l++){
    d = (data<<l)&0x80;
    GB1_PORT =              1 << GB1_WRB | 1 << GB1_PLB | chip_select << GB1_CSB | 0 << GB1_SCK | 0 << GB1_RCK | 1 << GB1_OEB | d ;
    GB1_PORT =              1 << GB1_WRB | 1 << GB1_PLB | chip_select << GB1_CSB | 1 << GB1_SCK | 0 << GB1_RCK | 1 << GB1_OEB | d ;
  }
}

unsigned char GB_read(unsigned char addrh,unsigned char addrl){
  unsigned char dat;
  GB_msbfirst_shift(addrh);
  GB_msbfirst_shift(addrl);

  // RDB low
  GB2_PORT =                             0 << GB2_RDB ;

  // RCK high
  GB1_PORT =              1 << GB1_WRB | 0 << GB1_PLB | chip_select << GB1_CSB | 0 << GB1_SCK | 1 << GB1_RCK | 1 << GB1_OEB ;

  // RCK low
  GB1_PORT =              1 << GB1_WRB | 0 << GB1_PLB | chip_select << GB1_CSB | 0 << GB1_SCK | 0 << GB1_RCK | 1 << GB1_OEB ;

  // Wait (read data)
  for (int l=0;l<GB_WAIT_RD;l++){
    __asm__ __volatile__ ("nop");
  }

  // PLB high
  GB1_PORT =              1 << GB1_WRB | 1 << GB1_PLB | chip_select << GB1_CSB | 0 << GB1_SCK | 0 << GB1_RCK | 1 << GB1_OEB ;

  // RDB high
  GB2_PORT =                             1 << GB2_RDB ;

  // LSBFIRST
  dat = (GB1_PIN&0x1);

  for (int l=1;l<=7;l++){
    GB1_PORT =              1 << GB1_WRB | 1 << GB1_PLB | chip_select << GB1_CSB | 1 << GB1_SCK | 0 << GB1_RCK | 1 << GB1_OEB ;
    GB1_PORT =              1 << GB1_WRB | 1 << GB1_PLB | chip_select << GB1_CSB | 0 << GB1_SCK | 0 << GB1_RCK | 1 << GB1_OEB ;
    dat |= (GB1_PIN&0x1)<<l;
  }
  return dat;
}


void GB_write(unsigned char addrh,unsigned char addrl, unsigned char wr_data)
{
  GB_msbfirst_shift(wr_data);
  GB_msbfirst_shift(addrh);
  GB_msbfirst_shift(addrl);

  // RCK high
  GB1_PORT =              1 << GB1_WRB | 1 << GB1_PLB | chip_select << GB1_CSB | 0 << GB1_SCK | 1 << GB1_RCK | 1 << GB1_OEB ;

  // RCK low
  GB1_PORT =              0 << GB1_WRB | 1 << GB1_PLB | chip_select << GB1_CSB | 0 << GB1_SCK | 0 << GB1_RCK | 1 << GB1_OEB ;

  // OEB low
  GB1_PORT =              0 << GB1_WRB | 1 << GB1_PLB | chip_select << GB1_CSB | 0 << GB1_SCK | 0 << GB1_RCK | 0 << GB1_OEB ;

  // Wait (write data)
  for (int l=0;l<GB_WAIT_WR;l++){
    __asm__ __volatile__ ("nop");
  }
  
  // WRB high
  GB1_PORT =              1 << GB1_WRB | 1 << GB1_PLB | chip_select << GB1_CSB | 0 << GB1_SCK | 0 << GB1_RCK | 0 << GB1_OEB ;

  // OEB high
  GB1_PORT =              1 << GB1_WRB | 1 << GB1_PLB | chip_select << GB1_CSB | 0 << GB1_SCK | 0 << GB1_RCK | 1 << GB1_OEB ;  
}


void main ()
{
  // RX data
  unsigned char rxd;
  // state
  // 0: IDLE(R/W)
  // 1: RD CS (0or1 CS)
  // 2: RD ADDR HH
  // 3: RD ADDR HL
  // 4: RD ADDR LH
  // 5: RD ADDR LL 
  // 6: WR CS
  // 7: WR ADDR HH
  // 8: WR ADDR HL
  // 9: WR ADDR LL
  //10: WR ADDR LL  
  //11: WR DATA H
  //12: WR DATA L
  //13: PAGE RD CS
  //14: PAGE RD HH
  //15: PAGE RD HL
  
  unsigned char state;
  unsigned char address_hi;
  unsigned char address_lo;
  unsigned char rw_data;     // used read write data buffer

  unsigned int  address_pgrd;

  GB_init();
  
  // Wait 3 sec
  for(int l=0;l<3000;l++) {
    _delay_ms(1);
  }
  
  USART_init();
  state =0;
  while(1)
    {
      // R<0|1><ADDRESS>          ex. R10140    (READ  0x0140 with CS=1)
      // W<0|1><ADDRESS><DATA>    ex. W0D000FF  (WRITE FF to 0xD000 with CS=0)  
      // P<0|1><ADDRESS_HI>       ex. P100      (16KB PAGE READ from 0x0000 to 0x3FFF with CS=1)
      // Get new letter
      while (USART_rx_pop(&rxd)) {
	switch (state) {
	case 0:
	  if (rxd=='R')
	    state=1;
	  else if (rxd=='W')
	    state=6;
	  else if (rxd=='P')
	    state=13;
	  break;
	case 1:
	  chip_select = hex_to_bin(rxd)&0x1;
	  state=2;
	  break;
	case 2:
	  address_hi = hex_to_bin(rxd)<<4;
	  state=3;
	  break;
	case 3:
	  address_hi |= hex_to_bin(rxd);
	  state=4;
	  break;
	case 4:
	  address_lo = hex_to_bin(rxd)<<4;
	  state=5;
	  break;
	case 5:
	  address_lo |= hex_to_bin(rxd);
	  // TODO READ
	  rw_data=GB_read(address_hi,address_lo);
	  // output hi nibble
	  USART_tx_push(nibble_to_hex(rw_data>>4));
	  // output lo nibble
	  USART_tx_push(nibble_to_hex(rw_data&0xf));
	  state=0;
	  break;
	case 6:
	  chip_select = hex_to_bin(rxd)&0x1;
	  state=7;
	  break;	  
	case 7:
	  address_hi = hex_to_bin(rxd)<<4;
	  state=8;
	  break;
	case 8:
	  address_hi |= hex_to_bin(rxd);
	  state=9;
	  break;
	case 9:
	  address_lo = hex_to_bin(rxd)<<4;
	  state=10;
	  break;
	case 10:
	  address_lo |= hex_to_bin(rxd);
	  state=11;
	  break;
	case 11:
	  rw_data = hex_to_bin(rxd)<<4;
	  state=12;
	  break;
	case 12:
	  rw_data |= hex_to_bin(rxd);
	  GB_write(address_hi,address_lo,rw_data);
	  // output hi nibble
	  USART_tx_push(nibble_to_hex(rw_data>>4));
	  // output lo nibble
	  USART_tx_push(nibble_to_hex(rw_data&0xf));
	  state=0;
	  break;
	case 13:
	  chip_select = hex_to_bin(rxd)&0x1;
	  state=14;
	  break;
	case 14:
	  address_hi = hex_to_bin(rxd)<<4;
	  state=15;
	  break;
	case 15:
	  address_hi |= hex_to_bin(rxd);
	  for(address_pgrd=address_hi<<8;address_pgrd<((address_hi<<8)+0x4000); address_pgrd++){
	    rw_data=GB_read(address_pgrd>>8,(address_pgrd&0xff));
	    // output hi nibble
	    USART_tx_push(nibble_to_hex(rw_data>>4));
	    // output lo nibble
	    USART_tx_push(nibble_to_hex(rw_data&0xf));
	  }	    
	  state=0;
	  break;	  
	}


      } // RX POP
    } // INF
}
