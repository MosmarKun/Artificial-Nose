#include <Wire.h>
#include <map>
#include <vector>
#include <cmath>
#include <Multichannel_Gas_GMXXX.h>
#include <TFT_eSPI.h>
#undef min
#include <limits>
TFT_eSPI tft;
GAS_GMXXX<TwoWire> gas;
TFT_eSprite spr = TFT_eSprite(&tft);  // Sprite 
const int bufferSize = 25;  // Number of values to store for each sensor
// Create vectors to store the last 50 values for each sensor
std::vector<float> no2Values(bufferSize, 0.0);
std::vector<float> c2h5chValues(bufferSize, 0.0);
std::vector<float> vocValues(bufferSize, 0.0);
std::vector<float> coValues(bufferSize, 0.0);

// Create float variables to store the differences for each sensor
float no2Difference = 0.0;
float c2h5chDifference = 0.0;
float vocDifference = 0.0;
float coDifference = 0.0;
int M = 0;


String predict(std::map<String, std::vector<float>> calculatedData, std::vector<float> sensorValues) {
  String closestDataName = "Unknown";
  float minDist = std::numeric_limits<float>::max();

  for (const auto& entry : calculatedData) {
    const std::vector<float>& calculatedValues = entry.second;
    float distance = 0.0;

    // Calculate the Euclidean distance
    for (size_t i = 0; i < sensorValues.size(); ++i) {
      distance += pow(sensorValues[i] - calculatedValues[i], 2);
    }
    distance = sqrt(distance);

    if (distance < minDist) {
      minDist = distance;
      closestDataName = entry.first;
    }
  }

  return closestDataName;
}




void setup() {
  // put your setup code here, to run once:
  tft.begin();
  tft.setRotation(3);
  spr.createSprite(tft.width(),tft.height()); 
  gas.begin(Wire, 0x08);
  pinMode(WIO_5S_PRESS, INPUT_PULLUP);
}

