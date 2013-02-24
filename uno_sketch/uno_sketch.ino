

/*
//      George Farris <farrisg@gmsys.com>
//        Copyright (c), 2013
//
//      This program is free software; you can redistribute it and/or modify
//      it under the terms of the GNU General Public License as published by
//      the Free Software Foundation; either version 3 of the License, or
//      (at your option) any later version.
//
//      This program is distributed in the hope that it will be useful,
//      but WITHOUT ANY WARRANTY; without even the implied warranty of
//      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//      GNU General Public License for more details.
//
//      You should have received a copy of the GNU General Public License
//      along with this program; if not, write to the Free Software
//      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
//      MA 02110-1301, USA.

ASCII Table

   30 40 50 60 70 80 90 100 110 120
        -------------      ---------------------------------
 0:    (  2  <  F  P  Z  d   n   x
 1:    )  3  =  G  Q  [  e   o   y
 2:    *  4  >  H  R  \  f   p   z
 3: !  +  5  ?  I  S  ]  g   q   {
 4: "  ,  6  @  J  T  ^  h   r   |
 5: #  -  7  A  K  U  _  i   s   }
 6: $  .  8  B  L  V  `  j   t   ~
 7: %  /  9  C  M  W  a  k   u  DEL
 8: &  0  :  D  N  X  b  l   v
 9: ´  1  ;  E  O  Y  c  m   w


*/

/*

 This code is only for the Ardunio UNO 

 Protocol description

 Note that "board" will always be 'A' as only one board is supported at this time.
 This may change in the future.

 The board reads setup information according to the following rules:
 
 Digital pins available: 2 - 13 and A0 - A5 if no analog is used
 Analog Input pins available : A0 - A5 
 Analog Output pins          : 3,5,6,9,10,11
 Note: pins 0,1 and 13 have special uses,
 Pins 0 and 1 are the serial port, 0 - RX, 1 - TX
 Pin 13 is connected to the on board LED and can't be used without an external
 pulldown resister 
 
 Every command to the board is three or four characters.
 

  [Board] [I/O direction] [Pin]
  ===========================================================================
  [Board] 	- 'A'
  [I/O]		- 'DN<pin>' Configure as Digital Input no internal pullup (default)
  			- 'DI<pin>'     "      " Digital Input uses internal pullup
	  		- 'DO<pin>'     "      " Digital Output 
	  		- 'AI<pin>'     "      " Analog Input
			- 'AO<pin>'     "      " Analog Output
	        - 'L<pin>'  Set Digital Output to LOW
	        - 'H<pin>'  Set Digital Output to HIGH
			- '%<pin><value>'  Set Analog Output to value (0 - 255)
  [Pin]		- Ascii 'C' to 'T'  C = pin 2, R = pin A3, etc
 
  Examples transmitted to board:
    ADIF	Configure pin 5 as digital input with pullup
	AAIR	Configure pin A3 as analog input
	AHE		Set digital pin 4 HIGH
	A%D75	Set analog output to value of 75

  Examples received from board:  NOTE the end of message (eom) char '.'
	AHE.		Digital pin 4 is HIGH
	ALE.		Digital pin 4 is LOW
	AP89.		Analog pin A1 has value 89
	
  Available pins, pins with ~ can be analog Output
                  pins starting with A can be Analog Input
                  All pins can be digital except 0 and 1
  ----------------------------------------------------------------------------
  02 03 04 05 06 07 08 09 10 11 12 13 A0 A1 A2 A3 A4 A5
  C  D  E  F  G  H  I  J  K  L  M  N  O  P  Q  R  S  T
     ~     ~  ~        ~  ~  ~
  ============================================================================ 
  The board will return a '?' on error.
  The board will return a '!' on power up or reset.

*/

int board = 'A';	//First board 'A', second borad 'B' etc  pin 13 will blink board address
                        //after reset 1 blink for A, 2 for B etc

int cmd;
int chn;		//channel
int pin;		//actual pin on arduino
int eom = '.';           // end of message
int error = '?';         // error or unknown response
int reset = '!';         // board rest or power up


// this holds the direction of the I/O
// 0 = digital In, 1 = digital Out
// 2 = analog In, analog Out is not supported yet.
int ioPinsDirection[19];
int ioPinsValue[19];

void setup()
{
    Serial.begin(9600);
    Serial.write(reset);	// Send reset '!' to signal we are up and running
    
    // All pins are set to inputs by default so set the array to reflect that
    for (int i=2; i<=19; i++)
    {
        ioPinsDirection[i] = 0;
	ioPinsValue[i] = 0;

        pinMode(i, INPUT_PULLUP);
    }
    
    // blink LED to ID board 1 blink for A, 2 for B etc
    pinMode(13, OUTPUT);
    digitalWrite(13,LOW);

    int blinks = board - 64;
   
    delay(2000);  //wait a bit after reset.
    while (blinks--)
    {
    	digitalWrite(13,HIGH);
	delay(1000);
	digitalWrite(13,LOW);
	delay(1000);
    }
    pinMode(13,INPUT_PULLUP);
}

