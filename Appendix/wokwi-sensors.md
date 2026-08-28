# Приложение. Каталог датчиков и модулей для симулятора Wokwi

Этот раздел относится к **запасному треку курса**: работе в симуляторе [Wokwi](https://wokwi.com/) вместо реального оборудования. Он нужен, если вы пропустили занятие, доделываете задачу дома или хотите проверить идею до сборки схемы.

Здесь собраны компоненты, которых **нет в учебном наборе**, но которые доступны в симуляторе: ультразвуковой дальномер HC-SR04, DHT22, DS1307, PIR-датчик движения, термистор NTC, DS18B20, акселерометр MPU6050, тензодатчик HX711, поворотный энкодер KY-040, драйверы шаговых двигателей.

Компоненты, которые есть в наборе, описаны в [справочнике по железу](../Hardware/README.md), а работа с ними - в соответствующих занятиях.

> Ссылки на проекты Wokwi в тексте ведут на готовые примеры, которые можно открыть и запустить в браузере.

---

В этой теме студенты будут изучать различные типы датчиков и сенсоров, а также научатся подключать и программировать их с использованием Arduino. Они узнают, как считывать данные с датчиков, анализировать их и использовать полученные значения для управления другими устройствами.

Доступные сенсоры в [wokwi](https://docs.wokwi.com/getting-started/supported-hardware#sensors)
### Сенсоры
|Название|Описание|
|-|-|
|[HC-SR04](https://docs.wokwi.com/parts/wokwi-hc-sr04)|HC-SR04 Ультразвуковой датчик расстояния|
|[DHT22](https://docs.wokwi.com/parts/wokwi-dht22)|Цифровой датчик влажности и температуры|
|[DS1307 RTC](https://docs.wokwi.com/parts/wokwi-ds1307)|Модуль RTC (часы реального времени) с интерфейсом I2C и 56 байтами NV SRAM|
|[PIR Motion Sensor](https://docs.wokwi.com/parts/wokwi-pir-motion-sensor)|Пассивный инфракрасный (PIR) датчик движения|
|[Аналоговый датчик температуры (NTC)](https://docs.wokwi.com/parts/wokwi-ntc-temperature-sensor)|Аналоговый датчик температуры: NTC (отрицательный температурный коэффициент) термистор|
|DS18B20 Датчик температуры|Однопроводной цифровой датчик температуры|
|[MPU6050](https://docs.wokwi.com/parts/wokwi-mpu6050)|Интегрированный датчик с 3-осевым акселерометром, 3-осевым гироскопом и датчиком температуры с интерфейсом I2C|
|[Фоторезистор](https://docs.wokwi.com/parts/wokwi-photoresistor-sensor)|Фоторезисторный (LDR) датчик|
|[Тензодатчик HX711](https://docs.wokwi.com/parts/wokwi-hx711)|Усилитель тензодатчика HX711 с тензодатчиком 5 кг/50 кг/габариты|

#### Примеры
##### [HC-SR04](https://docs.wokwi.com/parts/wokwi-hc-sr04)
```c++
#include <SevSeg.h>

#define TRIG_PIN A3
#define ECHO_PIN A4

SevSeg sevseg;

void setup()
{
  uint8_t numDigits     = 4;
  uint8_t digitPins[]   = {2, 3, 4, 5};
  uint8_t segmentPins[] = {6, 7, 8, 9, 10, 11, 12, 13};
  uint8_t displayType   = COMMON_ANODE; // (Общий анод или общий катод)

  bool resistorsOnSegments = false;
  bool updateWithDelays    = false;
  bool leadingZeros        = false;
  bool disableDecPoint     = false;

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  sevseg.begin(displayType, numDigits, digitPins, segmentPins, resistorsOnSegments,
               updateWithDelays, leadingZeros, disableDecPoint);
  sevseg.setBrightness(90);
}

void loop()
{
  static uint32_t interval = 0;
  static uint16_t duration = 0;
  static float distance    = 0;

  if ((millis() - interval) >= 100) {
    interval = millis();

    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(5);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // Чтение времени сигналов на пинах TRIG и ECHO
    duration = pulseIn(ECHO_PIN, HIGH);

    // Расчет расстояния
    distance = (duration / 2) / 29;

    sevseg.setNumber(distance);
  }
  sevseg.refreshDisplay();
}
```
-   Библиотека  `SevSeg`  используется для управления 7-сегментным дисплеем.
-   Пины  `TRIG_PIN`  и  `ECHO_PIN`  определены для подключения датчика расстояния HC-SR04.
-   В функции  `setup()`  настраиваются пины и параметры дисплея.
-   В функции  `loop()`  происходит измерение расстояния и его отображение на дисплее.
-   Переменные  `interval`,  `duration`  и  `distance`  объявлены как статические, чтобы сохранять их значения между итерациями цикла  `loop()`.
##### [DHT22](https://docs.wokwi.com/parts/wokwi-dht22)
```c++
#include <dht.h>

dht DHT;

#define DHT22_PIN 5

struct {
  uint32_t total;
  uint32_t ok;
  uint32_t crc_error;
  uint32_t time_out;
  uint32_t connect;
  uint32_t ack_l;
  uint32_t ack_h;
  uint32_t unknown;
} stat = { 0, 0, 0, 0, 0, 0, 0, 0};

void setup() {
  Serial.begin(115200);
  Serial.println("dht22_test.ino");
  Serial.print("ВЕРСИЯ БИБЛИОТЕКИ: ");
  Serial.println(DHT_LIB_VERSION);
  Serial.println();
  Serial.println("Тип,\tСтатус,\tВлажность (%),\tТемпература (C)\tВремя (мкс)");
}

void loop() {
  readSensorData();
  displayData();
  delay(2000);
}

void readSensorData() {
  Serial.print("DHT22, \t");

  uint32_t start = micros();
  int chk = DHT.read22(DHT22_PIN);
  uint32_t stop = micros();

  stat.total++;
  switch (chk)
  {
    case DHTLIB_OK:
      stat.ok++;
      Serial.print("OK,\t");
      break;
    case DHTLIB_ERROR_CHECKSUM:
      stat.crc_error++;
      Serial.print("Ошибка контрольной суммы,\t");
      break;
    case DHTLIB_ERROR_TIMEOUT:
      stat.time_out++;
      Serial.print("Ошибка тайм-аута,\t");
      break;
    case DHTLIB_ERROR_CONNECT:
      stat.connect++;
      Serial.print("Ошибка подключения,\t");
      break;
    case DHTLIB_ERROR_ACK_L:
      stat.ack_l++;
      Serial.print("Ошибка ACK Low,\t");
      break;
    case DHTLIB_ERROR_ACK_H:
      stat.ack_h++;
      Serial.print("Ошибка ACK High,\t");
      break;
    default:
      stat.unknown++;
      Serial.print("Неизвестная ошибка,\t");
      break;
  }
}

void displayData() {
  Serial.print(DHT.humidity, 1);
  Serial.print(",\t");
  Serial.print(DHT.temperature, 1);
  Serial.print(",\t");
  Serial.print(stop - start);
  Serial.println();

  if (stat.total % 20 == 0)
  {
    Serial.println("\nВСЕГО\tOK\tCRC\tTO\tCON\tACK_L\tACK_H\tUNK");
    Serial.print(stat.total);
    Serial.print("\t");
    Serial.print(stat.ok);
    Serial.print("\t");
    Serial.print(stat.crc_error);
    Serial.print("\t");
    Serial.print(stat.time_out);
    Serial.print("\t");
    Serial.print(stat.connect);
    Serial.print("\t");
    Serial.print(stat.ack_l);
    Serial.print("\t");
    Serial.print(stat.ack_h);
    Serial.print("\t");
    Serial.print(stat.unknown);
    Serial.println("\n");
  }
}
```

- В данном коде используется библиотека `dht.h` для работы с датчиком `DHT22`. Код считывает данные с датчика и выводит их на последовательный порт.
- В функции `setup()` происходит инициализация последовательного порта и вывод информации о версии библиотеки.
- В функции `loop()` происходит считывание данных с датчика и их вывод на последовательный порт. Также в функции происходит обновление статистики и вывод ее значений каждые 20 итераций.
- В функции `readSensorData()`  происходит считывание данных с датчика
- В функции `displayData()` происходит вывод данных на последовательный порт.

##### [DS1307 RTC](https://docs.wokwi.com/parts/wokwi-ds1307)

[Пример](https://wokwi.com/projects/376383354533106689)
```c++
#include "RTClib.h"

RTC_DS1307 rtc;

enum DaysOfTheWeek {
  Sunday,
  Monday,
  Tuesday,
  Wednesday,
  Thursday,
  Friday,
  Saturday
};

void setup() {
  Serial.begin(115200);

  if (!rtc.begin()) {
    Serial.println("Failed to find RTC");
    Serial.flush();
    abort();
  }
}

void loop() {
  DateTime now = rtc.now();

  printCurrentTime(now);

  Serial.println();
  delay(3000);
}

void printCurrentTime(DateTime now) {
  Serial.print("Current time: ");
  Serial.print(now.year(), DEC);
  Serial.print('/');
  Serial.print(now.month(), DEC);
  Serial.print('/');
  Serial.print(now.day(), DEC);
  Serial.print(" (");
  Serial.print(getDayOfWeekString(now.dayOfTheWeek()));
  Serial.print(") ");
  Serial.print(now.hour(), DEC);
  Serial.print(':');
  Serial.print(now.minute(), DEC);
  Serial.print(':');
  Serial.print(now.second(), DEC);
  Serial.println();
}

String getDayOfWeekString(int dayOfWeek) {
  switch (dayOfWeek) {
    case Sunday:
      return "Sunday";
    case Monday:
      return "Monday";
    case Tuesday:
      return "Tuesday";
    case Wednesday:
      return "Wednesday";
    case Thursday:
      return "Thursday";
    case Friday:
      return "Friday";
    case Saturday:
      return "Saturday";
    default:
      return "Invalid day";
  }
}
```
В данном коде мы используем библиотеку `RTClib` для работы с модулем `RTC (Real-Time Clock)`. Мы объявляем объект `rtc` типа `RTC_DS1307`, который представляет собой модуль `RTC DS1307`.

Функция `printCurrentTime` для печати текущего времени.

Создана отдельная функция `getDayOfWeekString` для преобразования целого числа дня недели в строковое представление.

После вывода текущего времени мы добавляем пустую строку и задержку в `3` секунды с помощью функции `delay(3000)`.

`Enums` (перечисления) используются в программировании для определения набора именованных значений. Они предоставляют способ представления фиксированного числа возможных значений переменной. В предоставленном коде перечисление `DaysOfTheWeek` используется для представления дней недели.

>Использование `enum` имеет несколько преимуществ:
>- Читабельность: перечисления делают код более читабельным и понятным. Вместо использования произвольных чисел или строк для представления значений перечисления предоставляют осмысленные имена, передающие назначение переменной.
>- Безопасность типов. Перечисления обеспечивают безопасность типов, ограничивая возможные значения, которые может принимать переменная. В случае `DaysOfTheWeek` переменная может иметь только одно из семи предопределенных значений, что предотвращает случайное присвоение недопустимых значений.
>- Ясность кода. Перечисления улучшают ясность кода, предоставляя четкий и краткий способ определения набора связанных значений. Они делают код более удобным в сопровождении и понятным для других разработчиков.
>- Согласованность кода. Перечисления помогают поддерживать согласованность во всей кодовой базе. При использовании перечислений все экземпляры определенной переменной будут иметь одинаковый набор возможных значений, что обеспечивает согласованность и снижает вероятность ошибок.

Таким образом, перечисления используются для улучшения читаемости кода, безопасности типов, ясности кода и его согласованности. Они предоставляют удобный способ определения набора связанных значений и делают код более удобным в сопровождении и понятным.

##### [PIR Motion Sensor](https://docs.wokwi.com/parts/wokwi-pir-motion-sensor)

```c++
// Pin assignments
const int ledPin = 13;         // Pin for the LED
const int inputPin = 2;        // Pin for the PIR sensor

// Variables
int pirState = LOW;            // Assume no motion detected initially

void setup() {
  pinMode(ledPin, OUTPUT);     // Set LED pin as output
  pinMode(inputPin, INPUT);    // Set PIR sensor pin as input

  Serial.begin(9600);          // Initialize serial communication
}

void loop() {
  int val = digitalRead(inputPin);  // Read input value from PIR sensor

  if (val == HIGH) {                 // Check if motion is detected
    digitalWrite(ledPin, HIGH);      // Turn on the LED

    if (pirState == LOW) {
      // Motion has just been detected
      Serial.println("Motion detected!");
      pirState = HIGH;
    }
  } else {
    digitalWrite(ledPin, LOW);       // Turn off the LED

    if (pirState == HIGH) {
      // Motion has just ended
      Serial.println("Motion ended!");
      pirState = LOW;
    }
  }
}
```
Предоставленный код представляет собой простой тестер датчика `PIR` (пассивного инфракрасного излучения). Он использует `PIR`-датчик для обнаружения движения и включает светодиод при обнаружении движения.

- Назначение контактов выполнено для светодиода и `PIR`-датчика.
- Функция `setup()` вызывается один раз в начале программы. Он устанавливает контакт светодиода как выход, а контакт `PIR`-датчика как вход. Он также инициализирует последовательную связь.
- Функция `loop()` вызывается неоднократно. Он считывает входное значение с `PIR`-датчика с помощью функции `digitalRead()`.
- Если обнаружено движение (входное значение `HIGH`), светодиод включается с помощью функции `digitalWrite()`.
- - Если переменная `pirState` имеет значение `LOW`, это означает, что движение только что было обнаружено. В этом случае появится сообщение `"Обнаружено движение!"` выводится на последовательный монитор с помощью функции `Serial.println()`, а переменная `pirState` обновляется до `HIGH`.
- Если движение не обнаружено (входное значение `LOW`), светодиод выключается.
- - Если переменная `pirState` имеет значение `HIGH`, это означает, что движение только что закончилось. В этом случае появится сообщение "Движение окончено!" выводится на последовательный монитор, а переменная `pirState` обновляется до `LOW`.

> Этот код позволяет вам проверить функциональность PIR-датчика, наблюдая за включением и выключением светодиода при обнаружении движения.

##### [Analog Temperature Sensor (NTC)](https://docs.wokwi.com/parts/wokwi-ntc-temperature-sensor)
[Пример](https://wokwi.com/projects/376383375187961857)
```c++
/**
  Basic NTC Thermistor demo
  https://wokwi.com/arduino/projects/299330254810382858

  Assumes a 10K@25 degC NTC thermistor connected in series with a 10K resistor.

  Copyright (C) 2021, Uri Shaked
*/

const float BETA = 3950; // should match the Beta Coefficient of the thermistor

void setup() {
  Serial.begin(9600);
}

void loop() {
  int analogValue = analogRead(A0);
  float celsius = calculateTemperature(analogValue);
  printTemperature(celsius);
  delay(1000);
}

float calculateTemperature(int analogValue) {
  float resistance = 1023.0 / analogValue - 1;
  resistance = 10000.0 / resistance;
  float steinhart;
  steinhart = resistance / 10000.0; // (R/Ro)
  steinhart = log(steinhart); // ln(R/Ro)
  steinhart /= BETA; // 1/B * ln(R/Ro)
  steinhart += 1.0 / 298.15; // + (1/To)
  steinhart = 1.0 / steinhart; // Invert
  steinhart -= 273.15; // Convert to Celsius
  return steinhart;
}

void printTemperature(float celsius) {
  Serial.print("Temperature: ");
  Serial.print(celsius);
  Serial.println(" degC");
}
```
- Код считывает аналоговое значение с контакта `A0`, который подключен к термистору `NTC`. Термистор `NTC` - это тип резистора, сопротивление которого меняется в зависимости от температуры. Измерив сопротивление термистора, мы можем рассчитать температуру.

- Код предполагает, что термистор `NTC`  имеет значение 10K при 25 degC подключен последовательно с резистором 10K. Значение константы `beta` должно соответствовать коэффициенту бета используемого термистора.

- В функции настройки код инициализирует последовательную связь со скоростью `9600` бод.

- В функции цикла код считывает аналоговое значение с контакта `A0`, используя функцию `AnalogRead`. Затем он вызывает функцию `CalculTemperature` для преобразования аналогового значения в температуру в градусах Цельсия. Рассчитанная температура затем передается в функцию `printTemperature`, которая выводит ее на последовательный монитор.

- Затем код ждет 1 секунду, используя функцию задержки, прежде чем повторить процесс.

В целом, этот код демонстрирует базовую реализацию измерения температуры с использованием термистора `NTC` и `Arduino`. Его можно использовать в качестве отправной точки для более продвинутых проектов по измерению температуры.
##### DS18B20 Temperature Sensor

[Пример](https://wokwi.com/projects/376383156031357953)
```c++
#include <OneWire.h>
#include <DallasTemperature.h>

// Data wire is connected to the Arduino digital pin 4
#define ONE_WIRE_BUS 4

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to the Dallas Temperature sensor
DallasTemperature sensors(&oneWire);

void setup(void)
{
  // Start serial communication for debugging purposes
  Serial.begin(9600);

  // Start up the library
  sensors.begin();
}

void loop(void)
{
  // Call sensors.requestTemperatures() to issue a global temperature request to all devices on the bus
  sensors.requestTemperatures();

  Serial.print("Celsius temperature: ");
  // Why "byIndex"? You can have more than one IC on the same bus. 0 refers to the first IC on the wire
  Serial.print(sensors.getTempCByIndex(0));
  Serial.print(" - Fahrenheit temperature: ");
  Serial.println(sensors.getTempFByIndex(0));

  delay(1000);
}
```
Этот код используется для считывания данных о температуре с датчика температуры Далласа, подключенного к плате Arduino. Вот как это работает:

- В код включены необходимые библиотеки: `OneWire` и `DallasTemperature`.
- Провод данных датчика подключен к цифровому контакту `4` `Arduino` (`#define ONE_WIRE_BUS 4`).
- Создается экземпляр класса `OneWire`, которому в качестве параметра передается вывод провода передачи данных.
- Создается экземпляр класса `DallasTemperature`, которому передается экземпляр `OneWire` в качестве параметра.
- В функции `setup()` для целей отладки запускается последовательная связь со скоростью 9600 бод. Также инициализируется библиотека `DallasTemperature`.
- В функции `loop()` вызывается функция `Sensors.requestTemperatures()` для выдачи глобального запроса температуры всем устройствам на шине.
- Температура в градусах Цельсия получается с помощью` Sensors.getTempCByIndex(0)` и выводится на последовательный монитор.
- Температура в градусах Фаренгейта получается с помощью `Sensors.getTempFByIndex(0)` и выводится на последовательный монитор.
- Затем программа ждет 1 секунду, прежде чем повторить процесс.

Этот код позволяет считывать данные о температуре с датчика температуры Далласа и отображать их на последовательном мониторе.

##### [MPU6050](https://docs.wokwi.com/parts/wokwi-mpu6050)

[Пример](https://wokwi.com/projects/376383475393036289)
```c++
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

void setup() {
  Serial.begin(115200);

  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("");
  delay(100);
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  Serial.print(a.acceleration.x);
  Serial.print(",");
  Serial.print(a.acceleration.y);
  Serial.print(",");
  Serial.print(a.acceleration.z);
  Serial.print(", ");
  Serial.print(g.gyro.x);
  Serial.print(",");
  Serial.print(g.gyro.y);
  Serial.print(",");
  Serial.print(g.gyro.z);
  Serial.println("");

  delay(10);
}
```
Этот код используется для взаимодействия с датчиком `MPU6050` и считывания значений его акселерометра и гироскопа. `MPU6050` - широко используемый датчик для измерения движения и ориентации.

- Необходимые библиотеки включены в начале кода. Эти библиотеки предоставляют функции и определения для работы с датчиком `MPU6050` и связью `I2C`.

- Функция `setup()` вызывается один раз в начале программы. Он инициализирует последовательную связь со скоростью `115200` бод и проверяет, обнаружен ли чип `MPU6050`. Если чип не найден, на последовательный монитор выводится сообщение об ошибке.

- Диапазоны датчиков и полоса пропускания фильтра устанавливаются с помощью функций `mpu.setAccelerometerRange()`, `mpu.setGyroRange()` и `mpu.setFilterBandwidth()`. Эти функции настраивают датчик для измерения движения в определенных диапазонах и фильтрации шума.

- Функция `loop()` вызывается повторно после функции `setup()`. Он считывает значения акселерометра и гироскопа с датчика `MPU6050` с помощью функции `mpu.getEvent()`. Значения датчика хранятся в переменных `a (акселерометр)`, `g (гироскоп)` и `temp (температура)`.

- Значения акселерометра и гироскопа выводятся на последовательный монитор с помощью функций `Serial.print()` и `Serial.println()`. Значения разделяются запятыми, чтобы их было легче читать и анализировать.

- Задержка в `10` миллисекунд добавляется с помощью функции `delay()` для управления скоростью, с которой данные датчика считываются и распечатываются. Эта задержка гарантирует, что программа не перегружает последовательный монитор данными.

Запустив этот код на плате `Arduino`, подключенной к датчику `MPU6050`, вы сможете увидеть значения акселерометра и гироскопа в реальном времени в последовательном мониторе. Это может быть полезно для мониторинга движения и ориентации в различных приложениях, таких как робототехника, дроны и системы отслеживания движения.

##### [Photoresistor](https://docs.wokwi.com/parts/wokwi-photoresistor-sensor)
```c++
// Include the LiquidCrystal_I2C library
#include <LiquidCrystal_I2C.h>

// Define the pin for the Light Dependent Resistor (LDR)
#define LDR_PIN 2

// Create an instance of the LiquidCrystal_I2C class
LiquidCrystal_I2C lcd(0x27, 20, 4);

// Setup function runs once at the start of the program
void setup() {
  // Set the LDR pin as an input
  pinMode(LDR_PIN, INPUT);

  // Initialize the LCD
  lcd.init();

  // Turn on the backlight of the LCD
  lcd.backlight();
}

// Loop function runs repeatedly after the setup function
void loop() {
  // Set the cursor position on the LCD
  lcd.setCursor(2, 0);

  // Print the label for the light level
  lcd.print("Room: ");

  // Check the light level using the LDR pin
  if (digitalRead(LDR_PIN) == LOW) {
    // If the light level is low, print "Light!"
    lcd.print("Light!");
  } else {
    // If the light level is high, print "Dark"
    lcd.print("Dark  ");
  }

  // Delay for a short period of time
  delay(100);
}
```
Код использует библиотеку `LiquidCrystal_I2C` для управления ЖК-экраном, подключенным к плате Arduino. ЖК-экран представляет собой дисплей размером `20х4` символа.

- В функции `setup()` код устанавливает вывод `LDR` в качестве входа и инициализирует ЖК-экран. Также включается подсветка ЖК-дисплея.

- В функции `loop()` код постоянно проверяет уровень освещенности, используя вывод `LDR`. Если уровень освещенности низкий (темная комната), печатается `"Свет!"` на ЖК-экране. Если уровень освещенности высокий (яркая комната), на ЖК-экране отображается надпись `"Темно"`. Позиция курсора устанавливается на `(2, 0)` для отображения текста во втором столбце первой строки.

- Функция `delay (100)` используется для введения небольшой задержки в `100` миллисекунд между каждой итерацией цикла. Это предотвращает слишком быстрое обновление ЖК-экрана и обеспечивает более читаемое изображение.

В целом, код позволяет контролировать уровень освещенности в комнате с помощью `LDR` и отображать результат на ЖК-экране.

##### [HX711 Load Cell](https://docs.wokwi.com/parts/wokwi-hx711)
[Пример](https://wokwi.com/projects/344192176616374868)
```c++
#include "HX711.h"

HX711 scale;

void setup() {
  Serial.begin(9600);
  Serial.println("HX710B Demo with HX711 Library");
  Serial.println("Initializing the scale");

  scale.begin(A1, A0);

  Serial.println("Before setting up the scale:");
  Serial.print("read: \t\t");
  Serial.println(scale.read());
  Serial.print("read average: \t\t");
  Serial.println(scale.read_average(20));
  Serial.print("get value: \t\t");
  Serial.println(scale.get_value(5));
  Serial.print("get units: \t\t");
  Serial.println(scale.get_units(5), 1);

  scale.set_scale(2280.f);
  scale.tare();

  Serial.println("After setting up the scale:");
  Serial.print("read: \t\t");
  Serial.println(scale.read());
  Serial.print("read average: \t\t");
  Serial.println(scale.read_average(20));
  Serial.print("get value: \t\t");
  Serial.println(scale.get_value(5));
  Serial.print("get units: \t\t");
  Serial.println(scale.get_units(5), 1);

  Serial.println("Readings:");
}

void loop() {
  Serial.print("one reading:\t");
  Serial.print(scale.get_units(), 1);
  Serial.print("\t| average:\t");
  Serial.println(scale.get_units(10), 1);
  scale.power_down();
  delay(5000);
  scale.power_up();
}
```
Приведенный код является примером использования библиотеки HX711 с платой Arduino для считывания данных с датчика давления. Код инициализирует весы, устанавливает необходимые контакты и выполняет различные операции по чтению и отображению данных датчика.

- Подключите необходимую библиотеку:
`#include "HX711.h"`

Создайте экземпляр класса HX711:
`HX711 scale;`

Настройте плату Arduino:
```c++
void setup() {
  Serial.begin(9600);
  Serial.println("HX710B Demo with HX711 Library");
  Serial.println("Initializing the scale");

  scale.begin(A1, A0);
}
```

Перед настройкой весов выполните операции:
```c++
  Serial.println("Before setting up the scale:");
  Serial.print("read: \t\t");
  Serial.println(scale.read());
  Serial.print("read average: \t\t");
  Serial.println(scale.read_average(20));
  Serial.print("get value: \t\t");
  Serial.println(scale.get_value(5));
  Serial.print("get units: \t\t");
  Serial.println(scale.get_units(5), 1);

```
Установите весы и тарируйте вес:
```c++
  scale.set_scale(2280.f);
  scale.tare();
```
Выполните операции после настройки весов:
```c++
  Serial.println("After setting up the scale:");
  Serial.print("read: \t\t");
  Serial.println(scale.read());
  Serial.print("read average: \t\t");
  Serial.println(scale.read_average(20));
  Serial.print("get value: \t\t");
  Serial.println(scale.get_value(5));
  Serial.print("get units: \t\t");
  Serial.println(scale.get_units(5), 1);

```

Чтение и отображение данных датчика в цикле:
```c++
void loop() {
  Serial.print("one reading:\t");
  Serial.print(scale.get_units(), 1);
  Serial.print("\t| average:\t");
  Serial.println(scale.get_units(10), 1);
  scale.power_down();
  delay(5000);
  scale.power_up();
}
```

В цикле код непрерывно считывает данные датчика и выводит их на последовательный монитор. Он также переводит АЦП в спящий режим на 5 секунд, а затем снова его пробуждает.

## Устройства ввода
|Название|Описание|
|-|-|
|[Кнопка](https://docs.wokwi.com/parts/wokwi-pushbutton)|12 мм Тактильная кнопка-переключатель (кратковременная кнопка)|
|[Ползунковый переключатель](https://docs.wokwi.com/parts/wokwi-slide-switch)|Стандартный однополюсный двухпозиционный (SPDT) ползунковый переключатель|
|[DIP-переключатель 8](https://docs.wokwi.com/parts/wokwi-dip-switch-8)|Набор из 8 электрических переключателей в одном корпусе|
|[Клавиатура](https://docs.wokwi.com/parts/wokwi-membrane-keypad)|Стандартная клавиатура 4х4 (для ввода цифр)|
|[Аналоговый джойстик](https://docs.wokwi.com/parts/wokwi-analog-joystick)|Аналоговый джойстик с двумя осями (горизонтальная/вертикальная) и встроенной кнопкой|
|[Потенциометр](https://docs.wokwi.com/parts/wokwi-potentiometer)|Переменный резистор с ручкой управления (линейный потенциометр)|
|[Ползунковый потенциометр](https://docs.wokwi.com/parts/wokwi-slide-potentiometer)| Ползунковый переменный резистор (линейный потенциометр)|
|[Поворотный энкодер (KY-040)](https://docs.wokwi.com/parts/wokwi-ky-040)|Модуль поворотного энкодера KY-040 с 20 шагами на оборот.|
#### Примеры
##### [Кнопка](https://docs.wokwi.com/parts/wokwi-pushbutton)
[Пример](https://wokwi.com/projects/376384296063241217)
```c++
// Button Bounce counter
//
// Red button has bouncing simulation enabled,
// Blue button has bouncing simulation disabled.

#define BUTTON_PIN 4

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

int lastState = HIGH;
void loop() {
  int value = digitalRead(BUTTON_PIN);
  if (lastState != value) {
    lastState = value;
    if (value == HIGH) {
      Serial.println("Button released");
    }
    if (value == LOW) {
      Serial.println("Button pressed");
    }
  }
}

```

Предоставленный код представляет собой простой пример устранения дребезга кнопок в `Arduino` с использованием `C++`. Устранение дребезга кнопок - это метод, используемый для устранения ложных показаний, вызванных механическими переключателями или кнопками, которые могут вызывать множественные быстрые переходы между состояниями `HIGH` и `LOW` при нажатии или отпускании.

В этом коде у нас есть кнопка, подключенная к контакту `4` платы `Arduino`. Кнопка настроена как `INPUT_PULLUP`, что означает, что, когда кнопка не нажата, вывод внутренне переводится в состояние `HIGH`. Когда кнопка нажата, штифт переводится в `LOW` состояние.

Переменная `LastState` используется для отслеживания предыдущего состояния кнопки. В функции `loop()` мы читаем текущее состояние кнопки с помощью функции `digitalRead()`. Если текущее состояние отличается от предыдущего, это означает, что кнопка была нажата или отпущена.

Если текущее состояние `HIGH`, это означает, что кнопка отпущена, и мы печатаем "Кнопка отпущена" на последовательном мониторе. Если текущее состояние `LOW`, это означает, что кнопка была нажата, и мы печатаем `"Кнопка нажата"` на последовательном мониторе.

##### [Ползунковый переключатель](https://docs.wokwi.com/parts/wokwi-slide-switch)
Использование полузнкового переключателя для включения и выключения светодиода.
[Пример](https://wokwi.com/projects/376384660866004993)
```c++
// Define the pin numbers
const int LED_PIN = LED_BUILTIN;
const int SWITCH_PIN = 5;

void setup() {
  // Set the LED pin as an output
  pinMode(LED_PIN, OUTPUT);

  // Set the switch pin as an input with pull-up resistor enabled
  pinMode(SWITCH_PIN, INPUT_PULLUP);
}

void loop() {
  // Read the state of the switch
  int switchState = digitalRead(SWITCH_PIN);

  // Turn on the LED if the switch is pressed (LOW state)
  if (switchState == LOW) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }
}
```
Код представляет собой простую демонстрацию ползункового переключателя на плате `Arduino`. Он управляет светодиодом в зависимости от состояния переключателя. Вот как это работает:

В функции настройки код устанавливает вывод светодиода (`LED_PIN`) как выход, а контакт переключателя (`SWITCH_PIN`) как вход с включенным подтягивающим резистором. Эта конфигурация подготавливает контакты для считывания состояния переключателя и управления светодиодом.

В функции цикла код считывает состояние переключателя с помощью функции `digitalRead` и сохраняет его в переменной `switchState`.

Если переключатель нажат (состояние `LOW`), код устанавливает вывод светодиода в `HIGH` уровень с помощью функции `digitalWrite`. Это включит светодиод.

Если переключатель не нажат (состояние `HIGH`), код устанавливает вывод светодиода в состояние `LOW` с помощью функции `digitalWrite`. Это выключит светодиод.

 Использование одного полузункового переключателя для управления состоянием двух свтодиодов
 [Пример](https://wokwi.com/projects/376384674535243777)
```c++
const int LED_PIN = LED_BUILTIN;
const int SWITCH_PIN_1 = 5;
const int SWITCH_PIN_2 = 6;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(SWITCH_PIN_1, INPUT_PULLUP);
  pinMode(SWITCH_PIN_2, INPUT_PULLUP);
}

void loop() {
  digitalWrite(LED_PIN, digitalRead(SWITCH_PIN_1));
  digitalWrite(SWITCH_PIN_2, digitalRead(SWITCH_PIN_2));
}
```
`const int LED_PIN = LED_BUILTIN;` : эта строка создает постоянную переменную `LED_PIN` и назначает ее встроенному выводу светодиода на плате `Arduino`.

`const int SWITCH_PIN_1 = 5;` : Эта строка создает постоянную переменную `SWITCH_PIN_1` и присваивает ей значение 5.

`const int SWITCH_PIN_2 = 6;`: Эта строка создает постоянную переменную `SWITCH_PIN_2` и присваивает ей значение 6.

`void setup() { ... }` : это специальная функция в `Arduino`, которая автоматически вызывается один раз в начале программы. Он устанавливает режим вывода для `LED_PIN`, `SWITCH_PIN_1` и `SWITCH_PIN_2`. `pinMode` используется для указания того, будет ли вывод использоваться в качестве ввода или вывода.

`pinMode(LED_PIN, OUTPUT);`: В функции `setup()` эта строка устанавливает `LED_PIN` в качестве выходного контакта. Это означает, что `Arduino` может отправлять сигналы (высокие или низкие) для включения или выключения светодиода с помощью этого контакта.

`pinMode(SWITCH_PIN_1, INPUT_PULLUP);`: В функции `setup()` эта строка устанавливает `SWITCH_PIN_1` в качестве входного контакта с режимом подтягивающего резистора. Это означает, что Arduino будет считывать состояние переключателя, подключенного к этому выводу. Когда переключатель нажат, контакт будет подключен к земле.

`pinMode(SWITCH_PIN_2, INPUT_PULLUP);` : В функции `setup()` эта строка устанавливает `SWITCH_PIN_2` в качестве входного контакта с режимом подтягивающего резистора. Подобно `SWITCH_PIN_1`, он будет использоваться для чтения состояния другого коммутатора.

`void Loop() { ... }` : это еще одна специальная функция в `Arduino`, которая автоматически вызывается после `setup()`. Он запускается повторно, пока `Arduino` включен.

`digitalWrite(LED_PIN, digitalRead(SWITCH_PIN_1));` : В функции `loop()` эта строка считывает состояние `SWITCH_PIN_1` и устанавливает состояние `LED_PIN` в это значение. Это означает, что когда `SWITCH_PIN_1` подключен к земле (переключатель нажат), светодиод на `LED_PIN` загорится.

`digitalWrite(SWITCH_PIN_2, digitalRead(SWITCH_PIN_2));`: В функции `loop()` эта строка считывает состояние `SWITCH_PIN_2` и устанавливает состояние `SWITCH_PIN_2` в это значение. Кажется, в этой строке есть ошибка, так как она должна быть `digitalWrite(LED_PIN, digitalRead(SWITCH_PIN_2));` если намерение состоит в том, чтобы управлять светодиодом с помощью `SWITCH_PIN_2`.

Один свич два светодиода
[Пример](https://wokwi.com/projects/376384692587531265)
```c++
// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);                       // wait for a second
}
```
В функции `setup()` мы инициализируем вывод `LED_BUILTIN` как выходной, используя функцию `pinMode()`. Это устанавливает режим вывода на ВЫХОД, что позволяет нам управлять светодиодом, подключенным к этому выводу.

В функции `loop()` мы используем функцию `digitalWrite()` для включения светодиода, установив уровень напряжения на выводе `LED_BUILTIN` на `HIGH`. Затем мы используем функцию `delay()`, чтобы приостановить программу на 1 секунду.

После задержки мы снова используем `digitalWrite()`, чтобы выключить светодиод, установив уровень напряжения на выводе `LED_BUILTIN` на `LOW`. Затем у нас есть еще одна задержка в 1 секунду, прежде чем цикл повторится, в результате чего светодиод будет постоянно мигать.

Этот код можно использовать в качестве отправной точки для более сложных проектов `Arduino`, которые включают управление светодиодами или другими цифровыми выходами.

##### [DIP-переключатель 8](https://docs.wokwi.com/parts/wokwi-dip-switch-8)
DIP-переключатель 8 это механическое устройство, позволяющее установить одно из восьми возможных положений контактов. Это полезное устройство для управления различными функциями в проектах с Arduino.

DIP-переключатель 8 имеет восемь контактов, которые могут быть подключены к цифровым пинам Arduino. Каждый контакт может быть подключен либо к питанию (HIGH) для активации, либо к земле (LOW) для деактивации.

Для подключения DIP-переключателя 8 к Arduino выполните следующие шаги:

1.  Определите цифровые пины Arduino, к которым будут подключены контакты DIP-переключателя. Например, пины 2-9.
2.  Подключите первый контакт DIP-переключателя к пину 2, второй контакт к пину 3 и так далее.
3.  Подключите другой конец каждого контакта на DIP-переключателе к питанию (VCC) или земле (GND) на Arduino в зависимости от того, какое положение вы хотите установить.
4.  При необходимости, установите внутренние подтягивающие резисторы для каждого пина в режиме INPUT_PULLUP с помощью функции  `pinMode(pin, INPUT_PULLUP)`  в функции  `setup()`.
[Пример](https://wokwi.com/projects/376384858008800257)
```c++
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.println("PIND value:");

  for (int i = 0; i < 8; i++) {
    pinMode(i, INPUT_PULLUP);
  }
}

int previousValue = -1;

void loop() {
  int currentValue = PIND;

  if (currentValue != previousValue) {
    lcd.setCursor(6, 1);
    lcd.print(currentValue);
    lcd.print("   ");
    previousValue = currentValue;
  }
}
```

Пример использования DIP-8 для арифметических опреаций над цифрами в бинарном виде
```c++
// Required Libraries
#include <ShiftPWM.h>

// Pin Definitions
#define NUMBER1_PIN 2
#define NUMBER2_PIN 3
#define SHIFT_REGISTER_DATA_PIN 4
#define SHIFT_REGISTER_CLOCK_PIN 5
#define SHIFT_REGISTER_LATCH_PIN 6

// Variables
int number1;
int number2;
int result;

// ShiftPWM Object
ShiftPWM pwm;

void setup() {
  // Configure Arduino pins
  pinMode(NUMBER1_PIN, INPUT);
  pinMode(NUMBER2_PIN, INPUT);
  pinMode(SHIFT_REGISTER_DATA_PIN, OUTPUT);
  pinMode(SHIFT_REGISTER_CLOCK_PIN, OUTPUT);
  pinMode(SHIFT_REGISTER_LATCH_PIN, OUTPUT);

  // Initialize ShiftPWM
  pwm.Start(16);
}

void loop() {
  // Read the values of number1 and number2
  number1 = digitalRead(NUMBER1_PIN);
  number2 = digitalRead(NUMBER2_PIN);

  // Perform addition, subtraction, multiplication, and division operations
  result = number1 + number2;
  // result = number1 - number2;
  // result = number1 * number2;
  // result = number1 / number2;

  // Output the result to the serial monitor
  Serial.begin(9600);
  Serial.print("Result: ");
  Serial.println(result);

  // Display the result on the LEDs using the shift register
  pwm.SetOne(0, result & 0x01);
  pwm.SetOne(1, (result >> 1) & 0x01);
  pwm.SetOne(2, (result >> 2) & 0x01);
  pwm.SetOne(3, (result >> 3) & 0x01);
  pwm.SetOne(4, (result >> 4) & 0x01);
  pwm.SetOne(5, (result >> 5) & 0x01);
  pwm.SetOne(6, (result >> 6) & 0x01);
  pwm.SetOne(7, (result >> 7) & 0x01);

  // Update the shift register
  digitalWrite(SHIFT_REGISTER_LATCH_PIN, LOW);
  shiftOut(SHIFT_REGISTER_DATA_PIN, SHIFT_REGISTER_CLOCK_PIN, MSBFIRST, pwm.GetRegister());
  digitalWrite(SHIFT_REGISTER_LATCH_PIN, HIGH);
}
```
Чтобы выполнить операции сложения, вычитания, умножения и деления, вы можете раскомментировать соответствующие строки кода и закомментировать другие операции. Обязательно отрегулируйте номера контактов и другие переменные в соответствии с соединениями вашей схемы.

Для работы со сдвиговыми регистрами вы можете использовать библиотеку `ShiftPWM` или любую другую подобную библиотеку по вашему выбору. Обязательно установите библиотеку и включите ее в свой код.

Для работы с последовательным монитором вы можете настроить скорость передачи данных с помощью функции `Serial.begin()` и распечатать результаты операции с помощью функций `Serial.print()` или `Serial.println()`.

##### [Клавиатура](https://docs.wokwi.com/parts/wokwi-membrane-keypad)
Клавиатура является входным устройством, которое позволяет вводить данные в микроконтроллер Arduino. Использование клавиатуры с Arduino позволяет создать интерактивные проекты, такие как управление роботами, игры, парольные замки и другие системы с вводом данных.
###### Подключение клавиатуры

Клавиатура подключается к Arduino с использованием протокола PS/2 или USB. В случае протокола PS/2, вам понадобится адаптер для подключения клавиатуры к Arduino.

Для подключения клавиатуры с использованием протокола PS/2, выполните следующие шаги:

1.  Подключите клавиатуру к адаптеру PS/2.
2.  Подключите адаптер PS/2 к Arduino используя цифровые пины.
3.  Подключите VCC клавиатуры к 5V на Arduino.
4.  Подключите GND клавиатуры к GND на Arduino.

Для подключения клавиатуры с использованием протокола USB, выполните следующие шаги:

1.  Подключите USB кабель клавиатуры к USB-порту на Arduino.
2.  Если ваша клавиатура имеет дополнительные разъемы, проверьте документацию к вашей клавиатуре для необходимых подключений.
###### Использование клавиатуры

После успешного подключения клавиатуры к Arduino, вы можете использовать ее для считывания ввода и реагирования на нажатия клавиш.

Подключите клавиатуру к Arduino и выполните следующие шаги:

1.  Включите библиотеку Keyboard в верхней части кода:

```cpp
#include <Keyboard.h>

```

2.  В функции  `setup()`, вызовите функцию  `Keyboard.begin()`  для инициализации клавиатуры:

```cpp
void setup() {
  Keyboard.begin();
}

```

3.  В функции  `loop()`, используйте функцию  `Keyboard.write()`  для отправки символов на компьютер:

```cpp
void loop() {
  char character = 'A'; // Пример символа для отправки
  Keyboard.write(character);
}

```

4.  Загрузите код на Arduino и откройте программу, которая будет принимать ввод от клавиатуры. Вы должны видеть, что символ 'A' появляется в поле ввода программы.

###### Обработка нажатий клавиш

Помимо отправки символов на компьютер, вы также можете обрабатывать нажатия клавиш на Arduino и выполнить соответствующие действия.

1.  В функции  `loop()`, используйте функцию  `Keyboard.available()`  для проверки, есть ли доступные символы:

```cpp
void loop() {
  if (Keyboard.available()) {
    char character = Keyboard.read();
    // Обрабатывайте символ
  }
}

```

2.  Внутри блока кода, обрабатывайте символы в соответствии с вашей логикой:

```cpp
void loop() {
  if (Keyboard.available()) {
    char character = Keyboard.read();
    // Обрабатывайте символ
    if (character == 'A') {
      // Выполните действия для символа 'A'
    } else if (character == 'B') {
      // Выполните действия для символа 'B'
    }
  }
}

```

3.  Загрузите код на Arduino и проверьте, что ваша логика обрабатывает нажатия клавиш правильно.
[Пример](https://wokwi.com/projects/376450450215521281)
```c++
#include <Keypad.h>

const uint8_t ROWS = 4;
const uint8_t COLS = 4;
char keys[ROWS][COLS] = {
  { '1', '2', '3', 'A' },
  { '4', '5', '6', 'B' },
  { '7', '8', '9', 'C' },
  { '*', '0', '#', 'D' }
};

uint8_t colPins[COLS] = { 5, 4, 3, 2 }; // Pins connected to C1, C2, C3, C4
uint8_t rowPins[ROWS] = { 9, 8, 7, 6 }; // Pins connected to R1, R2, R3, R4

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

void setup() {
  Serial.begin(9600);
}

void loop() {
  char key = keypad.getKey();

  if (key != NO_KEY) {
    Serial.println(key);
  }
}
```
Этот код генерирует программу `Arduino`, которая использует библиотеку клавиатуры для считывания ввода с матричной клавиатуры `4x4`. Клавиатура состоит из `16` клавиш, расположенных в сетке `4х4`. Каждая клавиша представлена символом в массиве ключей.

Массив `colPins` определяет контакты `Arduino`, подключенные к столбцам клавиатуры, а массив `rowPins` определяет контакты, подключенные к строкам. Эти конфигурации контактов позволяют Arduino сканировать клавиатуру и определять, какая клавиша нажата.

В функции `setup()` программа инициализирует последовательную связь со скоростью `9600` бод. Это позволяет Arduino взаимодействовать с компьютером через последовательный порт.

Функция `loop()` постоянно проверяет нажатия клавиш, используя функцию `getKey()` из библиотеки клавиатуры. Если клавиша нажата, ее значение сохраняется в ключевой переменной. Затем программа проверяет, не равна ли ключевая переменная `NO_KEY`, что указывает на то, что произошло правильное нажатие клавиши. Если обнаружено правильное нажатие клавиши, программа печатает значение ключа на последовательном мониторе с помощью функции `Serial.println()`.

##### [Аналоговый джойстик](https://docs.wokwi.com/parts/wokwi-analog-joystick)
Джойстик - это устройство ввода, которое позволяет контролировать движение объектов в проектах с Arduino. Использование джойстика позволяет создавать интерактивные проекты, такие как игры, роботы и другие устройства, которые требуют точного управления.

###### Подключение джойстика

Джойстик обычно имеет 3 оси (X, Y, Z) и кнопку. Для подключения джойстика к Arduino, выполните следующие шаги:

1.  Подключите ось X джойстика к аналоговому пину на Arduino (например, A0).
2.  Подключите ось Y джойстика к аналоговому пину на Arduino (например, A1).
3.  Подключите кнопку джойстика к цифровому пину на Arduino (например, 2).
4.  Подключите GND джойстика к GND на Arduino.
5.  Подключите VCC (+5V) джойстика к 5V на Arduino.

###### Использование джойстика

После успешного подключения джойстика к Arduino, вы можете считывать его оси и состояние кнопки для контроля движения объектов в вашем проекте.

1.  В функции  `setup()`, установите режим кнопки джойстика как входной с подтягивающим резистором:

```cpp
void setup() {
  pinMode(2, INPUT_PULLUP);
}

```

2.  В функции  `loop()`, считывайте значения осей X и Y джойстика с помощью функции  `analogRead(pin)`:

```cpp
void loop() {
  int xValue = analogRead(A0);
  int yValue = analogRead(A1);
  // ...
}

```

3.  Обработайте значения осей X и Y с вашей логикой. Например, вы можете использовать их для управления движением робота или перемещения объекта на экране.

4.  Считывайте состояние кнопки джойстика с помощью функции  `digitalRead(pin)`:

```cpp
void loop() {
  int xValue = analogRead(A0);
  int yValue = analogRead(A1);
  int buttonState = digitalRead(2);
  // ...
}

```

5.  Обработайте состояние кнопки с вашей логикой. Например, вы можете использовать ее для выполнения определенных действий при нажатии кнопки.

[Пример](https://wokwi.com/projects/376460792695326721)
```c++
#define VERT_PIN A0
#define HORZ_PIN A1
#define SEL_PIN 2

void  setup()  {
	pinMode(VERT_PIN,  INPUT);
	pinMode(HORZ_PIN,  INPUT);
	pinMode(SEL_PIN,  INPUT_PULLUP);
	Serial.begin(115200);
}

void  loop()  {
	int vert =  analogRead(VERT_PIN);
	int horz =  analogRead(HORZ_PIN);
	bool selPressed =  digitalRead(SEL_PIN)  ==  LOW;
	Serial.print("Vertical: ");
	Serial.print(vert);
	Serial.print(" Horizontal: ");
	Serial.print(horz);
	Serial.print(" Pressed: ");
	Serial.println(selPressed);
	delay(1000);
}
```
Код определяет максимальное количество светодиодных модулей (MAX_DEVICES) и на основе этого значения вычисляет максимальные координаты X и Y светодиодной матрицы. Он также назначает номера контактов для контактов часов, данных и выбора микросхемы.

В функции setup() код инициализирует матрицу светодиодов, устанавливает яркость светодиодов на половину максимальной интенсивности и очищает матрицу.

Функция цикла() непрерывно считывает аналоговые входы с потенциометров, подключенных к вертикальным и горизонтальным выводам (VERT_PIN и HORZ_PIN). На основе считанных значений он соответственно обновляет текущие координаты X и Y (x и y).

Если значение по вертикали меньше 300, координата Y увеличивается на 1, но ограничивается максимальной координатой Y. Если значение по вертикали превышает 700, координата Y уменьшается на 1, но ограничивается 0. Аналогично, если значение по горизонтали превышает 700, координата X увеличивается на 1, но ограничивается максимальной координатой X. Если горизонтальное значение ниже 300, координата X уменьшается на 1, но ограничивается 0.

Если кнопка, подключенная к контакту выбора (SEL_PIN), нажата (LOW), светодиодная матрица очищается.

Наконец, код устанавливает светодиод в текущих координатах X и Y для включения (истина), обновляет матрицу светодиодов и добавляет задержку в 100 миллисекунд перед повторением цикла.

##### [Ползунковый потенциометр](https://docs.wokwi.com/parts/wokwi-slide-potentiometer)
Потенциометр - это электронный компонент, который позволяет регулировать напряжение или сопротивление. Использование потенциометра с Arduino позволяет создавать проекты, в которых можно регулировать параметры, такие как яркость светодиодов, скорость двигателей, частота звуков и т.д.

###### Подключение потенциометра

Потенциометр имеет 3 вывода: верхний вывод (VCC), средний вывод (связанный с перемещением регулятора потенциометра) и нижний вывод (GND). Для подключения потенциометра к Arduino, выполните следующие шаги:

1.  Подключите верхний вывод потенциометра (VCC) к 5V на Arduino.
2.  Подключите средний вывод потенциометра к аналоговому пину на Arduino (например, A0).
3.  Подключите нижний вывод потенциометра (GND) к GND на Arduino.

##### Использование потенциометра

После успешного подключения потенциометра к Arduino, вы можете считывать значение его положения и использовать его для регулировки параметров в вашем проекте.

1.  В функции  `setup()`, установите режим среднего вывода потенциометра как входной:

```cpp
void setup() {
  pinMode(A0, INPUT);
}

```

2.  В функции  `loop()`, считывайте значение положения потенциометра с помощью функции  `analogRead(pin)`:

```cpp
void loop() {
  int potValue = analogRead(A0);
  // ...
}

```

3.  Используйте значение положения потенциометра с вашей логикой. Например, вы можете использовать его для регулировки яркости светодиода:

```cpp
void loop() {
  int potValue = analogRead(A0);
  int brightness = map(potValue, 0, 1023, 0, 255); // Преобразование значения положения в диапазон яркости (0-255)
  analogWrite(LED_PIN, brightness); // Установка яркости светодиода
}

```

4.  Загрузите код на Arduino и проверьте, что ваша логика регулирует параметры в соответствии с положением потенциометра.

Управление двигателем.
```c++
#include <Servo.h>

Servo myservo;  // create servo object to control a servo

int potpin = 0;  // analog pin used to connect the potentiometer
int val;    // variable to read the value from the analog pin

void setup() {
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  val = analogRead(potpin);            // reads the value of the potentiometer (value between 0 and 1023)
  val = map(val, 0, 1023, 0, 180);     // scale it to use it with the servo (value between 0 and 180)
  myservo.write(val);                  // sets the servo position according to the scaled value
  delay(15);                           // waits for the servo to get there
}
```
Во-первых, мы включаем библиотеку `Servo`, которая предоставляет функции для управления серводвигателем. Мы создаем экземпляр класса `Servo` под названием `myservo` для управления сервоприводом.

Далее мы определяем переменную `potpin` для хранения номера аналогового контакта, к которому подключен потенциометр. Мы также объявляем переменную `val` для хранения значения, считываемого с потенциометра.

В функции `setup()` мы подключаем серводвигатель к контакту `9` с помощью функции `Attach()`.

В функции `loop()` мы считываем значение с потенциометра с помощью функции `AnalogRead()`. Эта функция возвращает значение `от 0 до 1023`, представляющее уровень напряжения на аналоговом выводе. Затем мы используем функцию `map()` для масштабирования этого значения в диапазоне `от 0 до 180`, который представляет собой диапазон положений, в которые может перемещаться серводвигатель. Наконец, мы используем функцию `write()`, чтобы установить положение сервопривода в соответствии с масштабированным значением.

Мы добавляем небольшую задержку в 15 миллисекунд, используя функцию `delay()`, чтобы позволить серводвигателю достичь желаемого положения перед считыванием следующего значения с потенциометра.

##### [Поворотный энкодер (KY-040)](https://docs.wokwi.com/parts/wokwi-ky-040)
Поворотный энкодер - это устройство, которое преобразует механическое вращение в электрический сигнал. Он обычно используется для измерения угла поворота или смещения. Поворотный энкодер состоит из двух основных компонентов: вала, который вращается с физическим объектом, и оборудования, которое генерирует электрический сигнал в зависимости от положения вала.

Arduino позволяет подключать и использовать поворотные энкодеры для измерения и управления угловым положением объектов. В этом конспекте мы рассмотрим базовые шаги по подключению и использованию поворотного энкодера с Arduino.

###### Подключение поворотного энкодера

Поворотные энкодеры имеют обычно три вывода: две линии энкодера (A и B) и общий вывод (GND). Для подключения поворотного энкодера к Arduino, выполните следующие шаги:

1.  Подключите линию энкодера A к цифровому пину Arduino.
2.  Подключите линию энкодера B к другому цифровому пину Arduino.
3.  Подключите общий вывод (GND) поворотного энкодера к GND на Arduino.

###### Использование поворотного энкодера

После подключения поворотного энкодера к Arduino, вы можете использовать библиотеку  `RotaryEncoder`  для работы с ним. Вот пример кода для получения угла поворота энкодера с помощью этой библиотеки:Copy

```c++
#include <RotaryEncoder.h>

// Подключение линии энкодера A к пину 2
// Подключение линии энкодера B к пину 3
RotaryEncoder encoder(2, 3);

void setup() {
  Serial.begin(9600);
}

void loop() {
  // Получение значения угла поворота энкодера
  int angle = encoder.read();

  // Вывод значения угла в монитор порта
  Serial.println(angle);

  delay(100);
}

```

В этом примере мы подключаем линию энкодера `A` к пину `2` и линию энкодера `B` к пину `3`. Затем мы создаем экземпляр класса  `RotaryEncoder`  и используем метод  `read()`  для получения значения угла поворота энкодера. Значение угла выводится в монитор порта каждые 100 миллисекунд.

```c++
#define ENCODER_CLK 2
#define ENCODER_DT  3

void setup() {
  Serial.begin(115200);
  pinMode(ENCODER_CLK, INPUT);
  pinMode(ENCODER_DT, INPUT);
}

int lastClk = HIGH;

void loop() {
  int newClk = digitalRead(ENCODER_CLK);
  if (newClk != lastClk) {
    // There was a change on the CLK pin
    lastClk = newClk;
    int dtValue = digitalRead(ENCODER_DT);
    if (newClk == LOW && dtValue == HIGH) {
      Serial.println("Rotated clockwise >>");
    }
    if (newClk == LOW && dtValue == LOW) {
      Serial.println("Rotated counterclockwise <<");
    }
  }
}
```

## Двигатели
Управление двигателями является важной частью многих проектов, которые используют `Arduino`. Возможность управлять двигателями позволяет создавать различные виды проектов, включая роботов, автоматические системы и другие устройства, требующие движения.

`Arduino` имеет несколько способов управления двигателями, включая использование цифровых и аналоговых пинов, а также использование специализированных модулей. Каждый из этих способов имеет свои преимущества и подходит для разных видов двигателей и требуемой функциональности.

В этом конспекте мы рассмотрим основные методы управления двигателями с использованием Arduino. Мы покажем, как подключить и настроить двигатели, а также приведем примеры кода для различных сценариев управления двигателями.

Управление двигателями с Arduino открывает широкие возможности для создания интересных и уникальных проектов. Если вы интересуетесь робототехникой, автоматизацией или просто хотите научиться управлять двигателями, этот конспект будет полезным введением в тему. Далее мы рассмотрим базовые шаги и код для старта вашего проекта управления двигателями с `Arduino`.
Arduino позволяет управлять двигателями различных типов, от простых DC-моторов до шаговых и сервоприводов. Управление двигателями с помощью Arduino открывает широкие возможности для создания различных проектов, включая роботику, автоматизацию и многое другое. В этом конспекте мы рассмотрим основные методы управления различными типами двигателей с помощью Arduino.

### Управление DC-моторами

DC-моторы - самые простые и распространенные типы двигателей. Они имеют два вывода: один для питания (обычно 5-12 В) и другой для управления направлением вращения. Для управления DC-моторами с помощью Arduino, вы можете использовать модуль моторного контроллера или создать свою собственную схему, используя транзисторы и резисторы. В любом случае, подключение и управление DC-моторами осуществляется с использованием цифровых пинов Arduino.

1.  Подключите DC-мотор к модулю моторного контроллера или к своей схеме управления.
2.  Подключите питание модуля моторного контроллера (обычно 5-12 В) к внешнему источнику питания.
3.  Подключите сигнальные пины модуля моторного контроллера к цифровым пинам Arduino.
4.  В программе Arduino, используйте функции  `pinMode()`  и  `digitalWrite()`  для управления пинами модуля моторного контроллера и контроля направления и скорости вращения DC-мотора.

### Управление шаговыми двигателями

Шаговые двигатели обладают отличными характеристиками, идеально подходящими для управления точными движениями. Они имеют несколько выводов, каждый из которых управляет определенным шагом двигателя. Для управления шаговыми двигателями с использованием Arduino, вы можете использовать специальные драйверы шаговых двигателей, такие как A4988 или DRV8825.

1.  Подключите шаговой двигатель к драйверу шагового двигателя.
2.  Подключите питание драйвера шагового двигателя (обычно 5-12 В) к внешнему источнику питания.
3.  Подключите сигнальные пины драйвера шагового двигателя к цифровым пинам Arduino.
4.  В программе Arduino, используйте библиотеку  `Stepper`  и создайте экземпляр класса  `Stepper`, указав количество шагов и пины управления.
5.  Используйте методы  `setSpeed()`  и  `step()`  для установки скорости двигателя и выполнения шагов.

### Управление сервоприводами

Сервоприводы - это компактные устройства, обеспечивающие точное позиционирование. Они имеют три вывода: питание (обычно 5 В), общий GND и пин управления. Для управления сервоприводами с использованием Arduino, вы можете использовать библиотеку  `Servo`, которая предоставляет простой интерфейс для работы с сервоприводами.

1.  Подключите сервопривод к Arduino, подключив питание к 5 В, GND к GND и пин управления к цифровому пину.
2.  В программе Arduino, подключите библиотеку  `Servo`  и создайте экземпляр класса  `Servo`.
3.  Используйте метод  `attach()`  для привязки сервопривода к цифровому пину.
4.  Используйте методы  `write()`  или  `writeMicroseconds()`  для установки угла поворота сервопривода.

### Моторы

|Название|Описание|
|-|-|
|[Микросервомотор](https://docs.wokwi.com/parts/wokwi-servo)|Стандартный микросервомотор|
|[Биполярный шаговый двигатель](https://docs.wokwi.com/parts/wokwi-stepper-motor)|Биполярный шаговый двигатель|
|[A4988](https://docs.wokwi.com/parts/wokwi-a4988)|Драйвер шагового двигателя A4988|
|[Двухосный шаговый двигатель](https://docs.wokwi.com/parts/wokwi-biaxial-stepper)|Концентрический двухосный шаговый двигатель, содержащий два шаговых двигателя, упакованных в один корпус|

#### Примеры
##### [Микросервомотор](https://docs.wokwi.com/parts/wokwi-servo)

```c++
#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position

void setup() {
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  sweepServo(0, 180, 1); // sweep from 0 to 180 degrees
  sweepServo(180, 0, -1); // sweep from 180 to 0 degrees
}

void sweepServo(int start, int end, int step) {
  for (pos = start; pos != end; pos += step) {
    myservo.write(pos); // tell servo to go to position in variable 'pos'
    delay(15); // waits 15ms for the servo to reach the position
  }
}
```

- Приведенный код является примером управления серводвигателем с помощью платы `Arduino`. Он использует библиотеку `Servo` для создания сервообъекта и управления его положением.

- В функции настройки сервообъект прикрепляется к контакту `9` платы `Arduino` с помощью метода `Attach`.

- В функции `loop` функция `SweepServo` вызывается дважды. Первый вызов меняет сервопривод от 0 до 180 градусов с шагом 1, а второй вызов меняет сервопривод от 180 до 0 градусов с шагом -1.

Функция `SweepServo` делает код более модульным и простым для понимания. Он выделяет логику развертки сервопривода в отдельную функцию, делая код более читабельным и удобным в сопровождении.

##### [Биполярный шаговый двигатель](https://docs.wokwi.com/parts/wokwi-stepper-motor)
Двухфазный шаговый двигатель (Bipolar Stepper Motor) - это тип двигателя, который может выполнять точные пошаговые движения. Он состоит из двух фаз, каждая из которых имеет свою намотку, что позволяет управлять точным положением и скоростью вращения. Arduino позволяет управлять двухфазным шаговым двигателем, подключая его к соответствующему драйверу и используя специальную библиотеку.

###### Подключение двухфазного шагового двигателя к Arduino

Для подключения двухфазного шагового двигателя к Arduino, выполните следующие шаги:

1.  Подключите драйвер шагового двигателя (например, A4988 или DRV8825) к Arduino, подключив питание (обычно 5-12 В) к внешнему источнику питания и GND к GND Arduino.
2.  Подключите пины направления (DIR) и шага (STEP) драйвера шагового двигателя к соответствующим пинам Arduino.
3.  Подключите выводы фаз двухфазного шагового двигателя (обычно помечены как A и B) к выходам драйвера шагового двигателя. Обратите внимание, что порядок подключения проводов фаз может влиять на направление вращения двигателя.

###### Управление двухфазным шаговым двигателем с помощью Arduino

С помощью Arduino и специальной библиотеки  `Stepper`  вы можете управлять двухфазным шаговым двигателем. Вот пример кода для поворота двигателя вперед и назад:

```c++
#include <Stepper.h>

// Определение количества шагов на один оборот двигателя
const int stepsPerRevolution = 200;

// Подключение пинов шага и направления к Arduino
const int stepPin = 2;
const int dirPin = 3;

// Создание экземпляра класса Stepper
Stepper myStepper(stepsPerRevolution, stepPin, dirPin);

void setup() {
  // Настройка скорости двигателя
  myStepper.setSpeed(60);
}

void loop() {
  // Вращение двигателя вперед на один оборот
  myStepper.step(stepsPerRevolution);
  delay(1000);

  // Вращение двигателя назад на половину оборота
  myStepper.step(-stepsPerRevolution / 2);
  delay(1000);
}
```

В этом примере мы подключаем пин шага (`STEP`) шагового двигателя к пину `2` `Arduino` и пин направления (`DIR`) к пину `3` `Arduino`. Затем мы создаем экземпляр класса  `Stepper`  с указанием количества шагов на один оборот и пинов управления. В методе  `setup()`  мы устанавливаем скорость двигателя, а в методе  `loop()`  мы выполняем повороты вперед и назад с помощью метода  `step()`.

##### [A4988](https://docs.wokwi.com/parts/wokwi-a4988)
A4988 - это популярный драйвер шагового двигателя, который позволяет управлять шаговыми двигателями с высокой точностью и контролируемостью. Он широко используется в различных промышленных и робототехнических приложениях. A4988 позволяет подключать и управлять двумя фазами шагового двигателя и контролировать его скорость, направление и шаговый режим.

###### Подключение драйвера A4988 к Arduino

Для подключения драйвера A4988 к Arduino, выполните следующие шаги:

1.  Питание: Подключите питание (обычно 5-12 В) к пинам VCC и GND на драйвере A4988. Обратите внимание, что напряжение питания должно быть совместимо с требованиями вашего шагового двигателя.

2.  Шаговые и направляющие пины: Подключите пины шага (STEP) и направления (DIR) на драйвере A4988 к соответствующим пинам Arduino. Эти пины позволяют управлять скоростью и направлением вращения шагового двигателя.

3.  Управление микрошагами: Драйвер A4988 также поддерживает функцию микрошага, которая позволяет улучшить контроль и плавность движения шагового двигателя. Для включения или отключения микрошага используйте пины MS1, MS2 и MS3 на драйвере A4988. Выбор определенного режима микрошага определяется сочетанием состояний этих пинов.

###### Использование драйвера A4988 с Arduino

Для управления шаговым двигателем с помощью драйвера A4988 и Arduino можно использовать специальную библиотеку  `AccelStepper`. Вот пример кода, демонстрирующий простейший способ управления двигателем с помощью A4988:

```c++
#include <AccelStepper.h>

// Определение пинов шага и направления
const int stepPin = 2;
const int dirPin = 3;

// Создание экземпляра класса AccelStepper
AccelStepper stepper(1, stepPin, dirPin);

void setup() {
  // Установка начальной скорости и длины шага
  stepper.setMaxSpeed(1000);
  stepper.setSpeed(500);
}

void loop() {
  // Вращение двигателя на один оборот вперед
  stepper.move(200);
  stepper.runToPosition();
  delay(1000);

  // Вращение двигателя на половину оборота назад
  stepper.move(-100);
  stepper.runToPosition();
  delay(1000);
}

```

В этом примере мы создаем экземпляр класса  `AccelStepper`  и указываем пины шага и направления. Затем мы устанавливаем максимальную скорость и длину шага с помощью методов  `setMaxSpeed()`  и  `setSpeed()`.

В методе  `loop()`  мы используем методы  `move()`  и  `runToPosition()`  для выполнения движения шагового двигателя. Метод  `move()`  указывает на количество шагов, на которое нужно повернуть двигатель, а метод  `runToPosition()`  запускает двигатель и ожидает, пока он не достигнет целевой позиции. Между поворотами двигателя мы добавляем задержку с помощью функции  `delay()`.
##### [Двухосный шаговый двигатель](https://docs.wokwi.com/parts/wokwi-biaxial-stepper)
Двухосный шаговый двигатель (Two-Axis Stepper Motor) - это тип двигателя, который может выполнять точные пошаговые движения вдоль двух осей одновременно. Он состоит из двух независимых шаговых двигателей, каждый из которых контролирует движение по одной из осей. Arduino позволяет управлять двухосным шаговым двигателем, подключая его к соответствующим драйверам и используя специальные библиотеки.

###### Подключение двухосного шагового двигателя к Arduino

Для подключения двухосного шагового двигателя к Arduino, выполните следующие шаги:

1.  Подключите драйверы шагового двигателя (например, A4988 или DRV8825) к Arduino, подключив питание (обычно 5-12 В) к внешнему источнику питания и GND к GND Arduino.
2.  Подключите пины направления (DIR) и шага (STEP) каждого драйвера шагового двигателя к соответствующим пинам Arduino.
3.  Подключите выводы фаз двухосного шагового двигателя (обычно помечены как A и B для первой оси и C и D для второй оси) к выходам соответствующих драйверов шагового двигателя. Обратите внимание, что порядок подключения проводов фаз может влиять на направление движения каждой из осей.

###### Управление двухосным шаговым двигателем с помощью Arduino

С помощью Arduino и специальных библиотек, таких как  `AccelStepper`, вы можете управлять двухосным шаговым двигателем. Вот пример кода для управления движением каждой оси независимо:Copy

```c++
#include  <Stepper.h>
const  int stepsPerRevolution =  200;

Stepper stepper1(stepsPerRevolution,  2,  3,  4,  5);
Stepper stepper2(stepsPerRevolution,  8,  9,  10,  11);

void  setup()  {
	// set the speed at 20 rpm for one stepper, 90 rpm for another:
	stepper1.setSpeed(20);
	stepper2.setSpeed(90);
	// initialize the serial port:
	Serial.begin(9600);
}

void  loop()  {
	// step one revolution in one direction:
	Serial.println("clockwise");
	stepper1.step(stepsPerRevolution);
	stepper2.step(stepsPerRevolution);
	delay(500);

	// step one revolution in the other direction:

	Serial.println("counterclockwise");
	stepper1.step(-stepsPerRevolution);
	stepper2.step(-stepsPerRevolution);
	delay(500);
}
```

В этом примере мы создаем экземпляры класса  `Stepper`  для каждой оси и указываем пины шага и направления. Затем мы устанавливаем максимальную скорость и длину шага для каждой оси с помощью методов  `setMaxSpeed()`  и  `setSpeed()`.

В методе  `loop()`  мы используем методы  `move()`  и  `runToPosition()`  для выполнения движения каждой оси независимо. Метод  `move()`  указывает на количество шагов, на которое нужно переместить ось, а метод  `runToPosition()`  запускает двигатель и ожидает, пока он не достигнет целевой позиции. Между перемещениями каждой оси мы добавляем задержку с помощью функции  `delay()`.

## Дополнительные материалы

[Подробнее про функции библиотеки TFT](https://wikihandbk.com/wiki/Arduino:%D0%91%D0%B8%D0%B1%D0%BB%D0%B8%D0%BE%D1%82%D0%B5%D0%BA%D0%B8/TFT)
[Большая статья на Амперке, посвященная библиотеке UTFT](http://wiki.amperka.ru/%D0%BF%D1%80%D0%BE%D0%B4%D1%83%D0%BA%D1%82%D1%8B:tft-lcd-240x320)
[LCDWIKI3](http://www.lcdwiki.com/1.44inch_SPI_Module_ST7735S_SKU:MSP1443)
[Документация](https://docs.wokwi.com/parts/wokwi-ili9341)
[Пример](https://wokwi.com/projects/377635992487870465)