void loop() {
  // put your main code here, to run repeatedly:
  float no2, c2h5ch, voc, co;


  no2 = gas.getGM102B(); 
  c2h5ch = gas.getGM302B(); 
  voc = gas.getGM502B(); 
  co = gas.getGM702B(); 
  // Create a vector with the sensor values
  std::vector<float> sensorValues = {no2, c2h5ch, voc, co};

  // Add your calculated data to the map
  std::map<String, std::vector<float>> calculatedData;

  calculatedData["Air"] = {228.44, 135.67, 142.34, 131.51};
  calculatedData["Air"] = {300.44, 250.67, 240.34, 104.51};
  calculatedData["Perfume"] = {787.81, 862.09, 869.70, 852.43};
  calculatedData["Rose"] = {601.00, 502.00, 506.00, 147.00};
  calculatedData["Coffee"] = {690.38, 683.69, 696.01, 320.95};

    // Add the latest values to the vectors
  no2Values.push_back(no2);
  c2h5chValues.push_back(c2h5ch);
  vocValues.push_back(voc);
  coValues.push_back(co);

  if (no2Values.size() > bufferSize) {
    no2Values.erase(no2Values.begin());
  }
  if (c2h5chValues.size() > bufferSize) {
    c2h5chValues.erase(c2h5chValues.begin());
  }
  if (vocValues.size() > bufferSize) {
    vocValues.erase(vocValues.begin());
  }
  if (coValues.size() > bufferSize) {
    coValues.erase(coValues.begin());
  }

// Calculate the difference between the last and first value in each Values vector for all sensors
if (no2Values.size() == bufferSize) {
  if (no2Values.front() - no2 > no2 - no2Values.front()) {
    no2Difference = no2Values.front() - no2 +7;
  } else if (no2Values.front() - no2 < no2 - no2Values.front()) {
    no2Difference = no2 - no2Values.front();
  } else {
    no2Difference = 0;
  }
}

if (c2h5chValues.size() == bufferSize) {
  if (c2h5chValues.front() - c2h5ch > c2h5ch - c2h5chValues.front()) {
    c2h5chDifference = c2h5chValues.front() - c2h5ch +7;
  } else if (c2h5chValues.front() - c2h5ch < c2h5ch - c2h5chValues.front()) {
    c2h5chDifference = c2h5ch - c2h5chValues.front();
  } else {
    c2h5chDifference = 0;
  }
}

if (vocValues.size() == bufferSize) {
  if (vocValues.front() - voc > voc - vocValues.front()) {
    vocDifference = vocValues.front() - voc+7;
  } else if (vocValues.front() - voc < voc - vocValues.front()) {
    vocDifference = voc - vocValues.front();
  } else {
    vocDifference = 0;
  }
}

if (coValues.size() == bufferSize) {
  if (coValues.front() - co > co - coValues.front()) {
    coDifference = coValues.front() - co +7;
  } else if (coValues.front() - co < co - coValues.front()) {
    coDifference = co - coValues.front();
  } else {
    coDifference = 0;
  }
}
  
  // Check if all differences are less than 10 to determine if you can predict
  bool canPredict = ((no2Difference) < 10.0 && 
                     (c2h5chDifference) < 10.0 && 
                     (vocDifference) < 10.0 && 
                     (coDifference) < 150.0); 
  
  String dataName = "Predicting";
  if (canPredict) {
      // Predict the data name based on sensor values
   dataName = predict(calculatedData, sensorValues);
  }


  float val;
  spr.fillSprite(TFT_BLACK);
  spr.setFreeFont(&FreeSansBoldOblique18pt7b); 
  spr.setTextColor(TFT_BLUE);
  spr.drawString("Predict: " + dataName, 10, 10 , 1);// Print the test text in the custom font
  for(int8_t line_index = 0;line_index < 5 ; line_index++)
  {
    spr.drawLine(0, 50 + line_index, tft.width(), 50 + line_index, TFT_GREEN);
  }
  spr.setFreeFont(&FreeSansBoldOblique9pt7b);
  if (digitalRead(WIO_5S_PRESS) == LOW) { 
    if(M == 0){
      M = 1;
    }
    else{
      M = 0;
    }
  }  
  if (M == 0) {
  // GM102B NO2 sensor
  val = no2Difference;
  if (val > 999) val = 999;
  spr.setTextColor(TFT_WHITE);
  spr.drawString("NO2:", 60 - 24, 100 -24 , 1);// Print the test text in the custom font
  spr.drawRoundRect(60 - 24,100,80,40,5,TFT_WHITE); 
  spr.setTextColor(TFT_WHITE);
  spr.drawNumber(val,60 - 20,100+10,1);
  spr.setTextColor(TFT_GREEN);
  // GM302B C2H5CH sensor
  val = c2h5chDifference;
  if (val > 999) val = 999;
  spr.setTextColor(TFT_WHITE);
  spr.drawString("C2H5CH:", 230 -24 , 100 - 24 , 1);// Print the test text in the custom font
  spr.drawRoundRect(230 - 24,100,80,40,5,TFT_WHITE);
  spr.setTextColor(TFT_WHITE);
  spr.drawNumber(val,230 - 20,100+10,1);
  spr.setTextColor(TFT_GREEN);
  // GM502B VOC sensor
  val = vocDifference;
  if (val > 999) val = 999;
  spr.setTextColor(TFT_WHITE);
  spr.drawString("VOC:", 60 - 24, 180 -24 , 1);// Print the test text in the custom font
  spr.drawRoundRect(60 - 24,180,80,40,5,TFT_WHITE);
  spr.setTextColor(TFT_WHITE);
  spr.drawNumber(val,60 - 20,180+10,1);
  spr.setTextColor(TFT_GREEN);
  // GM702B CO sensor
  val = coDifference;
  if (val > 999) val = 999;
  spr.setTextColor(TFT_WHITE);
  spr.drawString("CO:", 230 -24 , 180 - 24, 1);// Print the test text in the custom font
  spr.drawRoundRect(230 - 24 ,180,80,40,5,TFT_WHITE);
  spr.setTextColor(TFT_WHITE);
  spr.drawNumber(val ,230 - 20 ,180+10,1);
  spr.setTextColor(TFT_GREEN);
  
  spr.pushSprite(0, 0);
  } 
  else{
    // GM102B NO2 sensor
  val = no2;
  if (val > 999) val = 999;
  spr.setTextColor(TFT_WHITE);
  spr.drawString("NO2:", 60 - 24, 100 -24 , 1);// Print the test text in the custom font
  spr.drawRoundRect(60 - 24,100,80,40,5,TFT_WHITE); 
  spr.setTextColor(TFT_WHITE);
  spr.drawNumber(val,60 - 20,100+10,1);
  spr.setTextColor(TFT_GREEN);
  // GM302B C2H5CH sensor
  val = c2h5ch;
  if (val > 999) val = 999;
  spr.setTextColor(TFT_WHITE);
  spr.drawString("C2H5CH:", 230 -24 , 100 - 24 , 1);// Print the test text in the custom font
  spr.drawRoundRect(230 - 24,100,80,40,5,TFT_WHITE);
  spr.setTextColor(TFT_WHITE);
  spr.drawNumber(val,230 - 20,100+10,1);
  spr.setTextColor(TFT_GREEN);
  // GM502B VOC sensor
  val = voc;
  if (val > 999) val = 999;
  spr.setTextColor(TFT_WHITE);
  spr.drawString("VOC:", 60 - 24, 180 -24 , 1);// Print the test text in the custom font
  spr.drawRoundRect(60 - 24,180,80,40,5,TFT_WHITE);
  spr.setTextColor(TFT_WHITE);
  spr.drawNumber(val,60 - 20,180+10,1);
  spr.setTextColor(TFT_GREEN);
  // GM702B CO sensor
  val = co;
  if (val > 999) val = 999;
  spr.setTextColor(TFT_WHITE);
  spr.drawString("CO:", 230 -24 , 180 - 24, 1);// Print the test text in the custom font
  spr.drawRoundRect(230 - 24 ,180,80,40,5,TFT_WHITE);
  spr.setTextColor(TFT_WHITE);
  spr.drawNumber(val ,230 - 20 ,180+10,1);
  spr.setTextColor(TFT_GREEN);
  
  spr.pushSprite(0, 0);
  }
    // Print the data in the desired format
  Serial.print(no2);
  Serial.print(",");
  Serial.print(c2h5ch);
  Serial.print(",");
  Serial.print(voc);
  Serial.print(",");
  Serial.println(co);
  
  delay(100);

}
