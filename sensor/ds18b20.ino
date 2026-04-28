#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define ONE_WIRE_BUS 2
#define FAN_PIN 9

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);
  sensors.begin();
  pinMode(FAN_PIN, OUTPUT);

  lcd.init();
  lcd.backlight();
}

void loop() {
  sensors.requestTemperatures();
  float suhu = sensors.getTempCByIndex(0);

  bool fanStatus;

  if (suhu > 35) {
    digitalWrite(FAN_PIN, HIGH);
    fanStatus = true;
  } else {
    digitalWrite(FAN_PIN, LOW);
    fanStatus = false;
  }

  // Serial
  Serial.println(suhu);

  // LCD
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("S:");
  lcd.print(suhu);
  lcd.print("C");

  lcd.setCursor(0, 1);
  lcd.print("Fan: ");
  if (fanStatus) {
    lcd.print("ON");
  } else {
    lcd.print("OFF");
  }

  delay(1000);
}
