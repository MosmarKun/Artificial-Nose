#include <TFT_eSPI.h>
#include <Multichannel_Gas_GMXXX.h>
#include <Wire.h>
GAS_GMXXX<TwoWire> gas;

TFT_eSPI tft; 
// Stock font and GFXFF reference handle
TFT_eSprite spr = TFT_eSprite(&tft);  // Sprite 

void setup() {
  // put your setup code here, to run once:
  tft.begin();
  tft.setRotation(3);
  spr.createSprite(tft.width(), tft.height()); 
  gas.begin(Wire, 0x08); // use the hardware I2C
  Serial.begin(9600);  // Initialize the serial communication
}

void loop() {
  // put your main code here, to run repeatedly:
  int val;

  // Initialize variables to store sensor readings
  int NO2, C2H5CH, VOC, CO;

  // GM102B NO2 sensor
  NO2 = gas.getGM102B();
  if (NO2 > 999) NO2 = 999;

  // GM302B C2H5CH sensor
  C2H5CH = gas.getGM302B();
  if (C2H5CH > 999) C2H5CH = 999;

  // GM502B VOC sensor
  VOC = gas.getGM502B();
  if (VOC > 999) VOC = 999;

  // GM702B CO sensor
  CO = gas.getGM702B();
  if (CO > 999) CO = 999;

  // Print the data in the desired format
  Serial.print(NO2);
  Serial.print(",");
  Serial.print(C2H5CH);
  Serial.print(",");
  Serial.print(VOC);
  Serial.print(",");
  Serial.println(CO);

  delay(100);
}