void loop()
{
    int direction;
	char avalue[5];

    if (Serial.available() > 0)
    {
    	// right now we handle one board which is board 'A'
    	if (Serial.read() == board )
	{
	    //Serial.write("Board A\n");
            while (Serial.available() == 0)
            { delayMicroseconds(100); }
            cmd = Serial.read();
            //Serial.write(cmd);
            
            //Serial.write(" Command\n");
	    //Serial.print(sin);
	    switch (cmd) 
	    {
        	case 72:        // 'H' set digital pin HIGH
                    while (Serial.available() == 0)
                    { delayMicroseconds(100); }
                    chn = Serial.read();
                    pin = chn - 65;
                    if (pin > 1)
                    {
                      if (ioPinsDirection[pin] == 1)                    
                        digitalWrite(pin, HIGH);
                    } else
                      Serial.write(error);  //error, pins 0 and 1 can't be used
                    break;              

            case 76:        // 'L' set digital pin LOW
                    while (Serial.available() == 0)
                    { delayMicroseconds(100); }
                    chn = Serial.read();
                    pin = chn - 65;
                    if (pin > 1)
                    {
                      if (ioPinsDirection[pin] == 1)
                        digitalWrite(pin, LOW);
                    } else
                      Serial.write(error);
                    break;               

            case 37:        // '%' set analog out value
                    while (Serial.available() == 0)
                    { delayMicroseconds(100); }
                    chn = Serial.read();
                    //Serial.write(chn);
                    
					Serial.readBytesUntil('.', avalue, 4);
                      //Serial.println(avalue);		
			pin = chn - 65;
					if (pin > 1)
                    
                    {
                      if (ioPinsDirection[pin] == 3)
					  {
						//Serial.println("analog write...");                        
						analogWrite(pin, atoi(avalue));
					  }
                    } else
                      Serial.write(error);
                    break;               


        	case 65:	// 'A' configure as analog
                    while (Serial.available() == 0)
                    { delayMicroseconds(100); }	    
                    direction = Serial.read();
        	    
                    while (Serial.available() == 0)
                    { delayMicroseconds(100); }
                    chn = Serial.read();
		    
                    pin = chn - 65;
				    if (pin >= 14 && pin <= 19)
				    {
        		    	if (direction == 'I')
						{
						    ioPinsDirection[pin] = 2;  // pin is analog input
						    analogRead(pin);
						}
				    } else if (direction == 'O')
					{
						if (pin == 3 || pin == 5 || pin == 6 | pin == 9 || pin == 10 || pin == 11)
						{
							ioPinsDirection[pin] = 3;  // pin is analog output
						} else
							Serial.write(error);
					} else
    	                Serial.write(error);  // error
        		    break;
        	case 68:	// 'D' configure as Digital pin 
                    while (Serial.available() == 0)
                    { delayMicroseconds(100); }	    
                    direction = Serial.read();
        	    
                    while (Serial.available() == 0)
                    { delayMicroseconds(100); }
                    chn = Serial.read();
		    
				    pin = chn - 65;
				    if (pin >= 2 && pin <= 19)
				    {
	        	    	if (direction == 'I')
						{
						    ioPinsDirection[pin] = 0;  // pin is digital input with pullup
						    pinMode(pin, INPUT_PULLUP);
						} else if (direction == 'N')
						{
						    ioPinsDirection[pin] = 0;  // pin is digital input
						    pinMode(pin, INPUT);
						} else if (direction == 'O')
                        {
						    ioPinsDirection[pin] = 1;  // pin is digital output
						    pinMode(pin, OUTPUT);
                            digitalWrite(pin,LOW);
                            //Serial.write(chn);
                            //Serial.write(" Pin set to output");
						}		
				    } else
	                      Serial.write(error);
                    break;
		    }
		}
    }
    // loop through all the inputs
    for (int i=2; i<19; i++)
    {
	if (ioPinsDirection[i] == 0)  // digital
	{
	    int bit = digitalRead(i);
	    // if the bit is changed transmit otherwise ignore
	    if (ioPinsValue[i] != bit)
	    {
		ioPinsValue[i] = bit;
		Serial.write('A');	//tx board
		Serial.write(i+65);	// tx channel aka pin
		if (bit == LOW)
		    Serial.write('L');
		else
		    Serial.write('H');
                Serial.write(eom);
	    }
	} else if (ioPinsDirection[i] == 2) // analog
        {
	    int av = analogRead(i) / 10;
	    
            // if the value is changed transmit otherwise ignore
	    if (ioPinsValue[i] <= av-2 || ioPinsValue[i] >= av+2)
	    {
		ioPinsValue[i] = av;
		Serial.write('A');	//tx board
		Serial.write(i+65);
		Serial.print(av);	// tx channel aka pin
                Serial.write(eom);		
	    }
        }
    }
}
