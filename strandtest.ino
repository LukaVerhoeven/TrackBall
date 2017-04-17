#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

#define PIN 6

//lcd
#include <LCD16x2.h>
#include <Wire.h>

// Parameter 1 = number of pixels in strip
// Parameter 2 = pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)

LCD16x2 lcd;
int AmountLeds = 147;
//min and max x of the area that needs to be tracked
int MaxX = 300;
int MinX = 130;
//min and max y of your screen
int MinY = 0;
int MaxY = 478;
//min and max of the area that needs to be tracked
int TrackMinY = 80;
int TrackMaxY = 410;

//double factor = MaxX/AmountLeds;
bool inverted = true;
 int testdata = 0;
 
Adafruit_NeoPixel strip = Adafruit_NeoPixel(AmountLeds, PIN, NEO_GRB + NEO_KHZ800);
int buttons;

bool turnLedOn = true;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(0);
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'

  //LCD
  Wire.begin();
  lcd.lcdClear();
  lcd.lcdGoToXY(1,1);
  lcd.lcdWrite("y:");
  lcd.lcdGoToXY(1,2);
  lcd.lcdWrite("x:");
}

void loop() {
  lcd.lcdSetBlacklight(255);
  buttons = lcd.readButtons();
  
  if(buttons==14){
     for(uint16_t i=0; i<strip.numPixels(); i++) {
        strip.setPixelColor(i, strip.Color(0, 0, 0));
    }
    strip.show();
  }
  
  String data = Serial.readString();
  if(data == "q"){
    for(uint16_t i=0; i<strip.numPixels(); i++) {
        strip.setPixelColor(i, strip.Color(0, 0, 0));
    }
    strip.show();
  }else{
    StaticJsonBuffer<200> jsonBuffer;
    
    JsonObject& root = jsonBuffer.parseObject(data);
    double x  = root["x"];    
    double y  = root["y"];
    if(inverted){
      y = MaxY - y;
      abs(y);
    }
    //Serial.println(data +" = " + y);
  
    //double xfactor = x/factor;
    // int LightLed = (int) x/factor;
//    char charBuf[20];
//    data.toCharArray(charBuf, 20);
//    lcd.lcdGoToXY(7,2);
//    lcd.lcdWrite(buttons);

    if(y > TrackMinY && y < TrackMaxY){
      int LightLed = map(y, TrackMinY, TrackMaxY, 0, AmountLeds);      

      if(LightLed > 99 && LightLed < AmountLeds){
        lcd.lcdGoToXY(3,1);
        lcd.lcdWrite(LightLed);
      }else if(LightLed > 9 && LightLed < 100){
        lcd.lcdGoToXY(3,1);
        lcd.lcdWrite(0);
        lcd.lcdGoToXY(4,1);
        lcd.lcdWrite(LightLed);
      }else if(LightLed < 10){
       lcd.lcdGoToXY(3,1);
        lcd.lcdWrite(0);
        lcd.lcdGoToXY(4,1);
        lcd.lcdWrite(0);
        lcd.lcdGoToXY(5,1);
        lcd.lcdWrite(LightLed);
      }else{
        lcd.lcdGoToXY(7,1);
        lcd.lcdWrite("ERROR");
        lcd.lcdGoToXY(7,2);
        lcd.lcdWrite("OUT RANGE");
      }

      lcd.lcdGoToXY(7,2);
      lcd.lcdWrite(turnLedOn);
      
      if(x > MinX && x < MaxX){
        if(turnLedOn){
          followBall(LightLed , strip.Color(255, 0, 0));
          turnLedOn = false;
        }
      }else{
        turnLedOn = true;
      }
    }
    if(x > 99){
      lcd.lcdGoToXY(3,2);
      lcd.lcdWrite(x);
    }else if(x > 9){
      lcd.lcdGoToXY(3,2);
      lcd.lcdWrite(0);
      lcd.lcdGoToXY(4,2);
      lcd.lcdWrite(x);
    }else if(x < 10){
     lcd.lcdGoToXY(3,2);
      lcd.lcdWrite(0);
      lcd.lcdGoToXY(4,2);
      lcd.lcdWrite(0);
      lcd.lcdGoToXY(5,2);
      lcd.lcdWrite(x);
    }


    
    //Serial.println(1);  
  }
  //Serial.print('test');
  //followBall(testdata , strip.Color(0, 0, 255));
  // testdata++;

  
  //  // Some example procedures showing how to display to the pixels:
//  colorWipe(strip.Color(255, 0, 0), 10); // Red
//  colorWipe(strip.Color(0, 255, 0), 20); // Green
//  colorWipe(strip.Color(0, 0, 255), 10); // Blue
//  // Send a theater pixel chase in...
//  theaterChase(strip.Color(127, 127, 127), 50); // White
//  theaterChase(strip.Color(127,   0,   0), 50); // Red
//  theaterChase(strip.Color(  0,   0, 127), 50); // Blue
//
//  rainbow(20);
//  rainbowCycle(20);
//  theaterChaseRainbow(50);
}
void followBall(uint16_t led, uint32_t color){
  strip.setPixelColor(led, color);
  strip.show();
}
// Fill the dots one after the other with a color
void colorWipe(uint32_t c, uint8_t wait) {
  for(uint16_t i=0; i<strip.numPixels(); i++) {
      strip.setPixelColor(i, c);
      strip.show();
      delay(wait);
  }
}

void rainbow(uint8_t wait) {
  uint16_t i, j;

  for(j=0; j<256; j++) {
    for(i=0; i<strip.numPixels(); i++) {
      strip.setPixelColor(i, Wheel((i+j) & 255));
    }
    strip.show();
    delay(wait);
  }
}

// Slightly different, this makes the rainbow equally distributed throughout
void rainbowCycle(uint8_t wait) {
  uint16_t i, j;

  for(j=0; j<256*5; j++) { // 5 cycles of all colors on wheel
    for(i=0; i< strip.numPixels(); i++) {
      strip.setPixelColor(i, Wheel(((i * 256 / strip.numPixels()) + j) & 255));
    }
    strip.show();
    delay(wait);
  }
}

//Theatre-style crawling lights.
void theaterChase(uint32_t c, uint8_t wait) {
  for (int j=0; j<10; j++) {  //do 10 cycles of chasing
    for (int q=0; q < 3; q++) {
      for (int i=0; i < strip.numPixels(); i=i+3) {
        strip.setPixelColor(i+q, c);    //turn every third pixel on
      }
      strip.show();
     
      delay(wait);
     
      for (int i=0; i < strip.numPixels(); i=i+3) {
        strip.setPixelColor(i+q, 0);        //turn every third pixel off
      }
    }
  }
}

//Theatre-style crawling lights with rainbow effect
void theaterChaseRainbow(uint8_t wait) {
  for (int j=0; j < 256; j++) {     // cycle all 256 colors in the wheel
    for (int q=0; q < 3; q++) {
        for (int i=0; i < strip.numPixels(); i=i+3) {
          strip.setPixelColor(i+q, Wheel( (i+j) % 255));    //turn every third pixel on
        }
        strip.show();
       
        delay(wait);
       
        for (int i=0; i < strip.numPixels(); i=i+3) {
          strip.setPixelColor(i+q, 0);        //turn every third pixel off
        }
    }
  }
}

// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
uint32_t Wheel(byte WheelPos) {
  if(WheelPos < 85) {
   return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
  } else if(WheelPos < 170) {
   WheelPos -= 85;
   return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  } else {
   WheelPos -= 170;
   return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
}

