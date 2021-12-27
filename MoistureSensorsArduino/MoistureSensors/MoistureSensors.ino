void setup() {
Serial.begin(9600); // open serial port, set the baud rate as 9600 bps
}
void loop() {
int val1;
int val2;
int val3;
int val4;
int val5;
String stringin1;
String stringin2;
String stringin3;
String stringin4;
String stringin5;
val1 = analogRead(0); //connect sensor to Analog 0
val2 = analogRead(1);
val3 = analogRead(2);
val4 = analogRead(3);
val5 = analogRead(4);
stringin1 = "s1:";
stringin2 = "s2:";
stringin3 = "s3:";
stringin4 = "s4:";
stringin5 = "s5:";
//Serial.println(stringin1 + val1); //print the value to serial port
//Serial.println(stringin2 + val2);
//Serial.println(stringin3 + val3);
//Serial.println(stringin4 + val4);
//Serial.println(stringin5 + val5);
Serial.println(stringin1 + val1 + "; " +stringin2 + val2 + "; " + stringin3 + val3 + "; " + stringin4 + val4 + "; " + stringin5 + val5);
delay(1000*5);
}
